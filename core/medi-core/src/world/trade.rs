//! Merchant decisions: expectations (C4), rivals (K-014), options, departure, sell decision (S), after the kapan.

use super::*;
use crate::consts::{goods5, GoodKind, CUSTOMS, FREIGHT_PER_BULK_DAY};
use crate::pymath::{exp, log, max, min, pow, sqrt};

const LEVELS4: [f64; 4] = [0.25, 0.5, 0.75, 1.0];

impl Core {
    #[inline]
    pub fn winter(&self) -> bool {
        matches!(self.date.month(), 11 | 12 | 1 | 2)
    }

    #[inline]
    pub fn voyage(&self, a: Port, b: Port) -> f64 {
        self.days[a.idx()][b.idx()] * if self.winter() { 1.5 } else { 1.0 }
    }

    /// E2 commission (network off: 0).
    #[inline]
    pub fn comm(&self, _m: &M5, _p: Port) -> f64 {
        0.0
    }

    /// DARA risk attitude (Arrow-Pratt; Roy 1952 safety-first).
    pub fn risk(&self, m: &M5) -> f64 {
        if !m.dara {
            return m.risk_aversion;
        }
        let w = max(m.net_worth(), 1.0) / m.start_capital;
        let mut ra = m.risk_aversion * min(3.0, max(0.5, pow(w, -0.5)));
        if w < 0.4 {
            ra += 1.0;
        }
        ra
    }

    /// Cache of intermediate results that stay fixed during one merchant decision (same day, same merchant):
    /// normal prices (median), risk attitude, known loadings per market. Pure speed; results are bit-identical.
    pub fn ctx(&self) -> Ctx {
        Ctx { normal: vec![None; self.markets.len()], risk: None, buckets: None }
    }

    #[inline]
    fn normal_c(m: &M5, mi: usize, ctx: &mut Ctx) -> f64 {
        *ctx.normal[mi].get_or_insert_with(|| Self::normal_of(m, mi))
    }

    #[inline]
    fn risk_c(&self, m: &M5, ctx: &mut Ctx) -> f64 {
        *ctx.risk.get_or_insert_with(|| self.risk(m))
    }

    /// `_expect`: C4 expectation (lognormal widening with age + reversion to the normal price).
    pub fn expect(&self, m: &M5, mi: usize, travel: f64) -> f64 {
        if m.informed {
            return self.best_bid(mi);
        }
        let r = self.risk(m);
        self.expect_n(m, mi, travel, Self::normal_of(m, mi), r)
    }

    /// Normal price: median of the last 20 observations.
    #[inline]
    fn normal_of(m: &M5, mi: usize) -> f64 {
        let hist = &m.hist[mi];
        pymath::np_median(&hist[hist.len().saturating_sub(20)..])
    }

    /// `expect` (uninformed merchant), with the normal price given.
    fn expect_n(&self, m: &M5, mi: usize, travel: f64, normal: f64, risk: f64) -> f64 {
        let (price, oday) = m.obs[mi];
        let h = (self.day - oday) as f64 + travel;
        let sigma = sqrt(self.sig0 + self.sig1 / 365.0 * h) * m.overconf;
        let log_med = log(normal) + (log(price) - log(normal)) * exp(-h / self.cfg.revert_days);
        exp(log_med - (risk - 0.5) * sigma)
    }

    /// `_expect_fwd` (B): weighted mean of a fundamental projection and the price history (Brock & Hommes 1998).
    pub fn expect_fwd(&self, m: &M5, mi: usize, travel: f64) -> f64 {
        self.expect_fwd_c(m, mi, travel, &mut self.ctx())
    }

    pub fn expect_fwd_c(&self, m: &M5, mi: usize, travel: f64, ctx: &mut Ctx) -> f64 {
        if m.informed {
            return self.best_bid(mi);
        }
        let normal = Self::normal_c(m, mi, ctx);
        let risk = self.risk_c(m, ctx);
        let c4 = self.expect_n(m, mi, travel, normal, risk);
        if !self.cfg.forward || !self.cfg.forward_fund || m.w_fund <= 0.0 {
            return c4;
        }
        let g = self.market_keys[mi].1;
        let mut f = normal;
        if goods5(g).kind == GoodKind::Harvest {
            let mk = &self.markets[mi];
            if let Some((ratio, hday)) = m.hnews[mi] {
                if self.day - hday < 365 {
                    f *= min(3.0, max(1.0 / 3.0, pow(ratio, 1.0 / mk.cfg.elasticity)));
                }
            }
            let dth = pymath::fmod_py(mk.days_to_harvest() as f64 - travel, 365.0);
            f *= 1.0 + self.cfg.season_carry * ((1.0 - dth / 365.0) - 0.5);
        }
        let (_, oday) = m.obs[mi];
        let h = (self.day - oday) as f64 + travel;
        let sigma = sqrt(self.sig0 + self.sig1 / 365.0 * h) * m.overconf;
        f *= exp(-(risk - 0.5) * sigma);
        m.w_fund * f + (1.0 - m.w_fund) * c4
    }

    #[inline]
    pub fn impact(&self, depth0: f64, crowd: f64, q_own: f64) -> f64 {
        let own = self.cfg.forward && self.cfg.forward_impact;
        depth0 / (depth0 + crowd + if own { q_own } else { 0.0 })
    }

    /// `_rivals`: rival loadings heard of -> (crowding, imitation bonus).
    pub fn rivals(&self, m: &M5, d: Port, g: Good, depth0: f64) -> (f64, f64) {
        self.rivals_b(m, d, g, depth0, None)
    }

    /// Known loadings per market (order kept): computed once instead of `rivals` scanning every record for each
    /// (target, good). The sum is taken in the same order, so the result is bit-identical.
    pub fn known_buckets(&self, m: &M5) -> Vec<Vec<f64>> {
        let since = self.day - self.cfg.load_memory_days;
        let mut b = vec![Vec::new(); self.markets.len()];
        for v in m.known_loads.values() {
            if v.4 >= since {
                if let Some(mi) = self.mi(v.1, v.2) {
                    b[mi].push(v.3);
                }
            }
        }
        b
    }

    pub fn rivals_b(&self, m: &M5, d: Port, g: Good, depth0: f64, buckets: Option<&[Vec<f64>]>) -> (f64, f64) {
        let cfg = &self.cfg;
        if !cfg.rival_info || m.known_loads.is_empty() {
            return (0.0, 0.0);
        }
        let since = self.day - cfg.load_memory_days;
        let own = 0.0;
        let mut known = match (buckets, self.mi(d, g)) {
            (Some(b), Some(mi)) => pymath::sum(b[mi].iter().copied()),
            _ => pymath::sum(m.known_loads.values().filter(|v| v.1 == d && v.2 == g && v.4 >= since).map(|v| v.3)),
        };
        if cfg.visibility && !m.seen_buys.is_empty() {
            let mut known_ids: Option<std::collections::HashSet<Mid, FxBuild>> = None;
            for &(mid, o, gg, q, _day) in &m.seen_buys {
                if gg != g || o == d {
                    continue;
                }
                let ids = known_ids.get_or_insert_with(|| m.known_loads.values().map(|v| v.5).collect());
                if ids.contains(&mid) {
                    continue;
                }
                let tot = pymath::sum(
                    self.port_list.iter().filter(|&&x| x != o && self.has_market(x, g)).map(|&x| self.demand(x, g)),
                );
                let tot = if tot == 0.0 { 1.0 } else { tot };
                known += q * self.demand(d, g) / tot;
            }
        }
        if let Some(mi) = self.mi(d, g) {
            if let Some((q_h, day_h)) = m.harbor[mi] {
                if day_h >= since {
                    known += q_h;
                }
            }
        }
        if known <= 0.0 {
            return (own, 0.0);
        }
        let crowd = if m.level == 0 && !cfg.l0_counts_rivals {
            0.0
        } else if m.level >= 2 {
            0.5 * known
        } else {
            known
        };
        let bonus = m.imitation * 0.10 * min(1.0, known / depth0);
        (crowd + own, bonus)
    }

