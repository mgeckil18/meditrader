//! D5b3f diagnostic records (`experiments/d5b3f_entry_diag.py::DiagWorld`) and experiment output (`run()`).
//! Does not change behaviour: read-only (same principle as Python's `check`). When enabled, `Core::diag` is set.

use serde_json::{json, Value};

use crate::pymath::max;

use super::*;

/// Per-port signal in one entry round (`DiagWorld._entry_signal`).
#[derive(Clone, Debug)]
pub struct Sig {
    pub track: Option<f64>,
    pub voy: f64,
    pub belief: f64,
    pub alt: f64,
    pub conv: f64,
    pub ruin: f64,
    pub pool_units: f64,
    pub route: Option<Route>,
    pub n_here: i64,
}

#[derive(Clone, Debug, Default)]
pub struct Diag {
    /// signals of this round (port -> latest signal)
    pub sig: PortMap<Sig>,
    pub elog: Vec<Value>,
    /// (day, own expectation, public record, exiting?, voyages in the last year)
    pub xlog: Vec<(i64, f64, Option<f64>, bool, i64)>,
    /// merchant -> (entry day, belief seen at entry); insertion order kept
    pub born: IndexMap<Mid, (i64, Option<f64>)>,
}

/// A number in JSON: if not finite, the string "inf"/"nan" rather than what Python's `json.dump` writes (the comparison
/// tools read both).
pub fn jf(x: f64) -> Value {
    if x.is_finite() {
        json!(x)
    } else if x.is_nan() {
        json!("nan")
    } else if x > 0.0 {
        json!("inf")
    } else {
        json!("-inf")
    }
}

fn jo(x: Option<f64>) -> Value {
    x.map(jf).unwrap_or(Value::Null)
}

impl World {
    /// Turns diagnostic records on (after a cold or warm start, before the first step).
    pub fn enable_diag(&mut self) {
        self.core.diag = Some(Box::default());
    }

    /// `DiagWorld._entry_signal` record.
    pub(super) fn diag_signal(&mut self, p: Port, belief: f64, alt: f64, conv: f64, ruin: f64) {
        if self.core.diag.is_none() {
            return;
        }
        let n_here =
            self.merchants.iter().filter(|m| !m.is_player && m.loc == p && m.state == MState::Buying).count() as i64;
        let c = &self.core;
        let sig = Sig {
            track: c.public_track(),
            voy: c.public_voy,
            belief,
            alt,
            conv,
            ruin,
            pool_units: c.pool[p] / c.cfg.capital,
            route: c.public_route,
            n_here,
        };
        self.core.diag.as_mut().unwrap().sig.set(p, sig);
    }

    /// End of `DiagWorld._entry_opportunity`: entry records of this round.
    pub(super) fn diag_entries(&mut self, n0: usize) {
        let c = &mut self.core;
        let Some(d) = c.diag.as_mut() else { return };
        for &(day, p, r_exp, k, _belief) in &c.entry_log[n0..] {
            let sg = d.sig.get(p).expect("sinyal");
            d.elog.push(json!({
                "day": day, "p": p, "r_exp": jf(r_exp), "k": k,
                "lam": jf(c.cfg.entry_attention * sg.pool_units * sg.conv),
                "track": jo(sg.track), "voy": jf(sg.voy), "belief": jf(sg.belief), "alt": jf(sg.alt),
                "conv": jf(sg.conv), "ruin": jf(sg.ruin), "pool_units": jf(sg.pool_units), "route": sg.route,
                "n_here": sg.n_here,
            }));
        }
    }

    /// `DiagWorld._new_merchant` (day > 0): belief seen at entry = the latest entry record of that port.
    pub(super) fn diag_born(&mut self, id: Mid, port: Port) {
        let c = &mut self.core;
        if c.day <= 0 {
            return;
        }
        let Some(d) = c.diag.as_mut() else { return };
        let pn = serde_json::to_value(port).unwrap();
        let last = d.elog.iter().rev().find(|x| x["p"] == pn).and_then(|x| x["belief"].as_f64());
        d.born.insert(id, (c.day, last));
    }

    /// Run (`D5World.run`): `years` years from `start_date`.
    pub fn run(&mut self) {
        let sd = self.core.start_date;
        let (y, mo, dd) = sd.ymd();
        let end = Date::new(y + self.core.cfg.years, mo, dd);
        while self.core.date < end {
            self.step();
        }
    }

