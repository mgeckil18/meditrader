//! Cold start: `D5World.__init__` (and the `_plan`, `_build_markets`, `_build_pools`, `_build_demand`,
//! `_required_fleet`, `_init_ships` it calls) and `D1Sim.__init__`. Same order and same operation order as Python.
//! Market parameters are the resolved form of the `H` preset in `sim/engine.py` (`D1Config` defaults + V2/V3/F/H
//! + `_build_markets` arguments); the dump comparison checks every field.

use super::*;
use crate::consts::{goods5, recipe, GoodKind, CLASS_NAMES, N_CATS, POOR_INCOME_YEAR, WAGE};
use crate::date::START_DATE;
use crate::map::{self, Sup};
use crate::market::{MarketCfg, NormalMode, PriceRule, Pricing, Rural, Shop, Storer};
use crate::pymath::max;
use crate::rng::{int_to_u32_words, Generator, Pcg64};

use Good::*;

/// `CLASS_TEMPLATE`: (rel, shares [CER, OIL, WIN, CLC, CLF, PEP], substitution base [CER, OIL], wheat share)
struct ClassT {
    rel: f64,
    shares: [f64; N_CATS],
    subs: [f64; N_CATS],
    wheat: f64,
}

const CLASS_TEMPLATE: [ClassT; 3] = [
    ClassT {
        rel: 12.0,
        shares: [0.08, 0.03, 0.05, 0.01, 0.14, 0.04],
        subs: [0.3, 0.3, 0.0, 0.0, 0.0, 0.0],
        wheat: 0.95,
    },
    ClassT {
        rel: 3.0,
        shares: [0.20, 0.06, 0.06, 0.07, 0.03, 0.01],
        subs: [0.6, 0.4, 0.0, 0.0, 0.0, 0.0],
        wheat: 0.85,
    },
    ClassT { rel: 1.0, shares: [0.35, 0.07, 0.06, 0.06, 0.0, 0.0], subs: [0.85, 0.5, 0.0, 0.0, 0.0, 0.0], wheat: 0.70 },
];

fn ports5(p: Port) -> &'static map::PortDef {
    &map::get().ports[p.idx()]
}

/// `corsair_norm()`: divisor that makes the corsair multiplier average 1 (fixed stream, 200,000 steps).
pub fn corsair_norm() -> f64 {
    const N: usize = 200_000;
    let mut r = Generator::new(Pcg64::from_entropy(&int_to_u32_words(12345)));
    let eps: Vec<f64> = (0..N).map(|_| r.standard_normal()).collect();
    let jump: Vec<bool> = (0..N).map(|_| r.random() < CORSAIR_JUMP_P).collect();
    let (mut x, mut tot) = (0.0, 0.0);
    for i in 0..N {
        x = CORSAIR_RHO * x + CORSAIR_SIGMA * eps[i] + if jump[i] { CORSAIR_JUMP } else { 0.0 };
        tot += pymath::exp(x);
    }
    tot / N as f64
}

use crate::consts::{CORSAIR_JUMP, CORSAIR_JUMP_P, CORSAIR_RHO, CORSAIR_SIGMA};

/// Python `_plan` outputs.
struct Plan0 {
    income_ref: PortMap<[f64; 3]>,
    local_cons: PortMap<[f64; N_GOODS]>,
    demand_l: PortMap<[f64; N_GOODS]>,
    pool_target: Vec<((Port, Good), f64)>,
    supply: PortMap<[f64; N_GOODS]>,
}

fn class_income(p: Port) -> [f64; 3] {
    let pp = ports5(p);
    std::array::from_fn(|k| pp.classes[k] * pp.pop * CLASS_TEMPLATE[k].rel * POOR_INCOME_YEAR / 365.0)
}

fn class_shares(p: Port, k: usize) -> [f64; N_CATS] {
    let mut sh = CLASS_TEMPLATE[k].shares;
    sh[2] *= ports5(p).wine_factor;
    sh
}

