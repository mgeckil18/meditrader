//! R1 risk model (K-030: leg + region hazard, dynamic corsair pressure) and the Ö3 ship market (D5b3j).
//! Ö3 origin: proposed by Claude, brought forward by the user (2026-11-06). Valuation by Tobin's q; sunk cost delays exit.

use super::*;
use crate::config::HazardModel;
use crate::consts::{
    region, Region, CORSAIR_JUMP, CORSAIR_JUMP_P, CORSAIR_RHO, CORSAIR_SIGMA, LOSS_PER_DAY_SUMMER, LOSS_PER_DAY_WINTER,
    NAT_PER_EDGE,
};
use crate::pymath::{exp, max, min, pow};

impl Core {
    /// Loss probability per voyage. actual=True: with today's corsair pressure; otherwise the long-run mean.
    pub fn p_loss(&self, days: f64, a: Port, b: Port, actual: bool) -> f64 {
        if self.cfg.hazard_model != HazardModel::Leg {
            let pd = if self.winter() { LOSS_PER_DAY_WINTER } else { LOSS_PER_DAY_SUMMER };
            return 1.0 - pow(1.0 - pd, days);
        }
        if !actual {
            return self.ploss0[self.winter() as usize][a.idx()][b.idx()];
        }
        1.0 - pymath::prod(self.leg_hazards_s(a, b, actual, self.winter(), 1.0).0.into_iter().map(|h| 1.0 - h))
    }

    /// With the realised voyage time (legs stretch by `days / base`): with `hazard_days` on, loss depends on duration.
    pub fn p_loss_real(&self, days: f64, a: Port, b: Port) -> (f64, Vec<(f64, f64)>) {
        if self.cfg.hazard_model != HazardModel::Leg {
            return (self.p_loss(days, a, b, true), Vec::new());
        }
        let scale = if self.cfg.hazard_days.is_some() { days / max(self.voyage(a, b), 1e-9) } else { 1.0 };
        let (h, parts) = self.leg_hazards_s(a, b, true, self.winter(), scale);
        (1.0 - pymath::prod(h.into_iter().map(|h| 1.0 - h)), parts)
    }

    /// Leg hazards of a route: ([combined], [(natural, corsair)]).
    pub fn leg_hazards(&self, a: Port, b: Port, actual: bool) -> (Vec<f64>, Vec<(f64, f64)>) {
        self.leg_hazards_w(a, b, actual, self.winter())
    }

    pub fn leg_hazards_w(&self, a: Port, b: Port, actual: bool, w: bool) -> (Vec<f64>, Vec<(f64, f64)>) {
        self.leg_hazards_s(a, b, actual, w, 1.0)
    }

    /// `scale`: leg duration multiplier (realised / base). No effect with `hazard_days` off.
    pub fn leg_hazards_s(&self, a: Port, b: Port, actual: bool, w: bool, scale: f64) -> (Vec<f64>, Vec<(f64, f64)>) {
        let mut out = Vec::new();
        let mut parts = Vec::new();
        for &(x, y) in &self.legs[a.idx()][b.idx()] {
            let regs = crate::map::get().edge_regions(x, y);
            let nat = NAT_PER_EDGE * if w { pymath::max_iter(regs.iter().map(|&r| region(r).0)).unwrap() } else { 1.0 };
            let cor = 1.0
                - pymath::prod(
                    regs.iter().map(|&r| 1.0 - region(r).1 * if actual { self.corsair[r.idx()] } else { 1.0 }),
                );
            let (nat, cor) = match self.cfg.hazard_days {
                Some(r) => {
                    let e = crate::map::get().edge_days(x, y) * scale / r;
                    (1.0 - pow(1.0 - nat, e), 1.0 - pow(1.0 - cor, e))
                }
                None => (nat, cor),
            };
            parts.push((nat, cor));
            out.push(1.0 - (1.0 - nat) * (1.0 - cor));
        }
        (out, parts)
    }