    /// K-036: does the port supply this good structurally (rural production or a production pool)? Common knowledge:
    /// what a port produces. Not the current state of quantity (shortage, glut).
    pub fn structural_supply(&self, p: Port, mi: usize, g: Good) -> bool {
        self.markets[mi].rural.annual_capacity > 0.0 || self.pool_idx(p, g).is_some()
    }

    /// K-036: supply curve in the current port: [(price, quantity available)], price = ask x {1; 1.15; 1.35; 1.6; 2}.
    /// Available = `origin_horizon` days of rural supply (at that price) + storer stock (if below its floor) + pool output
    /// (if below its reservation) + cargo of selling merchants - local use over the same period - other buyers' plans.
    pub fn origin_curve(&self, p: Port, mi: usize, g: Good, ask: f64) -> Vec<(f64, f64)> {
        let mk = &self.markets[mi];
        let h = self.cfg.origin_horizon;
        let dth = mk.days_to_harvest();
        let pool = self.pool_idx(p, g).map(|i| &self.pools[i].1);
        let fee = 1.0 + self.cfg.kapan_fee;
        let sellers = self.waiting_cache[p.idx()][g.idx()];
        let others = self.buying_cache[p.idx()][g.idx()] + h * self.demand(p, g);
        [1.0, 1.15, 1.35, 1.6, 2.0]
            .iter()
            .map(|&f| {
                let px = ask * f;
                let pr = px / fee;
                let mut s = h * mk.rural.offered_at(pr, dth) + sellers;
                for st in &mk.storers {
                    if st.stock > 0.0 && st.sell_floor() <= pr {
                        s += st.stock;
                    }
                }
                if let Some(pl) = pool {
                    if pl.output > 0.0 && pl.reservation <= pr {
                        s += pl.output;
                    }
                }
                (px, (s - others).max(0.0))
            })
            .collect()
    }

    /// `_options(m, origin, asks)`: profitable (good, target) options, by descending score.
    pub fn options(&self, m: &M5, origin: Port, asks: Option<&[(Good, f64)]>) -> Vec<Opt> {
        self.options_c(m, origin, asks, &mut self.ctx())
    }

    pub fn options_c(&self, m: &M5, origin: Port, asks: Option<&[(Good, f64)]>, ctx: &mut Ctx) -> Vec<Opt> {
        let cfg = &self.cfg;
        let mut opts: Vec<Opt> = Vec::new();
        let sar = self.ship_at_risk(m);
        if ctx.buckets.is_none() && cfg.rival_info && !m.known_loads.is_empty() {
            ctx.buckets = Some(self.known_buckets(m));
        }
        // K-040: gain of the lots in the hold by target (only when planning from the current port)
        let hgain: Vec<f64> = if self.mixed() && origin == m.loc && !m.hold.is_empty() {
            self.port_list.iter().map(|&d| self.hold_gain(m, d, ctx)).collect()
        } else {
            Vec::new()
        };
        let cap_v = self.avail_cap(m);
        let (lf, ls) = (self.lot_fee(), self.lot_setup());
        for (mi, g) in self.markets_at(origin) {
            let ask = match asks {
                Some(a) => a.iter().find(|x| x.0 == g).unwrap().1,
                None => self.best_ask(mi),
            };
            let spec = goods5(g);
            let (tc, cf, hf) = (self.ship_day_cost(m), self.call_fee(), self.hfee(g));
            let curve = if cfg.origin_supply {
                match asks {
                    None => Some(self.origin_curve(origin, mi, g, ask)),
                    Some(_) if !self.structural_supply(origin, mi, g) => continue,
                    Some(_) => None,
                }
            } else {
                None
            };
            for &d in &self.port_list {
                if d == origin || (origin == m.loc && m.commit.is_some_and(|c| c != d)) {
                    continue;
                }
                let Some(dmi) = self.mi(d, g) else { continue };
                let days = self.voyage(origin, d);
                let hg = if hgain.is_empty() { 0.0 } else { hgain[d.idx()] };
                let e0 = self.expect_fwd_c(m, dmi, days, ctx);
                let depth0 = cfg.depth_days * self.demand(d, g);
                let (crowd, bonus) = self.rivals_b(m, d, g, depth0, ctx.buckets.as_deref());
                let depth = depth0 - 0.0 - crowd;
                let q_max = min(min(cap_v / spec.bulk, m.cash / ask), depth);
                if q_max < 1.0 {
                    continue;
                }
                if let Some(curve) = curve.as_deref() {
                    // K-036: supply curve at departure: quantity available at each price level; single-price clearing
                    let p_loss = self.p_loss(days, origin, d, false);
                    let mut best: Option<Opt> = None;
                    // M2.1: with the fill decision on, the load is chosen together with the waiting time, not from today's supply:
                    // supply flow ≈ avail / origin_horizon (per day); waiting days in port for the rest enter the score.
                    let fracs: &[f64] = if cfg.fill_decision { &[0.25, 0.5, 0.75, 1.0] } else { &[1.0] };
                    for &(px, avail) in curve {
                        for &f in fracs {
                            let cap = min(min(cap_v / spec.bulk, m.cash / px), depth);
                            let (q, fill_days) = if cfg.fill_decision {
                                let q = cap * f;
                                let flow = avail / max(cfg.origin_horizon, 1.0);
                                (
                                    q,
                                    if q <= avail {
                                        0.0
                                    } else if flow > 1e-9 {
                                        (q - avail) / flow
                                    } else {
                                        f64::INFINITY
                                    },
                                )
                            } else {
                                (min(cap, avail), 0.0)
                            };
                            if q < 1.0 || !fill_days.is_finite() || fill_days > 60.0 {
                                continue;
                            }
                            let e = e0 * self.impact(depth0, crowd, q);
                            let hd = self.handle_days(origin, g, q) + self.handle_days(d, g, q);
                            let net =
                                e * (1.0 - CUSTOMS) * (1.0 - p_loss) * self.cargo_survival(g, 0.0, days + fill_days)
                                    - self.freight_u(g, days)
                                    - p_loss * sar / q
                                    - self.sea_wear_cost(m, days) / q
                                    - (tc * (days + 3.0 + hd + fill_days + 2.0 * ls) + cf + 2.0 * lf) / q
                                    - 2.0 * hf;
                            let margin = net / px - 1.0 + bonus;
                            if margin > cfg.hurdle {
                                let score = (margin * q * px + hg) / (days + 3.0 + hd + fill_days + 2.0 * ls);
                                if best.is_none() || score > best.unwrap().score {
                                    best = Some(Opt { score, g, d, max_bid: net / (1.0 + cfg.hurdle), q });
                                }
                            }
                        }
                    }
                    if let Some(b) = best {
                        opts.push(b);
                    }
                    continue;
                }
                let p_loss = self.p_loss(days, origin, d, false);
                let grid: &[f64] = if cfg.forward && cfg.forward_impact { &LEVELS4 } else { &LEVELS4[3..] };
                let mut best: Option<Opt> = None;
                for &f in grid {
                    let q = q_max * f;
                    let e = e0 * self.impact(depth0, crowd, q);
                    let hd = self.handle_days(origin, g, q) + self.handle_days(d, g, q);
                    let net = e * (1.0 - CUSTOMS) * (1.0 - p_loss) * self.cargo_survival(g, 0.0, days)
                        - self.freight_u(g, days)
                        - p_loss * sar / max(q, 1.0)
                        - self.sea_wear_cost(m, days) / max(q, 1.0)
                        - (tc * (days + 3.0 + hd + 2.0 * ls) + cf + 2.0 * lf) / max(q, 1.0)
                        - 2.0 * hf;
                    let margin = net / ask - 1.0 + bonus;
                    if margin > cfg.hurdle {
                        let score = (margin * q * ask + hg) / (days + 3.0 + hd + 2.0 * ls);
                        if best.is_none() || score > best.unwrap().score {
                            best = Some(Opt { score, g, d, max_bid: net / (1.0 + cfg.hurdle), q });
                        }
                    }
                }
                if let Some(b) = best {
                    opts.push(b);
                }
            }
        }
        opts.sort_by(|a, b| (-a.score).partial_cmp(&-b.score).expect("NaN skor"));
        opts
    }

