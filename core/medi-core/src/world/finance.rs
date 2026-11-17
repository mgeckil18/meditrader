//! Hybrid finance (K-022, K-023): debt, per-voyage pricing by the lender; voyage settlement (`_settle`).
//! K-022/K-023 user note: not final, being tested by experiment.

use super::*;
use crate::config::LoanType;
use crate::consts::{goods5, CUSTOMS};
use crate::pymath::{erf, exp, log, max, min, pow, sqrt};

impl Core {
    /// `_own_view`: the merchant's belief about voyage returns (learning from experience; Malmendier & Nagel 2016).
    pub fn own_view(&self, m: &M5, frac: f64, deploy: f64) -> (f64, f64, i64) {
        let cfg = &self.cfg;
        let rec: Vec<f64> = m.record.iter().filter(|x| self.day - x.0 <= cfg.rep_window).map(|x| x.1).collect();
        let n = rec.len();
        let frac = frac / max(deploy, 1e-6);
        let mu =
            if n > 0 { (cfg.rep_k * frac + n as f64 * pymath::np_mean(&rec)) / (cfg.rep_k + n as f64) } else { frac };
        let sd = if n >= 5 {
            pymath::np_std(&rec)
        } else {
            match self.pop_roi {
                Some(p) => p.1,
                None => 0.2,
            }
        };
        let sd = max(0.02, sd * m.overconf);
        (mu * deploy, sd * deploy, n as i64)
    }

    pub fn deploy(&self, o: &Opt, k: f64, p: Port) -> f64 {
        min(1.0, o.q * self.best_ask(self.mix(p, o.g)) / max(k, 1.0))
    }

    /// `_lender_view` (K-023): the lender's voyage expectation (mu, sigma).
    fn lender_view(&self, p: Port, o: &Opt, k: f64) -> (f64, f64) {
        let cfg = &self.cfg;
        let (g, d, q) = (o.g, o.d, o.q);
        let travel = self.voyage(p, d);
        let dmi = self.mix(d, g);
        let (price, oday) = self.current[p][dmi];
        let hist = &self.current_hist[p][dmi];
        let normal = pymath::np_median(&hist[hist.len().saturating_sub(20)..]);
        let h = (self.day - oday) as f64 + travel;
        let e0 = exp(log(normal) + (log(max(price, 1e-9)) - log(normal)) * exp(-h / cfg.revert_days));
        let since = self.day - cfg.load_memory_days;
        let mut seen = std::collections::HashSet::new();
        let mut crowd = 0.0;
        if let Some(book) = self.lender_book.get(p) {
            for &(day, dd, gg, qq, mid) in book {
                if day >= since && dd == d && gg == g {
                    crowd += qq;
                    seen.insert(mid);
                }
            }
        }
        if let Some(loads) = self.loads.get(p) {
            for v in loads.values() {
                if v.1 == d && v.2 == g && v.4 >= since && !seen.contains(&v.5) {
                    crowd += v.3;
                }
            }
        }
        let depth0 = cfg.depth_days * self.demand(d, g);
        let e = e0 * depth0 / (depth0 + crowd + q);
        let net = e * (1.0 - CUSTOMS) * (1.0 - self.p_loss(travel, p, d, false)) - self.freight_u(g, travel);
        let ask = self.best_ask(self.mix(p, g));
        let margin = net / ask - 1.0;
        let sd = match self.route_stats.0.get(&(p, d, g)) {
            Some(st) if st.0 >= 8 => st.4,
            _ => match self.pop_roi {
                Some(pr) => pr.1,
                None => 0.3,
            },
        };
        let dep = min(1.0, q * ask / max(k, 1.0));
        (margin * dep, max(0.02, sd) * dep)
    }

    /// `_lender_quote`: (yearly time rate, per-voyage risk premium, PD, lender's mu), or None
    /// (credit rationing).
    fn lender_quote(&self, p: Port, o: &Opt, k: f64, b: f64, t: f64) -> Option<(f64, f64, f64, f64)> {
        let cfg = &self.cfg;
        let (mu, sd) = self.lender_view(p, o, k);
        let travel = self.voyage(p, o.d);
        let i_ann = cfg.bond_rate + cfg.lender_markup;
        let base = 1.0 + i_ann * t / 365.0;
        let lost = self.p_loss(travel, p, o.d, false);
        let calib = self.lender_calib.get(p).copied().unwrap_or(1.0);
        let (mut owed, mut pd) = (b * base, 0.0);
        let plain = cfg.loan_type == LoanType::Plain;
        for _ in 0..4 {
            let z = (owed / k - 1.0 - mu) / sd;
            pd = min(1.0, calib * 0.5 * (1.0 + erf(z / sqrt(2.0))) + if plain { lost } else { 0.0 });
            let denom = 1.0 - pd * (1.0 - cfg.lender_rr) - if plain { 0.0 } else { lost };
            if pd > cfg.lender_pd_max || denom <= 0.05 {
                return None;
            }
            owed = b * base / denom;
        }
        Some((i_ann, owed / b - base, pd, mu))
    }

