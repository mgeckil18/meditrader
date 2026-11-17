//! Speed benchmark: start from a Python state dump, run N days (no digests), report time per day.
//! Usage: bench STATE.json DAYS
use medi_core::world::World;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let days: usize = a[2].parse().expect("days");
    let mut w = World::from_json(&std::fs::read_to_string(&a[1]).expect("cannot read file")).expect("state");
    let t = std::time::Instant::now();
    for _ in 0..days {
        w.step();
    }
    let s = t.elapsed().as_secs_f64();
    let mut r = medi_core::prof::report();
    r.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    for (n, t, _) in r {
        println!("  {n:28} {:6.1}%  {:.3} ms/day", 100.0 * t / s, 1e3 * t / days as f64);
    }
    println!(
        "{days} days: {s:.3} s, {:.3} ms/day, {:.2} s/year, merchants {}",
        1e3 * s / days as f64,
        365.0 * s / days as f64,
        w.merchants.len()
    );
}
