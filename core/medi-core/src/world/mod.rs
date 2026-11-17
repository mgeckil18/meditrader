//! `sim/world5.py::D5World` (the base setup's code path). Split into files in the same order as the Python sections:
//!   info.rs    observation, rumours, arrival, price current
//!   trade.rs   options, expectations, rivals, departure, sell decision
//!   kapan.rs   wholesale market (kapan), competitive retail, urban demand, producer pools
//!   finance.rs debt and lender pricing, voyage settlement
//!   entry.rs   monthly step, public record, entry signal, Bühlmann, exit
//!   ships.rs   Ö3 ship market, R1 risk model
//!
//! For the borrow checker the world is split in two: `Core` (everything except the merchant list) and `World` (merchants +
//! departed + Core). Functions working on one merchant live on `Core` and take `&mut M5`; functions that walk the
//! merchant list live on `World`. If a Python function reads the merchant list, it is on `World` here.

pub mod diag;
mod entry;
mod finance;
mod info;
mod init;
mod kapan;
mod ships;
mod snapshot;
mod trade;
pub mod types;

use indexmap::IndexMap;
use serde::{Deserialize, Serialize};

use crate::config::Config;
use crate::consts::{self, Good, Port, N_GOODS};
use crate::date::Date;
use crate::ledger::Ledger;
use crate::market::Market;
use crate::pymath;
use crate::rng::RngStreams;
pub use types::*;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Core {
    pub cfg: Config,
    pub rng: RngStreams,
    pub ledger: Ledger,
    pub day: i64,
    pub date: Date,
    pub port_list: Vec<Port>,
    pub good_list: Vec<Good>,
    /// market order (keys of Python `self.markets`)
    pub market_keys: Vec<(Port, Good)>,
    pub markets: Vec<Market>,
    pub pools: Vec<((Port, Good), Pool)>,

    // --- fixed calibration
    pub income_ref: PortMap<[f64; 3]>,
    pub local_cons: PortMap<[f64; N_GOODS]>,
    #[serde(rename = "demand_L")]
    pub demand_l: PortMap<[f64; N_GOODS]>,
    pub cls: PortMap<Vec<ClassDemand>>,
    pub normal_wage: PortMap<f64>,
    pub wage_yday: PortMap<f64>,
    pub n_init: i64,

    // --- R1 risk
    #[serde(rename = "_corsair_x")]
    pub corsair_x: Vec<f64>,
    #[serde(rename = "_corsair_z")]
    pub corsair_z: f64,
    pub corsair: Vec<f64>,
    /// (day, from, to, lost, cause, month, loaded, ship age in days (-1 = none), days in port (-1 = unknown), sea days)
    pub dep_log: Vec<(i64, Port, Port, bool, Option<String>, u32, bool, i64, i64, i64)>,

    // --- kapan and retail (in market order)
    pub kapan_price: Vec<Option<f64>>,
    pub kapan_quote: Vec<Option<f64>>,
    pub kapan_bid: Vec<Option<f64>>,
    pub kapan_traded: Vec<Option<bool>>,
    pub kapan_today: Vec<Option<f64>>,
    pub kapan_volume: Vec<Option<f64>>,
    pub shop_exits: i64,
    pub shop_entries: i64,
    pub pool_investments: i64,

    // --- price current and capital pool
    pub current: PortMap<Vec<(f64, i64)>>,
    pub current_hist: PortMap<Vec<Vec<f64>>>,
    pub pool: PortMap<f64>,
    pub pending: Vec<Pending>,

    // --- Ö3 ship market
    pub ship_list: Vec<Listing>,
    pub ship_px: f64,
    pub yard_next: f64,
    pub ship_log: Vec<Vec<f64>>,
    pub ships_lost: i64,
    /// M1.4: ships captured and offered / sold
    #[serde(default)]
    pub prizes: i64,
    #[serde(default)]
    pub prizes_sold: i64,
    #[serde(rename = "_ship_buyers")]
    pub ship_buyers: Vec<Buyer>,
    pub candidates: Vec<(Port, f64, i64, i64)>,

    // --- track record, entry, exit
    #[serde(rename = "_track_known")]
    pub track_known: bool,
    pub trailing_median: f64,
    pub voy_log: Vec<VoyLog>,
    pub pop_roi: Option<(f64, f64, f64)>,
    pub entry_log: Vec<(i64, Port, f64, i64, f64)>,
    #[serde(rename = "_next")]
    pub next_id: i64,
    pub entries: i64,
    pub exits: i64,
    pub bankruptcies: i64,
    pub reroutes: i64,
    /// S1: number of sale agreements made
    #[serde(default)]
    pub contracts: i64,
    /// Measurement: monthly price / reference (`px_log`); not written to the state file (may contain NaN)
    #[serde(skip, default)]
    pub px_log: Vec<Vec<f64>>,
    /// I0: reroute records (details: `trade.rs` sell_plan; the last field is the price found on arrival)
    #[serde(default)]
    pub rr_log: Vec<Vec<f64>>,
    /// I1: news between neighbouring ports (arrival day, port, [(market, price, day)])
    #[serde(default)]
    pub courier_q: Vec<(i64, Port, Vec<(usize, f64, i64)>)>,
    pub debt_bankruptcies: i64,
    pub commissions: f64,
    pub ruin_days: Vec<i64>,
    pub agg_hist: Vec<f64>,
    pub public_agg: Option<f64>,
    #[serde(rename = "_prev_val")]
    pub prev_val: IdMap<f64>,
    #[serde(rename = "_gone_seen")]
    pub gone_seen: usize,
    pub t0_day: i64,
    pub start_date: Date,
    pub pub_log: Vec<(i64, Option<f64>, f64)>,
    #[serde(with = "pyf::opt")]
    pub cred_k: Option<f64>,
    pub cred_log: Vec<CredLog>,
    #[serde(rename = "_public_voy")]
    pub public_voy: f64,
    #[serde(rename = "_public_route")]
    pub public_route: Option<Route>,
    #[serde(rename = "_last_voyage")]
    pub last_voyage: (f64, f64),

    // --- information: news, rumours
    pub news: PortMap<Vec<(i64, Port, i64, Vec<(Good, f64)>)>>,
    pub loads: PortMap<IdMap<Load>>,
    pub harbor_news: PortMap<Vec<(i64, MarketInfo)>>,
    pub hnews_board: PortMap<Vec<(i64, MarketInfo)>>,
    pub port_buys: PortMap<Vec<(Mid, Port, Good, f64, i64)>>,
    #[serde(rename = "_load_id")]
    pub load_id: i64,
    #[serde(rename = "_news_id")]
    pub news_id: i64,
    pub departures: Vec<(i64, Port, Port, Good, f64, i64)>,
    pub flows: PairList<(i64, Port, Port, Good), f64>,

    // --- finance
    pub loan_log: Vec<LoanLog>,
    pub fin_log: Vec<(i64, i64, f64, i64, String, f64)>,
    pub loan_el: PortMap<f64>,
    pub loan_el_all: Option<f64>,
    pub route_stats: PairList<(Port, Port, Good), (i64, f64, f64, f64, f64)>,
    pub lender_book: PortMap<Vec<(i64, Port, Good, f64, Mid)>>,
    pub lender_calib: PortMap<f64>,
    pub rationed: i64,

    /// `log["n_npc"]` (the ship market's shipyard looks at the fleet of the last 5 years)
    pub n_npc: Vec<i64>,

    // --- derived (not in the dump)
    #[serde(skip)]
    pub mkt: Vec<[Option<usize>; N_GOODS]>,
    #[serde(skip)]
    pub days: Vec<Vec<f64>>,
    #[serde(skip)]
    pub legs: Vec<Vec<Vec<(Port, Port)>>>,
    #[serde(skip)]
    pub waiting_cache: Vec<[f64; N_GOODS]>,
    /// `origin_supply`: remaining quantity of merchants with a buy plan in port (start of day)
    #[serde(skip)]
    pub buying_cache: Vec<[f64; N_GOODS]>,
    /// Expected loss probability (`p_loss(_, a, b, actual=False)`), [winter][a][b]: fixed, independent of corsair pressure.
    #[serde(skip)]
    pub ploss0: [Vec<Vec<f64>>; 2],
    /// `expect` constants: `0.03 ** 2` and `vol_annual ** 2` (same glibc call, once).
    /// D5b3f diagnostic records (if enabled)
    #[serde(skip)]
    pub diag: Option<Box<diag::Diag>>,
    #[serde(skip)]
    pub sig0: f64,
    #[serde(skip)]
    pub sig1: f64,
}

