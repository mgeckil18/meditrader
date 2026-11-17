//! Money and goods accounting (`sim/ledger.py`). Money is integer-valued f64 (soldi). Checked every day.

use indexmap::IndexMap;
use serde::{Deserialize, Serialize};

use crate::consts::Good;
use crate::pymath;

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Ledger {
    pub money_in: IndexMap<String, f64>,
    pub money_out: IndexMap<String, f64>,
    /// key "GOOD|source"
    pub goods_in: IndexMap<String, f64>,
    pub goods_out: IndexMap<String, f64>,
    pub money_start: f64,
    pub goods_start: IndexMap<String, f64>,
}

fn bump(map: &mut IndexMap<String, f64>, k: &str, v: f64) {
    if let Some(x) = map.get_mut(k) {
        *x += v;
    } else {
        map.insert(k.to_string(), 0.0 + v);
    }
}

impl Ledger {
    pub fn money_source(&mut self, name: &str, amount: f64) {
        bump(&mut self.money_in, name, amount);
    }
    pub fn money_sink(&mut self, name: &str, amount: f64) {
        bump(&mut self.money_out, name, amount);
    }
    pub fn goods_source(&mut self, g: Good, name: &str, q: f64) {
        bump(&mut self.goods_in, &format!("{}|{}", g.name(), name), q);
    }
    pub fn goods_sink(&mut self, g: Good, name: &str, q: f64) {
        bump(&mut self.goods_out, &format!("{}|{}", g.name(), name), q);
    }

    pub fn check(&self, money_total: f64, goods: &[(Good, f64)]) {
        let expected = self.money_start + pymath::sum(self.money_in.values().copied())
            - pymath::sum(self.money_out.values().copied());
        assert!(money_total == expected, "money inconsistent: {money_total} != {expected}");
        for &(g, total) in goods {
            let pre = format!("{}|", g.name());
            let sel =
                |m: &IndexMap<String, f64>| pymath::sum(m.iter().filter(|(k, _)| k.starts_with(&pre)).map(|(_, v)| *v));
            let exp =
                self.goods_start.get(g.name()).copied().unwrap_or(0.0) + sel(&self.goods_in) - sel(&self.goods_out);
            assert!((total - exp).abs() <= 1e-6 * exp.abs().max(1.0), "{} inconsistent: {total} != {exp}", g.name());
        }
    }
}
