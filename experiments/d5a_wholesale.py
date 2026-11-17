"""Experiment D5a: institutional wholesale market (kapan) replacing hand patches.
Run (repo root): python3 experiments/d5a_wholesale.py   (~3 min)
Report (Turkish): docs/experiments/D5a.md

(Original notes in Turkish below.)

Deney D5a: kurumsal toptan pazar (kapan), K-013.

Soru: D5'teki darboğaz ve likidite sorunları, el yaması olmadan, gerçek bir kurumla çözülüyor mu?
Kurulum: 3 liman (Venedik ithalatçı; Korfu yağ ihracatçısı; İskenderiye buğday ihracatçısı), 2 mal.
Karşılaştırma:
  A  sadece dükkân (D5'in yamasız hali)
  B  D5 yamaları (doğrudan üreticiden alım, iskele satışı, yeniden sermayelendirme, anlık derinlik paylaşımı)
  C  kapan (yamalar kapalı)
Kullanım:  python3 experiments/d5a_wholesale.py   (~3 dk)
Rapor:     docs/experiments/D5a.md
"""
import json
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sim.world5 import CUSTOMS, FREIGHT_PER_BULK_DAY, GOODS5, D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5a"
OUT.mkdir(parents=True, exist_ok=True)
BASE = dict(ports=["VEN", "COR", "ALE"], goods=["WHT", "OIL"], years=10)
OFF = dict(direct_farm_buying=False, dock_sales=False, recapitalize=False, share_depth=False)
SETUPS = {
    "A sadece dükkân": dict(**OFF),
    "B D5 yamaları": dict(),
    "C kapan": dict(wholesale=True, **OFF),
}
ROUTES = {"WHT": ("ALE", "VEN"), "OIL": ("COR", "VEN")}
SEEDS = range(5)


def metrics(w, r):
    last = slice(-1825, None)
    out = {"exploded": False}
    for (p, g) in w.markets:
        ask = r[f"{p}_{g}_ask"]
        out[f"{p}_{g}"] = float(np.median(ask[last]) / GOODS5[g].ref)
        if np.max(ask) > 50 * GOODS5[g].ref:
            out["exploded"] = True
    # Fark / taşıma maliyeti (perakende fiyatlarla, ihracatçıdan ithalatçıya)
    for g, (src, dst) in ROUTES.items():
        days = w.days[(src, dst)]
        ps, pd = np.median(r[f"{src}_{g}_ask"][last]), np.median(r[f"{dst}_{g}_ask"][last])
        cost = FREIGHT_PER_BULK_DAY * GOODS5[g].bulk * days + pd * (CUSTOMS + 0.03)
        out[f"spread_{g}"] = float((pd - ps) / cost)
    out["frac_selling"] = float(np.mean(r["frac_selling"][last]))
    out["n_merchants"] = float(np.mean(r["n_npc"][last]))
    shops = [s for mk in w.markets.values() for s in mk.shops]
    out["trapped_shops"] = sum(1 for s in shops if s.cash < 0.1 * s.target * s.mid and s.stock < 0.1 * s.target)
    out["n_shops"] = len(shops)
    return out


def main():
    summary = {}
    for name, kw in SETUPS.items():
        rows = []
        for seed in SEEDS:
            w = D5World(D5Config(seed=seed, **BASE, **kw))
            r = w.run()
            rows.append(metrics(w, r))
            if seed == 1:
                fig, axs = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
                for ax, g in zip(axs, ("WHT", "OIL")):
                    for p in w.port_list:
                        ax.plot(r["date"], np.array(r[f"{p}_{g}_ask"]) / GOODS5[g].ref, lw=0.8, label=p)
                    ax.set_yscale("log"); ax.set_ylabel(f"{g} perakende / ref"); ax.legend(loc="upper left")
                fig.suptitle(f"D5a — {name} (seed 1)")
                fig.tight_layout(); fig.savefig(OUT / f"d5a_{name.split()[0]}.png", dpi=110); plt.close(fig)
        agg = {"exploded": f"{sum(x['exploded'] for x in rows)}/{len(rows)}"}
        for k in rows[0]:
            if k != "exploded":
                agg[k] = float(np.median([x[k] for x in rows]))
        summary[name] = agg
        print(name, "ok")
    w1 = D5World(D5Config(seed=7, **BASE, **SETUPS["C kapan"])); a = w1.run()
    w2 = D5World(D5Config(seed=7, **BASE, **SETUPS["C kapan"])); b = w2.run()
    summary["determinism_same_seed"] = bool(np.array_equal(a["VEN_WHT_ask"], b["VEN_WHT_ask"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
