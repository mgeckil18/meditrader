//! Institutional wholesale market (kapan, K-013), competitive retail (K-016), urban demand (LES + CES), producer pools.

use super::*;
use crate::consts::{goods5, CAT_GOODS, CUSTOMS, N_CATS, WAGE};
use crate::pymath::{max, min, pow};

const LEVELS: [f64; 8] = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5];

#[derive(Clone, Copy)]
enum Who {
    Shop(usize),
    Storer(usize),
    MBuy(usize),
    MSell(usize),
    Pool(usize),
    PInput(usize),
    Farm,
}

impl Core {
    /// Lerner rule under logit competition mu_i = 1/(eps_i - 1) (Anderson, de Palma & Thisse 1992).
    pub fn set_markups(&mut self, mi: usize) {
        let cfg = &self.cfg;
        for s in self.markets[mi].shops.iter_mut() {
            let eps = cfg.retail_beta * (1.0 - s.share) + cfg.market_elasticity * s.share;
            let mu = if eps > 1.0 { 1.0 / (eps - 1.0) } else { cfg.markup_max };
            s.markup = min(cfg.markup_max, max(cfg.markup_min, mu));
        }
    }

    pub fn retail_prices(&mut self, mi: usize) {
        if let Some(q) = self.kapan_quote[mi] {
            let d = self.cfg.retail_cost_days;
            for s in self.markets[mi].shops.iter_mut() {
                s.cost_ref += (q - s.cost_ref) / d;
                s.mid = s.cost_ref;
            }
        }
        self.set_markups(mi);
    }

    /// Derived demand: a shop's stepped buy orders in the kapan (price, quantity).
    fn shop_schedule(&self, s: &crate::market::Shop) -> Vec<(f64, f64)> {
        let eps = self.cfg.market_elasticity;
        let base = s.target_cover_days * s.request_rate;
        let rf = s.req_price / (1.0 + s.markup);
        let gaps: Vec<f64> =
            LEVELS.iter().map(|&m| max(0.0, min(s.room_mult * base, base * pow(m, -eps)) - s.stock)).collect();
        let mut out = Vec::new();
        for (k, &m) in LEVELS.iter().enumerate() {
            let q = gaps[k] - if k + 1 < gaps.len() { gaps[k + 1] } else { 0.0 };
            if q > 1e-9 {
                out.push((rf * m, q));
            }
        }
        if self.cfg.budget_bids {
            let mut left = s.cash;
            let mut capped = Vec::new();
            let mut idx: Vec<usize> = (0..out.len()).collect();
            idx.sort_by(|&a, &b| (-out[a].0).partial_cmp(&-out[b].0).unwrap());
            for i in idx {
                let (pr, q) = out[i];
                let q = min(q, left / max(pr, 1e-9));
                if q > 1e-9 {
                    capped.push((pr, q));
                    left -= q * pr;
                }
            }
            out = capped;
        }
        out
    }

    /// Customers go to their usual shop (share); if it has no goods they search from the cheapest.
    fn buy_compete(&mut self, mi: usize, qty: f64) -> (f64, f64) {
        let mk = &mut self.markets[mi];
        let (mut bought, mut paid) = (0.0, 0.0);
        let mut unmet = 0.0;
        for s in mk.shops.iter_mut() {
            let req = qty * s.share;
            s.requests_today += req;
            let q = min(req, s.stock);
            s.stocked_out = q < req - 1e-9;
            s.unmet_frac = if req > 0.0 { (req - q) / req } else { 0.0 };
            unmet += req - q;
            if q > 0.0 {
                let pay = pymath::round(q * s.ask()) as f64;
                s.op_profit += pay - q * s.cost_ref;
                s.cash += pay;
                s.stock -= q;
                bought += q;
                paid += pay;
            }
        }
        for i in mk.sorted_shops(|s| s.ask(), false) {
            if unmet <= 1e-9 {
                break;
            }
            let s = &mut mk.shops[i];
            s.requests_today += unmet;
            let q = min(unmet, s.stock);
            if q <= 0.0 {
                continue;
            }
            let pay = pymath::round(q * s.ask()) as f64;
            s.op_profit += pay - q * s.cost_ref;
            s.cash += pay;
            s.stock -= q;
            unmet -= q;
            bought += q;
            paid += pay;
        }
        (bought, paid)
    }