    /// Monthly corsair pressure: log-AR(1) per region + rare jumps.
    pub fn corsair_step(&mut self) {
        for &k in Region::all() {
            let r = self.rng.get("corsair");
            let mut x = CORSAIR_RHO * self.corsair_x[k.idx()] + CORSAIR_SIGMA * r.normal(0.0, 1.0);
            if r.random() < CORSAIR_JUMP_P {
                x += CORSAIR_JUMP;
            }
            self.corsair_x[k.idx()] = x;
            self.corsair[k.idx()] = exp(x) / self.corsair_z;
        }
    }

    /// Replacement value (the merchant's ship; the new price if one is on order).
    pub fn ship_r(&self, m: &M5) -> f64 {
        if !self.cfg.ship_market || m.is_player {
            return 0.0;
        }
        match m.ship {
            None => {
                if m.on_order >= 0 {
                    self.cfg.ship_price
                } else {
                    0.0
                }
            }
            Some(b) => self.ship_r_built(b as f64),
        }
    }

    pub fn ship_r_built(&self, built: f64) -> f64 {
        let cfg = &self.cfg;
        let age = max(0.0, (self.day as f64 - built) / 365.0);
        cfg.ship_price * max(cfg.ship_scrap, 1.0 - (1.0 - cfg.ship_scrap) * age / cfg.ship_life)
    }

    /// Track-record value: equity + dividends + ship.
    pub fn value(&self, m: &M5) -> f64 {
        m.equity() + m.divs + self.ship_r(m)
    }

    pub fn annuity(&self, r: f64) -> f64 {
        let h = self.cfg.invest_horizon;
        if r.abs() < 1e-9 {
            h
        } else {
            (1.0 - pow(1.0 + r, -h)) / r
        }
    }

    pub fn ship_worth(&self, belief: f64, r: f64, rv: f64) -> f64 {
        rv + (belief - r) * (self.cfg.capital + rv) * self.annuity(r)
    }

    pub fn yard_delivery(&self) -> f64 {
        max((self.day + self.cfg.yard_days) as f64, self.yard_next)
    }

    pub fn new_surplus(&self, belief: f64, r: f64) -> f64 {
        let p = self.cfg.ship_price;
        let d = exp(-r * (self.yard_delivery() - self.day as f64) / 365.0);
        d * self.ship_worth(belief, r, p) - p
    }

    pub fn foreign_surplus(&self, belief: f64, r: f64) -> f64 {
        match self.cfg.foreign_premium {
            None => f64::NEG_INFINITY,
            Some(f) => {
                let p = self.cfg.ship_price;
                self.ship_worth(belief, r, p) - (1.0 + f) * p
            }
        }
    }

    pub fn listed_r(&self) -> f64 {
        if self.ship_list.is_empty() {
            return 0.0;
        }
        let v: Vec<f64> = self.ship_list.iter().map(|x| self.ship_r_built(x.built as f64)).collect();
        pymath::np_mean(&v)
    }

    pub fn sale_value(&self, rv: f64) -> f64 {
        max(self.ship_px * rv, self.cfg.ship_price * self.cfg.ship_scrap)
    }

    pub fn sunk_term(&self, m: &M5, r: f64) -> f64 {
        let rv = self.ship_r(m);
        if rv <= 0.0 {
            return 0.0;
        }
        (rv - self.sale_value(rv)) / ((self.cfg.capital + rv) * self.annuity(r))
    }

    pub fn ship_surplus(&self, belief: f64, r: f64) -> f64 {
        let mut best = max(self.new_surplus(belief, r), self.foreign_surplus(belief, r));
        if !self.ship_list.is_empty() {
            let rv = self.listed_r();
            best = max(best, self.ship_worth(belief, r, rv) - self.sale_value(rv));
        }
        best
    }

