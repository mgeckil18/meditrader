//! Day trace: start from a Python dump, run N days, write a digest at the end of each day (same format as `state_io.py trace`).
//! Usage: trace STATE.json DAYS OUT.jsonl [days with full dumps, comma separated]
//!        trace cold:CFG.json DAYS OUT.jsonl [...]   (cold start from a config)

use std::io::Write;

use medi_core::digest::digest;
use medi_core::world::World;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() < 4 {
        eprintln!("usage: trace STATE.json DAYS OUT.jsonl [DAYS_WITH_DUMPS]");
        std::process::exit(2);
    }
    let days: usize = a[2].parse().expect("days");
    let full: Vec<usize> = a.get(4).map(|s| s.split(',').map(|x| x.parse().unwrap()).collect()).unwrap_or_default();
    // "cold:CFG.json" = cold start from a config; otherwise a full state dump
    let src = std::fs::read_to_string(a[1].strip_prefix("cold:").unwrap_or(&a[1])).expect("cannot read file");
    let made = if a[1].starts_with("cold:") {
        medi_core::config::Config::from_json(&src).and_then(World::new)
    } else {
        World::from_json(&src)
    };
    let mut w = made.unwrap_or_else(|e| {
        eprintln!("{e}");
        std::process::exit(1)
    });
    let mut f = std::io::BufWriter::new(std::fs::File::create(&a[3]).unwrap());
    let write = |w: &World, i: usize, f: &mut std::io::BufWriter<std::fs::File>| {
        let v = w.to_value();
        writeln!(f, "{}", serde_json::json!({"day": w.core.day, "digest": digest(&v)})).unwrap();
        if full.contains(&i) {
            std::fs::write(format!("{}.day{}.json", a[3], i), serde_json::to_string(&v).unwrap()).unwrap();
        }
    };
    write(&w, 0, &mut f);
    let frm: usize = std::env::var("TRACE_FROM").ok().and_then(|x| x.parse().ok()).unwrap_or(0);
    for i in 0..days {
        w.step();
        if i + 1 < frm && !full.contains(&(i + 1)) {
            continue;
        }
        write(&w, i + 1, &mut f);
    }
}
