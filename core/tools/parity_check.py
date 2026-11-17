"""Bit-exact parity check: Python reference engine (sim/world5.py) vs Rust core (core/medi-core).

Both engines start from the same cold-start configuration, run N days, and write full canonical
state dumps at fixed days. The dumps are compared field by field.

Rust has mechanisms added after the Python engine was frozen (K-033). Every one sits behind a
config flag that is off here, so their state fields must stay at their default (empty / zero / false).
The check asserts that, drops those fields, and requires the rest to be identical, bit for bit
(through the canonical per-field hash that the day trace uses).

Usage (from repo root, after `cargo build --release` in core/):
    python3 core/tools/parity_check.py [SETUP] [SEED] [DAYS] [EVERY]
Defaults: VRS-B-R1-O3 0 60 10. Exit code 0 = identical, 1 = divergence.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "core" / "tools"))
TRACE = ROOT / "core" / "target" / "release" / "trace"
STATE_IO = ROOT / "core" / "tools" / "state_io.py"

# Top-level keys that exist only in the Rust state, and merchant fields added after the freeze.
RUST_ONLY_TOP = {"prizes", "prizes_sold", "contracts", "courier_q"}
RUST_ONLY_MERCHANT = {"loaded", "unload_left", "qty_prev", "fill_ema", "packet_all",
                      "hold", "considered", "fill_val", "pre_land", "commit", "contract"}
# Rust-only bookkeeping that is always written but only read by flagged mechanisms (cargo spoilage,
# per-lot accounting). Dropped without a default check.
DEP_LOG_PY_COLS = 6
RUST_BOOKKEEPING = {"cargo_day", "lot_flow", "rr"}  # rr = reroute diagnostic log (also top-level rr_log)


def digest(tree):
    from state_io import digest as d
    return d(tree)


def is_default(v):
    return v in (None, False, 0, 0.0, -1, [], {}, "")


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)


def main():
    setup = sys.argv[1] if len(sys.argv) > 1 else "VRS-B-R1-O3"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    every = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    at = ",".join(str(d) for d in range(0, days + 1, every))
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        run([sys.executable, STATE_IO, "cfg", f"{setup}@cold", seed, t / "cfg.json"])
        run([sys.executable, STATE_IO, "trace", f"{setup}@cold", seed, days, t / "py.jsonl", at])
        run([TRACE, f"cold:{t / 'cfg.json'}", days, t / "rs.jsonl", at])
        bad = 0
        for d in at.split(","):
            py = json.loads((t / f"py.jsonl.day{d}.json").read_text())
            rs = json.loads((t / f"rs.jsonl.day{d}.json").read_text())
            for k in RUST_ONLY_TOP:
                v = rs.pop(k, None)
                if not is_default(v):
                    print(f"day {d}: Rust-only field {k} not at default: {str(v)[:80]}")
                    bad += 1
            rs.pop("rr_log", None)
            for i, m in enumerate(rs.get("merchants", []) + [g[0] for g in rs.get("gone", [])]):
                for k in RUST_BOOKKEEPING:
                    m.pop(k, None)
                for k in RUST_ONLY_MERCHANT:
                    v = m.pop(k, None)
                    if not is_default(v):
                        print(f"day {d}: merchants[{i}].{k} not at default: {str(v)[:80]}")
                        bad += 1
            # dep_log rows gained diagnostic columns in Rust (loaded?, age, port days, voyage days)
            if "dep_log" in rs:
                rs["dep_log"] = [r[:DEP_LOG_PY_COLS] for r in rs["dep_log"]]
            # canonical hash per field (state_io.digest: same serialisation the day trace uses)
            hp, hr = digest(py), digest(rs)
            keys = set(hp) | set(hr)
            diff = sorted(k for k in keys if hp.get(k) != hr.get(k))
            if diff:
                print(f"day {d}: differing keys {diff[:10]}")
                bad += 1
            else:
                print(f"day {d}: identical ({len(keys)} top-level fields)")
        print("PARITY OK" if bad == 0 else "PARITY FAILED")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