fn plan(ports: &[Port], goods: &[Good]) -> Plan0 {
    let rf = |g: Good| goods5(g).reff;
    let mut l: PortMap<[f64; N_GOODS]> = PortMap::default();
    let mut income_ref = PortMap::default();
    for &p in ports {
        let inc = class_income(p);
        income_ref.set(p, inc);
        let mut lp = [0.0; N_GOODS];
        for (k, &yk) in inc.iter().enumerate() {
            let sh = class_shares(p, k);
            let w = CLASS_TEMPLATE[k].wheat;
            lp[WHT.idx()] += sh[0] * yk * w / rf(WHT);
            lp[BRL.idx()] += sh[0] * yk * (1.0 - w) / rf(BRL);
            for (ci, c) in [(1, OIL), (2, WIN), (3, CLC), (4, CLF), (5, PEP)] {
                lp[c.idx()] += sh[ci] * yk / rf(c);
            }
        }
        l.set(p, lp);
    }
    let local_cons = l.clone();
    let mut pool_target = Vec::new();
    for ((p, g), served) in map::get().pools.iter() {
        let (p, g) = (*p, *g);
        if !ports.contains(&p) || !goods.contains(&g) {
            continue;
        }
        let v = pymath::sum(served.iter().filter(|q| ports.contains(q)).map(|&q| local_cons[q][g.idx()]));
        pool_target.push(((p, g), v));
    }
    let mut need_in: PortMap<[f64; N_GOODS]> = PortMap::default();
    for &p in ports {
        need_in.set(p, [0.0; N_GOODS]);
    }
    for &((p, g), out) in &pool_target {
        for &(inp, a) in recipe(g).0 {
            need_in[p][inp.idx()] += a * out;
        }
    }
    for &p in ports {
        for g in [WOL, ALM] {
            l[p][g.idx()] = need_in[p][g.idx()];
        }
    }
    let mut supply: PortMap<[f64; N_GOODS]> = PortMap::default();
    for &p in ports {
        supply.set(p, [0.0; N_GOODS]);
    }
    for (g, plan) in map::get().supply.iter() {
        let g = *g;
        if !goods.contains(&g) {
            continue;
        }
        let mut deficit = 0.0;
        let mut exporters: Vec<(Port, f64)> = Vec::new();
        for &p in ports {
            let v = plan.iter().find(|x| x.0 == p).map(|x| x.1).unwrap_or(Sup::Own(0.0));
            match v {
                Sup::Exp(w) => exporters.push((p, w)),
                Sup::Own(v) => {
                    supply[p][g.idx()] = v * l[p][g.idx()];
                    deficit += (1.0 - v) * l[p][g.idx()];
                }
            }
        }
        let ws = pymath::sum(exporters.iter().map(|x| x.1));
        let wsum = if ws == 0.0 { 1.0 } else { ws };
        for &(p, w) in &exporters {
            supply[p][g.idx()] = l[p][g.idx()] + w / wsum * deficit;
        }
    }
    Plan0 { income_ref, local_cons, demand_l: l, pool_target, supply }
}

