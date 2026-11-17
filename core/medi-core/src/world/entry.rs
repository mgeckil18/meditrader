//! Monthly step, public record (K-029), entry signal, Bühlmann credibility (Ö1), exit at voyage end, bankruptcy.
//! K-029 user note: not final, to be checked against the literature. Ö1 Bühlmann: added by Claude, supported by experiment.

use super::*;
use crate::config::{ColdTrack, CredRule, HazardModel, HurdleRule, PublicTrack};
use crate::consts::goods5;
use crate::consts::GoodKind;
use crate::pymath::{erf, exp, log, max, min, pow, sqrt};

impl Core {
    pub fn public_track(&self) -> Option<f64> {
        match self.cfg.public_track {
            PublicTrack::Aggregate => self.public_agg,
            PublicTrack::SurvivorMedian => {
                if self.track_known {
                    Some(self.trailing_median)
                } else {
                    None
                }
            }
        }
    }

    /// Expected yearly return for a multi-year decision (optimizer's curse correction; Smith & Winkler 2006).
    pub fn belief(&self, r_opp: f64, voyage_frac: f64, track: Option<f64>) -> f64 {
        let Some(track) = track else { return r_opp };
        let lag = (self.cfg.entry_lag_days[0] + self.cfg.entry_lag_days[1]) as f64 / 2.0;
        track + max(0.0, voyage_frac) * exp(-lag / self.cfg.revert_days) / self.cfg.invest_horizon
    }

    /// Share of investors convinced by excess return x (required premium lognormal, median risk_premium + extra).
    pub fn convinced(&self, x: f64, extra: f64) -> f64 {
        if x <= 0.0 {
            return 0.0;
        }
        let z = (log(x) - log(self.cfg.risk_premium + extra)) / self.cfg.investor_sigma;
        0.5 * (1.0 + erf(z / sqrt(2.0)))
    }

    /// Half-width of the Dixit band kappa*sigma (band_kappa = 0: off).
    pub fn band(&self) -> f64 {
        if self.cfg.band_kappa <= 0.0 {
            return 0.0;
        }
        let i1 = self.cfg.public_track == PublicTrack::Aggregate;
        let v: Vec<f64> = self.pub_log[self.pub_log.len().saturating_sub(24)..]
            .iter()
            .filter_map(|x| if i1 { x.1 } else { Some(x.2) })
            .collect();
        if v.len() < 6 {
            return 0.0;
        }
        self.cfg.band_kappa * pymath::np_std(&v)
    }

    pub fn mrets(m: &M5) -> Vec<f64> {
        let e = &m.emarks;
        (1..e.len()).filter(|&i| e[i - 1] > 1.0).map(|i| e[i] / e[i - 1] - 1.0).collect()
    }

    /// K-029: personal expectation; Bühlmann: Z = n / (n + k).
    pub fn own_expect(&self, m: &M5) -> Option<f64> {
        let pubt = self.public_track()?;
        let own = match self.cfg.cred_rule {
            CredRule::Buhlmann => {
                let r = Self::mrets(m);
                let Some(k) = self.cred_k else { return Some(pubt) };
                if r.len() < 3 {
                    return Some(pubt);
                }
                let n = r.len() as f64;
                let z = n / (n + k);
                return Some(z * 12.0 * pymath::sum(r.iter().copied()) / n + (1.0 - z) * pubt);
            }
            CredRule::Fixed => {
                if m.emarks.len() >= 4 {
                    let e = &m.emarks;
                    Some((e[e.len() - 1] / max(e[0], 1.0) - 1.0) * 12.0 / (e.len() - 1) as f64)
                } else {
                    None
                }
            }
        };
        let Some(own) = own else { return Some(pubt) };
        let n = m.record.iter().filter(|x| self.day - x.0 <= 365).count() as f64;
        let w = n / (n + self.cfg.shrink_k);
        Some(w * own + (1.0 - w) * pubt)
    }

