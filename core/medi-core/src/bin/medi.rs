//! Experiment runner.
//!   medi snapshot CFG.json K STATE.json         build a warm-start snapshot (`build_snapshot`); meta goes to .meta.json
//!   medi run CFG.json NAME OUT.json [STATE.json] run with diagnostics; warm_start configs need a snapshot
//! CFG.json: output of `python3 core/tools/state_io.py cfg SETUP SEED CFG.json YEARS` (D5Config, Python field names).

use medi_core::config::Config;
use medi_core::world::World;

fn die(msg: impl std::fmt::Display) -> ! {
    eprintln!("medi: {msg}");
    std::process::exit(1)
}

fn read(p: &str) -> String {
    std::fs::read_to_string(p).unwrap_or_else(|e| die(format!("{p}: {e}")))
}

fn write_atomic(p: &str, s: &str) {
    let tmp = format!("{p}.tmp");
    std::fs::write(&tmp, s).unwrap_or_else(|e| die(format!("{tmp}: {e}")));
    std::fs::rename(&tmp, p).unwrap_or_else(|e| die(format!("{p}: {e}")));
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let cmd = a.get(1).map(String::as_str).unwrap_or("");
    let cfg = || -> Config { Config::from_json(&read(&a[2])).unwrap_or_else(|e| die(e)) };
    match cmd {
        "snapshot" if a.len() == 5 => {
            let k: i64 = a[3].parse().unwrap_or_else(|_| die("K"));
            let (state, meta) = World::build_snapshot(&cfg(), k).unwrap_or_else(|e| die(e));
            let out = &a[4];
            let meta_path = out.strip_suffix(".json").unwrap_or(out).to_string() + ".meta.json";
            write_atomic(&meta_path, &meta.to_string());
            write_atomic(out, &state.to_string());
            println!("{meta}");
        }
        "run" if a.len() == 5 || a.len() == 6 => {
            let cfg = cfg();
            let mut w = if cfg.warm_start {
                let snap = a.get(5).unwrap_or_else(|| die("warm_start: a snapshot file is required"));
                World::warm(cfg, &read(snap))
            } else {
                World::new(cfg)
            }
            .unwrap_or_else(|e| die(e));
            w.enable_diag();
            w.run();
            write_atomic(&a[4], &w.diag_output(&a[3]).to_string());
            // diagnostic: if MEDI_STATE=path is set, the full end-of-run state is written there
            if let Ok(sp) = std::env::var("MEDI_STATE") {
                write_atomic(&sp, &w.to_value().to_string());
            }
            println!("{} {} {}", a[3], w.core.cfg.seed, w.core.entries);
        }
        _ => die("usage: medi snapshot CFG.json K STATE.json | medi run CFG.json NAME OUT.json [STATE.json]"),
    }
}