    /// Output of `d5b3f_entry_diag.run()` (same fields, same order).
    pub fn diag_output(&self, name: &str) -> Value {
        let c = &self.core;
        let d = c.diag.as_ref().expect("diagnostics off");
        let end = c.day;
        let cap = c.cfg.capital;
        let v0_of = |m: &M5| if m.v0 != 0.0 { m.v0 } else { m.start_capital };

        // _agg
        let mut ppl: Vec<(&M5, i64, f64)> =
            self.merchants.iter().filter(|m| !m.is_player).map(|m| (m, end, m.net_worth())).collect();
        ppl.extend(self.gone.iter().filter(|g| !g.0.is_player).map(|g| (&g.0, g.1, g.2)));
        let pnl = pymath::sum(ppl.iter().map(|&(m, _, v)| v + m.divs - v0_of(m)));
        let capy = pymath::sum(
            ppl.iter().map(|&(m, d_, _)| v0_of(m) * max(((d_ - m.born_day.max(m.t0)) as f64) / 365.0, 1.0 / 365.0)),
        );
        let agg = pnl / capy;

        // _returns
        let mut ppl2: Vec<(&M5, i64, f64)> =
            self.merchants.iter().filter(|m| !m.is_player).map(|m| (m, end, m.equity() + c.ship_r(m))).collect();
        ppl2.extend(self.gone.iter().filter(|g| !g.0.is_player).map(|g| (&g.0, g.1, g.2 + g.0.exit_ship)));
        let rets: Vec<Value> = ppl2
            .iter()
            .map(|&(m, d_, v)| {
                let v0 = v0_of(m);
                let yrs = max(((d_ - m.born_day.max(m.t0)) as f64) / 365.0, 1.0 / 365.0);
                json!([jf((v + m.divs - v0) / (v0 * yrs)), jf(v0 * yrs), m.born_day <= c.t0_day, jf(yrs)])
            })
            .collect();

        // entry cohort
        let mut gone_day: IndexMap<Mid, i64> = IndexMap::new();
        for g in &self.gone {
            gone_day.insert(g.0.id, g.1);
        }
        let find = |id: Mid| -> &M5 {
            self.merchants
                .iter()
                .find(|m| m.id == id)
                .or_else(|| self.gone.iter().rev().find(|g| g.0.id == id).map(|g| &g.0))
                .expect("entered merchant not found")
        };
        let cohort: Vec<Value> = d
            .born
            .iter()
            .map(|(&id, &(d0, bel))| {
                let m = find(id);
                let gone = gone_day.contains_key(&id);
                let d1 = gone_day.get(&id).copied().unwrap_or(end);
                let life = (d1 - d0).max(1);
                let mut val = match m.marks.last() {
                    Some(&x) => x,
                    None => m.net_worth() + m.divs,
                };
                if gone && m.broke {
                    val = 0.1 * m.start_capital;
                }
                let ret = pymath::pow(val / m.start_capital, 365.0 / life.max(180) as f64) - 1.0;
                json!({"d0": d0, "life": life, "belief": jo(bel), "ret": jf(ret), "gone": gone, "broke": m.broke})
            })
            .collect();

        // voyage bias
        let vl: Vec<&VoyLog> = c.voy_log.iter().filter(|x| x.0 > 365 + c.t0_day).collect();
        let bias: Vec<(f64, f64)> = vl.iter().filter(|x| x.7 > 0.0).map(|x| ((x.6 - x.8) * x.5, x.7 * x.5)).collect();
        let voy_bias = pymath::sum(bias.iter().map(|x| x.0)) / max(pymath::sum(bias.iter().map(|x| x.1)), 1.0);

        let fleet: Vec<f64> = c.n_npc.iter().step_by(30).map(|&x| x as f64).collect();
        let xlog: Vec<Value> = d
            .xlog
            .iter()
            .map(
                |&(day, e, pubt, retire, n)| json!({"day": day, "e": jf(e), "pub": jo(pubt), "retire": retire, "n": n}),
            )
            .collect();
        let pub_log: Vec<Value> = c.pub_log.iter().map(|x| json!([x.0, jo(x.1), jf(x.2)])).collect();
        let cred_log: Vec<Value> = c
            .cred_log
            .iter()
            .filter(|x| x.0 >= c.t0_day)
            .map(|x| json!([x.0, jf(x.1), jf(x.2), jf(x.3), x.4, jo(x.5)]))
            .collect();
        let ship_log: Vec<Value> = c
            .ship_log
            .iter()
            .filter(|x| x[0] >= c.t0_day as f64)
            .map(|x| Value::Array(x.iter().map(|&v| jf(v)).collect()))
            .collect();
        let ship_ages: Vec<Value> = self
            .merchants
            .iter()
            .filter(|m| !m.is_player && m.ship.is_some())
            .map(|m| jf((c.day - m.ship.unwrap()) as f64 / 365.0))
            .collect();
        json!({
            "name": name, "fleet": fleet, "n_init": c.n_init, "agg": jf(agg), "seed": c.cfg.seed,
            "entries": c.entries, "exits": c.exits, "bankruptcies": c.bankruptcies,
            "elog": d.elog, "slog": [], "xlog": xlog, "cohort": cohort, "t0": c.t0_day,
            "pub_log": pub_log, "voy_bias": jf(voy_bias), "n_markets": c.markets.len(),
            "trailing_end": jf(c.trailing_median), "cap": jf(cap), "rets": rets, "cred_log": cred_log,
            "dep_log": c.dep_log, "ship_log": ship_log, "ships_lost": c.ships_lost, "ship_ages": ship_ages,
            "prizes": c.prizes, "prizes_sold": c.prizes_sold,
            "reroutes": c.reroutes, "rr_log": c.rr_log, "contracts": c.contracts,
            "ledger": &c.ledger, "flows": c.flows.0.iter().map(|(k, v)| json!([k.0, k.1, k.2, k.3, jf(*v)])).collect::<Vec<_>>(),
            "px_log": c.px_log.iter().map(|r| r.iter().map(|&x| jf(x)).collect::<Vec<_>>()).collect::<Vec<_>>(),
            "market_keys": c.market_keys.iter().map(|k| (k.0, k.1)).collect::<Vec<_>>(),
        })
    }
}
