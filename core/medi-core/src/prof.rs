//! Simple phase timer (for when perf is unavailable). Enabled with `MEDI_PROF=1`; when off it costs one branch.
use std::cell::RefCell;
use std::time::Instant;

thread_local! {
    static ON: bool = std::env::var("MEDI_PROF").is_ok();
    static ACC: RefCell<Vec<(&'static str, f64, u64)>> = const { RefCell::new(Vec::new()) };
}

pub struct Lap(Option<Instant>);

impl Lap {
    pub fn start() -> Lap {
        Lap(if ON.with(|x| *x) { Some(Instant::now()) } else { None })
    }
    /// Adds the time since the last mark to phase `name`.
    pub fn mark(&mut self, name: &'static str) {
        if let Some(t) = self.0 {
            let now = Instant::now();
            let dt = (now - t).as_secs_f64();
            ACC.with(|a| {
                let mut a = a.borrow_mut();
                match a.iter_mut().find(|x| x.0 == name) {
                    Some(x) => {
                        x.1 += dt;
                        x.2 += 1
                    }
                    None => a.push((name, dt, 1)),
                }
            });
            self.0 = Some(now);
        }
    }
}

pub fn report() -> Vec<(&'static str, f64, u64)> {
    ACC.with(|a| a.borrow().clone())
}
