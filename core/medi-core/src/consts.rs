//! Constants from `sim/world5.py` and `sim/engine.py`: goods, classes, hazard constants. Ports, regions and legs
//! live in the map data (`map.rs`); `Port` and `Region` are indices into the map.
//! Values match Python (placeholders are marked ⚠️ there). Constants that are ints in Python (e.g. `ref`) are
//! integer-valued f64 here; arithmetic results are the same.

use serde::{Deserialize, Serialize};

macro_rules! named_enum {
    ($name:ident { $($v:ident),* $(,)? }) => {
        #[allow(clippy::upper_case_acronyms)]
        #[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
        pub enum $name { $($v),* }
        impl $name {
            pub const ALL: &'static [$name] = &[$($name::$v),*];
            pub fn name(self) -> &'static str {
                match self { $($name::$v => stringify!($v)),* }
            }
            pub fn idx(self) -> usize { self as usize }
        }
    };
}

named_enum!(Good { WHT, BRL, OIL, WIN, WOL, ALM, PEP, CLC, CLF });

pub const N_GOODS: usize = 9;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GoodKind {
    Harvest,
    Continuous,
    Produced,
}

pub struct G5 {
    pub reff: f64,
    pub bulk: f64,
    pub kind: GoodKind,
    pub harvest_month: u32,
    pub self_share: f64,
}

pub const fn goods5(g: Good) -> G5 {
    use GoodKind::*;
    let (reff, bulk, kind, hm, ss) = match g {
        Good::WHT => (100.0, 1.0, Harvest, 7, 0.4),
        Good::BRL => (60.0, 1.0, Harvest, 6, 0.4),
        Good::OIL => (150.0, 1.0, Harvest, 11, 0.2),
        Good::WIN => (80.0, 1.0, Harvest, 9, 0.2),
        Good::WOL => (10.0, 0.6, Harvest, 5, 0.1),
        Good::ALM => (50.0, 0.3, Continuous, 7, 0.0),
        Good::PEP => (400.0, 0.05, Continuous, 7, 0.0),
        Good::CLC => (22.0, 0.3, Produced, 7, 0.0),
        Good::CLF => (60.0, 0.3, Produced, 7, 0.0),
    };
    G5 { reff, bulk, kind, harvest_month: hm, self_share: ss }
}

pub const POOR_INCOME_YEAR: f64 = 250.0;
pub const WAGE: f64 = 2.5;
pub const CUSTOMS: f64 = 0.03;
pub const FREIGHT_PER_BULK_DAY: f64 = 0.6;
pub const LOSS_PER_DAY_SUMMER: f64 = 0.001;
pub const LOSS_PER_DAY_WINTER: f64 = 0.003;
pub const NAT_PER_EDGE: f64 = 0.004;
pub const CORSAIR_RHO: f64 = 0.8;
pub const CORSAIR_SIGMA: f64 = 0.25;
pub const CORSAIR_JUMP_P: f64 = 0.05;
pub const CORSAIR_JUMP: f64 = 1.0;

/// Urban consumption categories (`CONSUMER_CATS`): CER (grain: wheat + barley CES), OIL, WIN, CLC, CLF, PEP.
pub const N_CATS: usize = 6;
pub const CAT_GOODS: [Option<Good>; N_CATS] =
    [None, Some(Good::OIL), Some(Good::WIN), Some(Good::CLC), Some(Good::CLF), Some(Good::PEP)];
pub const CLASS_NAMES: [&str; 3] = ["zengin", "orta", "yoksul"];
pub const WAGE_SHARES: [f64; 3] = [0.0, 0.3, 0.7];

/// Leontief recipe: (inputs, labour days per unit).
/// Shelf life tau of cargo on board (days; Weibull scale). Rough values ⚠️ (user: "set roughly, take a note"):
/// grain suffers damp and weevils, wine sours, oil leaks; pepper and alum keep.
pub fn cargo_tau(g: Good) -> f64 {
    match g {
        Good::WHT | Good::BRL => 120.0,
        Good::WIN => 150.0,
        Good::OIL => 200.0,
        Good::WOL => 250.0,
        Good::CLC | Good::CLF => 300.0,
        Good::PEP => 400.0,
        Good::ALM => 1000.0,
    }
}

