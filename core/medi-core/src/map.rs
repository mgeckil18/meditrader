//! Map data (M0, docs/design/trade-structure.md §8): ports, regions, legs, supply plan, production pools.
//! One map is installed per process (`install`); if accessed before that, the default `classic6` (the Python oracle's map,
//! K-033: never changed). `Port` and `Region` are indices into the map; written by name in JSON.

use std::collections::HashMap;
use std::sync::OnceLock;

use serde::Deserialize;

use crate::consts::{Good, Port, Region};

pub const DEFAULT_MAP: &str = include_str!("../../maps/classic6.json");

#[derive(Clone, Debug, Deserialize)]
pub struct PortDef {
    pub id: String,
    #[serde(default)]
    pub name: String,
    pub pop: f64,
    pub classes: [f64; 3],
    #[serde(default = "one")]
    pub wine_factor: f64,
    /// large | medium | small (informational only; behaviour comes from the properties)
    #[serde(default)]
    pub tier: String,
    #[serde(default)]
    pub lat: f64,
    #[serde(default)]
    pub lon: f64,
}

fn one() -> f64 {
    1.0
}

#[derive(Clone, Debug, Deserialize)]
pub struct RegionDef {
    pub id: String,
    /// natural hazard multiplier in winter
    pub winter_mult: f64,
    /// calm-period corsair probability (per leg)
    pub corsair: f64,
}

#[derive(Clone, Debug, Deserialize)]
struct EdgeRaw {
    a: String,
    b: String,
    days: f64,
    regions: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
struct SupRaw {
    port: String,
    #[serde(default)]
    own: Option<f64>,
    #[serde(default)]
    exp: Option<f64>,
}

#[derive(Clone, Debug, Deserialize)]
struct SupplyRaw {
    good: Good,
    plan: Vec<SupRaw>,
}

#[derive(Clone, Debug, Deserialize)]
struct PoolRaw {
    port: String,
    good: Good,
    serves: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
struct MapRaw {
    name: String,
    home: String,
    ports: Vec<PortDef>,
    regions: Vec<RegionDef>,
    edges: Vec<EdgeRaw>,
    supply: Vec<SupplyRaw>,
    pools: Vec<PoolRaw>,
}

/// Supply plan entry: self-sufficiency ratio or exporter weight.
#[derive(Clone, Copy, Debug)]
pub enum Sup {
    Own(f64),
    Exp(f64),
}

#[derive(Debug)]
pub struct MapData {
    pub name: String,
    pub home: Port,
    pub ports: Vec<PortDef>,
    pub regions: Vec<RegionDef>,
    /// (a, b, days, regions), in file order
    pub edges: Vec<(Port, Port, f64, Vec<Region>)>,
    /// goods in file order
    pub supply: Vec<(Good, Vec<(Port, Sup)>)>,
    pub pools: Vec<((Port, Good), Vec<Port>)>,
    pub all_ports: Vec<Port>,
    pub all_regions: Vec<Region>,
    port_ix: HashMap<String, u16>,
    region_ix: HashMap<String, u8>,
}

impl MapData {
    pub fn parse(s: &str) -> Result<MapData, String> {
        let r: MapRaw = serde_json::from_str(s).map_err(|e| format!("harita: {e}"))?;
        let port_ix: HashMap<String, u16> = r.ports.iter().enumerate().map(|(i, p)| (p.id.clone(), i as u16)).collect();
        let region_ix: HashMap<String, u8> =
            r.regions.iter().enumerate().map(|(i, x)| (x.id.clone(), i as u8)).collect();
        if port_ix.len() != r.ports.len() || region_ix.len() != r.regions.len() {
            return Err("map: duplicate port or region id".into());
        }
        let p = |s: &str| port_ix.get(s).map(|&i| Port(i)).ok_or_else(|| format!("harita: bilinmeyen liman {s}"));
        let rg = |s: &str| region_ix.get(s).map(|&i| Region(i)).ok_or_else(|| format!("map: unknown region {s}"));
        let mut edges = Vec::new();
        for e in &r.edges {
            let regs = e.regions.iter().map(|x| rg(x)).collect::<Result<Vec<_>, _>>()?;
            if regs.is_empty() {
                return Err(format!("map: leg {}-{} has no region", e.a, e.b));
            }
            edges.push((p(&e.a)?, p(&e.b)?, e.days, regs));
        }
        let mut supply = Vec::new();
        for s in &r.supply {
            let mut plan = Vec::new();
            for x in &s.plan {
                let v = match (x.own, x.exp) {
                    (Some(o), None) => Sup::Own(o),
                    (None, Some(w)) => Sup::Exp(w),
                    _ => return Err(format!("map: {:?} {} needs own or exp (exactly one)", s.good, x.port)),
                };
                plan.push((p(&x.port)?, v));
            }
            supply.push((s.good, plan));
        }
        let mut pools = Vec::new();
        for x in &r.pools {
            pools.push(((p(&x.port)?, x.good), x.serves.iter().map(|s| p(s)).collect::<Result<Vec<_>, _>>()?));
        }
        let n = r.ports.len();
        let nr = r.regions.len();
        Ok(MapData {
            name: r.name.clone(),
            home: p(&r.home)?,
            ports: r.ports,
            regions: r.regions,
            edges,
            supply,
            pools,
            all_ports: (0..n as u16).map(Port).collect(),
            all_regions: (0..nr as u8).map(Region).collect(),
            port_ix,
            region_ix,
        })
    }