    /// `_finance`: borrow or sail on own cash; expected wealth - risk penalty - fear of ruin.
    pub fn finance(&mut self, m: &mut M5, opts: Vec<Opt>) -> Vec<Opt> {
        let cfg = self.cfg.clone();
        let o0 = opts[0];
        let ask = self.best_ask(self.mix(m.loc, o0.g));
        let room = m.capacity / goods5(o0.g).bulk - o0.q;
        if room <= 1.0 || m.cash / ask > o0.q * 1.05 {
            return opts;
        }
        let cash = m.cash;
        let gamma = self.risk(m);
        let p = m.loc;
        let pool = self.pool.get(p).copied().unwrap_or(0.0);
        let (_, lv) = self.ret_of(&o0, cash, p, None, 0.0);
        self.last_voyage = lv;
        let (mu0, sd0, n_rec) = self.own_view(m, lv.0, self.deploy(&o0, cash, p));
        let mut best_u = cash * (1.0 + mu0) - 0.5 * gamma * pow(sd0 * cash, 2.0) / cash;
        let mut best: Option<(f64, Vec<Opt>, (f64, f64, f64))> = None;
        let b_max = min(min(cfg.loan_lev * cash, room * ask), cfg.colleg_max_frac * pool);
        for f in [0.25, 0.5, 0.75, 1.0] {
            let b = pymath::int(b_max * f) as f64;
            if b < 0.05 * cfg.capital {
                continue;
            }
            m.cash = cash + b;
            let o2 = self.options(m, p, None);
            m.cash = cash;
            if o2.is_empty() {
                continue;
            }
            let k = cash + b;
            let (_, lv) = self.ret_of(&o2[0], k, p, None, 0.0);
            self.last_voyage = lv;
            let (frac, t) = lv;
            let (mut mu, sd, _) = self.own_view(m, frac, self.deploy(&o2[0], k, p));
            let Some((i_ann, prem, pd_l, mu_l)) = self.lender_quote(p, &o2[0], k, b, t) else {
                self.rationed += 1;
                continue;
            };
            if m.level >= 1 {
                mu = (1.0 - cfg.lender_signal_w) * mu + cfg.lender_signal_w * mu_l;
            }
            let owed = b * (1.0 + i_ann * t / 365.0 + prem);
            let z = (owed / k - 1.0 - mu) / sd;
            let mut p_ruin = 0.5 * (1.0 + erf(z / sqrt(2.0)));
            if cfg.loan_type == LoanType::Plain {
                let tr = self.voyage(p, o2[0].d);
                p_ruin = min(1.0, p_ruin + self.p_loss(tr, p, o2[0].d, false));
            }
            let u =
                k * (1.0 + mu) - owed - 0.5 * gamma * pow(sd * k, 2.0) / cash - cfg.ruin_weight * gamma * p_ruin * cash;
            if u > best_u {
                best_u = u;
                best = Some((b, o2, (i_ann, prem, pd_l)));
            }
        }
        let amt = best.as_ref().map(|x| x.0).unwrap_or(0.0);
        let choice = if best.is_some() { "debt" } else { "none" };
        self.fin_log.push((self.day, m.level, gamma, n_rec, choice.to_string(), amt / cash));
        if let Some((amt, o2, (i_ann, prem, pd_l))) = best {
            self.pool[p] -= amt;
            m.cash += amt;
            self.ledger.money_source("loan_in", amt);
            m.debt = Some(Debt(amt, p, i_ann, self.day, prem));
            m.debt_pd = Some(pd_l);
            let row = (self.day, o2[0].d, o2[0].g, o2[0].q, m.id);
            match self.lender_book.get_mut(p) {
                Some(b) => b.push(row),
                None => self.lender_book.set(p, vec![row]),
            }
            return o2;
        }
        opts
    }

    /// Loan matures at voyage end. A merchant who cannot pay goes bankrupt (full liability; K-022).
    fn repay(&mut self, m: &mut M5) {
        let Debt(b, port, rate, day0, prem) = m.debt.expect("debt");
        let days = (self.day - day0).max(1);
        let contract = b * (1.0 + rate * days as f64 / 365.0 + prem);
        let mut owed = contract;
        if self.cfg.loan_type == LoanType::Sea && m.debt_lost {
            owed = 0.0;
        }
        let paid = pymath::int(min(m.cash, owed.ceil())) as f64;
        m.cash -= paid;
        self.pool[port] += paid;
        self.ledger.money_sink("loan_out", paid);
        let default = paid < owed - 1.0;
        self.loan_log.push(LoanLog(self.day, port, b, days, paid, contract, m.level, default, m.debt_lost, m.debt_pd));
        m.debt = None;
        m.debt_lost = false;
        if default {
            m.broke = true;
        }
    }