    /// Bühlmann-Straub (1970) estimator: (k, s², a, I).
    pub fn buhlmann(r: &[Vec<f64>], nmin: usize) -> Option<(f64, f64, f64, i64)> {
        let r: Vec<&Vec<f64>> = r.iter().filter(|x| x.len() >= nmin).collect();
        let ii = r.len();
        if ii < 10 {
            return None;
        }
        let n: Vec<f64> = r.iter().map(|x| x.len() as f64).collect();
        let mb: Vec<f64> = r.iter().map(|x| pymath::sum(x.iter().copied()) / x.len() as f64).collect();
        let nn = pymath::sum(n.iter().copied());
        let s2 = pymath::sum((0..ii).map(|i| pymath::sum(r[i].iter().map(|&x| pow(x - mb[i], 2.0)))))
            / pymath::sum(n.iter().map(|&k| k - 1.0));
        let xb = pymath::sum((0..ii).map(|i| n[i] * mb[i])) / nn;
        let a = (pymath::sum((0..ii).map(|i| n[i] * pow(mb[i] - xb, 2.0))) - (ii as f64 - 1.0) * s2)
            / (nn - pymath::sum(n.iter().map(|&k| k * k)) / nn);
        Some((if a > 0.0 { s2 / a } else { f64::INFINITY }, s2, a, ii as i64))
    }

    /// K-029: exit decision at the end of a voyage.
    pub fn exit_decision(&mut self, m: &mut M5) {
        if self.diag.is_none() {
            return self.exit_decision0(m);
        }
        // DiagWorld._exit_decision: expectation before the decision, record after (also on early return)
        let e = self.own_expect(m);
        self.exit_decision0(m);
        if let Some(e) = e {
            let n = m.record.iter().filter(|x| self.day - x.0 <= 365).count() as i64;
            let row = (self.day, e, self.public_track(), m.retire, n);
            self.diag.as_mut().unwrap().xlog.push(row);
        }
    }

    fn exit_decision0(&mut self, m: &mut M5) {
        if self.cfg.ship_market && m.ship.is_none() {
            return;
        }
        let Some(e) = self.own_expect(m) else { return };
        let prem = self.cfg.exit_premium.unwrap_or(self.cfg.risk_premium);
        let mut short = self.cfg.bond_rate + prem - self.band() - e;
        if self.cfg.ship_market {
            short -= self.sunk_term(m, self.cfg.bond_rate + prem);
        }
        if short > 0.0 {
            let u = self.rng.get("exit_voyage").random();
            if u < self.convinced(short, 0.0) {
                m.retire = true;
            }
        }
    }

    fn entry_signal(&self, r_bar: f64, ruin_price: f64) -> (f64, f64, f64) {
        let cfg = &self.cfg;
        let mut track = self.public_track();
        if track.is_none() && cfg.cold_track == ColdTrack::Neutral {
            track = Some(cfg.bond_rate + cfg.risk_premium);
        }
        let belief = self.belief(r_bar, if cfg.entry_bonus { self.public_voy } else { 0.0 }, track);
        let alt = cfg.bond_rate;
        let conv = match cfg.hurdle_rule {
            HurdleRule::Common => self.convinced(belief - alt - cfg.risk_premium - self.band(), 0.0),
            HurdleRule::Lognormal => self.convinced(belief - alt, ruin_price),
        };
        (belief, alt, conv)
    }

