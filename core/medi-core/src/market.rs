//! Single (port, good) market engine: `sim/engine.py::D1Sim` (`external_wholesale` mode) and the `sim/model.py` agents.
//! Wholesale trades happen in the world's kapan; here: harvest, trades between shops, price updates and costs.

use serde::{Deserialize, Serialize};

use crate::consts::Good;
use crate::date::{Date, START_DATE};
use crate::ledger::Ledger;
use crate::pymath::{self, exp, log, max, min, pow};
use crate::rng::RngStreams;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MarketCfg {
    pub good: Good,
    pub harvest_month: u32,
    pub continuous_supply: bool,
    pub yield_sigma: f64,
    pub elasticity: f64,
    pub spoilage_per_day: f64,
    pub farm_spoilage_per_day: f64,
    pub interdealer: bool,
    pub harvest_news_weight: f64,
    pub external_wholesale: bool,
    #[serde(default)]
    pub yield_overrides: serde_json::Map<String, serde_json::Value>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Rural {
    pub annual_capacity: f64,
    pub harvest_month: u32,
    pub ref_price: f64,
    pub floor_price: f64,
    pub supply_elasticity: f64,
    pub stock: f64,
    pub adaptive_ref: bool,
    pub ref_memory_days: f64,
    pub expected_price: f64,
    pub self_share: f64,
    pub self_compress_min: f64,
    pub own_daily: f64,
    pub front_load: f64,
    pub continuous_horizon: f64,
}

impl Rural {
    pub fn set_own_consumption(&mut self, shock: f64) {
        let own_year = self.annual_capacity * self.self_share * min(1.0, max(self.self_compress_min, shock));
        self.own_daily = own_year / 365.0;
    }
    pub fn sellable(&self, dth: i64) -> f64 {
        max(0.0, self.stock - self.own_daily * dth as f64)
    }
    fn pace(&self, avail: f64, dth: i64) -> f64 {
        if self.continuous_horizon > 0.0 {
            return avail / self.continuous_horizon;
        }
        let season_pos = 1.0 - dth as f64 / 365.0;
        avail / (dth.max(1) as f64) * (1.0 + self.front_load * (1.0 - 2.0 * season_pos))
    }
    pub fn offered_at(&self, price: f64, dth: i64) -> f64 {
        let avail = self.sellable(dth);
        if price < self.floor_price || avail <= 0.0 {
            return 0.0;
        }
        let pace = self.pace(avail, dth);
        let rf = if self.adaptive_ref { self.expected_price } else { self.ref_price };
        let factor = pow(price / rf, self.supply_elasticity);
        min(avail, pace * min(3.0, max(0.2, factor)))
    }
    pub fn observe(&mut self, price: f64) {
        if self.adaptive_ref {
            self.expected_price += (price - self.expected_price) / self.ref_memory_days;
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum PriceRule {
    Linear,
    Log,
    Cover,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Pricing {
    Mid,
    Lerner,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Shop {
    pub id: String,
    pub cash: f64,
    pub stock: f64,
    pub target: f64,
    pub capacity: f64,
    pub margin: f64,
    pub mid: f64,
    pub avg_cost: f64,
    pub kappa: f64,
    pub max_daily_move: f64,
    pub min_markup: f64,
    pub rent: f64,
    pub price_rule: PriceRule,
    pub room_mult: f64,
    pub anchor: f64,
    pub memory_days: f64,
    pub memory_price: f64,
    pub withdraw_rate: f64,
    pub working_capital_mult: f64,
    pub target_cover_days: f64,
    pub request_memory_days: f64,
    pub request_rate: f64,
    pub requests_today: f64,
    pub thin_guard: f64,
    pub normal_request: f64,
    pub prop_gain: f64,
    pub pricing: Pricing,
    pub cost_ref: f64,
    pub markup: f64,
    pub req_price: f64,
    pub share: f64,
    pub op_profit: f64,
    pub withdrawn: f64,
    // attributes added later in Python (default if missing)
    pub marks: Vec<f64>,
    pub stocked_out: bool,
    pub unmet_frac: f64,
    pub peak_paid: f64,
    pub broke_months: i64,
    /// Transient identity (not in the dump). Python tracks a shop by object identity; the `id` string is not unique
    /// (`sk{shop_entries}e`, the counter is reset in a snapshot).
    #[serde(skip)]
    pub tag: usize,
}

impl Shop {
    pub fn cover_ratio(&self) -> f64 {
        let cover = self.stock / max(self.request_rate, 1e-9);
        cover / self.target_cover_days
    }
    pub fn stock_ratio(&self) -> f64 {
        self.stock / self.target
    }
    pub fn signal_ratio(&self) -> f64 {
        if self.price_rule == PriceRule::Cover {
            if self.thin_guard > 0.0 && self.request_rate < self.thin_guard * self.normal_request {
                return if self.stock > 0.0 { max(1.0, self.cover_ratio()) } else { 1.0 };
            }
            return self.cover_ratio();
        }
        self.stock_ratio()
    }
    pub fn end_of_day_requests(&mut self) {
        self.request_rate += (self.requests_today - self.request_rate) / self.request_memory_days;
        self.requests_today = 0.0;
    }
    pub fn withdrawal(&self) -> f64 {
        let excess = self.cash - self.working_capital_mult * self.target * self.mid;
        if excess > 0.0 {
            pymath::int(excess * self.withdraw_rate) as f64
        } else {
            0.0
        }
    }
    pub fn scarcity_factor(&self) -> f64 {
        if self.prop_gain <= 0.0 {
            return 1.0;
        }
        let r = min(self.room_mult, max(1.0 / self.room_mult, self.signal_ratio()));
        pow(r, -self.prop_gain)
    }
    pub fn quote(&self) -> f64 {
        self.mid * self.scarcity_factor()
    }
    pub fn ask(&self) -> f64 {
        if self.pricing == Pricing::Lerner {
            return self.cost_ref * (1.0 + self.markup) * self.scarcity_factor();
        }
        let mut a = self.quote() * (1.0 + self.margin / 2.0);
        let r = if self.price_rule == PriceRule::Cover { self.cover_ratio() } else { self.stock_ratio() };
        #[allow(clippy::neg_cmp_op_on_partial_ord)] // NaN must take this branch, as in the Python original
        if !(r >= 1.5) {
            a = max(a, self.avg_cost * (1.0 + self.min_markup));
        }
        a
    }
    pub fn bid(&self) -> f64 {
        if self.pricing == Pricing::Lerner {
            return self.ask() / (1.0 + self.min_markup);
        }
        self.quote() * (1.0 - self.margin / 2.0)
    }
    pub fn desired_stock(&self) -> f64 {
        if self.price_rule == PriceRule::Cover {
            return self.target_cover_days * self.request_rate;
        }
        self.target
    }
    pub fn buy_room(&self, price: f64) -> f64 {
        let room = min(self.room_mult * self.desired_stock(), self.capacity) - self.stock;
        let affordable = if price > 0.0 { self.cash / price } else { 0.0 };
        max(0.0, min(room, affordable))
    }
    pub fn receive(&mut self, qty: f64, cost: f64) {
        let total_value = self.avg_cost * self.stock + cost;
        self.stock += qty;
        if self.stock > 0.0 {
            self.avg_cost = total_value / self.stock;
        }
    }
    pub fn update_mid(&mut self) {
        let mut mv = if matches!(self.price_rule, PriceRule::Log | PriceRule::Cover) {
            let ratio = if self.price_rule == PriceRule::Cover { self.cover_ratio() } else { self.stock_ratio() };
            let r = min(self.room_mult, max(1.0 / self.room_mult, ratio));
            -self.kappa * log(r)
        } else {
            -self.kappa * (self.stock_ratio() - 1.0)
        };
        if self.anchor > 0.0 {
            mv += self.anchor * log(self.memory_price / self.mid);
        }
        mv = max(-self.max_daily_move, min(self.max_daily_move, mv));
        self.mid *= 1.0 + mv;
        self.memory_price += (self.mid - self.memory_price) / self.memory_days;
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum NormalMode {
    Ema,
    Median,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Storer {
    pub id: String,
    pub cash: f64,
    pub stock: f64,
    pub capacity: f64,
    pub margin: f64,
    pub normal: f64,
    pub normal_memory_days: f64,
    pub fair: f64,
    pub fair_memory_days: f64,
    pub max_fair_mult: f64,
    pub carry_per_year: f64,
    pub season_pos: f64,
    pub withdraw_rate: f64,
    pub working_capital: f64,
    pub normal_mode: NormalMode,
    pub normal_years: usize,
    pub season_sum: f64,
    pub season_n: i64,
    pub season_history: Vec<f64>,
    pub shade: f64,
}

fn keep_last(v: &mut Vec<f64>, n: usize) {
    if v.len() > n {
        v.drain(..v.len() - n);
    }
}

impl Storer {
    pub fn on_harvest_news(&mut self, marketable_ratio: f64, elasticity: f64) {
        if self.normal_mode == NormalMode::Median && self.season_n > 0 {
            self.season_history.push(self.season_sum / self.season_n as f64);
            keep_last(&mut self.season_history, self.normal_years);
            self.normal = pymath::np_median(&self.season_history);
            self.season_sum = 0.0;
            self.season_n = 0;
        }
        let mult = pow(marketable_ratio, 1.0 / elasticity);
        self.fair = self.normal * min(self.max_fair_mult, max(1.0 / self.max_fair_mult, mult));
    }
    pub fn observe(&mut self, w: f64) {
        if self.normal_mode == NormalMode::Median {
            self.season_sum += w;
            self.season_n += 1;
        } else {
            self.normal += (w - self.normal) / self.normal_memory_days;
        }
        if self.fair_memory_days > 0.0 {
            self.fair += (w - self.fair) / self.fair_memory_days;
        }
    }
    pub fn fair_today(&self) -> f64 {
        self.fair * (1.0 + self.carry_per_year * (self.season_pos - 0.5))
    }
    fn inv_factor(&self) -> f64 {
        if self.shade <= 0.0 || self.capacity <= 0.0 {
            return 1.0;
        }
        1.0 - self.shade * (self.stock / self.capacity - 0.5)
    }
    pub fn bid(&self) -> f64 {
        self.fair_today() / (1.0 + self.margin / 2.0) * self.inv_factor()
    }
    pub fn sell_floor(&self) -> f64 {
        self.fair_today() * (1.0 + self.margin / 2.0) * self.inv_factor()
    }
    pub fn roll_continuous(&mut self) {
        if self.season_n > 0 {
            self.season_history.push(self.season_sum / self.season_n as f64);
            keep_last(&mut self.season_history, 12);
            self.normal = pymath::np_median(&self.season_history);
            self.season_sum = 0.0;
            self.season_n = 0;
            self.fair = self.normal;
        }
    }
    pub fn buy_room(&self, price: f64) -> f64 {
        max(0.0, min(self.capacity - self.stock, if price > 0.0 { self.cash / price } else { 0.0 }))
    }
    pub fn receive(&mut self, qty: f64, _cost: f64) {
        self.stock += qty;
    }
    pub fn withdrawal(&self) -> f64 {
        let excess = self.cash - self.working_capital;
        if excess > 0.0 {
            pymath::int(excess * self.withdraw_rate) as f64
        } else {
            0.0
        }
    }
}

/// `D1Sim` (external wholesale market mode).
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Market {
    pub cfg: MarketCfg,
    pub day: i64,
    pub date: Date,
    pub harvest_day: Option<i64>,
    pub harvest_ratio: Option<f64>,
    pub rng: RngStreams,
    pub rural: Rural,
    pub shops: Vec<Shop>,
    pub storers: Vec<Storer>,
}

impl Market {
    pub fn good(&self) -> Good {
        self.cfg.good
    }

    pub fn days_to_harvest(&self) -> i64 {
        let (y, _, _) = self.date.ymd();
        let mut h = Date::new(y, self.cfg.harvest_month, 1);
        if h <= self.date {
            h = Date::new(y + 1, self.cfg.harvest_month, 1);
        }
        h.days_since(self.date)
    }

    /// `_sorted_shops`: seeded shuffle, then stable sort. `desc` = `reverse=True` (ties keep their order).
    pub fn sorted_shops(&mut self, key: impl Fn(&Shop) -> f64, desc: bool) -> Vec<usize> {
        let order = self.rng.get("market").permutation(self.shops.len());
        let mut keyed: Vec<(usize, f64)> = order.into_iter().map(|i| (i, key(&self.shops[i]))).collect();
        if desc {
            keyed.sort_by(|a, b| b.1.partial_cmp(&a.1).expect("NaN"));
        } else {
            keyed.sort_by(|a, b| a.1.partial_cmp(&b.1).expect("NaN"));
        }
        keyed.into_iter().map(|x| x.0).collect()
    }

    pub fn money_total(&self) -> f64 {
        pymath::sum(self.shops.iter().map(|s| s.cash)) + pymath::sum(self.storers.iter().map(|s| s.cash))
    }

    pub fn goods_total(&self) -> f64 {
        self.rural.stock
            + pymath::sum(self.shops.iter().map(|s| s.stock))
            + pymath::sum(self.storers.iter().map(|s| s.stock))
    }

    fn harvest(&mut self, ledger: &mut Ledger) {
        let g = self.good();
        if self.cfg.continuous_supply {
            let qty = self.rural.annual_capacity / 365.0;
            self.rural.stock += qty;
            ledger.goods_source(g, "production", qty);
            return;
        }
        if self.date.month() == self.cfg.harvest_month && self.date.day() == 1 {
            assert!(self.cfg.yield_overrides.is_empty(), "yield_overrides not ported");
            let _year_idx = self.date.year() - START_DATE.0;
            let ys = self.cfg.yield_sigma;
            let shock = exp(self.rng.get("harvest").normal(0.0, ys));
            let qty = self.rural.annual_capacity * shock;
            self.rural.stock += qty;
            ledger.goods_source(g, "harvest", qty);
            self.rural.set_own_consumption(shock);
            let r = &self.rural;
            let marketable = r.annual_capacity * shock - r.own_daily * 365.0;
            let normal = r.annual_capacity * (1.0 - r.self_share);
            if normal > 0.0 {
                self.harvest_ratio = Some(max(0.05, marketable / normal));
                self.harvest_day = Some(self.day);
                let el = self.cfg.elasticity;
                for st in self.storers.iter_mut() {
                    st.on_harvest_news(max(0.05, marketable / normal), el);
                }
            }
            let w = self.cfg.harvest_news_weight;
            if w > 0.0 {
                let implied = pow(shock, 1.0 / self.cfg.elasticity);
                for s in self.shops.iter_mut() {
                    s.mid *= pow(implied, w);
                }
            }
        }
    }

    /// `step_pre` (external wholesale market): harvest only.
    pub fn step_pre(&mut self, ledger: &mut Ledger) {
        assert!(self.cfg.external_wholesale);
        self.harvest(ledger);
    }

    fn interdealer(&mut self) {
        let shops = &mut self.shops;
        let mut sellers: Vec<usize> = (0..shops.len()).filter(|&i| shops[i].signal_ratio() > 1.3).collect();
        let mut buyers: Vec<usize> = (0..shops.len()).filter(|&i| shops[i].signal_ratio() < 0.7).collect();
        sellers.sort_by(|&a, &b| shops[a].quote().partial_cmp(&shops[b].quote()).unwrap());
        buyers.sort_by(|&a, &b| shops[b].quote().partial_cmp(&shops[a].quote()).unwrap());
        while !sellers.is_empty() && !buyers.is_empty() {
            let (se, bu) = (sellers[0], buyers[0]);
            if shops[bu].quote() < shops[se].quote() {
                break;
            }
            let price = (shops[bu].quote() + shops[se].quote()) / 2.0;
            let qty = min(
                min(shops[se].stock - shops[se].desired_stock(), shops[bu].desired_stock() - shops[bu].stock),
                shops[bu].cash / price,
            );
            if qty <= 0.0 {
                break;
            }
            let cost = pymath::round(qty * price) as f64;
            shops[bu].cash -= cost;
            shops[se].cash += cost;
            shops[se].stock -= qty;
            shops[bu].receive(qty, cost);
            if shops[se].signal_ratio() <= 1.3 {
                sellers.remove(0);
            }
            if shops[bu].signal_ratio() >= 0.7 {
                buyers.remove(0);
            }
        }
    }

    fn upkeep(&mut self, ledger: &mut Ledger) {
        let g = self.good();
        for s in self.shops.iter_mut() {
            let loss = s.stock * self.cfg.spoilage_per_day;
            s.stock -= loss;
            ledger.goods_sink(g, "spoilage", loss);
            let rent = min(s.rent, s.cash);
            s.cash -= rent;
            ledger.money_sink("rent", rent);
            let w = s.withdrawal();
            s.cash -= w;
            s.withdrawn += w;
            ledger.money_sink("owner_consumption", w);
        }
        let loss = self.rural.stock * self.cfg.farm_spoilage_per_day;
        self.rural.stock -= loss;
        ledger.goods_sink(g, "spoilage", loss);
        let eat = min(self.rural.stock, self.rural.own_daily);
        self.rural.stock -= eat;
        ledger.goods_sink(g, "farm_consumption", eat);
        for st in self.storers.iter_mut() {
            let loss = st.stock * self.cfg.farm_spoilage_per_day;
            st.stock -= loss;
            ledger.goods_sink(g, "spoilage", loss);
            let w = st.withdrawal();
            st.cash -= w;
            ledger.money_sink("owner_consumption", w);
        }
    }

    /// `step_post`: the part of the day after urban buying (no records kept; the world keeps its own).
    pub fn step_post(&mut self, ledger: &mut Ledger) {
        let bids: Vec<f64> = self.shops.iter().map(|s| s.bid()).collect();
        let wholesale = pymath::np_mean(&bids);
        let season_pos = 1.0 - self.days_to_harvest() as f64 / 365.0;
        self.rural.observe(wholesale);
        for st in self.storers.iter_mut() {
            st.observe(wholesale);
            st.season_pos = season_pos;
        }
        if self.cfg.interdealer {
            self.interdealer();
        }
        for s in self.shops.iter_mut() {
            s.end_of_day_requests();
            s.update_mid();
        }
        self.upkeep(ledger);
        self.day += 1;
        self.date = self.date.add_days(1);
    }
}
