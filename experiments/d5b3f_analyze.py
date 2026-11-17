"""Experiment D5b3f (analysis): decomposes entry beliefs, realised returns of entry cohorts, stay decisions.
Run (repo root): python3 experiments/d5b3f_analyze.py   (reads experiments/out/d5b3f/)
Report (Turkish): docs/experiments/D5b3f.md

(Original notes in Turkish below.)

D5b3f çözümleme: out/d5b3f/*.json → giriş inancının ayrıştırması, giren kuşağının gerçekleşen getirisi, kalma kararı."""
import json
import pathlib
import statistics as st
import sys

OUT = pathlib.Path(__file__).resolve().parents[1] / "experiments" / "out" / __import__("os").environ.get("DIAG_OUT", "d5b3f")


def med(v):
    v = [x for x in v if x is not None]
    return round(st.median(v), 4) if v else None


def mean(v):
    v = [x for x in v if x is not None]
    return round(sum(v) / len(v), 4) if v else None


def summarize(name):
    runs = [json.load(open(f)) for f in sorted(OUT.glob(f"{name}_*.json"))]
    if not runs:
        return None
    S = {}
    for r in runs:
        r.setdefault("t0", 0)
    yrs = [(max(x["day"] for x in r["elog"]) - r["t0"]) / 365 for r in runs]
    S["seeds"] = len(runs)
    S["n_markets"] = runs[0]["n_markets"]
    S["entries_per_yr"] = mean([r["entries"] / y for r, y in zip(runs, yrs)])
    S["exits_per_yr"] = mean([r["exits"] / y for r, y in zip(runs, yrs)])
    S["bankr_per_yr"] = mean([r["bankruptcies"] / y for r, y in zip(runs, yrs)])
    E = [x for r in runs for x in r["elog"] if x["track"] is not None]
    S["track"] = mean([x["track"] for x in E])
    S["bonus"] = mean([x["belief"] - x["track"] for x in E])            # sicilin üstüne fırsattan gelen pay
    S["public_voy"] = med([x["voy"] for x in E])
    S["alt"] = mean([x["alt"] for x in E])
    S["ruin"] = mean([x["ruin"] for x in E])
    S["conv"] = mean([x["conv"] for x in E])
    S["pool_units_port"] = med([x["pool_units"] for x in E])
    S["frac_months_belief_gt_alt"] = mean([1.0 if x["belief"] > x["alt"] else 0.0 for x in E])
    S["frac_months_track_gt_alt"] = mean([1.0 if x["track"] > x["alt"] else 0.0 for x in E])
    K = [x for x in E if x["k"] > 0]
    S["entry_months"] = len(K)
    S["belief_at_entry"] = med([x["belief"] for x in K])
    S["track_at_entry"] = med([x["track"] for x in K])
    S["voy_at_entry"] = med([x["voy"] for x in K])
    S["entries_with_track_lt_alt"] = round(sum(x["k"] for x in K if x["track"] < x["alt"]) / max(sum(x["k"] for x in K), 1), 3)
    S["n_here_at_entry"] = med([x["n_here"] for x in K])
    C = [c for r in runs for c in r["cohort"] if c["life"] >= 180]
    S["cohort_n"] = len(C)
    S["cohort_belief"] = med([c["belief"] for c in C])
    S["cohort_ret_median"] = med([c["ret"] for c in C])
    S["cohort_ret_mean"] = mean([c["ret"] for c in C])
    S["cohort_broke"] = mean([1.0 if c["broke"] else 0.0 for c in C])
    L = [x for r in runs for x in r["slog"]]
    S["stay_checks"] = len(L)
    S["stay_track"] = mean([x["track"] for x in L])
    S["stay_voy"] = med([x["voy"] for x in L])
    S["stay_kept_approx"] = mean([1.0 if x["belief"] > x["bar"] + x["ruin"] else 0.0 for x in L])
    if "fleet" in runs[0]:
        S["n_init"] = mean([r["n_init"] for r in runs])
        S["fleet_y1"] = mean([r["fleet"][min(12, len(r["fleet"]) - 1)] for r in runs])
        S["fleet_end"] = mean([sum(r["fleet"][-12:]) / 12 for r in runs])
        S["agg"] = mean([r["agg"] for r in runs])
        S["entries_y1"] = mean([sum(x["k"] for x in r["elog"] if x["day"] < r["t0"] + 365) for r in runs])
    X = [x for r in runs for x in r.get("xlog", [])]
    if X:
        S["exit_checks_per_yr"] = mean([len(r["xlog"]) / y for r, y in zip(runs, yrs)])
        S["exit_retire_frac"] = mean([1.0 if x["retire"] else 0.0 for x in X])
        S["exit_e_median"] = med([x["e"] for x in X])
    if "fleet" in runs[0]:
        f = [x for r in runs for x in r["fleet"]]
        S["fleet_peak_trough"] = mean([max(r["fleet"]) / max(min(r["fleet"]), 1) for r in runs])
        S["fleet_cv"] = mean([float(__import__("statistics").pstdev(r["fleet"]) / max(__import__("statistics").mean(r["fleet"]), 1)) for r in runs])
    S["voy_bias"] = mean([r["voy_bias"] for r in runs])               # (beklenen − gerçekleşen) net / maliyet
    return S


if __name__ == "__main__":
    names = sys.argv[1].split(",") if len(sys.argv) > 1 else ["VRS", "F"]
    res = {n: summarize(n) for n in names}
    keys = [k for k in next(v for v in res.values() if v)]
    print(f"{'':28s}" + "".join(f"{n:>12s}" for n in names))
    for k in keys:
        print(f"{k:28s}" + "".join(f"{str(res[n][k]) if res[n] else '-':>12s}" for n in names))
    json.dump(res, open(OUT / f"summary_{'_'.join(names)}.json", "w"), indent=1)