    /// `_settle`: voyage over; diagnostic record, track record, exit decision, loan repayment.
    pub fn settle(&mut self, m: &mut M5) {
        if let Some(Voy(day0, g, q, exp_net, unit_cost, cash0, o, d, lvl)) = m.voy {
            // K-040: per lot with mixed cargo: the lot's cash flow minus its share of ship costs
            let realized = if self.mixed() {
                (m.lot_flow - m.voy_overhead) / max(q, 1e-9)
            } else {
                (m.cash - cash0) / max(q, 1e-9)
            };
            let margin = (realized + m.voy_overhead / max(q, 1e-9)) / max(unit_cost, 1e-9) - 1.0;
            self.voy_log.push(VoyLog(day0, self.day, g, o, d, q, exp_net, unit_cost, realized, lvl, m.loc, margin));
            let roi = margin;
            m.record.push((self.day, roi, unit_cost * q, (realized - unit_cost) * q, (self.day - day0).max(1)));
            let w = self.cfg.rep_window.max(365);
            let day = self.day;
            m.record.retain(|x| day - x.0 <= w);
            m.voy = None;
            if !m.is_player {
                self.exit_decision(m);
            }
        }
        // K-040: the loan is repaid when the ship is empty (voyage end), not while lots remain in the hold
        if m.debt.is_some() && (!self.mixed() || m.hold.is_empty()) {
            self.repay(m);
        }
    }

    /// Monthly: lender learning, route statistics.
    pub fn update_finance(&mut self) {
        let cfg = self.cfg.clone();
        let day = self.day;
        let recent: Vec<LoanLog> = self.loan_log.iter().filter(|x| day - x.0 <= 365).copied().collect();
        let ports = self.port_list.clone();
        for p in ports.iter().map(|&p| Some(p)).chain(std::iter::once(None)) {
            let sub: Vec<&LoanLog> = recent.iter().filter(|x| p.is_none() || Some(x.1) == p).collect();
            if sub.len() >= 5 {
                let v = pymath::sum(sub.iter().map(|x| max(0.0, x.5 - x.4))) / pymath::sum(sub.iter().map(|x| x.2));
                match p {
                    Some(p) => self.loan_el.set(p, v),
                    None => self.loan_el_all = Some(v),
                }
            }
        }
        for &p in &ports {
            let sub: Vec<&LoanLog> = recent.iter().filter(|x| x.1 == p && x.9.is_some()).collect();
            if sub.len() >= 10 {
                let dflt = pymath::sum(sub.iter().map(|x| if x.7 { 1.0 } else { 0.0 }));
                let pds = pymath::sum(sub.iter().map(|x| x.9.unwrap()));
                self.lender_calib.set(p, min(3.0, max(0.5, (dflt + 1.0) / (pds + 1.0))));
            }
            let book: Vec<_> = self
                .lender_book
                .get(p)
                .map(|b| b.iter().filter(|x| x.0 >= day - cfg.load_memory_days).copied().collect())
                .unwrap_or_default();
            self.lender_book.set(p, book);
        }
        let mut stats: IndexMap<(Port, Port, Good), Vec<(f64, i64)>> = IndexMap::new();
        for x in &self.voy_log {
            if day - x.1 <= 365 {
                stats.entry((x.3, x.4, x.2)).or_default().push((x.11, x.1 - x.0));
            }
        }
        self.route_stats.0 = stats
            .into_iter()
            .map(|(k, v)| {
                let rs: Vec<f64> = v.iter().map(|x| x.0).collect();
                let neg: Vec<f64> = rs.iter().map(|&r| if r < 0.0 { 1.0 } else { 0.0 }).collect();
                let ts: Vec<f64> = v.iter().map(|x| x.1 as f64).collect();
                (
                    k,
                    (
                        v.len() as i64,
                        pymath::np_mean(&neg),
                        pymath::np_mean(&rs),
                        pymath::np_median(&ts),
                        pymath::np_std(&rs),
                    ),
                )
            })
            .collect();
    }

    pub fn update_pop_roi(&mut self) {
        let day = self.day;
        let rec: Vec<&VoyLog> = self.voy_log.iter().filter(|x| day - x.1 <= 365).collect();
        if rec.len() >= 10 {
            let roi: Vec<f64> = rec.iter().map(|x| x.11).collect();
            let dur: Vec<f64> = rec.iter().map(|x| (x.1 - x.0) as f64).collect();
            self.pop_roi = Some((pymath::np_median(&roi), pymath::np_std(&roi), pymath::np_median(&dur)));
        }
    }
}