    /// Retail entry and exit (monthly; D3b mechanism).
    pub fn retail_entry_exit(&mut self) {
        let cfg = self.cfg.clone();
        self.rng.get("shop_entry_exit"); // Python creates the stream here unconditionally (visible in the state)
        for mi in 0..self.markets.len() {
            let (p, g) = self.market_keys[mi];
            let mut rets: Vec<(usize, f64)> = Vec::new();
            for (i, s) in self.markets[mi].shops.iter_mut().enumerate() {
                s.tag = i;
                s.marks.push(s.op_profit);
                if s.marks.len() > 12 {
                    s.marks.remove(0);
                }
                s.op_profit = 0.0;
                if s.marks.len() == 12 {
                    let capital = max(s.cash + s.stock * s.cost_ref, 1.0);
                    rets.push((s.tag, pymath::sum(s.marks.iter().copied()) / capital));
                }
            }
            self.close_broke_shops(mi);
            if rets.is_empty() {
                continue;
            }
            rets.retain(|(t, _)| self.markets[mi].shops.iter().any(|s| s.tag == *t));
            if rets.is_empty() {
                continue;
            }
            let med = pymath::np_median(&rets.iter().map(|x| x.1).collect::<Vec<_>>());
            let mut n = self.markets[mi].shops.len();
            let mut sorted = rets.clone();
            sorted.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
            for (id, ret) in sorted {
                if n > 1 && ret < cfg.bond_rate && self.rng.get("shop_entry_exit").random() < cfg.exit_prob {
                    let mk = &mut self.markets[mi];
                    let i = mk.shops.iter().position(|s| s.tag == id).unwrap();
                    let s = mk.shops.remove(i);
                    self.ledger.money_sink("shop_exit", s.cash);
                    self.ledger.goods_sink(g, "shop_exit", s.stock);
                    self.shop_exits += 1;
                    n -= 1;
                }
            }
            let mk = &mut self.markets[mi];
            let z = pymath::sum(mk.shops.iter().map(|s| s.share));
            for s in mk.shops.iter_mut() {
                s.share /= z;
            }
            let excess = med - (cfg.bond_rate + cfg.risk_premium);
            if excess > 0.0 && n < cfg.max_shops && self.rng.get("shop_entry_exit").random() < min(1.0, excess / 0.10) {
                let mk = &mut self.markets[mi];
                let t = mk.shops[0].clone();
                let rr = pymath::np_mean(&mk.shops.iter().map(|s| s.request_rate).collect::<Vec<_>>()) / (n + 1) as f64;
                let cash = (pymath::int(2.0 * t.target_cover_days * rr * (n + 1) as f64 * t.cost_ref) + 1) as f64;
                let req_price = pymath::np_mean(&mk.shops.iter().map(|s| s.req_price).collect::<Vec<_>>());
                let mut ns = t.clone();
                ns.tag = usize::MAX; // new object
                ns.id = format!("sk{}e", self.shop_entries);
                ns.cash = cash;
                ns.stock = 0.0;
                ns.share = 0.0;
                ns.request_rate = rr;
                ns.requests_today = 0.0;
                ns.withdrawn = 0.0;
                ns.op_profit = 0.0;
                ns.req_price = req_price;
                ns.avg_cost = t.cost_ref;
                ns.memory_price = ns.mid; // __post_init__
                ns.marks = Vec::new();
                ns.stocked_out = false;
                ns.unmet_frac = 0.0;
                ns.peak_paid = 0.0;
                ns.broke_months = 0;
                mk.shops.push(ns);
                self.ledger.money_source("shop_entry", cash);
                self.shop_entries += 1;
            }
            let _ = p;
        }
    }