    /// `_ret_of`: yearly return of an option. Returns: (return, (voyage profit / capital, cycle time)); the second is
    /// Python's `self._last_voyage`.
    pub fn ret_of(
        &self,
        o: &Opt,
        capital: f64,
        origin: Port,
        asks: Option<&[(Good, f64)]>,
        extra_days: f64,
    ) -> (f64, (f64, f64)) {
        let ask = match asks {
            Some(a) => a.iter().find(|x| x.0 == o.g).unwrap().1,
            None => self.best_ask(self.mix(origin, o.g)),
        };
        let net = o.max_bid * (1.0 + self.cfg.hurdle);
        let days = self.voyage(origin, o.d);
        let hd = self.handle_days(origin, o.g, o.q) + self.handle_days(o.d, o.g, o.q);
        let t = extra_days + 2.0 * days + 3.0 + hd + o.q / max(self.demand(o.d, o.g), 1e-9);
        let frac = (net - ask) * o.q / max(capital, 1.0);
        (frac * 365.0 / t, (frac, t))
    }

    /// Rough buy-price estimate from prices in another port (`m.obs[(q, g)][0] / (1 - 0.05)`).
    fn guessed_asks(&self, m: &M5, q: Port) -> Vec<(Good, f64)> {
        self.markets_at(q).map(|(mi, g)| (g, m.obs[mi].0 / (1.0 - 0.05))).collect()
    }

    /// `_best_from(m, p)`: (yearly return, voyage profit / capital, route, last `_last_voyage`).
    pub fn best_from(&self, m: &M5, p: Port) -> (f64, f64, Option<Route>, Option<(f64, f64)>) {
        let (mut best, mut voy, mut route) = (-1.0, 0.0, None);
        let mut last = None;
        let mut ctx = self.ctx();
        for &q in &self.port_list {
            let asks = if q == p { None } else { Some(self.guessed_asks(m, q)) };
            let opts = self.options_c(m, q, asks.as_deref(), &mut ctx);
            let v = if q == p { 0.0 } else { self.voyage(p, q) };
            for o in &opts {
                let (r_o, lv) = self.ret_of(o, max(m.cash, 1.0), q, asks.as_deref(), v);
                last = Some(lv);
                if r_o > best {
                    best = r_o;
                    voy = lv.0;
                    route = Some((q, o.d, o.g));
                }
            }
        }
        (best, voy, route, last)
    }

    pub fn reposition(&mut self, m: &mut M5) {
        let (mut best, mut best_port) = (0.0, None);
        let mut ctx = self.ctx();
        for &q in &self.port_list {
            if q == m.loc {
                continue;
            }
            let asks = self.guessed_asks(m, q);
            let opts = self.options_c(m, q, Some(&asks), &mut ctx);
            if let Some(o) = opts.first() {
                let v = self.voyage(m.loc, q);
                let mut score = o.score * 0.5 / (1.0 + v / 10.0);
                if self.cfg.ship_risk && self.cfg.ballast_risk {
                    // M2.1: ship risk on an empty voyage (converted to a daily cost)
                    score -= self.p_loss(v, m.loc, q, false) * self.ship_at_risk(m) / (v + 3.0);
                }
                // S-028: ship time and port call fee of an empty voyage
                score -= (self.ship_day_cost(m) * v + self.call_fee() + self.sea_wear_cost(m, v)) / (v + 3.0);
                if score > best {
                    best = score;
                    best_port = Some(q);
                }
            }
        }
        if let Some(p) = best_port {
            self.depart(m, p);
        }
        m.wait = 0;
    }

