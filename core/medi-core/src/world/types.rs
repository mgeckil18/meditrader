//! Parts of the world state. The JSON format is shared with `core/tools/state_io.py` (the Python dump writes it).
//! Python tuples are tuple structs here; written as arrays in JSON.

use std::hash::{BuildHasherDefault, Hasher};
use std::ops::{Index, IndexMut};

use indexmap::IndexMap;
use serde::de::DeserializeOwned;
use serde::{Deserialize, Deserializer, Serialize, Serializer};

use crate::consts::{n_ports, Good, Port};

/// Merchant id: "m12" in Python -> 12. 0 = the representative "public" merchant; negative = a ship being fitted out ("pend{i}" -> -1-i).
pub type Mid = i64;

/// Fast hash for integer keys (FxHash, as used by rustc). Much cheaper than the default SipHash;
/// IndexMap keeps insertion order, so behaviour does not change.
#[derive(Default, Clone, Copy)]
pub struct FxHasher(u64);

impl Hasher for FxHasher {
    #[inline]
    fn write(&mut self, bytes: &[u8]) {
        for &b in bytes {
            self.write_u64(b as u64);
        }
    }
    #[inline]
    fn write_u64(&mut self, x: u64) {
        self.0 = (self.0.rotate_left(5) ^ x).wrapping_mul(0x51_7c_c1_b7_27_22_0a_95);
    }
    #[inline]
    fn write_i64(&mut self, x: i64) {
        self.write_u64(x as u64)
    }
    #[inline]
    fn finish(&self) -> u64 {
        self.0
    }
}

pub type FxBuild = BuildHasherDefault<FxHasher>;
/// Integer-keyed map (loads, merchants), insertion ordered.
pub type IdMap<V> = IndexMap<i64, V, FxBuild>;

/// Set of non-negative ids (news ids come from an increasing counter): a bit set, O(1) membership.
/// A sorted list in JSON (Python `set` -> sorted).
#[derive(Clone, Debug, Default)]
pub struct IdSet(Vec<u64>);

impl IdSet {
    #[inline]
    pub fn contains(&self, x: &i64) -> bool {
        let x = *x as usize;
        self.0.get(x >> 6).is_some_and(|w| w >> (x & 63) & 1 == 1)
    }
    #[inline]
    pub fn insert(&mut self, x: i64) {
        assert!(x >= 0, "IdSet: negatif kimlik {x}");
        let x = x as usize;
        if self.0.len() <= x >> 6 {
            self.0.resize((x >> 6) + 1, 0);
        }
        self.0[x >> 6] |= 1 << (x & 63);
    }
    pub fn iter(&self) -> impl Iterator<Item = i64> + '_ {
        self.0
            .iter()
            .enumerate()
            .flat_map(|(i, &w)| (0..64).filter(move |b| w >> b & 1 == 1).map(move |b| (i * 64 + b) as i64))
    }
    pub fn len(&self) -> usize {
        self.0.iter().map(|w| w.count_ones() as usize).sum()
    }
    pub fn is_empty(&self) -> bool {
        self.0.iter().all(|&w| w == 0)
    }
}

impl Serialize for IdSet {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.collect_seq(self.iter())
    }
}

impl<'de> Deserialize<'de> for IdSet {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let v: Vec<i64> = Vec::deserialize(d)?;
        let mut s = IdSet::default();
        for x in v {
            if x < 0 {
                return Err(serde::de::Error::custom(format!("IdSet: negatif kimlik {x}")));
            }
            s.insert(x);
        }
        Ok(s)
    }
}

/// Cache of intermediate results during one merchant decision (see `Core::ctx`).
pub struct Ctx {
    pub normal: Vec<Option<f64>>,
    pub risk: Option<f64>,
    pub buckets: Option<Vec<Vec<f64>>>,
}

/// Value per port (`{port: value}` dicts). Only ports in `port_list` are set.
#[derive(Clone, Debug)]
pub struct PortMap<T>(pub Vec<Option<T>>);

impl<T> Default for PortMap<T> {
    fn default() -> Self {
        PortMap((0..n_ports()).map(|_| None).collect())
    }
}

impl<T> PortMap<T> {
    pub fn get(&self, p: Port) -> Option<&T> {
        self.0[p.idx()].as_ref()
    }
    pub fn get_mut(&mut self, p: Port) -> Option<&mut T> {
        self.0[p.idx()].as_mut()
    }
    pub fn contains(&self, p: Port) -> bool {
        self.0[p.idx()].is_some()
    }
    pub fn set(&mut self, p: Port, v: T) {
        self.0[p.idx()] = Some(v);
    }
}