    /// Target share: logit (p_i^-beta) among shops with goods; approached with inertia.
    pub fn update_shares(&mut self, mi: usize) {
        let cfg = &self.cfg;
        let mk = &mut self.markets[mi];
        let ok: Vec<usize> = (0..mk.shops.len()).filter(|&i| !mk.shops[i].stocked_out).collect();
        if ok.is_empty() {
            return;
        }
        let pmin = pymath::min_iter(ok.iter().map(|&i| mk.shops[i].ask())).unwrap();
        let mut w = vec![None; mk.shops.len()];
        for &i in &ok {
            w[i] = Some(pow(pmin / mk.shops[i].ask(), cfg.retail_beta));
        }
        let tot = pymath::sum(ok.iter().map(|&i| w[i].unwrap()));
        for (i, s) in mk.shops.iter_mut().enumerate() {
            let target = w[i].unwrap_or(0.0) / tot;
            s.share += (target - s.share) / cfg.retail_inertia_days;
            if !s.stocked_out {
                s.peak_paid = max(s.peak_paid * (1.0 - 1.0 / 365.0), s.ask());
            }
            if cfg.price_discovery && s.stocked_out {
                s.req_price = min(s.req_price * (1.0 + s.max_daily_move * s.unmet_frac), max(s.req_price, s.peak_paid));
            } else {
                s.req_price += (s.ask() - s.req_price) / s.request_memory_days;
            }
        }
        let z = pymath::sum(mk.shops.iter().map(|s| s.share));
        for s in mk.shops.iter_mut() {
            s.share /= z;
        }
    }

    /// S-025: share of discretionary buyers remaining at price p, relative to the reference price: min(1, S(p)/S(p_ref)).
    pub fn wtp_factor(&self, k: usize, c: usize, p: f64) -> f64 {
        let Some(w) = &self.cfg.wtp else { return 1.0 };
        if !w.cats.contains(&c) {
            return 1.0;
        }
        let p_ref = if c == 0 { 1.0 } else { goods5(CAT_GOODS[c].unwrap()).reff };
        let mu = pymath::log(w.median[k] * p_ref);
        let surv = |x: f64| 0.5 * (1.0 - pymath::erf((pymath::log(x) - mu) / (w.sigma * std::f64::consts::SQRT_2)));
        let s0 = surv(p_ref);
        if s0 <= 1e-12 {
            return 0.0;
        }
        // budget limit: discretionary spending cannot exceed beta*s (more buyers when cheaper, but the budget is fixed)
        min(1.0, surv(p) / s0)
    }

    /// `_urban(port, asks)`: the port's class-based demand (LES + CES, sigma = 2).
    pub fn urban(&mut self, port: Port, asks: &[(Good, f64)]) {
        let sig = 2.0;
        let pr = |g: Good| asks.iter().find(|x| x.0 == g).map(|x| x.1);
        // want: WHT, BRL, OIL, WIN, CLC, CLF, PEP
        let order = [Good::WHT, Good::BRL, Good::OIL, Good::WIN, Good::CLC, Good::CLF, Good::PEP];
        let mut want = [0.0f64; 7];
        let widx = |g: Good| order.iter().position(|&x| x == g).unwrap();
        for (ki, k) in self.cls[port].iter().enumerate() {
            let y = max(self.income_ref[port][ki], 0.0);
            let cer: Vec<(usize, f64)> =
                [Good::WHT, Good::BRL].iter().enumerate().filter_map(|(j, &c)| pr(c).map(|p| (j, p))).collect();
            let den = pymath::sum(cer.iter().map(|&(j, p)| k.a[j] * pow(p, 1.0 - sig)));
            let mut pcat = [f64::INFINITY; N_CATS];
            pcat[0] = pow(den, 1.0 / (1.0 - sig));
            for c in 1..N_CATS {
                pcat[c] = pr(CAT_GOODS[c].unwrap()).unwrap_or(f64::INFINITY);
            }
            let avail: Vec<usize> = (0..N_CATS).filter(|&c| pcat[c] < f64::INFINITY).collect();
            let s = y - pymath::sum(avail.iter().map(|&c| pcat[c] * k.gamma[c]));
            let mut e = [0.0; N_CATS];
            if s >= 0.0 {
                for &c in &avail {
                    e[c] = pcat[c] * k.gamma[c] + k.beta[c] * s * self.wtp_factor(ki, c, pcat[c]);
                }
            } else {
                let f = y / max(pymath::sum(avail.iter().map(|&c| pcat[c] * k.gamma[c])), 1e-9);
                for &c in &avail {
                    e[c] = pcat[c] * k.gamma[c] * f;
                }
            }
            for &(j, p) in &cer {
                let g = [Good::WHT, Good::BRL][j];
                want[widx(g)] += e[0] * k.a[j] * pow(p, 1.0 - sig) / den / p;
            }
            for &c in &avail[1..] {
                want[widx(CAT_GOODS[c].unwrap())] += e[c] / pcat[c];
            }
        }
        for (wi, &g) in order.iter().enumerate() {
            let Some(mi) = self.mi(port, g) else { continue };
            let (b, paid) = self.buy_compete(mi, want[wi]);
            self.ledger.money_source("urban_consumers", paid);
            self.ledger.goods_sink(g, "consumption", b);
        }
    }