    pub fn depart(&mut self, m: &mut M5, dest: Port) {
        assert!(m.contract.is_empty(), "departure with an open sale agreement");
        if self.cfg.port_costs.is_some() && m.qty > 0.0 {
            // S-028: loading fee: the whole bought load; on a reroute the landed part is reloaded
            let g = m.good.expect("cargo good");
            let units = if m.state == MState::Selling {
                if self.cfg.handling.is_some() {
                    max(0.0, m.qty - m.unload_left / goods5(g).bulk)
                } else {
                    m.qty
                }
            } else {
                m.qty
            };
            let fee = min(pymath::round(units * self.hfee(g)) as f64, max(m.cash, 0.0));
            if fee > 0.0 {
                m.cash -= fee;
                m.cost_basis += fee;
                self.ledger.money_sink("handling_fee", fee);
            }
        }
        if self.mixed() && m.qty > 0.0 && m.state == MState::Buying {
            // K-040: loading cost of a new lot (declaration, weighing)
            let fee = min(self.lot_fee(), max(m.cash, 0.0));
            if fee > 0.0 {
                m.cash -= fee;
                m.cost_basis += fee;
                self.ledger.money_sink("lot_fee", fee);
            }
        }
        if self.mixed() && m.qty > 0.0 && m.state == MState::Selling {
            // the lot being sold also sails: put it in the hold to keep the records whole
            let g = m.good.unwrap();
            let lot = Lot {
                g,
                qty: m.qty,
                cost_basis: m.cost_basis,
                cargo_day: m.cargo_day,
                voy: m.voy.take(),
                overhead: m.voy_overhead,
                flow: m.lot_flow,
                target: Some(dest),
            };
            Core::push_lot(m, lot);
            m.good = None;
            m.qty = 0.0;
            m.cost_basis = 0.0;
            m.cargo_day = -1;
            m.voy_overhead = 0.0;
            m.lot_flow = 0.0;
        }
        m.considered.clear();
        m.commit = None;
        m.loaded = 0.0;
        m.unload_left = 0.0;
        m.qty_prev = 0.0;
        m.fill_ema = 0.0;
        let base = self.voyage(m.loc, dest);
        let z = self.rng.get("voyage").normal(0.0, 0.25);
        let days = 2.max(pymath::round(base * exp(z)));
        let u = self.rng.get("voyage").random();
        let (pl, parts) = self.p_loss_real(days as f64, m.loc, dest);
        let lost = u < pl;
        let leg = self.cfg.hazard_model == crate::config::HazardModel::Leg;
        // cause of loss: by the share of each leg hazard (M1.3 log)
        let cause_of = |c: &mut Core| {
            let nat = pymath::sum(parts.iter().map(|x| x.0));
            let cor = pymath::sum(parts.iter().map(|x| x.1));
            let u2 = c.rng.get("loss_cause").random();
            if u2 < cor / (nat + cor) {
                "corsair"
            } else {
                "wreck"
            }
        };
        let age = m.ship.map(|b| self.day - b).unwrap_or(-1);
        let port_days = if m.arrive_day >= 0 { self.day - m.arrive_day } else { -1 };
        if m.empty() && self.cfg.ballast_risk && leg {
            // M1.4: an empty voyage is at risk too
            let mut cause = None;
            if lost {
                let k = cause_of(self);
                cause = Some(k.to_string());
                if self.cfg.ship_market && !m.is_player && m.ship.is_some() {
                    self.lose_ship(m, k == "corsair");
                }
            }
            self.dep_log.push((self.day, m.loc, dest, lost, cause, self.date.month(), false, age, port_days, days));
        }
        if self.cfg.sea_wear.is_some() {
            let w = min(pymath::round(self.sea_wear_cost(m, days as f64)) as f64, max(m.cash, 0.0));
            if w > 0.0 {
                m.cash -= w;
                if self.mixed() {
                    Core::share_overhead(m, w);
                } else {
                    m.cost_basis += if m.qty > 0.0 { w } else { 0.0 };
                }
                self.ledger.money_sink("ship_repairs", w);
            }
        }
        if self.mixed() && !m.hold.is_empty() {
            // K-040: lots in the hold: flow records, rival information, loss
            for l in &m.hold {
                let key = (self.date.year(), m.loc, dest, l.g);
                *self.flows.0.entry(key).or_insert(0.0) += l.qty;
                self.departures.push((self.day, m.loc, dest, l.g, l.qty, m.level));
                if self.cfg.rival_info {
                    self.load_id += 1;
                    let item = Load(m.loc, dest, l.g, l.qty, self.day, m.id);
                    self.loads[m.loc].insert(self.load_id, item);
                    m.known_loads.insert(self.load_id, item);
                }
            }
            if m.qty <= 0.0 && leg {
                let mut cause = None;
                if lost {
                    cause = Some(cause_of(self).to_string());
                }
                self.dep_log.push((
                    self.day,
                    m.loc,
                    dest,
                    lost,
                    cause.clone(),
                    self.date.month(),
                    true,
                    age,
                    port_days,
                    days,
                ));
                if lost {
                    if self.cfg.ship_market && !m.is_player && m.ship.is_some() {
                        self.lose_ship(m, cause.as_deref() == Some("corsair"));
                    }
                    if m.debt.is_some() {
                        m.debt_lost = true;
                    }
                }
            }
            if lost {
                for l in std::mem::take(&mut m.hold) {
                    self.ledger.goods_sink(l.g, "shipwreck", l.qty);
                }
            }
        }
        if m.qty > 0.0 {
            let g = m.good.expect("cargo good");
            let freight = if self.cfg.sea_wear.is_some() {
                0.0
            } else {
                min(pymath::round(FREIGHT_PER_BULK_DAY * goods5(g).bulk * m.qty * days as f64) as f64, m.cash)
            };
            m.cash -= freight;
            m.cost_basis += freight;
            self.ledger.money_sink("freight", freight);
            let key = (self.date.year(), m.loc, dest, g);
            *self.flows.0.entry(key).or_insert(0.0) += m.qty;
            let mut corsair = false;
            if leg {
                let mut cause = None;
                if lost {
                    let k = cause_of(self);
                    corsair = k == "corsair";
                    cause = Some(k.to_string());
                }
                self.dep_log.push((self.day, m.loc, dest, lost, cause, self.date.month(), true, age, port_days, days));
            }
            if lost {
                self.ledger.goods_sink(g, "shipwreck", m.qty);
                if self.cfg.ship_market && !m.is_player {
                    self.lose_ship(m, corsair);
                } else if self.cfg.ship_loss > 0.0 {
                    let sl = pymath::int(min(self.cfg.ship_loss, m.cash)) as f64;
                    m.cash -= sl;
                    self.ledger.money_sink("ship_loss", sl);
                }
                if m.debt.is_some() {
                    m.debt_lost = true;
                }
                m.qty = 0.0;
                m.cost_basis = 0.0;
            }
        }
        if m.qty > 0.0 {
            let g = m.good.unwrap();
            self.departures.push((self.day, m.loc, dest, g, m.qty, m.level));
            if self.cfg.rival_info {
                self.load_id += 1;
                let item = Load(m.loc, dest, g, m.qty, self.day, m.id);
                self.loads[m.loc].insert(self.load_id, item);
                m.known_loads.insert(self.load_id, item);
            }
        }
        let since = self.day - self.cfg.load_memory_days;
        m.known_loads.retain(|_, v| v.4 >= since);
        let prices: Vec<(Good, f64)> = self.markets_at(m.loc).map(|(mi, g)| (g, self.best_bid(mi))).collect();
        m.packet = Some(Packet(m.loc, self.day, prices));
        if self.cfg.info_relay {
            // I1: everything it knows (including today's prices at the departure port; obs is current from observation)
            m.packet_all = m.obs.iter().enumerate().filter(|x| x.1 .1 > 0).map(|(mi, &(p, d))| (mi, p, d)).collect();
        }
        if self.cfg.forward {
            m.packet_hnews = m.hnews.clone();
        }
        if self.cfg.rival_info {
            m.packet_harbor = m.harbor.clone();
        }
        m.carried = m.known_loads.clone();
        if m.qty > 0.0 && m.voy.is_none() {
            if let Some(plan) = m.plan {
                m.voy = Some(Voy(
                    self.day,
                    m.good.unwrap(),
                    m.qty,
                    plan.2 * (1.0 + self.cfg.hurdle),
                    m.cost_basis / m.qty,
                    m.cash,
                    m.loc,
                    dest,
                    m.level,
                ));
                m.voy_overhead = 0.0;
                m.lot_flow = 0.0;
            }
        }
        m.state = MState::Sailing;
        m.dest = Some(dest);
        m.arrive_day = self.day + days;
        m.plan = None;
        m.wait = 0;
    }