impl<T> Index<Port> for PortMap<T> {
    type Output = T;
    fn index(&self, p: Port) -> &T {
        self.0[p.idx()].as_ref().unwrap_or_else(|| panic!("PortMap: {p:?} yok"))
    }
}

impl<T> IndexMut<Port> for PortMap<T> {
    fn index_mut(&mut self, p: Port) -> &mut T {
        self.0[p.idx()].as_mut().unwrap_or_else(|| panic!("PortMap: {p:?} yok"))
    }
}

impl<T: Serialize> Serialize for PortMap<T> {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        let m: IndexMap<&str, &T> =
            Port::all().iter().filter_map(|&p| self.0[p.idx()].as_ref().map(|v| (p.name(), v))).collect();
        m.serialize(s)
    }
}

impl<'de, T: DeserializeOwned> Deserialize<'de> for PortMap<T> {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let m: IndexMap<Port, T> = IndexMap::deserialize(d)?;
        let mut out = PortMap::default();
        for (k, v) in m {
            out.0[k.idx()] = Some(v);
        }
        Ok(out)
    }
}

/// Ordered map whose key cannot be a JSON string: [[key, value], ...] in JSON.
#[derive(Clone, Debug)]
pub struct PairList<K: std::hash::Hash + Eq, V>(pub IndexMap<K, V>);

impl<K: std::hash::Hash + Eq, V> Default for PairList<K, V> {
    fn default() -> Self {
        PairList(IndexMap::new())
    }
}

impl<K: std::hash::Hash + Eq + Serialize, V: Serialize> Serialize for PairList<K, V> {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        let v: Vec<(&K, &V)> = self.0.iter().collect();
        v.serialize(s)
    }
}

impl<'de, K: std::hash::Hash + Eq + DeserializeOwned, V: DeserializeOwned> Deserialize<'de> for PairList<K, V> {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        let v: Vec<(K, V)> = Vec::deserialize(d)?;
        Ok(PairList(v.into_iter().collect()))
    }
}

/// Float that may be infinite/NaN ("inf" / "-inf" / "nan" in JSON).
pub mod pyf {
    use serde::{Deserialize, Deserializer, Serializer};

    pub fn serialize<S: Serializer>(x: &f64, s: S) -> Result<S::Ok, S::Error> {
        if x.is_finite() {
            s.serialize_f64(*x)
        } else if x.is_nan() {
            s.serialize_str("nan")
        } else if *x > 0.0 {
            s.serialize_str("inf")
        } else {
            s.serialize_str("-inf")
        }
    }

    #[derive(Deserialize)]
    #[serde(untagged)]
    enum NumOrStr {
        N(f64),
        S(String),
    }

    pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<f64, D::Error> {
        match NumOrStr::deserialize(d)? {
            NumOrStr::N(x) => Ok(x),
            NumOrStr::S(s) => match s.as_str() {
                "inf" => Ok(f64::INFINITY),
                "-inf" => Ok(f64::NEG_INFINITY),
                "nan" => Ok(f64::NAN),
                _ => Err(serde::de::Error::custom(format!("float: {s}"))),
            },
        }
    }