    /// Producer pools: production, input use, capacity (trading happens in the kapan).
    pub fn pools_step(&mut self) {
        let mut wages = PortMap::default();
        for &p in &self.port_list {
            wages.set(p, 0.0);
        }
        let first_of_month = self.date.day() == 1;
        for pi in 0..self.pools.len() {
            let (p, g) = self.pools[pi].0;
            let in_ask: Vec<(Good, f64)> =
                self.pools[pi].1.recipe.inputs.iter().map(|&(i, _)| (i, self.best_ask(self.mix(p, i)))).collect();
            let omi = self.mix(p, g);
            let bids: Vec<f64> = self.markets[omi].shops.iter().map(|s| s.bid()).collect();
            let out_bid = pymath::np_mean(&bids);
            let pool = &mut self.pools[pi].1;
            let unit_cost =
                pymath::sum(pool.recipe.inputs.iter().map(|&(i, q)| q * in_ask.iter().find(|x| x.0 == i).unwrap().1))
                    + pool.recipe.labor * WAGE;
            let margin = (out_bid - unit_cost) / out_bid;
            let mut q = pool.rate();
            for &(i, a) in &pool.recipe.inputs.clone() {
                q = min(q, pool.input(i) / a);
            }
            q = max(0.0, min(q, pool.cash / (pool.recipe.labor * WAGE)));
            if q > 0.0 {
                for &(i, a) in &pool.recipe.inputs.clone() {
                    *pool.input_mut(i) -= q * a;
                    self.ledger.goods_sink(i, "production_input", q * a);
                }
                pool.output += q;
                self.ledger.goods_source(g, "production", q);
                let w = pymath::round(q * pool.recipe.labor * WAGE) as f64;
                pool.cash -= w;
                wages[p] += w;
                self.ledger.money_sink("wages", w);
            }
            let stock_days = pool.output / max(pool.rate(), 1e-9);
            let f = if stock_days < 15.0 {
                1.0
            } else if stock_days < 30.0 {
                0.85
            } else {
                0.7
            };
            pool.reservation = unit_cost * f;
            let desired = 0.85 + 2.0 * (margin - pool.margin_target) - 0.02 * (stock_days - 10.0);
            pool.util += pool.util_speed * (min(1.0, max(0.1, desired)) - pool.util);
            pool.util_hist.push(pool.util);
            if first_of_month && pool.util_hist.len() >= 90 {
                let u = pymath::np_mean(&pool.util_hist[pool.util_hist.len() - 90..]);
                if u > 0.92 && margin > pool.margin_target {
                    pool.capacity *= 1.01;
                } else if u < 0.6 {
                    pool.capacity *= 0.99;
                }
            }
            let excess = pool.cash - 90.0 * pool.rate() * unit_cost;
            if excess > 0.0 {
                let d = pymath::int(excess * 0.01) as f64;
                pool.cash -= d;
                self.ledger.money_sink("producer_dividends", d);
            }
        }
        self.wage_yday = wages;
    }
}