    /// A shop with no cash and no stock for a month closes; if no shop is left, a new one opens.
    fn close_broke_shops(&mut self, mi: usize) {
        let (p, g) = self.market_keys[mi];
        let quote = self.kapan_quote[mi].unwrap_or(goods5(g).reff);
        let dem = self.demand(p, g);
        let mk = &mut self.markets[mi];
        let template = mk.shops.first().cloned();
        let mut i = 0;
        while i < mk.shops.len() {
            let s = &mut mk.shops[i];
            let day_need = max(s.share, 0.05) * dem * quote;
            let broke = s.stock < 1.0 && s.cash < day_need;
            s.broke_months = if broke { s.broke_months + 1 } else { 0 };
            if s.broke_months >= 1 {
                let s = mk.shops.remove(i);
                self.ledger.money_sink("shop_exit", s.cash);
                self.ledger.goods_sink(g, "shop_exit", s.stock);
                self.shop_exits += 1;
            } else {
                i += 1;
            }
        }
        if mk.shops.is_empty() {
            if let Some(t) = template {
                let cash = (pymath::int(2.0 * t.target_cover_days * dem * quote) + 1) as f64;
                let mut ns = t.clone();
                ns.tag = usize::MAX; // new object
                ns.id = format!("sk{}r", self.shop_entries);
                ns.cash = cash;
                ns.stock = 0.0;
                ns.share = 1.0;
                ns.request_rate = dem;
                ns.requests_today = 0.0;
                ns.withdrawn = 0.0;
                ns.op_profit = 0.0;
                ns.req_price = quote;
                ns.cost_ref = quote;
                ns.avg_cost = quote;
                ns.memory_price = ns.mid;
                ns.marks = Vec::new();
                ns.stocked_out = false;
                ns.broke_months = 0;
                ns.unmet_frac = 0.0;
                ns.peak_paid = 0.0;
                mk.shops.push(ns);
                self.ledger.money_source("shop_entry", cash);
                self.shop_entries += 1;
            }
        }
        let z = pymath::sum(mk.shops.iter().map(|x| x.share));
        let z = if z == 0.0 { 1.0 } else { z };
        for x in mk.shops.iter_mut() {
            x.share /= z;
        }
    }
}

impl World {
    fn ruin_price(&self) -> f64 {
        let c = &self.core;
        if !c.cfg.entry_ruin {
            return 0.0;
        }
        let n = c.ruin_days.iter().filter(|&&d| c.day - d <= 365).count() as f64;
        let fleet = self.merchants.iter().filter(|m| !m.is_player).count().max(1) as f64;
        c.cfg.entry_ruin_weight * 0.9 * n / fleet
    }

    /// `_public_return(p)`: the "commonly known" opportunity in a port.
    fn public_return(&mut self, p: Port) -> f64 {
        let c = &self.core;
        let here: Vec<&M5> =
            self.merchants.iter().filter(|m| !m.is_player && m.loc == p && m.state == MState::Buying).collect();
        if here.len() >= 3 {
            let mut vals = Vec::with_capacity(here.len());
            let mut last = None;
            for m in here {
                let v = c.best_from(m, p);
                if v.3.is_some() {
                    last = v.3;
                }
                vals.push(v);
            }
            vals.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
            let mid = vals[vals.len() / 2];
            let c = &mut self.core;
            if let Some(l) = last {
                c.last_voyage = l;
            }
            c.public_voy = mid.1;
            c.public_route = mid.2;
            return mid.0;
        }
        let cfg = &c.cfg;
        let nm = c.market_keys.len();
        let mut rep = M5 {
            id: 0,
            cash: cfg.capital,
            capacity: cfg.capacity,
            is_player: false,
            informed: false,
            state: MState::Buying,
            loc: p,
            dest: None,
            arrive_day: -1,
            good: None,
            qty: 0.0,
            cost_basis: 0.0,
            plan: None,
            wait: 0,
            risk_aversion: 1.0,
            obs: c.current[p].clone(),
            hist: c.current_hist[p].iter().map(|h| h[h.len().saturating_sub(20)..].to_vec()).collect(),
            heard: Default::default(),
            heard_h: Default::default(),
            heard_hn: Default::default(),
            born_day: 0,
            start_capital: cfg.capital,
            divs: 0.0,
            marks: Vec::new(),
            level: 1,
            imitation: 0.0,
            overconf: 1.0,
            p_hear: cfg.p_hear,
            dara: false,
            known_loads: if cfg.rival_info { c.loads[p].clone() } else { IdMap::default() },
            w_fund: 0.0,
            hnews: vec![None; nm],
            seen_buys: Vec::new(),
            reservation: 0.0,
            harbor: vec![None; nm],
            home: p,
            record: Vec::new(),
            debt: None,
            debt_lost: false,
            broke: false,
            emarks: Vec::new(),
            retire: false,
            v0: 0.0,
            t0: -1,
            ship: None,
            on_order: -1,
            exit_ship: 0.0,
            voy: None,
            voy_overhead: 0.0,
            loaded: 0.0,
            unload_left: 0.0,
            qty_prev: 0.0,
            fill_ema: 0.0,
            rr: Vec::new(),
            cargo_day: -1,
            packet_all: Vec::new(),
            hold: Vec::new(),
            considered: Vec::new(),
            fill_val: 0.0,
            lot_flow: 0.0,
            pre_land: false,
            commit: None,
            contract: Vec::new(),
            packet: None,
            packet_hnews: Vec::new(),
            packet_harbor: Vec::new(),
            carried: IdMap::default(),
            debt_pd: None,
        };
        // Ships being fitted out are visible in port (level 1; entry cobweb buffer)
        for (i, x) in c.pending.iter().enumerate() {
            if x.1 == p {
                if let Some(route) = x.2 {
                    let i = i as i64;
                    rep.known_loads.insert(
                        -1 - i,
                        Load(route.0, route.1, route.2, cfg.capacity / goods5(route.2).bulk, c.day, -1 - i),
                    );
                }
            }
        }
        let (best, voy, route, last) = c.best_from(&rep, p);
        let c = &mut self.core;
        if let Some(l) = last {
            c.last_voyage = l;
        }
        c.public_voy = voy;
        c.public_route = route;
        best
    }

