//! Information: price current, observation, news and rumour spread, arrival, new merchants.

use super::*;
use crate::consts::goods5;
use crate::pymath::{exp, max, min};
use crate::rng::Generator;

fn push_trim(h: &mut Vec<f64>, x: f64, n: usize) {
    h.push(x);
    if h.len() > n {
        h.remove(0);
    }
}

impl Core {
    pub fn best_bid(&self, mi: usize) -> f64 {
        let g = self.market_keys[mi].1;
        if self.cfg.price_discovery && !self.kapan_traded[mi].unwrap_or(true) {
            if let Some(b) = self.kapan_bid[mi] {
                return b;
            }
        }
        self.kapan_price[mi].unwrap_or(goods5(g).reff)
    }

    pub fn best_ask(&self, mi: usize) -> f64 {
        let g = self.market_keys[mi].1;
        self.kapan_price[mi].unwrap_or(goods5(g).reff) * (1.0 + self.cfg.kapan_fee)
    }

    pub fn update_current(&mut self) {
        for mi in 0..self.market_keys.len() {
            let p = self.market_keys[mi].0;
            let b = self.best_bid(mi);
            let day = self.day;
            self.current[p][mi] = (b, day);
            push_trim(&mut self.current_hist[p][mi], b, 40);
        }
    }

    /// I1: merges fresher entries into the port's price current.
    pub fn merge_board(&mut self, p: Port, entries: &[(usize, f64, i64)]) {
        for &(mi, price, day) in entries {
            if day > self.current[p][mi].1 {
                self.current[p][mi] = (price, day);
                push_trim(&mut self.current_hist[p][mi], price, 40);
            }
        }
    }

    /// I1: news between neighbouring ports: send, and process what arrives.
    pub fn couriers(&mut self) {
        let Some(every) = self.cfg.courier_every else { return };
        let day = self.day;
        let mut keep = Vec::new();
        for (d, p, e) in std::mem::take(&mut self.courier_q) {
            if d <= day {
                self.merge_board(p, &e);
            } else {
                keep.push((d, p, e));
            }
        }
        self.courier_q = keep;
        let edges: Vec<(Port, Port, f64)> = crate::map::get().edges.iter().map(|e| (e.0, e.1, e.2)).collect();
        for (a, b, days) in edges {
            for (x, y) in [(a, b), (b, a)] {
                if self.rng.get("courier").random() < 1.0 / every {
                    let e: Vec<(usize, f64, i64)> = self.current[x]
                        .iter()
                        .enumerate()
                        .filter(|t| t.1 .1 > 0)
                        .map(|(mi, &(p, d))| (mi, p, d))
                        .collect();
                    self.courier_q.push((day + pymath::round(days).max(1), y, e));
                }
            }
        }
    }

    pub fn observe(&mut self, m: &mut M5, p: Port) {
        let cfg = &self.cfg;
        if cfg.forward {
            for (mi, _) in self.markets_at(p) {
                let mk = &self.markets[mi];
                if let (Some(hd), Some(hr)) = (mk.harvest_day, mk.harvest_ratio) {
                    m.hnews[mi] = Some((hr, hd));
                }
            }
        }
        if cfg.visibility {
            let since = self.day - cfg.load_memory_days;
            m.seen_buys.retain(|b| b.4 >= since);
            if let Some(pb) = self.port_buys.get(p) {
                for b in pb {
                    if b.0 != m.id && b.4 == self.day - 1 {
                        m.seen_buys.push(*b);
                    }
                }
            }
        }
        if cfg.rival_info {
            let wt = self.waiting_cache[p.idx()];
            for (mi, g) in self.markets_at(p) {
                m.harbor[mi] = Some((wt[g.idx()], self.day));
            }
        }
        let ids: Vec<usize> = self.markets_at(p).map(|x| x.0).collect();
        for mi in ids {
            let b = self.best_bid(mi);
            m.obs[mi] = (b, self.day);
            push_trim(&mut m.hist[mi], b, 40);
        }
    }