    /// `_sell_plan` (S): each day sell / wait / reroute (optimal stopping; the seller's side of McCall 1970).
    pub fn sell_plan(&mut self, m: &mut M5) {
        let cfg = &self.cfg;
        let g = m.good.expect("cargo good");
        let r_d = (cfg.bond_rate + cfg.risk_premium) / 365.0;
        let here = m.loc;
        let hmi = self.mix(here, g);
        let mut ctx = self.ctx();
        if cfg.rival_info && !m.known_loads.is_empty() {
            ctx.buckets = Some(self.known_buckets(m));
        }
        let e_here = self.expect_fwd_c(m, hmi, 0.0, &mut ctx);
        let value = e_here * m.qty;
        let hold = (value + m.start_capital) * r_d / m.qty;
        let waiting = self.waiting_cache[here.idx()][g.idx()];
        let mut rate = self.demand(here, g);
        if cfg.visibility {
            rate = max(self.kapan_today[hmi].unwrap_or(0.0), 0.1 * rate);
        }
        let depth0 = cfg.depth_days * self.demand(here, g);
        let t_here = waiting / max(rate, 1e-9);
        let p_here = e_here * self.impact(depth0, max(0.0, waiting - m.qty), if cfg.forward { m.qty } else { 0.0 });
        let age = self.cargo_age(m);
        // S-028: ship time, port call fee, handling, customs on landing (sunk for the landed part)
        let (tc, cf, hf) = (self.ship_day_cost(m), self.call_fee(), self.hfee(g));
        let aboard = if self.cfg.port_costs.is_none() {
            m.qty
        } else if cfg.handling.is_some() {
            min(m.qty, m.unload_left / goods5(g).bulk)
        } else {
            0.0
        };
        let on_dock = max(0.0, m.qty - aboard);
        let cust_here = if self.entry_duty() { CUSTOMS * aboard / max(m.qty, 1e-9) } else { CUSTOMS };
        let reload_days =
            if cfg.handling.is_some() { on_dock * goods5(g).bulk / self.handle_rate_g(here, g) } else { 0.0 };
        // waiting cargo spoils too: over the mean wait (half the queue)
        let v_stay =
            p_here * (1.0 - cust_here) * (1.0 - self.comm(m, here)) * self.cargo_survival(g, age, t_here / 2.0)
                - hold * t_here
                - tc * t_here / max(m.qty, 1.0)
                - hf * aboard / max(m.qty, 1.0);
        // K-040: selling here frees space; this value enters only the stay/carry comparison, not the asking price
        let v_cmp = v_stay + if self.mixed() { m.fill_val * goods5(g).bulk } else { 0.0 };
        let (mut best, mut best_d) = (v_cmp * (1.0 + cfg.reroute_margin), None);
        let mut best_info = (0.0, 0.0, 0.0, 0.0);
        for &d in &self.port_list {
            if d == here || (self.mixed() && m.commit.is_some_and(|c| c != d)) {
                continue;
            }
            let Some(dmi) = self.mi(d, g) else { continue };
            let days = self.voyage(here, d);
            let d0 = cfg.depth_days * self.demand(d, g);
            let (crowd, _) = self.rivals_b(m, d, g, d0, ctx.buckets.as_deref());
            let e_raw = self.expect_fwd_c(m, dmi, days, &mut ctx);
            let imp_d = self.impact(d0, crowd, m.qty);
            let e = e_raw * imp_d;
            let t_d = days + reload_days + (crowd + m.qty) / max(self.demand(d, g), 1e-9) / 2.0;
            let pl = self.p_loss(days, here, d, false);
            let v = e * (1.0 - CUSTOMS) * (1.0 - self.comm(m, d)) * (1.0 - pl) * self.cargo_survival(g, age, t_d)
                - self.freight_u(g, days)
                - self.sea_wear_cost(m, days) / max(m.qty, 1.0)
                - hold * t_d
                - pl * self.ship_at_risk(m) / max(m.qty, 1.0)
                - (tc * t_d + cf) / max(m.qty, 1.0)
                - hf * (1.0 + on_dock / max(m.qty, 1.0));
            if v > best {
                best = v;
                best_d = Some(d);
                best_info = (e_raw, imp_d, t_d, (self.day - m.obs[dmi].1) as f64);
            }
        }
        // S1: no lot goes to the hold while a contracted delivery is under way
        if let (Some(d), true) = (best_d, m.contract.is_empty()) {
            if m.wait >= 1 || m.pre_land {
                self.reroutes += 1;
                // I0 diagnostic: what the reroute expected (the price found on arrival is appended)
                let imp_here = self.impact(depth0, max(0.0, waiting - m.qty), if cfg.forward { m.qty } else { 0.0 });
                m.rr = vec![
                    self.day as f64,
                    here.idx() as f64,
                    d.idx() as f64,
                    g.idx() as f64,
                    e_here,
                    imp_here,
                    t_here,
                    best_info.0,
                    best_info.1,
                    best_info.2,
                    best_info.3,
                    m.qty,
                ];
                if self.mixed() {
                    // K-040: put the rest in the hold, move to the next lot or to buying (partial sale)
                    self.stow(m, d);
                } else {
                    self.depart(m, d);
                }
                return;
            }
        }
        m.reservation = max(0.0, v_stay / ((1.0 - cust_here) * (1.0 - self.comm(m, here))));
        if m.pre_land {
            m.pre_land = false;
            self.start_landing(m);
            if self.cfg.sale_contract {
                self.make_contract(m);
            }
        }
    }

    pub fn plan_merchant(&mut self, m: &mut M5) {
        if m.plan.is_some() || m.broke {
            return;
        }
        if self.cfg.ship_market && m.ship.is_none() && !m.is_player {
            return;
        }
        let mut opts = self.options(m, m.loc, None);
        if !opts.is_empty() && self.cfg.debt && !m.is_player && m.debt.is_none() {
            opts = self.finance(m, opts);
        }
        if let Some(o) = opts.first() {
            m.plan = Some(Plan(o.g, o.d, o.max_bid, o.q));
        }
    }