    fn entry_opportunity(&mut self) {
        self.core.update_pop_roi();
        self.core.update_finance();
        let n = (self.merchants.iter().filter(|m| !m.is_player).count() + self.core.pending.len()) as i64;
        let mut rows: Vec<(Port, f64, f64)> = Vec::new();
        let mut routes: PortMap<Option<Route>> = PortMap::default();
        let ruin = self.ruin_price();
        for pi in 0..self.core.port_list.len() {
            let p = self.core.port_list[pi];
            let br = self.core.cfg.bond_rate;
            self.core.pool[p] *= 1.0 + br / 12.0;
            let r_exp = self.public_return(p);
            let c = &mut self.core;
            let sm = c.cfg.entry_smooth_months;
            let mut hist: Vec<f64> = c.entry_log.iter().filter(|x| x.1 == p).map(|x| x.2).collect();
            let keep = (sm - 1).max(0) as usize;
            if sm - 1 != 0 {
                hist = hist[hist.len().saturating_sub(keep)..].to_vec();
            }
            hist.push(r_exp);
            let r_bar = pymath::sum(hist.iter().map(|&x| max(0.0, x))) / sm as f64;
            let (belief, alt, conv) = c.entry_signal(r_bar, ruin);
            self.diag_signal(p, belief, alt, conv, ruin);
            let c = &mut self.core;
            c.ship_candidates(p, belief, alt);
            rows.push((p, r_exp, belief));
            routes.set(p, c.public_route);
        }
        let k = self.ship_clear(n, &routes);
        let n0 = self.core.entry_log.len();
        let day = self.core.day;
        for (p, r_exp, belief) in rows {
            let kp = k.get(p).copied().unwrap_or(0);
            self.core.entry_log.push((day, p, r_exp, kp, belief));
        }
        self.diag_entries(n0);
    }

