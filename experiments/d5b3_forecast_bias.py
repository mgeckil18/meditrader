"""Experiment D5b3 (diagnostic): how biased are merchants' voyage expectations?
Run (repo root): python3 experiments/d5b3_forecast_bias.py
Report (Turkish): docs/experiments/D5b3.md

(Original notes in Turkish below.)

D5b3 teşhis: tüccarın sefer beklentisi ne kadar yanlı? Kalkışta beklenen birim gelir (plan) ile sefer
bitince gerçekleşen birim gelir karşılaştırılır. Kullanım: python3 experiments/d5b3_forecast_bias.py
Rapor: docs/experiments/D5b3.md
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5b_diversity import BASE  # noqa: E402
from d5b2_factorial import SETUPS as F  # noqa: E402
from sim.world5 import D5Config, D5World, GOODS5, FREIGHT_PER_BULK_DAY  # noqa: E402

IMP = dict(F["GBSL"], forward_fund=False)
SETUPS = {"GBSL·imp (eski giriş)": IMP,
          "fırsat + colleganza": dict(IMP, entry_rule="opportunity", colleganza=True)}


def run(args):
    name, seed = args
    w = D5World(D5Config(seed=seed, **BASE, **SETUPS[name]))
    w.run()
    rows = []
    for (d0, d1, g, o, d, q, exp_net, unit_cost, realized, lvl, sold_at, *_) in w.voy_log:
        exp_gross = exp_net + FREIGHT_PER_BULK_DAY * GOODS5[g].bulk * w._voyage(o, d)
        rows.append((d0 / 365, g, o, d, sold_at, lvl, exp_gross / unit_cost - 1, realized / unit_cost - 1, d1 - d0))
    return name, seed, rows


def summarize(rows):
    exp = np.array([r[6] for r in rows]); rea = np.array([r[7] for r in rows])
    return {"n": len(rows), "exp_margin_med": float(np.median(exp)), "real_margin_med": float(np.median(rea)),
            "real_margin_mean": float(np.mean(rea)), "frac_loss": float(np.mean(rea < 0)),
            "frac_rerouted": float(np.mean([r[3] != r[4] for r in rows])),
            "days_med": float(np.median([r[8] for r in rows]))}


if __name__ == "__main__":
    with Pool(8) as pool:
        res = pool.map(run, [(n, s) for n in SETUPS for s in range(4)])
    out = {}
    for name in SETUPS:
        rows = [r for n, s, rr in res if n == name for r in rr if r[0] >= 5]       # son 5 yıl
        out[name] = {"all": summarize(rows)}
        for key, f in (("level", lambda r: r[5]), ("good", lambda r: r[1]), ("route", lambda r: f"{r[2]}>{r[3]}")):
            for k in sorted({f(r) for r in rows}):
                sub = [r for r in rows if f(r) == k]
                if len(sub) >= 20:
                    out[name][f"{key}={k}"] = summarize(sub)
        print(name, json.dumps(out[name], ensure_ascii=False, indent=1))
    p = ROOT / "experiments" / "out" / "d5b3"
    p.mkdir(parents=True, exist_ok=True)
    (p / "forecast_bias.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