/// On disk a flat object: Core fields + merchants + gone. (Merged by hand because `serde(flatten)` cannot read
/// integer-keyed maps.)
#[derive(Clone, Debug)]
pub struct World {
    pub core: Core,
    pub merchants: Vec<M5>,
    pub gone: Vec<Gone>,
}

impl Core {
    /// Derived tables after the state is loaded.
    pub fn rebuild(&mut self) {
        let np = consts::n_ports();
        self.mkt = vec![[None; N_GOODS]; np];
        for (i, &(p, g)) in self.market_keys.iter().enumerate() {
            self.mkt[p.idx()][g.idx()] = Some(i);
        }
        self.days = consts::shortest_days();
        self.legs = consts::route_legs(&self.days);
        self.waiting_cache = vec![[0.0; N_GOODS]; np];
        self.buying_cache = vec![[0.0; N_GOODS]; np];
        self.ploss0 = [vec![vec![0.0; np]; np], vec![vec![0.0; np]; np]];
        self.sig0 = pymath::pow(0.03, 2.0);
        self.sig1 = pymath::pow(self.cfg.vol_annual, 2.0);
        for w in 0..2 {
            for a in Port::all() {
                for b in Port::all() {
                    let h = self.leg_hazards_w(*a, *b, false, w == 1).0;
                    self.ploss0[w][a.idx()][b.idx()] = 1.0 - pymath::prod(h.into_iter().map(|h| 1.0 - h));
                }
            }
        }
    }