    pub fn n_ports(&self) -> usize {
        self.ports.len()
    }
    pub fn n_regions(&self) -> usize {
        self.regions.len()
    }
    pub fn port(&self, id: &str) -> Option<Port> {
        self.port_ix.get(id).map(|&i| Port(i))
    }
    pub fn region(&self, id: &str) -> Option<Region> {
        self.region_ix.get(id).map(|&i| Region(i))
    }
    pub fn supply_plan(&self, g: Good) -> Option<&[(Port, Sup)]> {
        self.supply.iter().find(|x| x.0 == g).map(|x| x.1.as_slice())
    }
    /// Leg duration (days; in the file's direction).
    pub fn edge_days(&self, a: Port, b: Port) -> f64 {
        self.edges.iter().find(|e| e.0 == a && e.1 == b).unwrap_or_else(|| panic!("edge_days: {a:?}-{b:?}")).2
    }
    /// Regions of a leg (leg key in the file's direction).
    pub fn edge_regions(&self, a: Port, b: Port) -> &[Region] {
        &self.edges.iter().find(|e| e.0 == a && e.1 == b).unwrap_or_else(|| panic!("edge_regions: {a:?}-{b:?}")).3
    }
}

static MAP: OnceLock<MapData> = OnceLock::new();

/// Installs the map. Re-installing the same map is a no-op; a different one is an error.
pub fn install(s: &str) -> Result<&'static MapData, String> {
    let m = MapData::parse(s)?;
    let name = m.name.clone();
    let cur = MAP.get_or_init(|| m);
    if cur.name != name {
        return Err(format!("map '{}' is already installed in this process; cannot install '{}'", cur.name, name));
    }
    Ok(cur)
}

/// The installed map (or the default).
#[inline]
pub fn get() -> &'static MapData {
    MAP.get_or_init(|| MapData::parse(DEFAULT_MAP).expect("default map"))
}

/// Installs the map from the config's `map` field: empty or "classic6" = default; otherwise a file path or
/// `core/maps/<name>.json`.
pub fn install_from_cfg(map: &str) -> Result<&'static MapData, String> {
    if map.is_empty() || map == "classic6" {
        return install(DEFAULT_MAP);
    }
    let path = if map.ends_with(".json") {
        std::path::PathBuf::from(map)
    } else {
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../maps").join(format!("{map}.json"))
    };
    let s = std::fs::read_to_string(&path).map_err(|e| format!("{}: {e}", path.display()))?;
    install(&s)
}