    fn update_agg(&mut self) {
        let c = &mut self.core;
        let (mut num, mut den) = (0.0, 0.0);
        for m in self.merchants.iter().filter(|m| !m.is_player) {
            let vp = c.prev_val.get(&m.id).copied().unwrap_or(m.start_capital);
            num += c.value(m) - vp;
            den += vp;
        }
        for Gone(m, _, cash) in &self.gone[c.gone_seen..] {
            if m.is_player {
                continue;
            }
            let vp = c.prev_val.get(&m.id).copied().unwrap_or(m.start_capital);
            num += max(0.0, cash - m.debt.map(|d| d.0).unwrap_or(0.0)) + m.divs + m.exit_ship - vp;
            den += vp;
        }
        c.gone_seen = self.gone.len();
        c.prev_val = self.merchants.iter().filter(|m| !m.is_player).map(|m| (m.id, c.value(m))).collect();
        if den > 0.0 {
            c.agg_hist.push(num / den);
            if c.agg_hist.len() > 12 {
                c.agg_hist.remove(0);
            }
        }
        c.public_agg = if c.agg_hist.len() >= 3 {
            Some(pymath::sum(c.agg_hist.iter().copied()) * 12.0 / c.agg_hist.len() as f64)
        } else {
            None
        };
    }

    fn update_cred(&mut self) {
        let ms: Vec<&M5> = self.merchants.iter().filter(|m| !m.is_player).collect();
        let r: Vec<Vec<f64>> = ms.iter().map(|m| Core::mrets(m)).collect();
        let Some((k, s2, a, ii)) = Core::buhlmann(&r, 3) else { return };
        self.core.cred_k = Some(k);
        let q: Vec<Vec<f64>> = ms
            .iter()
            .map(|m| {
                let e = &m.emarks;
                let mut out = Vec::new();
                let mut i = e.len() as i64 - 1;
                while i > 2 {
                    let iu = i as usize;
                    if e[iu - 3] > 1.0 {
                        out.push(e[iu] / e[iu - 3] - 1.0);
                    }
                    i -= 3;
                }
                out
            })
            .collect();
        let kq = Core::buhlmann(&q, 2).map(|x| x.0 * 3.0);
        let day = self.core.day;
        self.core.cred_log.push(CredLog(day, k, s2, a, ii, kq));
    }

    pub(super) fn monthly(&mut self) {
        let c = &mut self.core;
        for mi in 0..c.markets.len() {
            let g = c.market_keys[mi].1;
            let mk = &mut c.markets[mi];
            if goods5(g).kind != GoodKind::Harvest || mk.rural.annual_capacity <= 0.0 {
                for st in mk.storers.iter_mut() {
                    st.roll_continuous();
                }
            }
        }
        for m in self.merchants.iter_mut() {
            if m.state == MState::Buying && m.empty() && m.cash > 1.2 * m.start_capital && m.debt.is_none() {
                let d = pymath::int(m.cash - 1.2 * m.start_capital) as f64;
                m.cash -= d;
                m.divs += d;
                c.ledger.money_sink("merchant_dividends", d);
                c.to_pool(m, d);
            }
            if let Some(debt) = m.debt {
                if m.state == MState::Buying && m.empty() && c.day - debt.3 > 30 {
                    c.settle(m);
                }
            }
            let mk = m.net_worth() + m.divs + c.ship_r(m);
            m.marks.push(mk);
            if m.marks.len() > 13 {
                m.marks.remove(0);
            }
            let v = c.value(m);
            m.emarks.push(v);
            if m.emarks.len() > 13 {
                m.emarks.remove(0);
            }
        }
        self.update_agg();
        let c = &mut self.core;
        c.pub_log.push((c.day, c.public_agg, c.trailing_median));
        if c.cfg.cred_rule == CredRule::Buhlmann {
            self.update_cred();
        }
        if self.core.cfg.hazard_model == HazardModel::Leg {
            self.core.corsair_step();
        }
        // trailing (used only for the public median at voyage-end exit)
        let c = &mut self.core;
        let rets: Vec<f64> = self
            .merchants
            .iter()
            .filter(|m| !m.is_player)
            .filter_map(|m| {
                if m.marks.len() < 13 || c.day - m.born_day < 365 {
                    None
                } else {
                    Some(m.marks[m.marks.len() - 1] / max(m.marks[0], 1.0) - 1.0)
                }
            })
            .collect();
        c.track_known = rets.len() >= 3;
        if !rets.is_empty() {
            c.trailing_median = pymath::np_median(&rets);
        }
        c.rng.get("entry_exit");
        self.entry_opportunity();
    }