    #[inline]
    pub fn mi(&self, p: Port, g: Good) -> Option<usize> {
        self.mkt[p.idx()][g.idx()]
    }
    #[inline]
    pub fn mix(&self, p: Port, g: Good) -> usize {
        self.mkt[p.idx()][g.idx()].unwrap_or_else(|| panic!("pazar yok: {p:?} {g:?}"))
    }
    #[inline]
    pub fn has_market(&self, p: Port, g: Good) -> bool {
        self.mkt[p.idx()][g.idx()].is_some()
    }
    /// Markets in port p (in market order): (index, good).
    pub fn markets_at(&self, p: Port) -> impl Iterator<Item = (usize, Good)> + '_ {
        self.market_keys.iter().enumerate().filter(move |(_, k)| k.0 == p).map(|(i, k)| (i, k.1))
    }
    #[inline]
    pub fn demand(&self, p: Port, g: Good) -> f64 {
        self.demand_l[p][g.idx()]
    }
    pub fn pool_idx(&self, p: Port, g: Good) -> Option<usize> {
        self.pools.iter().position(|(k, _)| *k == (p, g))
    }
}

impl World {
    pub fn from_json(s: &str) -> Result<World, String> {
        let mut v: serde_json::Value = serde_json::from_str(s).map_err(|e| format!("durum: {e}"))?;
        let o = v.as_object_mut().ok_or("state: not an object")?;
        crate::map::install_from_cfg(o.get("cfg").and_then(|c| c.get("map")).and_then(|x| x.as_str()).unwrap_or(""))?;
        let merchants = serde_json::from_value(o.remove("merchants").ok_or("merchants yok")?)
            .map_err(|e| format!("merchants: {e}"))?;
        let gone = serde_json::from_value(o.remove("gone").ok_or("gone yok")?).map_err(|e| format!("gone: {e}"))?;
        let core: Core = serde_json::from_value(v).map_err(|e| format!("core: {e}"))?;
        let mut w = World { core, merchants, gone };
        w.core.cfg.validate()?;
        w.core.rebuild();
        Ok(w)
    }

    pub fn to_value(&self) -> serde_json::Value {
        let mut v = serde_json::to_value(&self.core).expect("serialize");
        let o = v.as_object_mut().unwrap();
        o.insert("merchants".into(), serde_json::to_value(&self.merchants).unwrap());
        o.insert("gone".into(), serde_json::to_value(&self.gone).unwrap());
        v
    }

    // --- accounting -----------------------------------------------------------
    fn money_total(&self) -> f64 {
        let c = &self.core;
        pymath::sum(c.markets.iter().map(|m| m.money_total()))
            + pymath::sum(c.pools.iter().map(|(_, p)| p.cash))
            + pymath::sum(self.merchants.iter().map(|m| m.cash))
    }

    fn goods_totals(&self) -> Vec<(Good, f64)> {
        let c = &self.core;
        let mut out: Vec<(Good, f64)> = c.good_list.iter().map(|&g| (g, 0.0)).collect();
        let add = |out: &mut Vec<(Good, f64)>, g: Good, v: f64| {
            out.iter_mut().find(|x| x.0 == g).expect("mal").1 += v;
        };
        for m in &c.markets {
            add(&mut out, m.good(), m.goods_total());
        }
        for ((_, g), pl) in &c.pools {
            add(&mut out, *g, pl.output);
            for &(i, q) in &pl.inputs {
                add(&mut out, i, q);
            }
        }
        for m in &self.merchants {
            if m.qty > 0.0 {
                add(&mut out, m.good.expect("cargo good"), m.qty);
            }
            for l in &m.hold {
                add(&mut out, l.g, l.qty);
            }
        }
        out
    }