    pub fn after_kapan(&mut self, m: &mut M5) {
        if m.state == MState::Selling {
            if m.qty <= max(1e-9, self.cfg.dust_lot) {
                // S1: the remaining contracted crumbs go to the storer who already paid
                self.close_contract(m);
                if m.qty > 0.0 {
                    self.ledger.goods_sink(m.good.unwrap(), "lot_dust", m.qty);
                }
                m.qty = 0.0;
                m.cost_basis = 0.0;
                m.good = None;
                m.state = MState::Buying;
                m.wait = 0;
                self.settle(m);
                if self.mixed() {
                    m.lot_flow = 0.0;
                    m.cargo_day = -1;
                    m.unload_left = 0.0;
                    self.activate_next(m);
                }
                return;
            }
            m.wait += 1;
            if self.cfg.handling.is_some() {
                let before = m.unload_left;
                m.unload_left = max(0.0, m.unload_left - self.handle_rate_g(m.loc, m.good.unwrap()));
                // setup time (K-040) sits on top of the unloading counter: only goods actually on board are landed
                let b = goods5(m.good.unwrap()).bulk;
                let qb = m.qty * b;
                let units = max(0.0, min(before, qb) - min(m.unload_left, qb)) / b;
                self.land_goods(m, units);
                self.deliver(m);
            }
            return;
        }
        if m.state != MState::Buying {
            return;
        }
        m.wait += 1;
        let Some(plan) = m.plan else {
            if self.mixed() && !m.hold.is_empty() {
                // K-040: no new lot to buy; carry the hold
                let force = m.wait >= 7;
                self.hold_depart(m, force);
            } else if m.wait >= 7 {
                self.reposition(m);
            }
            return;
        };
        let Plan(g, d, _, q_max) = plan;
        if m.qty > 0.0 && m.cargo_day < 0 {
            m.cargo_day = self.day;
        }
        let target = min(self.avail_cap(m) / goods5(g).bulk, q_max);
        let bulk = goods5(g).bulk;
        let rate = self.handle_rate_g(m.loc, g);
        let su = if self.mixed() && m.qty > 0.0 { self.lot_setup() * rate } else { 0.0 };
        if self.cfg.handling.is_some() {
            m.loaded = min(m.qty * bulk + su, m.loaded + rate);
        }
        let ready = self.cfg.handling.is_none() || m.loaded >= m.qty * bulk + su - 1e-6;
        let go = if self.cfg.fill_decision && m.qty > 0.0 {
            // M2.1: marginal value theorem (Charnov 1976): depart when today's fill rate drops below the voyage's
            // mean rate (load / total cycle time).
            let dq = max(0.0, m.qty - m.qty_prev);
            m.fill_ema = if m.qty_prev <= 0.0 { dq } else { 0.5 * m.fill_ema + 0.5 * dq };
            m.qty_prev = m.qty;
            let left = if self.cfg.handling.is_some() { max(0.0, m.qty * bulk - m.loaded) / rate } else { 0.0 };
            let rest = self.voyage(m.loc, d) + left + self.handle_days(d, g, m.qty) + 3.0;
            m.qty >= 0.98 * target || m.cash < 1000.0 || m.wait >= 60 || m.fill_ema < m.qty / (m.wait as f64 + rest)
        } else {
            m.qty >= 0.9 * target || m.wait >= 5 || m.cash < 1000.0
        };
        if m.qty > 0.0 && go {
            if ready {
                self.depart(m, d);
            }
        } else if m.qty <= 0.0 && m.wait >= 7 {
            m.plan = None;
            if self.mixed() && !m.hold.is_empty() {
                self.hold_depart(m, true);
            } else {
                self.reposition(m);
            }
        }
    }
}

impl Core {
    // --- K-040 mixed cargo ------------------------------------------------------

    pub fn mixed(&self) -> bool {
        self.cfg.mixed.is_some()
    }

    fn lot_fee(&self) -> f64 {
        self.cfg.mixed.as_ref().map(|x| x.lot_fee).unwrap_or(0.0)
    }

    fn lot_setup(&self) -> f64 {
        self.cfg.mixed.as_ref().map(|x| x.lot_setup_days).unwrap_or(0.0)
    }

    /// Volume left for a new lot: including broken stowage (lots in the hold + the active lot).
    pub fn avail_cap(&self, m: &M5) -> f64 {
        let Some(mx) = &self.cfg.mixed else { return m.capacity };
        let n = m.hold.len() as f64 + 1.0;
        let used: f64 = m.hold.iter().map(|l| l.qty * goods5(l.g).bulk).sum();
        max(0.0, m.capacity * (1.0 - mx.stowage_loss * (n - 1.0)) - used)
    }

    /// Value the hold's lots gain if carried to `d` (there - here), total money.
    fn hold_gain(&self, m: &M5, d: Port, ctx: &mut Ctx) -> f64 {
        if m.hold.is_empty() {
            return 0.0;
        }
        let here = m.loc;
        let days = if d == here { 0.0 } else { self.voyage(here, d) };
        let pl = if d == here { 0.0 } else { self.p_loss(days, here, d, false) };
        let mut out = 0.0;
        for l in &m.hold {
            let age = if l.cargo_day >= 0 { (self.day - l.cargo_day) as f64 } else { 0.0 };
            let v_here = match self.mi(here, l.g) {
                Some(hmi) => self.best_bid(hmi) * (1.0 - CUSTOMS) * l.qty,
                None => 0.0,
            };
            let v_d = match self.mi(d, l.g) {
                Some(dmi) if d != here => {
                    let d0 = self.cfg.depth_days * self.demand(d, l.g);
                    let (crowd, _) = self.rivals_b(m, d, l.g, d0, ctx.buckets.as_deref());
                    let e = self.expect_fwd_c(m, dmi, days, ctx) * self.impact(d0, crowd, l.qty);
                    e * (1.0 - CUSTOMS) * (1.0 - pl) * self.cargo_survival(l.g, age, days) * l.qty - self.lot_fee()
                }
                _ => v_here,
            };
            out += v_d - v_here;
        }
        out
    }

    /// Put the unsold active lot in the hold (the landed part is reloaded) and move to the next.
    pub fn stow(&mut self, m: &mut M5, target: Port) {
        if m.commit.is_none() {
            m.commit = Some(target);
        }
        let g = m.good.expect("cargo good");
        if m.qty <= max(1e-9, self.cfg.dust_lot) {
            // dust: cannot be sold, discarded
            self.ledger.goods_sink(g, "lot_dust", m.qty);
            m.qty = 0.0;
            m.cost_basis = 0.0;
            m.good = None;
            m.voy = None;
            m.voy_overhead = 0.0;
            m.lot_flow = 0.0;
            m.cargo_day = -1;
            m.unload_left = 0.0;
            m.pre_land = false;
            self.activate_next(m);
            return;
        }
        if self.cfg.handling.is_some() {
            let on_dock = max(0.0, m.qty - m.unload_left / goods5(g).bulk);
            let fee = min(pymath::round(on_dock * self.hfee(g)) as f64, max(m.cash, 0.0));
            if fee > 0.0 {
                m.cash -= fee;
                m.cost_basis += fee;
                m.lot_flow -= fee;
                self.ledger.money_sink("handling_fee", fee);
            }
        }
        let lot = Lot {
            g,
            qty: m.qty,
            cost_basis: m.cost_basis,
            cargo_day: m.cargo_day,
            voy: m.voy.take(),
            overhead: m.voy_overhead,
            flow: m.lot_flow,
            target: Some(target),
        };
        Core::push_lot(m, lot);
        m.considered.push(g);
        m.good = None;
        m.qty = 0.0;
        m.cost_basis = 0.0;
        m.cargo_day = -1;
        m.voy_overhead = 0.0;
        m.lot_flow = 0.0;
        m.unload_left = 0.0;
        m.reservation = 0.0;
        m.pre_land = false;
        self.activate_next(m);
    }