    /// Candidate investors (same process as U; the criterion is the surplus in the ship market). A confirmed candidate buys this month.
    pub fn ship_candidates(&mut self, p: Port, belief: f64, alt: f64) {
        let cfg = self.cfg.clone();
        let gap = cfg.entry_confirm_gap * 30 - 5;
        let mut keep = Vec::new();
        let mut buyers = std::mem::take(&mut self.ship_buyers);
        let inv = |r: f64| Buyer { p: Some(p), m: None, r, belief, new: 0.0, foreign: 0.0, bid: 0.0 };
        for c in std::mem::take(&mut self.candidates) {
            if c.0 != p || c.2 > self.day {
                keep.push(c);
                continue;
            }
            if self.ship_surplus(belief, alt + c.1) <= 0.0 {
                continue;
            }
            if c.3 > 1 {
                keep.push((p, c.1, self.day + gap, c.3 - 1));
            } else {
                buyers.push(inv(alt + c.1));
            }
        }
        let unit = cfg.capital + cfg.ship_price;
        let lam = cfg.entry_attention * self.pool[p] / unit;
        let k = self.rng.get("entry_exit").poisson(lam);
        for _ in 0..k {
            let z = self.rng.get("entry_exit").standard_normal();
            let prem = cfg.risk_premium * exp(cfg.investor_sigma * z);
            if self.ship_surplus(belief, alt + prem) > 0.0 {
                if cfg.entry_confirm > 1 {
                    keep.push((p, prem, self.day + gap, cfg.entry_confirm - 1));
                } else {
                    buyers.push(inv(alt + prem));
                }
            }
        }
        self.candidates = keep;
        self.ship_buyers = buyers;
    }

    /// The ship of a merchant who exits or goes bankrupt is put up for sale (owner: the home port's investors).
    pub fn release_ship(&mut self, m: &mut M5) {
        if !self.cfg.ship_market || m.is_player {
            return;
        }
        let built = match m.ship {
            Some(b) => b,
            None if m.on_order >= 0 => m.on_order,
            None => return,
        };
        m.exit_ship = self.ship_r_built(built as f64);
        let owner = if self.pool.contains(m.home) { m.home } else { self.port_list[0] };
        self.ship_list.push(Listing { built, owner, day: self.day, prize: false });
        m.ship = None;
        m.on_order = -1;
    }

    pub fn to_pool(&mut self, m: &M5, amount: f64) {
        if self.pool.contains(m.home) {
            self.pool[m.home] += amount;
        }
    }
}

