# Determinism and the bit-exact Rust port

## Why determinism
Everything random in the simulation (storms, corsairs, harvests, rumours) comes from seeded generators, one stream per subsystem. The same seed and the same inputs give the same world. This lets an economic failure in year 37 be replayed exactly, makes save-scumming pointless, and keeps a lockstep multiplayer option open ([determinism](../../docs/design/determinism.md), Turkish).

## Why bit-exact, not "statistically similar"
The economy was designed in Python, one experiment at a time. Moving to Rust for speed raised a question: how do you know the new engine is the same model? Comparing averages over seeds hides small bugs. An agent-based market amplifies them: a 1-ulp difference on day 107 changes a shopkeeper's price, which changes a merchant's choice, which changes the world. So the target was: **from the same starting state, every field of the world state, including the internal state of every RNG stream, is identical on every day.**

## How

| Problem | Solution | Where |
|---|---|---|
| Python's `sum()` is compensated (Neumaier, 3.12+); NumPy reductions are pairwise | Reimplemented exactly | `pymath.rs` |
| `round()` is banker's rounding; `%` and `//` follow the divisor's sign | Reimplemented exactly | `pymath.rs` |
| `exp`, `log`, `pow`, `erf` differ between libm implementations | Call glibc `libm` like CPython does | `pymath.rs` |
| NumPy's `PCG64`, `SeedSequence` and distribution algorithms | Ported: ziggurat normal, Lemire integers, PTRS Poisson, Marsaglia-Tsang gamma/beta, shuffle | `rng/` |
| Python dicts keep insertion order | `IndexMap`; `shift_remove` on delete | throughout |
| Comparing two engines | Canonical JSON state dump on both sides, plus a per-field SHA-1 digest every day; the first diverging day and field are found from the digests | `core/tools/state_io.py`, `src/digest.rs`, `src/bin/trace.rs` |

## Tests
- `cargo test`: [`core/medi-core/tests/numeric.rs`](../../core/medi-core/tests/numeric.rs) checks `pymath` against NumPy 2.4.4 fixtures: 9,327 cases (sums, means, stds, medians, rounds, mods, floor divisions). It checks the RNG against 28 seeded streams with 11,200 draws across 9 methods. Each stream's internal state after seeding is compared as well.
- **Parity check** ([`core/tools/parity_check.py`](../../core/tools/parity_check.py)): cold-starts the Python engine and the Rust core from the same config, dumps the full state every 10 days, and requires identical digests. Fields added to Rust after the freeze must stay at their defaults and are then dropped. Runs in CI on every push (about 2 s). Exit code 0 means identical.
- **Regression for new mechanisms:** with all new flags off, a Rust run must reproduce the previous Rust output exactly (for example PF seed 0: fleet, reroutes, losses, departure log, price log).

## Results ([rust-core §4](../../docs/design/rust-core.md), Turkish)
- Bit-identical every day, every field: VRS setup 400 and 1,100 days, full-map F setup 150-200 days, from snapshots and from cold start.
- End to end: a full earlier experiment (D5b3j: 2 setups x 2 variants x 10 seeds x 10 years = 40 runs) was rerun in Rust. Output files were identical to Python's. The one exception, a log column, came from a log-only fix made in Python after those runs.
- Speed, single core, same machine:

| Setup | Python | Rust | Speed-up |
|---|---|---|---|
| VRS (3 ports, ~75 merchants) | 3.7 s / sim-year | 0.12-0.14 s | ~30x |
| F (full classic map, ~120-170 merchants) | 35.8 s / sim-year | 0.58-0.79 s | ~45-60x |

A 10-year full-map run went from ~6 minutes to 6-9 seconds. Every optimisation (bit sets for "heard" sets, FxHash, per-decision caches, precomputed constant powers) was re-verified with the day trace.

## Bugs that only bit-exactness could find
- **LLVM turns `pow(x, -1.0)` into `1.0 / x`.** glibc `pow` is not always correctly rounded, so the result differed by 1 ulp. That showed up on day 107 in one shopkeeper's profit field. Fix: `black_box` hides the arguments from the optimiser; constant powers are precomputed so this costs nothing.
- **Shop ids were not unique** after a snapshot rebase. Python removed shops by object identity, Rust by id string, so Rust removed the wrong shop in year 9 of one seed. Fix: a temporary tag inside the function.
- **An RNG stream is created unconditionally** on day 1 of a cold start; its existence is part of the state, so Rust does the same.
- **`serde(flatten)` cannot read integer-keyed maps** (JSON keys are strings); the world struct is merged by hand.
- **FMA breaks parity**, so `target-cpu=native` is forbidden in [`core/Cargo.toml`](../../core/Cargo.toml).

## Reproduce
```
cargo test --release --manifest-path core/Cargo.toml
cargo build --release --manifest-path core/Cargo.toml
pip install -r requirements.txt          # NumPy is pinned: fixtures and parity depend on its exact algorithms
python3 core/tools/parity_check.py                       # VRS-B-R1-O3, seed 0, 60 days
python3 core/tools/parity_check.py F-B-R1-O3 1 200 50    # full map, 200 days
```
Requires Python 3.12+ (for `sum()` semantics).