    /// A lot starts landing: lot fee and setup time.
    pub fn start_landing(&mut self, m: &mut M5) {
        let fee = min(self.lot_fee(), max(m.cash, 0.0));
        if fee > 0.0 {
            m.cash -= fee;
            m.cost_basis += fee;
            m.lot_flow -= fee;
            self.ledger.money_sink("lot_fee", fee);
        }
    }

    /// Make a hold lot not yet considered in this port active; otherwise switch to buying.
    pub fn activate_next(&mut self, m: &mut M5) {
        assert!(m.contract.is_empty(), "lot switch with an open sale agreement");
        let here = m.loc;
        let mut best: Option<(usize, f64)> = None;
        for (i, l) in m.hold.iter().enumerate() {
            if m.considered.contains(&l.g) {
                continue;
            }
            let Some(hmi) = self.mi(here, l.g) else { continue };
            // lots targeting this port first, then the one most expensive here (relative to reference)
            let r = self.best_bid(hmi) / goods5(l.g).reff + if l.target == Some(here) { 1e6 } else { 0.0 };
            if best.is_none_or(|b| r > b.1) {
                best = Some((i, r));
            }
        }
        let Some((i, _)) = best else {
            m.state = MState::Buying;
            m.wait = 0;
            return;
        };
        let l = m.hold.remove(i);
        m.good = Some(l.g);
        m.qty = l.qty;
        m.cost_basis = l.cost_basis;
        m.cargo_day = l.cargo_day;
        m.voy = l.voy;
        m.voy_overhead = l.overhead;
        m.lot_flow = l.flow;
        m.state = MState::Selling;
        if self.cfg.handling.is_some() {
            m.unload_left = m.qty * goods5(l.g).bulk + self.lot_setup() * self.handle_rate_g(here, l.g);
        }
        // decide first: landing starts only if the lot is to be sold (end of sell_plan)
        m.pre_land = true;
        self.sell_plan(m);
    }

    /// With no new lot, carry the hold to the port where it is worth most.
    pub fn hold_depart(&mut self, m: &mut M5, force: bool) {
        let mut ctx = self.ctx();
        if self.cfg.rival_info && !m.known_loads.is_empty() {
            ctx.buckets = Some(self.known_buckets(m));
        }
        let tc = self.ship_day_cost(m);
        let mut best: Option<(Port, f64)> = None;
        for &d in &self.port_list.clone() {
            if d == m.loc || m.commit.is_some_and(|c| c != d) {
                continue;
            }
            let v = self.voyage(m.loc, d);
            let gain = self.hold_gain(m, d, &mut ctx)
                - tc * v
                - self.call_fee()
                - self.sea_wear_cost(m, v)
                - self.p_loss(v, m.loc, d, false) * self.ship_at_risk(m);
            let sc = gain / (v + 3.0);
            if best.is_none_or(|b| sc > b.1) {
                best = Some((d, sc));
            }
        }
        if let Some((d, sc)) = best {
            if sc > 0.0 || force {
                self.depart(m, d);
            }
        }
    }

    /// K-040: value per volume unit of free space in this port (profit / volume of the best buy option).
    pub fn set_fill_val(&self, m: &mut M5) {
        if !self.mixed() {
            return;
        }
        let opts = self.options(m, m.loc, None);
        m.fill_val = match opts.first() {
            Some(o) if o.q > 0.0 => {
                let ask = self.best_ask(self.mix(m.loc, o.g));
                max(0.0, o.max_bid * (1.0 + self.cfg.hurdle) - ask) / goods5(o.g).bulk
            }
            _ => 0.0,
        };
    }

    /// K-040: put a lot in the hold; merge with a lot of the same good (quantity, cost, records weighted).
    pub fn push_lot(m: &mut M5, l: Lot) {
        if let Some(x) = m.hold.iter_mut().find(|x| x.g == l.g) {
            let q = x.qty + l.qty;
            if q > 0.0 {
                if x.cargo_day >= 0 && l.cargo_day >= 0 {
                    x.cargo_day = ((x.cargo_day as f64 * x.qty + l.cargo_day as f64 * l.qty) / q).round() as i64;
                } else if x.cargo_day < 0 {
                    x.cargo_day = l.cargo_day;
                }
            }
            x.voy = match (x.voy, l.voy) {
                (Some(a), Some(b)) => {
                    let qq = a.2 + b.2;
                    Some(Voy(
                        a.0.min(b.0),
                        a.1,
                        qq,
                        (a.3 * a.2 + b.3 * b.2) / qq.max(1e-9),
                        (a.4 * a.2 + b.4 * b.2) / qq.max(1e-9),
                        a.5,
                        a.6,
                        a.7,
                        a.8,
                    ))
                }
                (a, b) => a.or(b),
            };
            x.qty = q;
            x.cost_basis += l.cost_basis;
            x.overhead += l.overhead;
            x.flow += l.flow;
            if x.target.is_none() {
                x.target = l.target;
            }
        } else {
            m.hold.push(l);
        }
    }

    /// Split ship time costs over lots by cost share (per-lot profit records).
    pub fn share_overhead(m: &mut M5, amount: f64) {
        let tot = (if m.qty > 0.0 && m.voy.is_some() { m.cost_basis } else { 0.0 })
            + m.hold.iter().filter(|l| l.voy.is_some()).map(|l| l.cost_basis).sum::<f64>();
        if tot <= 0.0 {
            return;
        }
        if m.qty > 0.0 && m.voy.is_some() {
            m.voy_overhead += amount * m.cost_basis / tot;
        }
        for l in m.hold.iter_mut().filter(|l| l.voy.is_some()) {
            l.overhead += amount * l.cost_basis / tot;
        }
    }

    /// M2.1: the port's loading/unloading rate (volume units/day); infinite when off.
    pub fn handle_rate(&self, p: Port) -> f64 {
        match self.cfg.handling {
            None => f64::INFINITY,
            Some(r) => {
                let t = &crate::map::get().ports[p.idx()].tier;
                match t.as_str() {
                    "büyük" => r[0],
                    "küçük" => r[2],
                    _ => r[1],
                }
            }
        }
    }

    /// S-028: daily cost of ship time (for decisions). Crew + victuals (`ship_cost_day`), living,
    /// interest on ship capital and wear. In competitive equilibrium a ship's opportunity cost equals its full cost.
    pub fn ship_day_cost(&self, m: &M5) -> f64 {
        let Some(pc) = &self.cfg.port_costs else { return 0.0 };
        if !pc.time_cost {
            return 0.0;
        }
        let cfg = &self.cfg;
        let has_ship = !(cfg.ship_market && !m.is_player && m.ship.is_none());
        let mut c = cfg.living_cost;
        if has_ship {
            c += cfg.ship_cost_day;
        }
        let sv = self.ship_px * self.ship_r(m);
        if sv > 0.0 {
            c += sv * (cfg.bond_rate + cfg.risk_premium) / 365.0
                + cfg.ship_price * (1.0 - cfg.ship_scrap) / cfg.ship_life / 365.0;
        }
        c
    }

