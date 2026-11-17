"""Experiment D5b3e: route crowding: the engine's own contribution (ablation).
Run (repo root): python3 experiments/d5b3e_crowd_ablation.py YEARS [SETUP,...]
Report (Turkish): docs/experiments/D5b3e.md

(Original notes in Turkish below.)

Deney D5b3e E1: rota kalabalığına motorun kendi katkısı (ablation). Plan: docs/experiments/D5b3e.md, K-026.
Taban VRS (D5b3d). Kurulumlar:
  VRS   taban
  L0    düzey 0 da duyduğu rakip yüklerini sayar (K-014'teki "düzey 0 yok sayar" kapalı)
  NI    imitation kapalı (taklit çekimi yok)
  L0NI  ikisi
Ek ölçütler: rotalar arası ex-post getiri sapması, aktif rota sayısı, en kalabalık 5 rotanın payı.
Kullanım: python3 experiments/d5b3e_crowd_ablation.py 10 [kurulum,...]
"""
import json
import pathlib
import sys
import time
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import d5b3d_lender_entry as B  # noqa: E402
import d5b3c_finance as C  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b3e"
OUT.mkdir(parents=True, exist_ok=True)
VRS = B.SETUPS["VRS"]
SETUPS = {
    "VRS": VRS,
    "L0": dict(VRS, l0_counts_rivals=True),
    "NI": dict(VRS, imitation_on=False),
    "L0NI": dict(VRS, l0_counts_rivals=True, imitation_on=False),
    # E2-E3 (K-026, K-027)
    "N": dict(VRS, network=True),                       # muhabir ağı
    "H": dict(VRS, houses=True),                        # çok gemili büyük tüccar (filonun %30'u)
    "H6": dict(VRS, houses=True, house_share=0.6),      # doz: filonun %60'ı
    "NH": dict(VRS, network=True, houses=True),
    # E3 ayrıştırma: evin getiri kaybı ortak kasadan mı, kendi kargosunu saymaktan mı?
    "H-nopool": dict(VRS, houses=True, house_pool=False),
    "H-noint": dict(VRS, houses=True, house_internal=False),
    # Tam harita (6 liman × 9 mal; BASE'in 3 × 3 alt kümesi yerine)
    "F": dict(VRS, ports=None, goods=None),
    "FN": dict(VRS, ports=None, goods=None, network=True),
    "FH": dict(VRS, ports=None, goods=None, houses=True),
    "FNH": dict(VRS, ports=None, goods=None, network=True, houses=True),
}
LAST = B.LAST


def route_metrics(w):
    """Rota = (köken, hedef, mal). Ex-post sefer marjı rota ortalamaları ve sefer payları."""
    by = {}
    for x in w.voy_log:
        day0, day1, g, o, d, q, exp_net, uc, real, lvl, loc, margin = x[:12]
        if day0 < LAST + w.t0_day or q <= 0 or uc <= 0:
            continue
        by.setdefault((o, d, g), []).append(margin)
    n = np.array([len(v) for v in by.values()], float)
    mu = np.array([np.mean(v) for v in by.values()])
    tot = n.sum()
    grand = (n * mu).sum() / tot
    big = n >= 5                                   # gürültüyü azaltmak için en az 5 seferli rotalar
    disp = float(np.sqrt((n[big] * (mu[big] - grand) ** 2).sum() / n[big].sum())) if big.any() else float("nan")
    return {"route_disp": disp, "routes_active": int(big.sum()),
            "top5_share": float(np.sort(n)[::-1][:5].sum() / tot),
            "worst_route_share": float(n[mu < -0.2].sum() / tot)}


def run(args):
    name, seed = args
    B.SETUPS = {**B.SETUPS, name: SETUPS[name]}
    t0 = time.time()
    _, _, out = B.run((name, seed))
    w = C.LAST_WORLD
    out.update(route_metrics(w))
    alive = [m for m in w.merchants if not m.is_player]
    out["house_ship_share"] = float(np.mean([bool(m.house) for m in alive])) if alive else 0.0
    out["net_size"] = float(np.mean([len(m.network) for m in alive])) if alive and w.cfg.network else 0.0
    out["comm_share"] = w.commissions / max(1.0, sum(x[5] * x[7] for x in w.voy_log))
    out["n_houses"] = w.n_houses
    out["secs"] = time.time() - t0
    return name, seed, out


KEYS = ("crowd_median", "fill_median", "deep_loss", "loss_frac", "margin_sd", "agg_return", "fleet_last",
        "route_disp", "routes_active", "top5_share", "worst_route_share", "ret_median", "secs",
        "house_ship_share", "net_size", "comm_share", "n_houses")


def main(seeds, setups, tag):
    # Tam haritada koşu başına ~1,5 GB: paralellik NPROC ile sınırlı (varsayılan 8). Her koşu bitince
    # runs{tag}.jsonl'e yazılır; yarıda kalırsa yeniden başlatınca biten koşular atlanır.
    import os
    log = OUT / f"runs{tag}.jsonl"
    done = {}
    if log.exists():
        for line in log.read_text().splitlines():
            n, s, o = json.loads(line)
            done[(n, s)] = o
    todo = [(n, s) for n in setups for s in seeds if (n, s) not in done]
    nproc = int(os.environ.get("NPROC", "8"))
    if todo:
        with Pool(min(nproc, len(todo)), maxtasksperchild=1) as pool, log.open("a") as f:
            for n, s, o in pool.imap_unordered(run, todo):
                done[(n, s)] = o
                f.write(json.dumps([n, s, o]) + "\n")
                f.flush()
    res = [(n, s, done[(n, s)]) for n in setups for s in seeds]
    summary = {}
    for name in setups:
        rows = [o for n, s, o in res if n == name]
        summary[name] = {k: float(np.nanmedian([x.get(k, np.nan) for x in rows])) for k in KEYS}
        summary[name]["agg_return_seeds"] = [round(x["agg_return"], 3) for x in rows]
        summary[name]["crowd_seeds"] = [round(x["crowd_median"], 1) for x in rows]
        print(name, json.dumps({k: round(v, 3) if isinstance(v, float) else v for k, v in summary[name].items()},
                               ensure_ascii=False), flush=True)
    (OUT / f"summary{tag}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    seeds = range(int(sys.argv[1])) if len(sys.argv) > 1 else range(5)
    setups = {k: SETUPS[k] for k in sys.argv[2].split(",")} if len(sys.argv) > 2 else SETUPS
    tag = "_" + sys.argv[2].replace(",", "_") if len(sys.argv) > 2 else ""
    main(seeds, setups, tag)
