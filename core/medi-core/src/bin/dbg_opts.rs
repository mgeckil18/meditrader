//! Diagnostic: components of the option calculation for merchants waiting in one port of a snapshot (M1 review).
//!   dbg_opts CFG.json SNAP.json PORT
use medi_core::config::Config;
use medi_core::consts::Port;
use medi_core::world::World;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let cfg = Config::from_json(&std::fs::read_to_string(&a[1]).unwrap()).unwrap();
    let w = World::warm(cfg, &std::fs::read_to_string(&a[2]).unwrap()).unwrap();
    let p = Port::by_name(&a[3]).unwrap();
    let c = &w.core;
    let ms: Vec<_> = w.merchants.iter().filter(|m| m.loc == p && !m.is_player).take(3).collect();
    for m in ms {
        println!(
            "m {} state {:?} cash {:.0} plan {:?} known_loads {}",
            m.id,
            m.state,
            m.cash,
            m.plan,
            m.known_loads.len()
        );
        let mut ctx = c.ctx();
        for (mi, g) in c.markets_at(p) {
            let ask = c.best_ask(mi);
            for &d in &c.port_list {
                if d == p {
                    continue;
                }
                let Some(dmi) = c.mi(d, g) else { continue };
                let days = c.voyage(p, d);
                let e0 = c.expect_fwd_c(m, dmi, days, &mut ctx);
                let depth0 = c.cfg.depth_days * c.demand(d, g);
                if e0 > 1.3 * ask {
                    println!(
                        "  {:?}->{:?} ask {:.1} e0 {:.1} depth0 {:.0} obs {:?} kapan {:?}",
                        g, d, ask, e0, depth0, m.obs[dmi], c.kapan_price[dmi]
                    );
                }
            }
        }
        let opts = c.options(m, p, None);
        println!("  opts {}", opts.len());
    }
}
