"""Experiment D5b3d (diagnostic T1): gross return estimate vs lifetime median return.
Run (repo root): python3 experiments/d5b3d_return_gap.py [SETUP] [N_SEEDS]
Report (Turkish): docs/experiments/D5b3d.md

(Original notes in Turkish below.)

D5b3d teşhis T1: brüt getiri tahmini (~%12-27) ile ömür boyu getiri medyanı (~%0) neden bu kadar farklı?
Tüccar bazında: kâr = son değer + temettü − başlangıç sermayesi; sermaye-yıl ağırlıklı toplam getiri, ortalama, medyan.
Ayrıca batan kargoların değeri (sefer kaydına girmiyor) ve kısa ömürlüler.
Kullanım: python3 experiments/d5b3d_return_gap.py [kurulum] [seed sayısı]   Çıktı: out/d5b3d/return_gap.json
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5b_diversity import BASE, lifetime_return  # noqa: E402
from d5b3c_finance import SETUPS as C_SETUPS  # noqa: E402
from d5b3d_lender_entry import SETUPS as D_SETUPS  # noqa: E402
from sim.world5 import D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b3d"
NAME = "D'"


def run(args):
    name, seed = args                          # kurulum adı argüman: forkserver işçileri modülü yeniden yükler
    w = D5World(D5Config(seed=seed, **BASE, **{**C_SETUPS, **D_SETUPS}[name]))
    r = w.run()
    end = w.day
    people = [(m, end, m.net_worth()) for m in r["merchants"] if not m.is_player] + [g for g in r["gone"] if not g[0].is_player]
    rows = []
    for m, day, v in people:
        yrs = max((day - m.born_day) / 365.0, 1 / 365)
        rows.append(dict(ret=lifetime_return(m, day, v), pnl=v + m.divs - m.start_capital, cap_yrs=m.start_capital * yrs,
                         yrs=yrs, lvl=m.level, alive=day == end, born=m.born_day, divs=m.divs, start=m.start_capital))
    led = w.ledger
    return seed, rows, {k: float(v) for k, v in led.money_out.items()}, {k: float(v) for k, v in led.money_in.items()}


def main(n):
    with Pool(n) as pool:
        res = pool.map(run, [(NAME, s) for s in range(n)])
    rows = [x for _, rs, _, _ in res for x in rs]
    a = lambda k, sub=rows: np.array([x[k] for x in sub], dtype=float)  # noqa: E731
    out = {"n_people": len(rows),
           "agg_return": float(a("pnl").sum() / a("cap_yrs").sum()),
           "mean_lifetime": float(a("ret").mean()), "median_lifetime": float(np.median(a("ret"))),
           "neg_share": float((a("ret") < 0).mean()),
           "median_years": float(np.median(a("yrs")))}
    for lbl, sub in (("alive", [x for x in rows if x["alive"]]), ("gone", [x for x in rows if not x["alive"]]),
                     ("short_<1y", [x for x in rows if x["yrs"] < 1]), ("long_>=3y", [x for x in rows if x["yrs"] >= 3])):
        if sub:
            out[lbl] = {"n": len(sub), "agg": float(a("pnl", sub).sum() / a("cap_yrs", sub).sum()),
                        "median": float(np.median(a("ret", sub))), "pnl_share": float(a("pnl", sub).sum() / max(abs(a("pnl").sum()), 1))}
    for L in (0, 1, 2):
        sub = [x for x in rows if x["lvl"] == L]
        out[f"lvl{L}"] = {"n": len(sub), "agg": float(a("pnl", sub).sum() / a("cap_yrs", sub).sum()), "median": float(np.median(a("ret", sub)))}
    # Kâr kimde toplanıyor: en iyi %10'un kâr payı
    pnl = np.sort(a("pnl"))[::-1]
    out["top10_pnl_share"] = float(pnl[: max(1, len(pnl) // 10)].sum() / pnl[pnl > 0].sum())
    out["ledger_sinks"] = res[0][2]
    out["ledger_sources"] = res[0][3]
    (OUT / f"return_gap_{NAME.replace(chr(39), 'p')}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        NAME = sys.argv[1]
    main(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
