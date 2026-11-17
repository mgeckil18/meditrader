//! Counterpart of `D5Config`. Field names are the Python ones (JSON from `dataclasses.asdict(cfg)`).
//!
//! The ported code path is the one the current base setup (`*-B-R1-O3`) runs. Branches that were not ported (`houses`,
//! `network`, `colleganza`, `wholesale=False`, ...) are rejected explicitly by `validate()`: the engine never runs them wrongly.
//! When a branch is ported, its check is removed here and a new enum value is added.

use serde::{Deserialize, Serialize};

use crate::consts::{Good, Port};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum HazardModel {
    Leg,
    Daily,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum HurdleRule {
    Common,
    Lognormal,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PublicTrack {
    Aggregate,
    SurvivorMedian,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum CredRule {
    Buhlmann,
    Fixed,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum LoanType {
    Plain,
    Sea,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ColdTrack {
    Opportunity,
    Neutral,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Config {
    pub seed: u64,
    pub years: i64,
    pub kappa: f64,
    pub yield_sigma: f64,
    pub wages_endogenous: bool,
    pub capacity: f64,
    pub capital: f64,
    pub living_cost: f64,
    pub p_hear: f64,
    pub vol_annual: f64,
    pub revert_days: f64,
    pub hurdle: f64,
    pub free_entry: bool,
    pub exit_prob: f64,
    pub bond_rate: f64,
    pub risk_premium: f64,
    pub max_merchants: i64,
    pub add_bots: bool,
    pub depth_days: f64,
    pub reroute_after: i64,
    pub share_depth: bool,
    pub recapitalize: bool,
    pub wholesale: bool,
    pub kapan_fee: f64,
    pub retail_rule: String,
    pub retail_beta: f64,
    pub retail_inertia_days: f64,
    pub retail_cost_days: f64,
    pub market_elasticity: f64,
    pub markup_min: f64,
    pub markup_max: f64,
    pub retail_entry: bool,
    pub max_shops: usize,
    pub price_discovery: bool,
    pub shop_living_cost: f64,
    pub rival_info: bool,
    pub diversity: bool,
    pub homog_level: i64,
    pub imitation_on: bool,
    pub l0_counts_rivals: bool,
    pub ch_tau: f64,
    pub load_memory_days: i64,
    pub visibility: bool,
    pub forward: bool,
    pub forward_fund: bool,
    pub forward_impact: bool,
    pub sell_decision: bool,
    pub liquidity: bool,
    pub storer_shade: f64,
    pub season_carry: f64,
    pub entry_rule: String,
    pub spinup_years: f64,
    pub pool_mult: f64,
    pub entry_attention: f64,
    pub investor_sigma: f64,
    pub entry_lag_days: [i64; 2],
    pub invest_horizon: f64,
    pub entry_smooth_months: i64,
    pub colleganza: bool,
    pub reputation: String,
    pub rep_window: i64,
    pub debt: bool,
    pub loan_type: LoanType,
    pub loan_lev: f64,
    pub loan_premium: f64,
    pub ruin_weight: f64,
    pub colleg_max_frac: f64,
    pub colleg_min_n: i64,
    pub colleg_max_loss: f64,
    pub record_net_overhead: bool,
    pub loan_pricing: String,
    pub lender_markup: f64,
    pub lender_rr: f64,
    pub lender_pd_max: f64,
    pub lender_signal_w: f64,
    pub rep_k: f64,
    pub entry_ruin: bool,
    pub entry_ruin_weight: f64,
    pub cold_track: ColdTrack,
    pub entry_bonus: bool,
    pub warm_start: bool,
    pub hurdle_rule: HurdleRule,
    pub exit_rule: String,
    pub public_track: PublicTrack,
    pub exit_premium: Option<f64>,
    pub entry_confirm: i64,
    pub entry_confirm_gap: i64,
    pub band_kappa: f64,
    pub shrink_k: f64,
    pub cred_rule: CredRule,
    pub hazard_model: HazardModel,
    pub ship_loss: f64,
    pub ship_market: bool,
    pub ship_price: f64,
    pub ship_life: f64,
    pub ship_scrap: f64,
    pub yard_days: i64,
    pub yard_rate: f64,
    pub foreign_premium: Option<f64>,
    pub layup_cost_day: f64,
    pub layup_max_days: i64,
    pub rebuy_min_cash: f64,
    pub ship_cost_day: f64,
    pub budget_bids: bool,
    pub dust_lot: f64,
    pub network: bool,
    pub houses: bool,
    pub ports: Option<Vec<Port>>,
    pub goods: Option<Vec<Good>>,
    /// M1 (K-036): the option calculation looks at the real supply curve of the departure port (in the current port: rural
    /// supply for `origin_horizon` days, storer stock, pool output, selling merchants; minus local use and other buyers).
    /// In a remote port: no option if the port has no structural supply (rural, pool). Off = identical to Python.
    #[serde(default)]
    pub origin_supply: bool,
    #[serde(default = "five")]
    pub origin_horizon: f64,
    /// Fleet alarm: the run stops if the NPC count exceeds this (no silent capping). None = off.
    #[serde(default)]
    pub fleet_alarm: Option<i64>,
    /// M1.4 (added by Claude): leg hazard depends on duration. Some(r): per-leg values are for an r-day leg,
    /// leg hazard 1-(1-h)^(days/r). None = constant per leg (Python). classic6 mean leg is 60/7 days.
    #[serde(default)]
    pub hazard_days: Option<f64>,
    /// M1.4: an empty (ballast) voyage can also sink / be captured. Off = loaded ships only (Python).
    #[serde(default)]
    pub ballast_risk: bool,
    /// M1.4: probability that a ship captured by corsairs is offered for sale (prize market). 0 = the ship is gone.
    /// The sale price leaves the economy (to the corsairs). Value is a temporary proxy ⚠️.
    #[serde(default)]
    pub prize_share: f64,
    /// M2.1 (added by Claude): loading/unloading rate, volume units/day, [large, medium, small] port. None = instant.
    /// Values are temporary proxies ⚠️ (Gluzman: grain loading at two Cyprus landings took ~20 days).
    #[serde(default)]
    pub handling: Option<[f64; 3]>,
    /// M2.1: "keep filling or depart" decision (marginal value theorem; Charnov 1976). Off = 5-day rule.
    #[serde(default)]
    pub fill_decision: bool,
    /// M2.1: ship loss (loss probability x ship market value) enters option and repositioning values.
    #[serde(default)]
    pub ship_risk: bool,
    /// I1 (user's direction, Claude's design): a ship carries every price it knows (market, price, day); a port's price
    /// current is public and merchants in port read it daily. Off = departure port only (one hop), plus rumours.
    #[serde(default)]
    pub info_relay: bool,
    /// I1: news between neighbouring ports (coastal boat, courier, letter): on each leg, in each direction, on average once
    /// every this many days a port's price current reaches the other side after the leg time. None = off. Temporary proxy ⚠️.
    #[serde(default)]
    pub courier_every: Option<f64>,
    /// S-025 (K-037) interim solution: in the discretionary part of demand (beyond subsistence in LES, beta*s) each class has a
    /// lognormal reservation price distribution. Quantity x S_k(p)/S_k(p_ref), S_k(p) = P(r > p), ln r ~ N(ln(median_k*p_ref), sigma).
    /// None = pure LES (no reservation price).
    #[serde(default)]
    pub wtp: Option<WtpCfg>,
    /// Measurement: monthly kapan price / reference price, all markets.
    #[serde(default)]
    pub px_log: bool,
    /// Cargo spoilage on board (user, 2026-11-12): loss accelerating with time at sea, Weibull: remaining share
    /// exp(-(t/tau)^k), tau per good (`consts::cargo_tau`), k = `cargo_spoil_k`. Small on one voyage, large when cargo is hawked around.
    #[serde(default)]
    pub cargo_spoil: bool,
    #[serde(default = "two")]
    pub cargo_spoil_k: f64,
    /// Reroute threshold: another port must beat the value of staying by this fraction (default 0.05; Python).
    #[serde(default = "rr_margin_default")]
    pub reroute_margin: f64,
    /// Ship cost package (S-028, 2026-11-12): port call fee, handling fee, customs on landing, ship time
    /// cost in decisions. Levels are rough ⚠️ (research/history/ship-operating-costs-16c.md).
    #[serde(default)]
    pub port_costs: Option<PortCosts>,
    /// S-028 double-count test: instead of the cargo-volume freight proxy (0.6 x bulk x days), per-ship sea wear
    /// (repairs): this yearly share of the ship price, per day at sea. Rough ⚠️.
    #[serde(default)]
    pub sea_wear: Option<f64>,
    /// K-040 mixed cargo: a ship carries several lots; per-lot costs.
    #[serde(default)]
    pub mixed: Option<MixedCfg>,
    /// S2 (K-040): weighing/counting rate of valuable goods, units/day at a large port; tier ratio as in `handling`. Rough ⚠️.
    #[serde(default)]
    pub weigh_rate: Option<Vec<(crate::consts::Good, f64)>>,
    /// S1 (K-040): sale agreement with local storers on arrival; paid at agreement, delivered as unloaded.
    #[serde(default)]
    pub sale_contract: bool,
    /// Map (M0): empty or "classic6" = the Python oracle's map; otherwise `core/maps/<name>.json` or a path.
    #[serde(default)]
    pub map: String,
    // --- cold start and snapshot (K-029)
    #[serde(default)]
    pub n_merchants: Option<i64>,
    #[serde(default)]
    pub warm_years: i64,
    #[serde(default)]
    pub warm_min_years: i64,
    #[serde(default = "one")]
    pub warm_n: i64,
    #[serde(default)]
    pub yield_overrides: serde_json::Value,
}

fn five() -> f64 {
    5.0
}

fn one() -> i64 {
    1
}

impl Config {
    /// Reads from JSON; installs the map named in `map` first (ports are resolved by name).
    pub fn from_json(s: &str) -> Result<Config, String> {
        let v: serde_json::Value = serde_json::from_str(s).map_err(|e| format!("cfg: {e}"))?;
        crate::map::install_from_cfg(v.get("map").and_then(|x| x.as_str()).unwrap_or(""))?;
        serde_json::from_value(v).map_err(|e| format!("cfg: {e}"))
    }

    /// Branches that were not ported: explicit error.
    pub fn validate(&self) -> Result<(), String> {
        let mut bad = Vec::new();
        let mut need = |ok: bool, what: &str| {
            if !ok {
                bad.push(what.to_string())
            }
        };
        need(self.wholesale, "wholesale=True");
        need(self.retail_rule == "compete", "retail_rule='compete'");
        need(self.entry_rule == "opportunity", "entry_rule='opportunity'");
        need(self.exit_rule == "voyage", "exit_rule='voyage'");
        need(self.ship_market, "ship_market=True");
        need(self.free_entry, "free_entry=True");
        need(!self.share_depth, "share_depth=False");
        need(!self.recapitalize, "recapitalize=False");
        need(self.rival_info, "rival_info=True");
        need(self.sell_decision, "sell_decision=True");
        need(self.liquidity, "liquidity=True");
        need(self.budget_bids, "budget_bids=True");
        need(self.debt, "debt=True");
        need(self.loan_pricing == "voyage", "loan_pricing='voyage'");
        need(self.record_net_overhead, "record_net_overhead=True");
        need(!self.colleganza, "colleganza=False");
        need(self.reputation == "none", "reputation='none'");
        need(!self.network, "network=False");
        need(!self.houses, "houses=False");
        need(!self.wages_endogenous, "wages_endogenous=False");
        need(
            self.yield_overrides.is_null() || self.yield_overrides.as_object().is_some_and(|o| o.is_empty()),
            "yield_overrides={}",
        );
        if bad.is_empty() {
            Ok(())
        } else {
            Err(format!("the Rust engine has not ported these config branches: {}", bad.join(", ")))
        }
    }
}

/// K-040: mixed cargo and per-lot costs (levels rough ⚠️).
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MixedCfg {
    /// Fixed fee paid when a lot is landed or loaded (customs declaration, weighing, broker).
    pub lot_fee: f64,
    /// Extra handling time per lot (days), on every unloading and loading.
    pub lot_setup_days: f64,
    /// Broken stowage: each extra lot wastes this share of the hold.
    pub stowage_loss: f64,
}

/// S-028: ship cost package.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PortCosts {
    /// Fee per ship on arrival at any port (anchorage, port dues, pilot), money.
    pub call_fee: f64,
    /// Loading and unloading fee per volume unit (porters, lighters), each direction, money.
    pub handling_fee: f64,
    /// Customs is charged when goods are landed (on the unloaded quantity, at the local kapan price), not at sale.
    pub entry_duty: bool,
    /// Daily cost of ship time in decisions (crew + victuals + living + interest on ship capital + wear).
    pub time_cost: bool,
}

/// S-025: reservation price distribution (interim solution; values are temporary proxies ⚠️).
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct WtpCfg {
    /// Categories it applies to (0 grain, 1 oil, 2 wine, 3 coarse cloth, 4 fine cloth, 5 pepper)
    pub cats: Vec<usize>,
    /// Median reservation price per class (rich, middle, poor), as a multiple of the reference price
    pub median: [f64; 3],
    /// Standard deviation of ln r (spread of income and taste)
    pub sigma: f64,
}

fn rr_margin_default() -> f64 {
    0.05
}

fn two() -> f64 {
    2.0
}