    /// `_new_merchant(port, rng)`: `stream` is the stream to draw from ("merchants_entry").
    pub fn new_merchant(&mut self, port: Port, stream: &str) -> M5 {
        self.next_id += 1;
        let cfg = self.cfg.clone();
        let cap = cfg.capital;
        let nm = self.market_keys.len();
        let rng: &mut Generator = self.rng.get(stream);
        let risk_aversion = rng.uniform(0.5, 1.5);
        let mut m = M5 {
            id: self.next_id,
            cash: cap,
            capacity: cfg.capacity,
            is_player: false,
            informed: false,
            state: MState::Buying,
            loc: port,
            dest: None,
            arrive_day: -1,
            good: None,
            qty: 0.0,
            cost_basis: 0.0,
            plan: None,
            wait: 0,
            risk_aversion,
            obs: vec![(0.0, 0); nm],
            hist: vec![Vec::new(); nm],
            heard: IdSet::default(),
            heard_h: IdSet::default(),
            heard_hn: IdSet::default(),
            born_day: self.day,
            start_capital: cap,
            divs: 0.0,
            marks: Vec::new(),
            level: cfg.homog_level,
            imitation: 0.0,
            overconf: 1.0,
            p_hear: cfg.p_hear,
            dara: false,
            known_loads: IdMap::default(),
            w_fund: 0.0,
            hnews: vec![None; nm],
            seen_buys: Vec::new(),
            reservation: 0.0,
            harbor: vec![None; nm],
            home: port,
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
            packet_hnews: vec![None; nm],
            packet_harbor: vec![None; nm],
            carried: IdMap::default(),
            debt_pd: None,
        };
        if cfg.diversity {
            // Camerer, Ho & Chong (2004) Poisson(tau), truncated at 2
            m.level = 2.min(rng.poisson(cfg.ch_tau));
            m.imitation = if cfg.imitation_on { rng.beta(2.0, 5.0) } else { 0.0 };
            m.overconf = exp(rng.normal(-0.2, 0.3));
            let ph = cfg.p_hear * exp(rng.normal(0.0, 0.5));
            m.p_hear = min(max(ph, 0.05), 0.9);
            m.dara = true;
            m.w_fund = if cfg.forward { rng.beta(2.0, 2.0) } else { 0.0 };
        } else if cfg.forward {
            m.w_fund = 0.5;
        }
        // entry_rule "opportunity": knows the port's price current
        for mi in 0..nm {
            m.obs[mi] = self.current[port][mi];
            let h = &self.current_hist[port][mi];
            m.hist[mi] = h[h.len().saturating_sub(20)..].to_vec();
        }
        if cfg.rival_info {
            m.known_loads = self.loads[port].clone();
        }
        m
    }
}