    pub mod opt {
        use serde::{Deserialize, Deserializer, Serializer};
        pub fn serialize<S: Serializer>(x: &Option<f64>, s: S) -> Result<S::Ok, S::Error> {
            match x {
                None => s.serialize_none(),
                Some(v) => super::serialize(v, s),
            }
        }
        pub fn deserialize<'de, D: Deserializer<'de>>(d: D) -> Result<Option<f64>, D::Error> {
            #[derive(Deserialize)]
            struct W(#[serde(deserialize_with = "super::deserialize")] f64);
            Ok(Option::<W>::deserialize(d)?.map(|w| w.0))
        }
    }
}

/// Rumour of a rival loading: (origin, target, good, quantity, day, merchant).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Load(pub Port, pub Port, pub Good, pub f64, pub i64, pub Mid);

/// Route: (loading port, target, good).
pub type Route = (Port, Port, Good);

/// Plan: (good, target, maximum buy price, maximum quantity).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Plan(pub Good, pub Port, pub f64, pub f64);

/// Option: (score, good, target, maximum buy price, quantity).
#[derive(Clone, Copy, Debug)]
pub struct Opt {
    pub score: f64,
    pub g: Good,
    pub d: Port,
    pub max_bid: f64,
    pub q: f64,
}

/// Voyage diagnostic record (at departure): (day, good, qty, expected net, unit cost, cash, origin, target, level).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Voy(pub i64, pub Good, pub f64, pub f64, pub f64, pub f64, pub Port, pub Port, pub i64);

/// Loan: (principal, port, yearly rate, day, voyage premium).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Debt(pub f64, pub Port, pub f64, pub i64, pub f64);

/// Cargo info / harvest news in port: by market order (value, day); None if absent.
pub type MarketInfo = Vec<Option<(f64, i64)>>;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum MState {
    Buying,
    Selling,
    Sailing,
}

/// Price packet: (origin, day, [(good, price)]).
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Packet(pub Port, pub i64, pub Vec<(Good, f64)>);

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct M5 {
    pub id: Mid,
    pub cash: f64,
    pub capacity: f64,
    pub is_player: bool,
    pub informed: bool,
    pub state: MState,
    pub loc: Port,
    pub dest: Option<Port>,
    pub arrive_day: i64,
    pub good: Option<Good>,
    pub qty: f64,
    pub cost_basis: f64,
    pub plan: Option<Plan>,
    pub wait: i64,
    pub risk_aversion: f64,
    /// by market order (price, day)
    pub obs: Vec<(f64, i64)>,
    pub hist: Vec<Vec<f64>>,
    pub heard: IdSet,
    pub heard_h: IdSet,
    pub heard_hn: IdSet,
    pub born_day: i64,
    pub start_capital: f64,
    pub divs: f64,
    pub marks: Vec<f64>,
    pub level: i64,
    pub imitation: f64,
    pub overconf: f64,
    pub p_hear: f64,
    pub dara: bool,
    pub known_loads: IdMap<Load>,
    pub w_fund: f64,
    pub hnews: MarketInfo,
    pub seen_buys: Vec<(Mid, Port, Good, f64, i64)>,
    pub reservation: f64,
    pub harbor: MarketInfo,
    pub home: Port,
    /// (end day, return, volume, profit, duration)
    pub record: Vec<(i64, f64, f64, f64, i64)>,
    pub debt: Option<Debt>,
    pub debt_lost: bool,
    pub broke: bool,
    pub emarks: Vec<f64>,
    pub retire: bool,
    pub v0: f64,
    pub t0: i64,
    pub ship: Option<i64>,
    pub on_order: i64,
    pub exit_ship: f64,
    // attributes added later in Python
    pub voy: Option<Voy>,
    pub voy_overhead: f64,
    pub packet: Option<Packet>,
    pub packet_hnews: MarketInfo,
    pub packet_harbor: MarketInfo,
    pub carried: IdMap<Load>,
    pub debt_pd: Option<f64>,
    /// M2.1: quantity loaded onto the ship in this port (volume units)
    #[serde(default)]
    pub loaded: f64,
    /// M2.1: quantity waiting to be unloaded (volume units)
    #[serde(default)]
    pub unload_left: f64,
    /// M2.1: yesterday's cargo and the exponential mean of daily buying (fill decision)
    #[serde(default)]
    pub qty_prev: f64,
    #[serde(default)]
    pub fill_ema: f64,
    /// Day the cargo was first bought (-1 = no cargo); spoilage age
    #[serde(default = "neg1")]
    pub cargo_day: i64,
    /// I0: diagnostic record of the last reroute (empty = none)
    #[serde(default)]
    pub rr: Vec<f64>,
    /// I1: price table carried by the ship (market, price, day)
    #[serde(default)]
    pub packet_all: Vec<(usize, f64, i64)>,
    /// K-040 mixed cargo: lots carried on board besides the active lot
    #[serde(default)]
    pub hold: Vec<Lot>,
    /// K-040: goods already considered in this call (not sold, put in the hold)
    #[serde(default)]
    pub considered: Vec<Good>,
    /// K-040: value per volume unit of free space in this port (the space-freeing value of selling)
    #[serde(default)]
    pub fill_val: f64,
    /// K-040: the active lot's cash flow since departure (sales revenue - fees charged to the lot)
    #[serde(default)]
    pub lot_flow: f64,
    /// K-040: the active lot has not started landing yet (sell/carry decision first)
    #[serde(default)]
    pub pre_land: bool,
    /// K-040: next port committed to for a lot put in the hold during this call
    #[serde(default)]
    pub commit: Option<Port>,
    /// S1: agreed but undelivered quantity, by storer order (storer, quantity, price)
    #[serde(default)]
    pub contract: Vec<(usize, f64, f64)>,
}

/// K-040: a lot in the hold.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Lot {
    pub g: Good,
    pub qty: f64,
    pub cost_basis: f64,
    pub cargo_day: i64,
    pub voy: Option<Voy>,
    pub overhead: f64,
    pub flow: f64,
    /// Port the lot is being carried to for sale
    #[serde(default)]
    pub target: Option<Port>,
}