/// `D1Sim.__init__` (`H` preset, `_build_markets` arguments).
#[allow(clippy::too_many_arguments)]
fn build_market(
    cfg: &Config,
    p: Port,
    g: Good,
    need: f64,
    surplus: f64,
    harvest: bool,
    continuous: bool,
    salt: u64,
) -> Market {
    let spec = goods5(g);
    let pop = ports5(p).pop;
    let ref_price = spec.reff;
    let margin = 0.10;
    let self_share = if harvest { spec.self_share } else { 0.0 };
    let n_shop = 3usize;
    let target_days = 30.0;
    let n_storers = if harvest {
        if matches!(g, WHT | BRL) {
            2
        } else {
            1
        }
    } else if cfg.liquidity {
        1
    } else {
        0
    };
    let mcfg = MarketCfg {
        good: g,
        harvest_month: spec.harvest_month,
        continuous_supply: continuous,
        yield_sigma: if harvest { cfg.yield_sigma } else { 0.0 },
        elasticity: -0.4,
        spoilage_per_day: 0.0005,
        farm_spoilage_per_day: 0.0002,
        interdealer: true,
        harvest_news_weight: 0.0,
        external_wholesale: cfg.wholesale,
        yield_overrides: Default::default(),
    };
    let need_pc_year = need * 365.0 / pop;
    let daily_need = pop * need_pc_year / 365.0;
    let mut mk = Market {
        cfg: mcfg,
        day: 0,
        date: Date::new(START_DATE.0, START_DATE.1, START_DATE.2),
        harvest_day: None,
        harvest_ratio: None,
        rng: RngStreams::new(cfg.seed * 1000 + salt),
        rural: Rural {
            annual_capacity: daily_need * 365.0 * surplus / (1.0 - self_share),
            harvest_month: spec.harvest_month,
            ref_price,
            floor_price: 0.4 * ref_price,
            supply_elasticity: 1.0,
            stock: 0.0,
            adaptive_ref: false,
            ref_memory_days: 180.0,
            expected_price: ref_price,
            self_share,
            self_compress_min: 0.8,
            own_daily: 0.0,
            front_load: if harvest { 0.3 } else { 0.0 },
            continuous_horizon: if continuous { 30.0 } else { 0.0 },
        },
        shops: Vec::new(),
        storers: Vec::new(),
    };
    mk.rural.set_own_consumption(1.0);
    mk.rural.stock = mk.rural.annual_capacity * mk.days_to_harvest() as f64 / 365.0;
    let tgt = daily_need * target_days / n_shop as f64;
    for i in 0..n_shop {
        let r = mk.rng.get("init");
        let stock = tgt * r.uniform(0.7, 1.3);
        let mid = ref_price * r.uniform(0.95, 1.05);
        mk.shops.push(Shop {
            id: format!("sk{i}"),
            cash: pymath::int(2.0 * tgt * ref_price) as f64,
            stock,
            target: tgt,
            capacity: 3.0 * tgt,
            margin,
            mid,
            avg_cost: mid * (1.0 - margin / 2.0),
            kappa: cfg.kappa,
            max_daily_move: 0.03,
            min_markup: 0.02,
            rent: max(1.0, pymath::int(0.001 * daily_need / n_shop as f64 * ref_price) as f64),
            price_rule: PriceRule::Cover,
            room_mult: 2.0,
            anchor: 0.0,
            memory_days: 365.0,
            memory_price: mid,
            withdraw_rate: 0.01,
            working_capital_mult: 3.0,
            target_cover_days: target_days,
            request_memory_days: 14.0,
            request_rate: daily_need / n_shop as f64,
            requests_today: 0.0,
            thin_guard: 0.05,
            normal_request: daily_need / n_shop as f64,
            prop_gain: 0.1,
            pricing: Pricing::Mid,
            cost_ref: 0.0,
            markup: 0.0,
            req_price: 0.0,
            share: 0.0,
            op_profit: 0.0,
            withdrawn: 0.0,
            marks: Vec::new(),
            stocked_out: false,
            unmet_frac: 0.0,
            peak_paid: 0.0,
            broke_months: 0,
            tag: 0,
        });
    }
    for i in 0..n_storers {
        let capital = pymath::int(daily_need * 60.0 * ref_price / n_storers as f64) as f64;
        let normal = ref_price * (1.0 - margin / 2.0);
        mk.storers.push(Storer {
            id: format!("st{i}"),
            cash: capital,
            stock: 0.0,
            capacity: daily_need * 120.0 / n_storers as f64,
            margin: 0.04,
            normal,
            normal_memory_days: 7300.0,
            fair: normal,
            fair_memory_days: 0.0,
            max_fair_mult: 3.0,
            carry_per_year: 0.1,
            season_pos: 0.5,
            withdraw_rate: 0.01,
            working_capital: capital,
            normal_mode: NormalMode::Median,
            normal_years: 7,
            season_sum: 0.0,
            season_n: 0,
            season_history: Vec::new(),
            shade: if cfg.liquidity { cfg.storer_shade } else { 0.0 },
        });
    }
    mk
}