impl World {
    pub(super) fn arrivals(&mut self) {
        let c = &mut self.core;
        for m in self.merchants.iter_mut() {
            if !(m.state == MState::Sailing && m.arrive_day == c.day) {
                continue;
            }
            let dest = m.dest.expect("hedef");
            let Packet(origin, oday, prices) = m.packet.clone().expect("paket");
            for (k, v) in &m.carried {
                c.loads[dest].entry(*k).or_insert(*v);
            }
            if c.cfg.forward {
                c.hnews_board[dest].push((c.news_id, m.packet_hnews.clone()));
            }
            if c.cfg.rival_info {
                c.harbor_news[dest].push((c.news_id, m.packet_harbor.clone()));
            }
            c.news_id += 1;
            c.news[dest].push((c.news_id, origin, oday, prices.clone()));
            m.heard.insert(c.news_id);
            for &(g, price) in &prices {
                let mi = c.mix(origin, g);
                if oday > c.current[dest][mi].1 {
                    c.current[dest][mi] = (price, oday);
                    push_trim(&mut c.current_hist[dest][mi], price, 40);
                }
            }
            if !m.rr.is_empty() {
                let g = c.market_keys.iter().position(|&(p, gg)| p == dest && gg.idx() as f64 == m.rr[3]);
                if let Some(mi) = g {
                    let mut r = std::mem::take(&mut m.rr);
                    r.push(c.best_bid(mi));
                    // K-040: with mixed cargo a ship may arrive somewhere other than its target; log the arrival port
                    r.push(dest.idx() as f64);
                    c.rr_log.push(r);
                }
                m.rr.clear();
            }
            if c.cfg.info_relay {
                let pa = std::mem::take(&mut m.packet_all);
                c.merge_board(dest, &pa);
            }
            m.loc = dest;
            m.wait = 0;
            if c.cfg.port_costs.is_some() {
                // S-028: port call fee (per ship)
                let fee = min(c.call_fee(), max(m.cash, 0.0));
                if fee > 0.0 {
                    m.cash -= fee;
                    if c.mixed() {
                        Core::share_overhead(m, fee);
                    } else {
                        m.cost_basis += if m.qty > 0.0 { fee } else { 0.0 };
                    }
                    c.ledger.money_sink("port_call", fee);
                }
            }
            if c.mixed() {
                // K-040: all lots go to the hold; the one best sold here becomes active
                if m.qty > 0.0 {
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
                if m.hold.is_empty() {
                    m.state = MState::Buying;
                    c.settle(m);
                } else {
                    // the decision comes after the day's observation (sell_plan phase)
                    m.state = MState::Selling;
                }
                continue;
            }
            if c.cfg.handling.is_some() && m.qty > 0.0 {
                // M2.1: unloading; what is unloaded on the first day can be sold
                let b = goods5(m.good.unwrap()).bulk;
                m.unload_left = max(0.0, m.qty * b - c.handle_rate_g(dest, m.good.unwrap()));
                let units = m.qty - m.unload_left / b;
                c.land_goods(m, units);
            } else if m.qty > 0.0 {
                let q = m.qty;
                c.land_goods(m, q);
            }
            m.state = if m.qty > 0.0 { MState::Selling } else { MState::Buying };
            if m.qty <= 0.0 {
                c.settle(m);
            }
        }
    }

    pub(super) fn activate_pending(&mut self) {
        let day = self.core.day;
        for m in self.merchants.iter_mut() {
            if 0 <= m.on_order && m.on_order <= day {
                m.ship = Some(m.on_order);
                m.on_order = -1;
            }
        }
        if self.core.pending.is_empty() {
            return;
        }
        self.core.rng.get("merchants_entry");
        let pending = std::mem::take(&mut self.core.pending);
        let mut keep = Vec::new();
        for x in pending {
            if x.0 > day {
                keep.push(x);
                continue;
            }
            let mut nm = self.core.new_merchant(x.1, "merchants_entry");
            self.diag_born(nm.id, x.1);
            nm.ship = Some(x.3);
            nm.v0 = self.core.value(&nm);
            self.core.prev_val.insert(nm.id, nm.v0);
            let cash = nm.cash;
            self.merchants.push(nm);
            self.core.ledger.money_source("from_investors", cash);
            self.core.entries += 1;
        }
        self.core.pending = keep;
    }

    pub(super) fn hear(&mut self) {
        let c = &mut self.core;
        // --- _hear_loads (rival_info)
        {
            let since = c.day - c.cfg.load_memory_days;
            for i in 0..c.port_list.len() {
                let p = c.port_list[i];
                c.loads[p].retain(|_, v| v.4 >= since);
                let hn = &mut c.harbor_news[p];
                if hn.len() > 50 {
                    hn.drain(..hn.len() - 50);
                }
            }
            let mut r = c.rng.get("load_rumor").clone();
            for m in self.merchants.iter_mut() {
                if m.state == MState::Sailing {
                    continue;
                }
                for (nid, hb) in &c.harbor_news[m.loc] {
                    if m.heard_h.contains(nid) || r.random() >= m.p_hear {
                        continue;
                    }
                    m.heard_h.insert(*nid);
                    for (mi, v) in hb.iter().enumerate() {
                        if let Some((q, day)) = *v {
                            let mine = m.harbor[mi].map(|x| x.1).unwrap_or(-1);
                            if c.market_keys[mi].0 != m.loc && day > mine {
                                m.harbor[mi] = Some((q, day));
                            }
                        }
                    }
                }
            }
            for m in self.merchants.iter_mut() {
                if m.state == MState::Sailing {
                    continue;
                }
                for (k, v) in &c.loads[m.loc] {
                    if !m.known_loads.contains_key(k) && r.random() < m.p_hear {
                        m.known_loads.insert(*k, *v);
                    }
                }
            }
            *c.rng.get("load_rumor") = r;
        }
        if c.cfg.forward {
            for i in 0..c.port_list.len() {
                let p = c.port_list[i];
                let hb = &mut c.hnews_board[p];
                if hb.len() > 50 {
                    hb.drain(..hb.len() - 50);
                }
            }
            let mut r = c.rng.get("hnews_rumor").clone();
            for m in self.merchants.iter_mut() {
                if m.state == MState::Sailing {
                    continue;
                }
                for (nid, hb) in &c.hnews_board[m.loc] {
                    if m.heard_hn.contains(nid) || r.random() >= m.p_hear {
                        continue;
                    }
                    m.heard_hn.insert(*nid);
                    for (mi, v) in hb.iter().enumerate() {
                        if let Some((ratio, day)) = *v {
                            let mine = m.hnews[mi].map(|x| x.1).unwrap_or(-1);
                            if day > mine {
                                m.hnews[mi] = Some((ratio, day));
                            }
                        }
                    }
                }
            }
            *c.rng.get("hnews_rumor") = r;
        }
        if c.cfg.info_relay {
            // I1: the port's price current is public
            for m in self.merchants.iter_mut() {
                if m.state == MState::Sailing {
                    continue;
                }
                let board = &c.current[m.loc];
                for (mi, &(price, day)) in board.iter().enumerate() {
                    if day > m.obs[mi].1 {
                        m.obs[mi] = (price, day);
                        push_trim(&mut m.hist[mi], price, 40);
                    }
                }
            }
        }
        let mut r = c.rng.get("rumor").clone();
        for m in self.merchants.iter_mut() {
            if m.state == MState::Sailing {
                continue;
            }
            for (nid, origin, oday, prices) in &c.news[m.loc] {
                if m.heard.contains(nid) || r.random() >= m.p_hear {
                    continue;
                }
                m.heard.insert(*nid);
                for &(g, price) in prices {
                    let mi = c.mix(*origin, g);
                    if *oday > m.obs[mi].1 {
                        m.obs[mi] = (price, *oday);
                        push_trim(&mut m.hist[mi], price, 40);
                    }
                }
            }
        }
        *c.rng.get("rumor") = r;
        let day = c.day;
        for i in 0..c.port_list.len() {
            let p = c.port_list[i];
            c.news[p].retain(|n| day - n.2 < 90);
        }
    }
}
