"""Experiment D5a2: competitive retail (logit + Lerner markup + derived demand + entry).
Run (repo root): python3 experiments/d5a2_retail.py   (~2 min)
Report (Turkish): docs/experiments/D5a2.md

(Original notes in Turkish below.)

Deney D5a2: rekabetçi perakende (K-016).

Soru: Perakende fiyatı, mekanik bir çekiş olmadan, rekabetle toptan fiyata yakın bir seviyeye iniyor mu?
Fiyat yükseltmenin rekabetçi bir maliyeti var mı? Rockets and feathers kendiliğinden çıkıyor mu?
Kurulum: D5a'nın kapan dünyası (3 liman, 2 mal). Karşılaştırma:
  C   D5a: sabit marj + yerine koyma maliyetine mekanik iki yönlü çekiş
  N   sabit marj, çekiş yok (teşhis)
  R   rekabetçi perakende: logit müşteri payı + atalet, Lerner marjı, türetilmiş talep; 3 dükkân
  RE  R + perakende giriş-çıkışı (D3b mekanizması; işletme kârıyla, en çok 40 dükkân)
  REL RE + dükkâncının geçimi (sabit gider; tüccarla eşit: living_cost)
Kullanım:  python3 experiments/d5a2_retail.py   (~2 dk)
Rapor:     docs/experiments/D5a2.md
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

OUT = ROOT / "experiments" / "out" / "d5a2"
OUT.mkdir(parents=True, exist_ok=True)
BASE = dict(ports=["VEN", "COR", "ALE"], goods=["WHT", "OIL"], years=10, wholesale=True,
            direct_farm_buying=False, dock_sales=False, recapitalize=False, share_depth=False)
SETUPS = {
    "C D5a çekiş": dict(retail_rule="pull"),
    "N çekişsiz": dict(retail_rule="none"),
    "R rekabet": dict(retail_rule="compete"),
    "RE rekabet+giriş": dict(retail_rule="compete", retail_entry=True, max_shops=40),
    "REL rekabet+giriş+geçim": dict(retail_rule="compete", retail_entry=True, max_shops=40, shop_living_cost=30),
}
ROUTES = {"WHT": ("ALE", "VEN"), "OIL": ("COR", "VEN")}
SEEDS = range(5)
LAST = slice(-1825, None)


def passthrough(retail, kapan, h):
    """Δlog perakende = a⁺·max(Δlog toptan, 0) + a⁻·min(Δlog toptan, 0), h günlük örtüşmeyen aralıklar."""
    r, k = np.log(retail[LAST][::h]), np.log(kapan[LAST][::h])
    ok = np.isfinite(r) & np.isfinite(k)
    r, k = r[ok], k[ok]
    dr, dk = np.diff(r), np.diff(k)
    X = np.column_stack([np.maximum(dk, 0), np.minimum(dk, 0), np.ones_like(dk)])
    coef, *_ = np.linalg.lstsq(X, dr, rcond=None)
    return float(coef[0]), float(coef[1])


def metrics(w, r):
    out = {"exploded": False}
    for (p, g) in w.markets:
        ret = np.array(r[f"{p}_{g}_retail"], dtype=float)
        kap = np.array(r[f"{p}_{g}_kapan"], dtype=float)
        ref = GOODS5[g].ref
        out[f"{p}_{g}"] = float(np.nanmedian(ret[LAST]) / ref)
        out[f"{p}_{g}_markup"] = float(np.nanmedian(ret[LAST] / kap[LAST]) - 1)
        if np.nanmax(ret) > 50 * ref:
            out["exploded"] = True
        up7, dn7 = passthrough(ret, kap, 7)
        up30, dn30 = passthrough(ret, kap, 30)
        out[f"{p}_{g}_pt7"] = (up7, dn7)
        out[f"{p}_{g}_pt30"] = (up30, dn30)
        out[f"{p}_{g}_vol"] = float(np.nanstd(np.diff(np.log(kap[LAST]))))
        out[f"{p}_{g}_nosale"] = float(np.mean(~np.isfinite(ret[LAST])))      # rafta mal yok
        out[f"{p}_{g}_shops"] = len(w.markets[(p, g)].shops)
        cons = r.get(f"{p}_{g}_cons")
        if cons is not None:
            c = np.array(cons[LAST]) / w.local_cons[p][g]
            out[f"{p}_{g}_halfhungry"] = float(np.mean(c < 0.5))
            out[f"{p}_{g}_mincons"] = float(np.min(c))
            out[f"{p}_{g}_max"] = float(np.nanmax(ret[LAST]) / ref)
    for g, (src, dst) in ROUTES.items():
        days = w.days[(src, dst)]
        ps = np.nanmedian(r[f"{src}_{g}_kapan"][LAST])
        pd = np.nanmedian(r[f"{dst}_{g}_kapan"][LAST])
        cost = FREIGHT_PER_BULK_DAY * GOODS5[g].bulk * days + pd * (CUSTOMS + 0.03)
        out[f"spread_{g}"] = float((pd - ps) / cost)
    out["n_merchants"] = float(np.mean(r["n_npc"][LAST]))
    shops = [s for mk in w.markets.values() for s in mk.shops]
    out["trapped_shops"] = sum(1 for s in shops if s.cash < 0.1 * s.target * s.mid and s.stock < 0.1 * s.target)
    out["n_shops"] = len(shops)
    out["shop_entries"], out["shop_exits"] = r["shop_entries"], r["shop_exits"]
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
                fig, axs = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
                for ax, (p, g) in zip(axs, (("VEN", "WHT"), ("VEN", "OIL"), ("ALE", "WHT"))):
                    ref = GOODS5[g].ref
                    ax.plot(r["date"], np.array(r[f"{p}_{g}_kapan"]) / ref, lw=0.7, label="kapan (toptan)")
                    ax.plot(r["date"], np.array(r[f"{p}_{g}_retail"], dtype=float) / ref, lw=0.7, label="perakende")
                    ax.set_yscale("log"); ax.set_ylabel(f"{p} {g} / ref"); ax.legend(loc="upper left")
                fig.suptitle(f"D5a2 — {name} (seed 1)")
                fig.tight_layout(); fig.savefig(OUT / f"d5a2_{name.split()[0]}.png", dpi=110); plt.close(fig)
        agg = {"exploded": f"{sum(x['exploded'] for x in rows)}/{len(rows)}"}
        for k in rows[0]:
            if k == "exploded":
                continue
            if isinstance(rows[0][k], tuple):
                agg[k] = [float(np.median([x[k][i] for x in rows])) for i in range(2)]
            else:
                agg[k] = float(np.median([x[k] for x in rows]))
        summary[name] = agg
        print(name, json.dumps(agg, ensure_ascii=False))
    w1 = D5World(D5Config(seed=7, **BASE, **SETUPS["REL rekabet+giriş+geçim"])); a = w1.run()
    w2 = D5World(D5Config(seed=7, **BASE, **SETUPS["REL rekabet+giriş+geçim"])); b = w2.run()
    summary["determinism_same_seed"] = bool(np.array_equal(a["VEN_WHT_kapan"], b["VEN_WHT_kapan"]))
    print("determinism", summary["determinism_same_seed"])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