impl M5 {
    /// S1: contracted quantity awaiting delivery
    pub fn contract_left(&self) -> f64 {
        self.contract.iter().map(|x| x.1).sum()
    }
    /// Is the ship empty (active lot and hold)?
    pub fn empty(&self) -> bool {
        self.qty <= 0.0 && self.hold.is_empty()
    }
    pub fn net_worth(&self) -> f64 {
        self.cash
            + if self.qty > 0.0 { self.cost_basis } else { 0.0 }
            + self.hold.iter().map(|l| l.cost_basis).sum::<f64>()
    }
    pub fn equity(&self) -> f64 {
        let mut out = self.net_worth();
        if let Some(d) = self.debt {
            out -= d.0;
        }
        out
    }
}

/// Merchant who exited / went bankrupt: (merchant, day, cash at exit).
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Gone(pub M5, pub i64, pub f64);

/// Ship being fitted out: (arrival day, port, route, ship's build day).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Pending(pub i64, pub Port, pub Option<Route>, pub i64);

/// Ship for sale (laid up).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Listing {
    pub built: i64,
    pub owner: Port,
    pub day: i64,
    /// M1.4: corsair prize (no home-port investors own it; the price leaves the economy)
    #[serde(default)]
    pub prize: bool,
}

/// voy_log row: (departure, end, good, origin, target, qty, expected, cost, realised, level, sale port, margin).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct VoyLog(
    pub i64,
    pub i64,
    pub Good,
    pub Port,
    pub Port,
    pub f64,
    pub f64,
    pub f64,
    pub f64,
    pub i64,
    pub Port,
    pub f64,
);

/// loan_log row: (close, port, principal, days, paid, owed, level, default, cargo lost, lender's PD).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct LoanLog(pub i64, pub Port, pub f64, pub i64, pub f64, pub f64, pub i64, pub bool, pub bool, pub Option<f64>);

/// cred_log row: (day, k, s², a, I, quarterly k).
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct CredLog(
    pub i64,
    #[serde(with = "pyf")] pub f64,
    pub f64,
    pub f64,
    pub i64,
    #[serde(with = "pyf::opt")] pub Option<f64>,
);

/// Ship market buyer (`_ship_buyers` dicts).
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Buyer {
    /// port if an investor; None if a merchant who lost a ship (`m` set)
    pub p: Option<Port>,
    /// merchant index (valid only within the month; the list is always empty between days)
    pub m: Option<usize>,
    pub r: f64,
    pub belief: f64,
    pub new: f64,
    pub foreign: f64,
    pub bid: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Recipe {
    pub inputs: Vec<(Good, f64)>,
    pub labor: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Pool {
    pub good: Good,
    pub recipe: Recipe,
    pub capacity: f64,
    pub cash: f64,
    pub util: f64,
    pub output: f64,
    pub inputs: Vec<(Good, f64)>,
    pub input_days: f64,
    pub margin_target: f64,
    pub util_speed: f64,
    pub util_hist: Vec<f64>,
    pub divs: f64,
    pub reservation: f64,
}

impl Pool {
    pub fn rate(&self) -> f64 {
        self.capacity * self.util
    }
    pub fn input_mut(&mut self, g: Good) -> &mut f64 {
        &mut self.inputs.iter_mut().find(|x| x.0 == g).expect("pool input").1
    }
    pub fn input(&self, g: Good) -> f64 {
        self.inputs.iter().find(|x| x.0 == g).expect("pool input").1
    }
}

/// Demand parameters of an urban class (LES + CES). a: [WHT, BRL]; gamma/beta in CONSUMER_CATS order.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ClassDemand {
    pub name: String,
    pub a: [f64; 2],
    pub gamma: [f64; 6],
    pub beta: [f64; 6],
}

fn neg1() -> i64 {
    -1
}