impl World {
    /// `_kapan(p, g)`: daily wholesale clearing; a single price (intersection of the demand and supply curves).
    pub(super) fn kapan(&mut self, mi: usize) {
        let c = &mut self.core;
        let cfg = &c.cfg;
        let (p, g) = c.market_keys[mi];
        let dth = c.markets[mi].days_to_harvest();
        let mut buys: Vec<(f64, f64, Who)> = Vec::new();
        let mut sells: Vec<(f64, f64, Who)> = Vec::new();
        for (si, s) in c.markets[mi].shops.iter().enumerate() {
            for (pr, q) in c.shop_schedule(s) {
                buys.push((pr, q, Who::Shop(si)));
            }
        }
        for (ti, st) in c.markets[mi].storers.iter().enumerate() {
            if st.stock > 0.0 {
                sells.push((st.sell_floor(), st.stock, Who::Storer(ti)));
            }
            let q = st.buy_room(st.bid());
            if q > 0.0 {
                buys.push((st.bid(), q, Who::Storer(ti)));
            }
        }
        for (i, m) in self.merchants.iter().enumerate() {
            if m.loc != p {
                continue;
            }
            if m.state == MState::Selling && m.good == Some(g) && m.qty > 0.0 {
                let res = if cfg.sell_decision {
                    m.reservation
                } else {
                    let unit = m.cost_basis / m.qty;
                    unit * max(if m.wait > 60 { 0.2 } else { 0.5 }, 1.0 - 0.02 * m.wait as f64)
                };
                let q = if cfg.handling.is_some() { max(0.0, m.qty - m.unload_left / goods5(g).bulk) } else { m.qty };
                // S1: contracted goods (owned by the storer) are not sold in the market
                let q = if m.contract.is_empty() { q } else { max(0.0, q - m.contract_left()) };
                if q > 0.0 {
                    sells.push((res, q, Who::MSell(i)));
                }
            } else if m.state == MState::Buying {
                if let Some(Plan(pg, _, max_bid, q_max)) = m.plan {
                    if pg == g {
                        let q = min(min(c.avail_cap(m) / goods5(g).bulk, q_max) - m.qty, m.cash / max_bid);
                        if q > 0.0 {
                            buys.push((max_bid, q, Who::MBuy(i)));
                        }
                    }
                }
            }
        }
        if let Some(pli) = c.pool_idx(p, g) {
            let pl = &c.pools[pli].1;
            if pl.output > 0.0 {
                sells.push((pl.reservation, pl.output, Who::Pool(pli)));
            }
        }
        for (pli, ((pp, _), pl)) in c.pools.iter().enumerate() {
            if *pp != p {
                continue;
            }
            if let Some(&(_, a)) = pl.recipe.inputs.iter().find(|x| x.0 == g) {
                let need = max(0.0, a * pl.rate() * pl.input_days - pl.input(g));
                let maxp = 2.0 * goods5(g).reff;
                let q = min(need, pl.cash * 0.5 / maxp);
                if q > 0.0 {
                    buys.push((maxp, q, Who::PInput(pli)));
                }
            }
        }
        let rural = &c.markets[mi].rural;
        let farm = rural.stock > 0.0 && rural.annual_capacity > 0.0;
        c.kapan_traded[mi] = Some(false);
        if !buys.is_empty() {
            c.kapan_bid[mi] = pymath::max_iter(buys.iter().map(|x| x.0));
        }
        if buys.is_empty() || (sells.is_empty() && !farm) {
            return;
        }
        let s_at = |price: f64| -> f64 {
            let v = if farm { rural.offered_at(price, dth) } else { 0.0 };
            v + pymath::sum(sells.iter().filter(|x| x.0 <= price).map(|x| x.1))
        };
        let d_at = |price: f64| -> f64 { pymath::sum(buys.iter().filter(|x| x.0 >= price).map(|x| x.1)) };
        let lo = pymath::min_iter(sells.iter().map(|x| x.0).chain(if farm { Some(rural.floor_price) } else { None }))
            .unwrap();
        let hi = pymath::max_iter(buys.iter().map(|x| x.0)).unwrap();
        if hi < lo {
            c.kapan_quote[mi] = Some(lo);
            return;
        }
        let price = if d_at(lo) <= s_at(lo) {
            lo
        } else if d_at(hi) >= s_at(hi) {
            hi
        } else {
            let (mut a, mut b) = (lo, hi);
            for _ in 0..40 {
                let mid = (a + b) / 2.0;
                if d_at(mid) > s_at(mid) {
                    a = mid;
                } else {
                    b = mid;
                }
            }
            (a + b) / 2.0
        };
        let (dq, sq) = (d_at(price), s_at(price));
        let v = min(dq, sq);
        if v <= 1e-9 {
            return;
        }
        let fb = v / dq;
        let farm_offer = if farm { rural.offered_at(price, dth) } else { 0.0 };
        let rural_stock = rural.stock;
        // 1) Buyer shares
        let mut alloc: Vec<(Who, f64, f64)> = Vec::new();
        for &(pr, q, who) in &buys {
            if pr < price {
                continue;
            }
            let qq = q * fb;
            let cash = match who {
                Who::Shop(i) => c.markets[mi].shops[i].cash,
                Who::Storer(i) => c.markets[mi].storers[i].cash,
                Who::MBuy(i) => self.merchants[i].cash,
                Who::PInput(i) => c.pools[i].1.cash,
                _ => unreachable!(),
            };
            let cost = min(pymath::round(qq * price) as f64, cash);
            if cost <= 0.0 {
                continue;
            }
            alloc.push((who, min(qq, cost / price), cost));
        }
        let delivered = pymath::sum(alloc.iter().map(|a| a.1));
        if delivered <= 1e-9 {
            return;
        }
        let mut total_paid = 0.0;
        for &(who, qq, cost) in &alloc {
            total_paid += cost;
            match who {
                Who::Shop(i) => {
                    let s = &mut c.markets[mi].shops[i];
                    s.cash -= cost;
                    s.receive(qq, cost);
                }
                Who::Storer(i) => {
                    let s = &mut c.markets[mi].storers[i];
                    s.cash -= cost;
                    s.receive(qq, cost);
                }
                Who::MBuy(i) => {
                    let m = &mut self.merchants[i];
                    m.cash -= cost;
                    m.qty += qq;
                    m.cost_basis += cost;
                    m.good = Some(g);
                    if c.cfg.visibility {
                        c.port_buys[p].push((m.id, p, g, qq, c.day));
                    }
                }
                Who::PInput(i) => {
                    let pl = &mut c.pools[i].1;
                    pl.cash -= cost;
                    *pl.input_mut(g) += qq;
                }
                _ => unreachable!(),
            }
        }
        // 2) Seller shares: in proportion to the quantity delivered
        let mut shares: Vec<(Who, f64)> = Vec::new();
        if farm {
            shares.push((Who::Farm, farm_offer));
        }
        for &(pr, q, who) in &sells {
            if pr <= price {
                shares.push((who, q));
            }
        }
        let avail = pymath::sum(shares.iter().map(|x| x.1));
        let fs = delivered / avail;
        for x in shares.iter_mut() {
            x.1 *= fs;
        }
        if farm && shares[0].1 > rural_stock {
            let short = shares[0].1 - rural_stock;
            shares[0].1 = rural_stock;
            let others = pymath::sum(shares[1..].iter().map(|x| x.1));
            let others = if others == 0.0 { 1.0 } else { others };
            for x in shares[1..].iter_mut() {
                x.1 += short * x.1 / others;
            }
        }
        let qsum = pymath::sum(shares.iter().map(|x| x.1));
        let qsum = if qsum == 0.0 { 1.0 } else { qsum };
        let mut paid_out = 0.0;
        let last = shares.len() - 1;
        let fee_rate = c.cfg.kapan_fee;
        for (idx, &(who, qq)) in shares.iter().enumerate() {
            let proceeds = if idx == last { total_paid - paid_out } else { pymath::int(total_paid * qq / qsum) as f64 };
            paid_out += proceeds;
            let fee = pymath::round(proceeds * fee_rate) as f64;
            c.ledger.money_sink("kapan_fee", fee);
            let net = proceeds - fee;
            match who {
                Who::Farm => {
                    c.markets[mi].rural.stock -= qq;
                    c.ledger.money_sink("rural_farmers", net);
                }
                Who::Storer(i) => {
                    let s = &mut c.markets[mi].storers[i];
                    s.stock -= qq;
                    s.cash += net;
                }
                Who::MSell(i) => {
                    // S-028: if customs is charged on landing, it is not charged again on sale
                    let duty = if c.entry_duty() { 0.0 } else { pymath::round(net * CUSTOMS) as f64 };
                    c.ledger.money_sink("customs", duty);
                    let m = &mut self.merchants[i];
                    let comm = pymath::round(net * c.comm(m, p)) as f64;
                    if comm != 0.0 {
                        c.ledger.money_sink("commission", comm);
                        c.commissions += comm;
                    }
                    let unit = m.cost_basis / max(m.qty - m.contract_left(), 1e-9);
                    m.cash += net - duty - comm;
                    m.lot_flow += net - duty - comm;
                    m.cost_basis -= unit * qq;
                    m.qty -= qq;
                }
                Who::Pool(i) => {
                    let pl = &mut c.pools[i].1;
                    pl.output -= qq;
                    pl.cash += net;
                }
                _ => unreachable!(),
            }
        }
        c.kapan_price[mi] = Some(price);
        c.kapan_quote[mi] = Some(price);
        c.kapan_traded[mi] = Some(true);
        c.kapan_volume[mi] = Some(c.kapan_volume[mi].unwrap_or(0.0) + delivered);
        c.kapan_today[mi] = Some(delivered);
    }
}