impl World {
    /// Monthly ship market (`_ship_clear`). Returns: port -> entries this month.
    pub(super) fn ship_clear(&mut self, mut n: i64, routes: &PortMap<Option<Route>>) -> PortMap<i64> {
        let cfg = self.core.cfg.clone();
        let (kk, p_new) = (cfg.capital, cfg.ship_price);
        let scrap = cfg.ship_price * cfg.ship_scrap;
        let life = cfg.ship_life * 365.0;
        let day = self.core.day;
        let (mut n_scrap, mut n_layup_scrap) = (0i64, 0i64);
        for m in self.merchants.iter_mut() {
            // (1) a ship at the end of its life is broken up in port
            if let Some(s) = m.ship {
                if !m.is_player && (day - s) as f64 >= life && m.state == MState::Buying && m.empty() {
                    m.ship = None;
                    let v = pymath::int(scrap) as f64;
                    m.cash += v;
                    self.core.ledger.money_source("ship_scrap", v);
                    n_scrap += 1;
                }
            }
        }
        let c = &mut self.core;
        let mut keep = Vec::new();
        for x in std::mem::take(&mut c.ship_list) {
            // (2) laid-up ship: costs; broken up if it waits long or ages
            if !x.prize {
                c.pool[x.owner] -= 30.0 * cfg.layup_cost_day;
            }
            let old = (day - x.built) as f64 >= life;
            if old || day - x.day >= cfg.layup_max_days {
                let v = if old { c.ship_r_built(x.built as f64) } else { scrap };
                if !x.prize {
                    c.pool[x.owner] += v;
                }
                n_layup_scrap += 1;
                continue;
            }
            keep.push(x);
        }
        c.ship_list = keep;
        let mut buyers = std::mem::take(&mut c.ship_buyers);
        let rp = cfg.bond_rate + cfg.risk_premium;
        for (i, m) in self.merchants.iter().enumerate() {
            // (3) merchant who lost a ship: buys again, by own expectation
            if !m.is_player
                && m.ship.is_none()
                && m.on_order < 0
                && m.state == MState::Buying
                && m.qty <= 0.0
                && !m.retire
                && !m.broke
            {
                let e = self.core.own_expect(m);
                buyers.push(Buyer {
                    p: None,
                    m: Some(i),
                    r: rp,
                    belief: e.unwrap_or(rp),
                    new: 0.0,
                    foreign: 0.0,
                    bid: 0.0,
                });
            }
        }
        let c = &mut self.core;
        let rbar = if c.ship_list.is_empty() { p_new } else { c.listed_r() };
        for b in buyers.iter_mut() {
            let sn = c.new_surplus(b.belief, b.r);
            let sf = c.foreign_surplus(b.belief, b.r);
            b.new = sn;
            b.foreign = sf;
            let sn = max(sn, sf);
            let bid = c.ship_worth(b.belief, b.r, rbar) - max(0.0, sn);
            let cash = match b.m {
                Some(i) => self.merchants[i].cash - cfg.rebuy_min_cash * kk,
                None => c.pool[b.p.unwrap()] - kk,
            };
            b.bid = min(bid, cash) / rbar;
        }
        let mut order: Vec<usize> = (0..buyers.len()).collect();
        order.sort_by(|&a, &b| (-buyers[a].bid).partial_cmp(&-buyers[b].bid).expect("NaN bid"));
        let bids: Vec<Buyer> = order.into_iter().map(|i| buyers[i].clone()).collect();
        let ask_of = |c: &Core, x: &Listing| scrap / c.ship_r_built(x.built as f64);
        let mut sidx: Vec<usize> = (0..c.ship_list.len()).collect();
        sidx.sort_by(|&a, &b| ask_of(c, &c.ship_list[a]).partial_cmp(&ask_of(c, &c.ship_list[b])).unwrap());
        let asks: Vec<f64> = sidx.iter().map(|&i| ask_of(c, &c.ship_list[i])).collect();
        let mut k = 0;
        while k < bids.len().min(asks.len()) && bids[k].bid >= asks[k] {
            k += 1;
        }
        let (mut trades, mut new_inv, mut new_own, mut rebuy_exit, mut n_foreign) = (0i64, 0i64, 0i64, 0i64, 0i64);
        let mut entries: PortMap<i64> = PortMap::default();
        if k > 0 {
            // (4) single price: between the k-th bid and k-th ask, excluding the (k+1)-th quotes
            let lo = max(asks[k - 1], if k < bids.len() { bids[k].bid } else { f64::NEG_INFINITY });
            let hi = min(bids[k - 1].bid, if k < asks.len() { asks[k] } else { f64::INFINITY });
            c.ship_px = (lo + hi) / 2.0;
        } else if !bids.is_empty() && !asks.is_empty() {
            c.ship_px = max(bids[0].bid, cfg.ship_scrap);
        } else if !asks.is_empty() {
            c.ship_px = asks[0];
        } else if !bids.is_empty() {
            c.ship_px = max(bids[0].bid, cfg.ship_scrap);
        }
        let mut sold = vec![false; c.ship_list.len()];
        let [lo_, hi_] = cfg.entry_lag_days;
        for i in 0..k {
            let b = &bids[i];
            let si = sidx[i];
            if b.m.is_none() && n >= cfg.max_merchants {
                continue;
            }
            let x = c.ship_list[si];
            let rv = c.ship_r_built(x.built as f64);
            let price = c.ship_px * rv;
            if x.prize {
                // the pool is outside the ledger; the buying merchant's payment already leaves as `ship_purchase`
                c.prizes_sold += 1;
            } else {
                c.pool[x.owner] += price;
            }
            sold[si] = true;
            trades += 1;
            if let Some(mi) = b.m {
                let m = &mut self.merchants[mi];
                let ip = pymath::int(price) as f64;
                m.cash -= ip;
                c.ledger.money_sink("ship_purchase", ip);
                m.ship = Some(x.built);
                let pv = c.prev_val.get(&m.id).copied().unwrap_or(m.start_capital);
                c.prev_val.insert(m.id, pv + rv - ip);
            } else {
                let p = b.p.unwrap();
                c.pool[p] -= kk + price;
                let d = day + c.rng.get("entry_exit").integers(lo_, hi_ + 1);
                c.pending.push(Pending(d, p, routes.get(p).copied().flatten(), x.built));
                let e = entries.get(p).copied().unwrap_or(0);
                entries.set(p, e + 1);
                n += 1;
            }
        }
        let mut j = 0;
        c.ship_list.retain(|_| {
            j += 1;
            !sold[j - 1]
        });
        let nl = &c.n_npc[c.n_npc.len().saturating_sub(1825)..];
        let fleet = if nl.is_empty() { c.n_init as f64 } else { nl.iter().sum::<i64>() as f64 / nl.len() as f64 };
        let gap = 365.0 / max(cfg.yard_rate * max(fleet, 1.0), 1e-9);
        let pf = match cfg.foreign_premium {
            Some(f) => (1.0 + f) * p_new,
            None => f64::INFINITY,
        };
        for b in &bids[k..] {
            // (5) shipyard, a ready ship from abroad, or give up
            let foreign = b.foreign > b.new;
            let cost = if foreign { pf } else { p_new };
            let ok = max(b.new, b.foreign) > 0.0;
            if let Some(mi) = b.m {
                let m = &mut self.merchants[mi];
                if ok && m.cash - cost >= cfg.rebuy_min_cash * kk {
                    let ic = pymath::int(cost) as f64;
                    m.cash -= ic;
                    let pv = c.prev_val.get(&m.id).copied().unwrap_or(m.start_capital);
                    if foreign {
                        c.ledger.money_sink("foreign_ships", ic);
                        m.ship = Some(day);
                        c.prev_val.insert(m.id, pv + p_new - ic);
                        n_foreign += 1;
                    } else {
                        let d = c.yard_delivery();
                        c.yard_next = d + gap;
                        c.ledger.money_sink("shipbuilding", ic);
                        m.on_order = pymath::int(d);
                        c.prev_val.insert(m.id, pv + p_new - ic);
                        new_own += 1;
                    }
                } else {
                    m.retire = true;
                    rebuy_exit += 1;
                }
            } else {
                let p = b.p.unwrap();
                if ok && c.pool[p] >= kk + cost && n < cfg.max_merchants {
                    c.pool[p] -= kk + cost;
                    if foreign {
                        let d = day + c.rng.get("entry_exit").integers(lo_, hi_ + 1);
                        c.pending.push(Pending(d, p, routes.get(p).copied().flatten(), day));
                        n_foreign += 1;
                    } else {
                        let d = c.yard_delivery();
                        c.yard_next = d + gap;
                        let di = pymath::int(d);
                        c.pending.push(Pending(di, p, routes.get(p).copied().flatten(), di));
                        new_inv += 1;
                    }
                    let e = entries.get(p).copied().unwrap_or(0);
                    entries.set(p, e + 1);
                    n += 1;
                }
            }
        }
        let n_own = buyers.iter().filter(|b| b.m.is_some()).count() as f64;
        c.ship_log.push(vec![
            day as f64,
            c.ship_px,
            c.ship_list.len() as f64,
            trades as f64,
            new_inv as f64,
            new_own as f64,
            buyers.len() as f64,
            n_scrap as f64,
            n_layup_scrap as f64,
            max(0.0, c.yard_next - day as f64),
            rebuy_exit as f64,
            n_own,
            n_foreign as f64,
        ]);
        entries
    }
}

impl Core {
    /// Ship loss. On capture by corsairs, with probability `prize_share` the ship is offered for sale as a prize (M1.4,
    /// added by Claude): no owner, the sale price leaves the economy, no lay-up costs.
    pub fn lose_ship(&mut self, m: &mut M5, corsair: bool) {
        let built = m.ship.take();
        self.ships_lost += 1;
        if let (true, Some(b)) = (corsair && self.cfg.prize_share > 0.0, built) {
            if self.rng.get("prize").random() < self.cfg.prize_share {
                let owner = m.loc;
                self.ship_list.push(Listing { built: b, owner, day: self.day, prize: true });
                self.prizes += 1;
            }
        }
    }
}