impl World {
    /// Cold start (`D5World(cfg)`, `warm_start=False`).
    pub fn new(cfg: Config) -> Result<World, String> {
        cfg.validate()?;
        if cfg.warm_start {
            return Err("World::new is a cold start; use World::warm for warm_start".into());
        }
        if cfg.spinup_years > 0.0 && cfg.n_merchants.is_none() {
            return Err("spinup_years > 0 not ported (use a snapshot start)".into());
        }
        let port_list: Vec<Port> = cfg.ports.clone().unwrap_or_else(|| Port::all().to_vec());
        let good_list: Vec<Good> = cfg.goods.clone().unwrap_or_else(|| Good::ALL.to_vec());
        let pl = plan(&port_list, &good_list);
        let days = consts::shortest_days();

        // --- _build_markets
        let mut market_keys = Vec::new();
        let mut markets = Vec::new();
        for &p in &port_list {
            for &g in &good_list {
                let spec = goods5(g);
                let demand = pl.demand_l[p][g.idx()];
                let supply = pl.supply[p][g.idx()];
                let pool = pl.pool_target.iter().any(|x| x.0 == (p, g));
                if demand <= 0.0 && supply <= 0.0 && !pool {
                    continue;
                }
                let need = pymath::max_iter([demand, 0.05 * supply, 1.0]).unwrap();
                let surplus = if supply > 0.0 { 1.05 * supply / need } else { 0.0 };
                let harvest = spec.kind == GoodKind::Harvest && supply > 0.0;
                let continuous = spec.kind == GoodKind::Continuous && supply > 0.0;
                let salt = 100 + markets.len() as u64;
                markets.push(build_market(&cfg, p, g, need, surplus, harvest, continuous, salt));
                market_keys.push((p, g));
            }
        }
        let nm = markets.len();

        // --- _build_pools
        let mut pools = Vec::new();
        let mut normal_wage: PortMap<f64> = PortMap::default();
        for &p in &port_list {
            normal_wage.set(p, 0.0);
        }
        for &((p, g), out) in &pl.pool_target {
            let (inputs, labor) = recipe(g);
            let cost = pymath::sum(inputs.iter().map(|&(i, a)| a * goods5(i).reff)) + labor * WAGE;
            let input_days = 30.0;
            pools.push((
                (p, g),
                Pool {
                    good: g,
                    recipe: Recipe { inputs: inputs.to_vec(), labor },
                    capacity: out / 0.85,
                    cash: pymath::int(60.0 * out * cost) as f64,
                    util: 0.85,
                    output: out * 10.0,
                    inputs: inputs.iter().map(|&(i, a)| (i, a * out * input_days)).collect(),
                    input_days,
                    margin_target: 0.08,
                    util_speed: 0.05,
                    util_hist: Vec::new(),
                    divs: 0.0,
                    reservation: 0.0,
                },
            ));
        }
        for &((p, g), out) in &pl.pool_target {
            normal_wage[p] += out * recipe(g).1 * WAGE;
        }
        let wage_yday = normal_wage.clone();

        // --- _build_demand
        let sig = 2.0;
        let mut cls: PortMap<Vec<ClassDemand>> = PortMap::default();
        for &p in &port_list {
            let mut out = Vec::new();
            for (k, &yk) in pl.income_ref[p].iter().enumerate() {
                let sh = class_shares(p, k);
                let t = &CLASS_TEMPLATE[k];
                let w = t.wheat;
                let e: [f64; N_CATS] = std::array::from_fn(|c| sh[c] * yk);
                let a = [
                    w * pymath::pow(goods5(WHT).reff, sig - 1.0),
                    (1.0 - w) * pymath::pow(goods5(BRL).reff, sig - 1.0),
                ];
                let p_ref: [f64; N_CATS] =
                    std::array::from_fn(
                        |c| if c == 0 { 1.0 } else { goods5(crate::consts::CAT_GOODS[c].unwrap()).reff },
                    );
                let gamma: [f64; N_CATS] = std::array::from_fn(|c| t.subs[c] * e[c] / p_ref[c]);
                let s = yk - pymath::sum((0..N_CATS).map(|c| p_ref[c] * gamma[c]));
                let beta: [f64; N_CATS] = std::array::from_fn(|c| (e[c] - p_ref[c] * gamma[c]) / s);
                out.push(ClassDemand { name: CLASS_NAMES[k].to_string(), a, gamma, beta });
            }
            cls.set(p, out);
        }

        // --- _required_fleet
        let mut bulk_days = 0.0;
        for &g in &good_list {
            let spec = goods5(g);
            for &p in &port_list {
                let (srcs, deficit): (Vec<Port>, f64) = if spec.kind == GoodKind::Produced {
                    let srcs: Vec<Port> = map::get()
                        .pools
                        .iter()
                        .filter(|(k, served)| {
                            pl.pool_target.iter().any(|x| x.0 == *k) && k.1 == g && served.contains(&p)
                        })
                        .map(|(k, _)| k.0)
                        .collect();
                    if srcs.is_empty() || srcs[0] == p {
                        continue;
                    }
                    (srcs, pl.local_cons[p][g.idx()])
                } else {
                    let plan = map::get().supply_plan(g);
                    let srcs = port_list
                        .iter()
                        .copied()
                        .filter(|q| plan.is_some_and(|pl| pl.iter().any(|x| x.0 == *q && matches!(x.1, Sup::Exp(_)))))
                        .collect();
                    (srcs, max(0.0, pl.demand_l[p][g.idx()] - pl.supply[p][g.idx()]))
                };
                if deficit <= 0.0 || srcs.is_empty() || srcs.contains(&p) {
                    continue;
                }
                let d = pymath::min_iter(srcs.iter().map(|e| days[e.idx()][p.idx()])).unwrap();
                bulk_days += deficit * spec.bulk * (2.0 * d + 8.0);
            }
        }
        let required_fleet = bulk_days / cfg.capacity / 0.7;
        let n_init = cfg.n_merchants.unwrap_or_else(|| pymath::round(required_fleet));

        let corsair_z = corsair_norm();
        let tot = pymath::sum(port_list.iter().map(|&p| ports5(p).pop));
        let mut pool_m: PortMap<f64> = PortMap::default();
        let mut current = PortMap::default();
        let mut current_hist = PortMap::default();
        let mut loads = PortMap::default();
        let mut lender_book = PortMap::default();
        let mut news = PortMap::default();
        let mut port_buys = PortMap::default();
        let mut hn = PortMap::default();
        for &p in &port_list {
            current.set(p, market_keys.iter().map(|&(_, g)| (goods5(g).reff, -60)).collect::<Vec<_>>());
            current_hist.set(p, market_keys.iter().map(|&(_, g)| vec![goods5(g).reff]).collect::<Vec<_>>());
            pool_m.set(p, cfg.pool_mult * required_fleet * cfg.capital * ports5(p).pop / tot);
            loads.set(p, IdMap::default());
            lender_book.set(p, Vec::new());
            news.set(p, Vec::new());
            port_buys.set(p, Vec::new());
            hn.set(p, Vec::new());
        }
        let seed = cfg.seed;
        let core = Core {
            rng: RngStreams::new(seed),
            ledger: Ledger::default(),
            day: 0,
            date: Date::new(START_DATE.0, START_DATE.1, START_DATE.2),
            port_list: port_list.clone(),
            good_list,
            market_keys,
            markets,
            pools,
            income_ref: pl.income_ref,
            local_cons: pl.local_cons,
            demand_l: pl.demand_l,
            cls,
            normal_wage,
            wage_yday,
            n_init,
            corsair_x: vec![0.0; consts::n_regions()],
            corsair_z,
            corsair: vec![1.0 / corsair_z; consts::n_regions()],
            dep_log: Vec::new(),
            kapan_price: vec![None; nm],
            kapan_quote: vec![None; nm],
            kapan_bid: vec![None; nm],
            kapan_traded: vec![None; nm],
            kapan_today: vec![None; nm],
            kapan_volume: vec![None; nm],
            shop_exits: 0,
            shop_entries: 0,
            pool_investments: 0,
            current,
            current_hist,
            pool: pool_m,
            pending: Vec::new(),
            ship_list: Vec::new(),
            ship_px: 1.0,
            yard_next: 0.0,
            ship_log: Vec::new(),
            ships_lost: 0,
            prizes: 0,
            prizes_sold: 0,
            ship_buyers: Vec::new(),
            candidates: Vec::new(),
            track_known: false,
            trailing_median: 0.0,
            voy_log: Vec::new(),
            pop_roi: None,
            entry_log: Vec::new(),
            next_id: 0,
            entries: 0,
            exits: 0,
            bankruptcies: 0,
            reroutes: 0,
            contracts: 0,
            px_log: Vec::new(),
            rr_log: Vec::new(),
            courier_q: Vec::new(),
            debt_bankruptcies: 0,
            commissions: 0.0,
            ruin_days: Vec::new(),
            agg_hist: Vec::new(),
            public_agg: None,
            prev_val: IdMap::default(),
            gone_seen: 0,
            t0_day: 0,
            start_date: Date::new(START_DATE.0, START_DATE.1, START_DATE.2),
            pub_log: Vec::new(),
            cred_k: None,
            cred_log: Vec::new(),
            public_voy: 0.0,
            public_route: None,
            last_voyage: (0.0, 0.0),
            news,
            loads,
            harbor_news: hn.clone(),
            hnews_board: hn,
            port_buys,
            load_id: 0,
            news_id: 0,
            departures: Vec::new(),
            flows: Default::default(),
            loan_log: Vec::new(),
            fin_log: Vec::new(),
            loan_el: PortMap::default(),
            loan_el_all: None,
            route_stats: Default::default(),
            lender_book,
            lender_calib: PortMap::default(),
            rationed: 0,
            n_npc: Vec::new(),
            cfg,
            mkt: Vec::new(),
            days: Vec::new(),
            legs: Vec::new(),
            waiting_cache: Vec::new(),
            buying_cache: Vec::new(),
            ploss0: [Vec::new(), Vec::new()],
            sig0: 0.0,
            sig1: 0.0,
            diag: None,
        };
        let mut w = World { core, merchants: Vec::new(), gone: Vec::new() };
        w.core.rebuild();
        let c = &mut w.core;
        // retail competition: Lerner price, equal shares
        for mi in 0..c.markets.len() {
            let n = c.markets[mi].shops.len() as f64;
            for s in c.markets[mi].shops.iter_mut() {
                s.pricing = Pricing::Lerner;
                s.share = 1.0 / n;
                s.cost_ref = s.mid * (1.0 - s.margin / 2.0);
                s.req_price = s.mid;
            }
            c.set_markups(mi);
        }
        // merchants
        let ports = c.port_list.clone();
        for _ in 0..n_init {
            let i = c.rng.get("merchants_init").integers(0, ports.len() as i64) as usize;
            let m = c.new_merchant(ports[i], "merchants_init");
            w.merchants.push(m);
        }
        if w.core.cfg.ship_market {
            w.init_ships();
        }
        if w.core.cfg.add_bots {
            for informed in [false, true] {
                let mut b = w.core.new_merchant(map::get().home, "merchants_init");
                b.is_player = true;
                b.informed = informed;
                w.merchants.push(b);
            }
        }
        let (mt, gt) = (w.money_total(), w.goods_totals());
        w.core.ledger.money_start = mt;
        w.core.ledger.goods_start = gt.iter().map(|&(g, v)| (g.name().to_string(), v)).collect();
        Ok(w)
    }

    /// `_init_ships`: ages uniformly distributed.
    pub fn init_ships(&mut self) {
        let c = &mut self.core;
        let l = c.cfg.ship_life * 365.0;
        let day = c.day;
        let r = c.rng.get("ships_init");
        for m in self.merchants.iter_mut() {
            if !m.is_player && m.ship.is_none() {
                m.ship = Some(day - pymath::int(r.uniform(0.0, l)));
            }
        }
    }
}
