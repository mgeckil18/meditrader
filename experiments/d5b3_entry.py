"""Experiment D5b3: stable start (spin-up) and opportunity-driven entry.
Run (repo root): python3 experiments/d5b3_entry.py YEARS   e.g. 10
Report (Turkish): docs/experiments/D5b3.md

(Original notes in Turkish below.)

Deney D5b3: kararlı başlangıç ve fırsata bağlı giriş (K-020).

Soru: D5b2'de ısınma (14 tüccarla başlangıç, ilk yıl giriş yok) kıtlık patlamaları üretti; eski giriş kuralı
(gerçekleşen medyan getiri) yavaş, getiriler yılda %33 (rant). Kullanıcı: başlangıç kararlıya yakın olsun; giriş
halk sermayesine ve genel bilinen fırsata bağlı olsun; liman başına havuz; colleganza da olsun.
Kurulumlar (taban = D5b2'nin önerilen yapısı GBSL·imp):
  taban   eski giriş
  SU      + spin-up (3 yıl ön koşu)
  O       fırsata bağlı giriş (liman havuzu, liman konuşması, sicil + sefer kârı / ufuk)
  OC      O + colleganza
  OCS     OC + spin-up
v1 (budget_bids=False her yerde) → out/d5b3/*_v1.*; v2: bütçeli teklif.
Kullanım: python3 experiments/d5b3_entry.py 10    Rapor: docs/experiments/D5b3.md
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5b_diversity import BASE, metrics  # noqa: E402
from d5b2_factorial import SETUPS as F  # noqa: E402
from sim.world5 import D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b3"
OUT.mkdir(parents=True, exist_ok=True)
IMP = dict(F["GBSL"], forward_fund=False)
SETUPS = {
    "taban-eski": dict(IMP, budget_bids=False),   # v1 davranışı (bütçesiz dükkân teklifi)
    "taban": IMP,
    "SU": dict(IMP, spinup_years=3),
    "O": dict(IMP, entry_rule="opportunity"),
    "OC": dict(IMP, entry_rule="opportunity", colleganza=True),
    "OCS": dict(IMP, entry_rule="opportunity", colleganza=True, spinup_years=3),
}
SEEDS = range(5)


def run(args):
    name, seed = args
    w = D5World(D5Config(seed=seed, **BASE, **SETUPS[name]))
    r = w.run()
    out = metrics(w, r)
    n = np.array(r["n_npc"], dtype=float)
    out["fleet_start"] = float(n[0])
    out["fleet_y1"] = float(np.mean(n[:365]))
    out["fleet_last"] = float(np.mean(n[-1825:]))
    out["fleet_cv_last"] = float(np.std(n[-1825:]) / max(np.mean(n[-1825:]), 1))
    tr = np.array(r["track"], dtype=float)[-1825:]
    out["track_last_mean"] = float(np.mean(tr))
    out["track_last_sd"] = float(np.std(tr))
    out["entries"], out["exits"], out["bankruptcies_n"] = r["entries"], r["exits"], r["bankruptcies"]
    out["colleg_n"] = w.colleg_n
    out["colleg_ret"] = (w.colleg_out / w.colleg_in - 1) if w.colleg_in else float("nan")
    out["pool_end"] = float(sum(w.pool.values()) / w.cfg.capital)
    ms = [m for m in r["merchants"] if not m.is_player]
    out["trapped_n_end"] = sum(1 for m in ms if m.state == "selling" and m.wait > 180)
    yearly = [float(np.mean(np.array(r["track"], dtype=float)[365 * y:365 * (y + 1)])) for y in range(10)]
    return name, seed, out, yearly


def main():
    with Pool(min(20, len(SETUPS) * len(SEEDS))) as pool:
        res = pool.map(run, [(n, s) for n in SETUPS for s in SEEDS])
    summary = {}
    for name in SETUPS:
        rows = [o for n, s, o, y in res if n == name]
        agg = {k: f"{sum(x[k] for x in rows)}/{len(rows)}" for k in ("exploded", "explode_last", "dearth", "runaway")}
        agg["trapped_seeds"] = [x["trapped_n_end"] for x in rows]
        for k in rows[0]:
            if k not in ("exploded", "explode_last", "dearth", "runaway") and all(k in x for x in rows):
                agg[k] = float(np.nanmedian([x[k] for x in rows]))
        agg["track_yearly_seed0"] = [round(v, 3) for n, s, o, y in res if n == name and s == 0 for v in y]
        summary[name] = agg
        print(name, json.dumps(agg, ensure_ascii=False), flush=True)
    a = D5World(D5Config(seed=7, **dict(BASE, years=2), **SETUPS["OCS"])).run()
    b = D5World(D5Config(seed=7, **dict(BASE, years=2), **SETUPS["OCS"])).run()
    summary["determinism_same_seed"] = bool(np.array_equal(a["VEN_WHT_kapan"], b["VEN_WHT_kapan"]))
    print("determinism", summary["determinism_same_seed"])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        SEEDS = range(int(sys.argv[1]))
    main()