    pub(super) fn retire_flagged(&mut self) {
        let ms = std::mem::take(&mut self.merchants);
        let mut keep = Vec::with_capacity(ms.len());
        for mut m in ms {
            if !(m.retire && m.state == MState::Buying && m.empty()) || m.is_player {
                keep.push(m);
                continue;
            }
            let c = &mut self.core;
            c.settle(&mut m);
            if m.broke {
                keep.push(m);
                continue;
            }
            let cash = m.cash;
            c.to_pool(&m, cash);
            c.ledger.money_sink("to_bonds", cash);
            c.exits += 1;
            c.release_ship(&mut m);
            let day = c.day;
            self.gone.push(Gone(m, day, cash));
        }
        self.merchants = keep;
    }

    pub(super) fn upkeep(&mut self) {
        let ms = std::mem::take(&mut self.merchants);
        let mut keep = Vec::with_capacity(ms.len());
        for mut m in ms {
            let c = &mut self.core;
            let day = c.day;
            if m.broke {
                c.debt_bankruptcies += 1;
                c.ruin_days.push(day);
                c.release_ship(&mut m);
                let cash = m.cash;
                self.gone.push(Gone(m, day, cash));
                continue;
            }
            if m.qty <= 0.0 {
                m.cargo_day = -1;
            } else if c.cfg.cargo_spoil && m.cargo_day >= 0 {
                let g = m.good.expect("cargo good");
                let age = (day - m.cargo_day) as f64;
                let keep_frac = c.cargo_survival(g, max(age - 1.0, 0.0), if age >= 1.0 { 1.0 } else { 0.0 });
                // S1: the contracted part belongs to the storer; it does not spoil until delivery (short)
                let loss = (m.qty - m.contract_left()) * (1.0 - keep_frac);
                if loss > 0.0 {
                    m.qty -= loss;
                    m.cost_basis *= keep_frac;
                    c.ledger.goods_sink(g, "cargo_spoilage", loss);
                }
            }
            if c.cfg.cargo_spoil && !m.hold.is_empty() {
                // K-040: lots in the hold spoil too
                for l in m.hold.iter_mut() {
                    if l.cargo_day < 0 || l.qty <= 0.0 {
                        continue;
                    }
                    let age = (day - l.cargo_day) as f64;
                    let keep_frac = c.cargo_survival(l.g, max(age - 1.0, 0.0), if age >= 1.0 { 1.0 } else { 0.0 });
                    let loss = l.qty * (1.0 - keep_frac);
                    if loss > 0.0 {
                        l.qty -= loss;
                        l.cost_basis *= keep_frac;
                        c.ledger.goods_sink(l.g, "cargo_spoilage", loss);
                    }
                }
            }
            let lc = min(c.cfg.living_cost, m.cash);
            m.cash -= lc;
            c.ledger.money_sink("merchant_living", lc);
            let mut sc = pymath::int(min(pymath::round(c.cfg.ship_cost_day) as f64, m.cash)) as f64;
            if c.cfg.ship_market && !m.is_player && m.ship.is_none() {
                sc = 0.0;
            }
            if sc > 0.0 {
                m.cash -= sc;
                c.ledger.money_sink("ship_costs", sc);
            }
            if c.mixed() {
                Core::share_overhead(&mut m, lc + sc);
            } else if m.voy.is_some() {
                m.voy_overhead = m.voy_overhead + lc + sc;
            }
            let poor = m.cash < 0.1 * m.start_capital;
            if !m.is_player && m.state == MState::Buying && m.empty() && poor {
                let cash = m.cash;
                c.ledger.money_sink("merchant_exit", cash);
                c.to_pool(&m, cash);
                c.ruin_days.push(day);
                c.bankruptcies += 1;
                c.release_ship(&mut m);
                self.gone.push(Gone(m, day, cash));
                continue;
            }
            keep.push(m);
        }
        self.merchants = keep;
    }
}