pub fn recipe(g: Good) -> (&'static [(Good, f64)], f64) {
    match g {
        Good::CLC => (&[(Good::WOL, 1.0)], 4.0),
        Good::CLF => (&[(Good::WOL, 1.5), (Good::ALM, 0.2)], 12.0),
        _ => panic!("recipe: {g:?}"),
    }
}

macro_rules! map_index {
    ($name:ident, $t:ty, $all:ident, $names:ident, $lookup:ident, $what:literal) => {
        /// Index into the map; written by name in JSON.
        #[derive(Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
        pub struct $name(pub $t);
        impl $name {
            pub fn all() -> &'static [$name] {
                &crate::map::get().$all
            }
            #[allow(clippy::misnamed_getters)] // `name` is the map id, not a separate field
            pub fn name(self) -> &'static str {
                &crate::map::get().$names[self.0 as usize].id
            }
            #[inline]
            pub fn idx(self) -> usize {
                self.0 as usize
            }
            pub fn by_name(s: &str) -> Option<$name> {
                crate::map::get().$lookup(s)
            }
        }
        impl std::fmt::Debug for $name {
            fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                f.write_str(self.name())
            }
        }
        impl Serialize for $name {
            fn serialize<S: serde::Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
                s.serialize_str(self.name())
            }
        }
        impl<'de> Deserialize<'de> for $name {
            fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
                let s = String::deserialize(d)?;
                $name::by_name(&s)
                    .ok_or_else(|| serde::de::Error::custom(format!(concat!("unknown ", $what, " {}"), s)))
            }
        }
    };
}

map_index!(Port, u16, all_ports, ports, port, "port");
map_index!(Region, u8, all_regions, regions, region, "region");

/// Region: (winter multiplier, calm-period corsair probability).
pub fn region(r: Region) -> (f64, f64) {
    let x = &crate::map::get().regions[r.idx()];
    (x.winter_mult, x.corsair)
}

pub fn n_ports() -> usize {
    crate::map::get().n_ports()
}

pub fn n_regions() -> usize {
    crate::map::get().n_regions()
}

/// `shortest_days()`: Floyd-Warshall over all ports of the map. Returns: [a][b] days.
pub fn shortest_days() -> Vec<Vec<f64>> {
    let n = n_ports();
    let mut d = vec![vec![f64::INFINITY; n]; n];
    for (i, row) in d.iter_mut().enumerate() {
        row[i] = 0.0;
    }
    for (a, b, w, _) in crate::map::get().edges.iter() {
        d[a.idx()][b.idx()] = *w;
        d[b.idx()][a.idx()] = *w;
    }
    for k in 0..n {
        for i in 0..n {
            for j in 0..n {
                if d[i][k] + d[k][j] < d[i][j] {
                    d[i][j] = d[i][k] + d[k][j];
                }
            }
        }
    }
    d
}

/// `route_legs(d)`: legs of the shortest route (leg keys in the map's direction).
pub fn route_legs(d: &[Vec<f64>]) -> Vec<Vec<Vec<(Port, Port)>>> {
    let edges = &crate::map::get().edges;
    let edge = |x: Port, y: Port| -> Option<(Port, Port)> {
        for (a, b, _, _) in edges.iter() {
            if (*a, *b) == (x, y) || (*b, *a) == (x, y) {
                return Some((*a, *b));
            }
        }
        None
    };
    let all = Port::all();
    let n = all.len();
    let mut out = vec![vec![Vec::new(); n]; n];
    for &a in all {
        for &b in all {
            if a == b || !d[a.idx()][b.idx()].is_finite() {
                continue;
            }
            let mut path = Vec::new();
            let mut cur = a;
            while cur != b {
                let nxt = *all
                    .iter()
                    .find(|&&n| {
                        edge(cur, n).is_some()
                            && (d[cur.idx()][b.idx()] - d[cur.idx()][n.idx()] - d[n.idx()][b.idx()]).abs() < 1e-9
                    })
                    .expect("route_legs");
                path.push(edge(cur, nxt).unwrap());
                cur = nxt;
            }
            out[a.idx()][b.idx()] = path;
        }
    }
    out
}