    /// Freight proxy per unit of goods; none with `sea_wear` on (the cost is per ship).
    pub fn freight_u(&self, g: Good, days: f64) -> f64 {
        if self.cfg.sea_wear.is_some() {
            0.0
        } else {
            FREIGHT_PER_BULK_DAY * goods5(g).bulk * days
        }
    }

    /// S-028: sea wear (repairs) per ship, for `days` days at sea.
    pub fn sea_wear_cost(&self, m: &M5, days: f64) -> f64 {
        let Some(f) = self.cfg.sea_wear else { return 0.0 };
        let cfg = &self.cfg;
        if cfg.ship_market && !m.is_player && m.ship.is_none() {
            return 0.0;
        }
        cfg.ship_price * f / 365.0 * days
    }

    /// S-028: fee per ship on arrival at a port.
    pub fn call_fee(&self) -> f64 {
        self.cfg.port_costs.as_ref().map(|p| p.call_fee).unwrap_or(0.0)
    }

    /// S-028: one-way handling fee per unit of goods.
    pub fn hfee(&self, g: Good) -> f64 {
        self.cfg.port_costs.as_ref().map(|p| p.handling_fee * goods5(g).bulk).unwrap_or(0.0)
    }

    pub fn entry_duty(&self) -> bool {
        self.cfg.port_costs.as_ref().map(|p| p.entry_duty).unwrap_or(false)
    }

    /// S-028: goods landed: customs on landing (at the local kapan price) and the unloading fee.
    pub fn land_goods(&mut self, m: &mut M5, units: f64) {
        if units <= 0.0 || self.cfg.port_costs.is_none() {
            return;
        }
        let g = m.good.expect("cargo good");
        let mut cost = units * self.hfee(g);
        if self.entry_duty() {
            let px = self.mi(m.loc, g).and_then(|mi| self.kapan_price[mi]).unwrap_or(goods5(g).reff);
            let duty = min(pymath::round(units * px * CUSTOMS) as f64, max(m.cash, 0.0));
            m.cash -= duty;
            m.cost_basis += duty;
            m.lot_flow -= duty;
            self.ledger.money_sink("customs", duty);
        }
        cost = min(pymath::round(cost) as f64, max(m.cash, 0.0));
        if cost > 0.0 {
            m.cash -= cost;
            m.cost_basis += cost;
            m.lot_flow -= cost;
            self.ledger.money_sink("handling_fee", cost);
        }
    }

    /// S1 (K-040): sale agreement with local storers on arrival. With storers whose bid is above the merchant's
    /// acceptance price (`reservation`), up to their cash and space; paid now, goods delivered as unloaded.
    pub fn make_contract(&mut self, m: &mut M5) {
        let g = m.good.expect("cargo good");
        let Some(mi) = self.mi(m.loc, g) else { return };
        let res = m.reservation;
        let n = self.markets[mi].storers.len();
        let mut order: Vec<(usize, f64)> = (0..n).map(|i| (i, self.markets[mi].storers[i].bid())).collect();
        order.sort_by(|a, b| b.1.partial_cmp(&a.1).expect("NaN teklif"));
        for (i, b) in order {
            let left = m.qty - m.contract_left();
            if b < res || left < 1.0 {
                break;
            }
            let room = self.markets[mi].storers[i].buy_room(b);
            let q = min(left, room);
            if q < 1.0 {
                continue;
            }
            let pay = pymath::round(b * q) as f64;
            let fee = pymath::round(pay * self.cfg.kapan_fee) as f64;
            let duty = if self.entry_duty() { 0.0 } else { pymath::round((pay - fee) * CUSTOMS) as f64 };
            self.markets[mi].storers[i].cash -= pay;
            self.ledger.money_sink("contract_fee", fee);
            self.ledger.money_sink("customs", duty);
            let net = pay - fee - duty;
            let unit = m.cost_basis / max(left, 1e-9);
            m.cost_basis -= unit * q;
            m.cash += net;
            m.lot_flow += net;
            m.contract.push((i, q, b));
            self.contracts += 1;
        }
    }

    /// S1: contracted delivery from goods already landed.
    pub fn deliver(&mut self, m: &mut M5) {
        if m.contract.is_empty() {
            return;
        }
        let g = m.good.expect("cargo good");
        let Some(mi) = self.mi(m.loc, g) else { return };
        let b = goods5(g).bulk;
        let mut avail =
            if self.cfg.handling.is_some() { max(0.0, m.qty - min(m.unload_left, m.qty * b) / b) } else { m.qty };
        for c in m.contract.iter_mut() {
            if avail <= 0.0 {
                break;
            }
            let d = min(c.1, avail);
            self.markets[mi].storers[c.0].receive(d, c.2 * d);
            m.qty -= d;
            c.1 -= d;
            avail -= d;
        }
        m.contract.retain(|c| c.1 > 1e-9);
    }

    /// S1: when a lot closes, delivers the remaining contracted goods (whatever is on board) and closes the agreement.
    pub fn close_contract(&mut self, m: &mut M5) {
        if m.contract.is_empty() {
            return;
        }
        let g = m.good.expect("cargo good");
        let mi = self.mi(m.loc, g).expect("agreement market");
        for c in std::mem::take(&mut m.contract) {
            let d = min(c.1, max(m.qty, 0.0));
            if d > 0.0 {
                self.markets[mi].storers[c.0].receive(d, c.2 * d);
                m.qty -= d;
            }
        }
    }

    /// S2: handling rate by good (volume units/day): the slower of the port rate and the weighing rate.
    pub fn handle_rate_g(&self, p: Port, g: Good) -> f64 {
        let r = self.handle_rate(p);
        let (Some(w), Some(h)) = (&self.cfg.weigh_rate, self.cfg.handling) else { return r };
        let Some(&(_, u)) = w.iter().find(|x| x.0 == g) else { return r };
        let fac = r / h[0];
        min(r, u * fac * goods5(g).bulk)
    }

    /// Handling time of a lot in port (days).
    pub fn handle_days(&self, p: Port, g: Good, q: f64) -> f64 {
        if self.cfg.handling.is_none() {
            return 0.0;
        }
        q * goods5(g).bulk / self.handle_rate_g(p, g)
    }

    /// M2.1: ship value lost if the ship is lost (market price x replacement value).
    pub fn ship_at_risk(&self, m: &M5) -> f64 {
        if !self.cfg.ship_risk {
            return 0.0;
        }
        self.ship_px * self.ship_r(m)
    }
}

impl Core {
    /// Share of cargo that survives `extra` more days (current age `age`). 1 if spoilage is off.
    pub fn cargo_survival(&self, g: Good, age: f64, extra: f64) -> f64 {
        if !self.cfg.cargo_spoil {
            return 1.0;
        }
        let tau = crate::consts::cargo_tau(g);
        let k = self.cfg.cargo_spoil_k;
        exp(-(pow((age + extra) / tau, k) - pow(age / tau, k)))
    }

    pub fn cargo_age(&self, m: &M5) -> f64 {
        if m.cargo_day < 0 {
            0.0
        } else {
            (self.day - m.cargo_day) as f64
        }
    }
}
