//! K-029 snapshot: building (`build_snapshot`), warm start (`_load_warm` + `_rebase`).
//! The snapshot format is the full state dump (`to_value`), replacing Python's pickle.

use serde_json::{json, Value};

use super::*;
use crate::date::START_DATE;

impl World {
    /// `_snapshot_bytes`: state with logs emptied.
    pub fn snapshot_value(&self) -> Value {
        let mut w = self.clone();
        w.clear_logs();
        w.core.gone_seen = 0;
        w.to_value()
    }

    fn clear_logs(&mut self) {
        let c = &mut self.core;
        c.n_npc.clear();
        c.voy_log.clear();
        c.departures.clear();
        c.loan_log.clear();
        c.fin_log.clear();
        self.gone.clear();
        c.dep_log.clear();
        c.ship_log.clear();
        c.flows = Default::default();
    }

    /// `_rebase`: measurement starts now; logs and counters are reset, the world state stays.
    pub fn rebase(&mut self) {
        let c = &mut self.core;
        c.t0_day = c.day;
        c.start_date = c.date;
        self.clear_logs();
        let c = &mut self.core;
        c.gone_seen = 0;
        c.kapan_volume = vec![None; c.markets.len()];
        c.entries = 0;
        c.exits = 0;
        c.bankruptcies = 0;
        c.reroutes = 0;
        c.rr_log.clear();
        c.px_log.clear();
        c.debt_bankruptcies = 0;
        c.shop_entries = 0;
        c.pool_investments = 0;
        c.shop_exits = 0;
        c.rationed = 0;
        c.commissions = 0.0;
        c.ships_lost = 0;
        c.prizes = 0;
        c.prizes_sold = 0;
        c.n_init = self.merchants.iter().filter(|m| !m.is_player).count() as i64;
        let day = c.day;
        for i in 0..self.merchants.len() {
            let v = self.core.value(&self.merchants[i]);
            let m = &mut self.merchants[i];
            m.v0 = v;
            m.t0 = day;
        }
    }

    /// `_load_warm`: snapshot state + the run's config; the world RNG restarts with the run's seed
    /// (markets keep their own streams from the snapshot, as in Python).
    pub fn warm(cfg: Config, snapshot: &str) -> Result<World, String> {
        cfg.validate()?;
        let mut w = World::from_json(snapshot)?;
        w.core.rng = RngStreams::new(cfg.seed);
        w.core.cfg = cfg;
        w.core.rebuild();
        if w.core.cfg.ship_market && w.merchants.iter().filter(|m| !m.is_player).all(|m| m.ship.is_none()) {
            w.init_ships();
        }
        w.rebase();
        Ok(w)
    }

    /// `build_snapshot(cfg, k)`: pre-run (seed 1000 + k, `warm_years` years, cold start). After `warm_min_years`,
    /// at the start of each month: a candidate if the fleet is within ±5% of its 5-year mean and ships being fitted out are ≤ 2%
    /// of the fleet; the last candidate wins. Without candidates, the moment of smallest deviation. Returns: (state, meta).
    pub fn build_snapshot(cfg: &Config, k: i64) -> Result<(Value, Value), String> {
        let mut c = cfg.clone();
        c.warm_start = false;
        c.seed = 1000 + k as u64;
        c.years = cfg.warm_years;
        c.spinup_years = 0.0;
        let mut w = World::new(c)?;
        let t_min = Date::new(START_DATE.0 + cfg.warm_min_years, START_DATE.1, START_DATE.2);
        let end = Date::new(START_DATE.0 + cfg.warm_years, START_DATE.1, START_DATE.2);
        let (mut best, mut best_dev, mut best_ok, mut meta) = (None, f64::INFINITY, false, Value::Null);
        while w.core.date < end {
            w.step();
            if w.core.date.day() != 1 || w.core.date < t_min {
                continue;
            }
            let n = &w.core.n_npc;
            let last = &n[n.len().saturating_sub(1825)..];
            let mean5 = last.iter().sum::<i64>() as f64 / last.len() as f64;
            let n1 = *n.last().unwrap();
            let dev = (n1 as f64 - mean5).abs() / max(mean5, 1.0);
            let pend = w.core.pending.len() as f64 / n1.max(1) as f64;
            let ok = dev <= 0.05 && pend <= 0.02;
            if ok || (!best_ok && dev < best_dev) {
                best = Some(w.snapshot_value());
                best_dev = dev;
                best_ok = ok;
                meta = json!({"date": w.core.date, "fleet": n1, "mean5": mean5, "dev": dev,
                              "pending": w.core.pending.len(), "ok": ok,
                              "public_agg": w.core.public_agg, "seed": 1000 + k});
            }
        }
        best.map(|b| (b, meta)).ok_or_else(|| "no snapshot candidate (warm_years <= warm_min_years?)".into())
    }
}

use crate::pymath::max;
