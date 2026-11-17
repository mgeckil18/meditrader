"""Experiment D5a3: price discovery in a market with no goods (open bids + bounded tatonnement).
Run (repo root): python3 experiments/d5a3_discovery.py   (~2 min)
Report (Turkish): docs/experiments/D5a3.md

(Original notes in Turkish below.)

Deney D5a3: malı olmayan pazarda fiyat keşfi.

Soru: İthalatçı Venedik'te yağ neden günlerin üçte birinde yok (D5a2 B7)? Çözüm gerçek bir mekanizmayla mümkün mü?
Teşhis: İşlem olmayan günlerde herkesin gördüğü fiyat, son işlemin (çoğu zaman bir bolluk gününün) fiyatında donuyor.
Tüccarlar bu ucuz fiyata bakıp mal getirmiyor; rafı boş dükkâncının teklifi de yükselmiyor.
Mekanizma (price_discovery):
  1) İşlem olmayan oturumda açık fiyat = en yüksek alış teklifi (satıcının gerçekten alabileceği).
  2) Tâtonnement: müşterileri eli boş dönen dükkâncı teklifini yükseltir (karşılanmayan pay × günlük azami hareket),
     ama müşterilerinin son bir yılda ödediği en yüksek fiyatın üstüne çıkmaz.
Karşılaştırma: REL (D5a2'nin önerilen hali) / REL + fiyat keşfi.
Kullanım:  python3 experiments/d5a3_discovery.py   (~2 dk)
Rapor:     docs/experiments/D5a3.md
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5a2_retail import BASE, SETUPS, metrics  # noqa: E402
from sim.world5 import GOODS5, D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5a3"
OUT.mkdir(parents=True, exist_ok=True)
REL = SETUPS["REL rekabet+giriş+geçim"]
VARIANTS = {"REL": dict(REL), "REL+PD": dict(REL, price_discovery=True)}
SEEDS = range(5)


def run(args):
    name, seed = args
    w = D5World(D5Config(seed=seed, **BASE, **VARIANTS[name]))
    r = w.run()
    out = metrics(w, r)
    imp = sum(q for (y, o, d, g), q in r["flows"].items() if d == "VEN" and g == "OIL" and y >= 1565) / 5
    out["VEN_OIL_import_share"] = imp / (w.local_cons["VEN"]["OIL"] * 365)
    for (p, g) in w.markets:
        out[f"{p}_{g}_maxall"] = float(np.nanmax(np.array(r[f"{p}_{g}_retail"], dtype=float)) / GOODS5[g].ref)
    return name, seed, out


def main():
    with Pool(5) as pool:
        res = pool.map(run, [(n, s) for n in VARIANTS for s in SEEDS])
    summary = {}
    for name in VARIANTS:
        rows = [o for n, s, o in res if n == name]
        agg = {"exploded": f"{sum(x['exploded'] for x in rows)}/{len(rows)}"}
        for k in rows[0]:
            if k == "exploded":
                continue
            if isinstance(rows[0][k], tuple):
                agg[k] = [float(np.median([x[k][i] for x in rows])) for i in range(2)]
            else:
                agg[k] = float(np.median([x[k] for x in rows]))
                if k in ("VEN_OIL_nosale", "VEN_OIL_import_share", "VEN_WHT_maxall", "VEN_OIL_maxall"):
                    agg[k + "_seeds"] = [round(float(x[k]), 2) for x in rows]
        summary[name] = agg
        print(name, json.dumps(agg, ensure_ascii=False))
    a = D5World(D5Config(seed=7, **BASE, **VARIANTS["REL+PD"])).run()
    b = D5World(D5Config(seed=7, **BASE, **VARIANTS["REL+PD"])).run()
    summary["determinism_same_seed"] = bool(np.array_equal(a["VEN_OIL_kapan"], b["VEN_OIL_kapan"]))
    print("determinism", summary["determinism_same_seed"])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