    // --- main loop (`_step_wholesale`) -----------------------------------------
    pub fn step(&mut self) {
        let mut lap = crate::prof::Lap::start();
        let cfg_vis = self.core.cfg.visibility;
        if cfg_vis {
            let d = self.core.day;
            for i in 0..self.core.port_list.len() {
                let p = self.core.port_list[i];
                self.core.port_buys[p].retain(|b| b.4 >= d - 1);
            }
        }
        self.arrivals();
        lap.mark("arrivals");
        self.activate_pending();
        self.core.update_current();
        self.core.couriers();
        self.compute_waiting();
        lap.mark("activate+current+waiting");
        for m in self.merchants.iter_mut() {
            if m.state != MState::Sailing {
                let p = m.loc;
                self.core.observe(m, p);
            }
        }
        lap.mark("observe");
        self.hear();
        lap.mark("hear");
        for i in 0..self.merchants.len() {
            let m = &mut self.merchants[i];
            if m.state == MState::Selling && m.qty <= 0.0 && !m.hold.is_empty() {
                // K-040: arrival day: value of freed space and the first lot's decision
                self.core.set_fill_val(m);
                self.core.activate_next(m);
            } else if m.state == MState::Selling && m.qty > 0.0 {
                self.core.sell_plan(m);
            }
        }
        lap.mark("sell_plan");
        self.retire_flagged();
        lap.mark("retire");
        for m in self.merchants.iter_mut() {
            if m.state == MState::Buying {
                self.core.plan_merchant(m);
            }
        }
        lap.mark("plan_merchant");
        for i in 0..self.core.markets.len() {
            let c = &mut self.core;
            c.markets[i].step_pre(&mut c.ledger);
        }
        lap.mark("step_pre");
        self.core.pools_step();
        lap.mark("pools");
        for i in 0..self.core.markets.len() {
            self.kapan(i);
            self.core.retail_prices(i);
        }
        lap.mark("kapan+retail");
        for m in self.merchants.iter_mut() {
            self.core.after_kapan(m);
        }
        lap.mark("after_kapan");
        for pi in 0..self.core.port_list.len() {
            let port = self.core.port_list[pi];
            let asks: Vec<(Good, f64)> = self
                .core
                .markets_at(port)
                .map(|(i, g)| (g, pymath::sum(self.core.markets[i].shops.iter().map(|s| s.share * s.ask()))))
                .collect();
            self.core.urban(port, &asks);
        }
        for i in 0..self.core.markets.len() {
            self.core.update_shares(i);
            let c = &mut self.core;
            let slc = c.cfg.shop_living_cost;
            for s in c.markets[i].shops.iter_mut() {
                let x = pymath::min(slc, s.cash);
                s.op_profit -= slc + s.rent;
                s.cash -= x;
                c.ledger.money_sink("shop_living", x);
            }
        }
        for i in 0..self.core.markets.len() {
            let c = &mut self.core;
            c.markets[i].step_post(&mut c.ledger);
        }
        lap.mark("urban+shares+post");
        self.upkeep();
        lap.mark("upkeep");
        if self.core.date.day() == 1 {
            if self.core.cfg.px_log {
                let c = &mut self.core;
                let row: Vec<f64> = (0..c.market_keys.len())
                    .map(|mi| c.kapan_price[mi].unwrap_or(f64::NAN) / crate::consts::goods5(c.market_keys[mi].1).reff)
                    .collect();
                c.px_log.push(row);
            }
            self.monthly();
            if self.core.cfg.retail_entry {
                self.core.retail_entry_exit();
            }
        }
        lap.mark("monthly");
        self.log_common();
    }

    fn log_common(&mut self) {
        let n = self.merchants.iter().filter(|m| !m.is_player).count() as i64;
        if let Some(a) = self.core.cfg.fleet_alarm {
            if n > a {
                panic!("fleet alarm: day {}, {} NPC merchants > {} (fleet_alarm)", self.core.day, n, a);
            }
        }
        self.core.n_npc.push(n);
        self.core.ledger.check(self.money_total(), &self.goods_totals());
        self.core.day += 1;
        self.core.date = self.core.date.add_days(1);
    }

    /// `_waiting(p)` for each port (once at the start of the day; `_waiting_cache`).
    fn compute_waiting(&mut self) {
        let mut wc = vec![[0.0; N_GOODS]; consts::n_ports()];
        for &p in &self.core.port_list {
            for x in &self.merchants {
                if x.state == MState::Selling && x.loc == p && x.qty > 0.0 {
                    wc[p.idx()][x.good.unwrap().idx()] += x.qty;
                }
            }
        }
        self.core.waiting_cache = wc;
        if self.core.cfg.origin_supply {
            let mut bc = vec![[0.0; N_GOODS]; consts::n_ports()];
            for x in &self.merchants {
                if x.state == MState::Buying {
                    if let Some(Plan(g, _, _, q)) = x.plan {
                        bc[x.loc.idx()][g.idx()] += (q - x.qty).max(0.0);
                    }
                }
            }
            self.core.buying_cache = bc;
        }
    }
}
