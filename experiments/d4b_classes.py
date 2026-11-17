"""Experiment D4b: cloth-oscillation ablation (artifact) and three urban income classes.
Run (repo root): python3 experiments/d4b_classes.py   (~1 min)
Report (Turkish): docs/experiments/D4b.md

(Original notes in Turkish below.)

Deney D4b: (1) kumaş salınımının sınıflandırılması, (2) üç kent sınıfı.

(1) Ablasyon (Y16): Şoksuz dünyada kumaş alımı mevsimsel salınıyor. Kentin bütçe kararında
    tahıl fiyatları referansta sabitlenince salınım sürüyorsa → artifact (kumaşın kendi
    dinamiği); duruyorsa → fenomen (tahıl mevsimselliğinin bütçe yoluyla aktarımı).
(2) Sınıflar: zengin / orta / yoksul (docs/research/history/consumer-profiles-16c.md §4).
    Hipotez: kıtlıkta yoksulun kumaş talebi çöker ama zenginin sürer → toplam düşer, sıfıra inmez.

Kullanım:  python3 experiments/d4b_classes.py   (~1 dk)
Rapor:     docs/experiments/D4b.md
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
from experiments.d2_two_ports import monthly  # noqa: E402
from sim.multigood import CLASSES_3, D4Config, D4World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d4b"
OUT.mkdir(parents=True, exist_ok=True)
GOODS = ("WHT", "BRL", "OIL", "CLO")
CLASS_NAMES = [k.name for k in CLASSES_3]


def run(old_pace=False, **kw):
    w = D4World(D4Config(demand="les_ces", **kw), continuous_pace_fix=not old_pace)
    r = w.run()
    r["normal_q"] = w.normal_q
    return r


def season_amp(r, key):
    m = monthly(r[key], r["date"])[12:]
    yrs = len(m) // 12
    return float(np.mean([m[i * 12:(i + 1) * 12].max() / max(m[i * 12:(i + 1) * 12].min(), 1e-9)
                          for i in range(yrs)]))


def main():
    summary = {"ablation": {}, "shock": {}, "stability": {}}

    # (1) Ablasyon: şoksuz, verim gürültüsü kapalı
    fig, ax = plt.subplots(figsize=(11, 4))
    for label, kw in (("1 sınıf, eski satış hızı", dict(old_pace=True)), ("1 sınıf", {}),
                      ("3 sınıf", dict(classes=CLASSES_3))):
        for freeze in (False, True):
            r = run(seed=0, yield_sigma=0.0, freeze_cereal=freeze, **kw)
            key = f"{label} | tahıl {'sabit' if freeze else 'serbest'}"
            summary["ablation"][key] = {"cloth_amp": season_amp(r, "CLO_bought"),
                                        "wheat_amp": season_amp(r, "WHT_ask"),
                                        "cloth_price_amp": season_amp(r, "CLO_ask")}
            m = monthly(r["CLO_bought"], r["date"])
            ax.plot(range(len(m)), m / r["normal_q"]["CLO"], lw=0.9, ls="-" if not freeze else "--", label=key)
    ax.axhline(1, color="gray", lw=0.8)
    ax.set_xlabel("ay (1560 Mart'tan)"); ax.set_ylabel("kumaş alımı / normal")
    ax.set_title("Ablasyon: kentin bütçe kararında tahıl fiyatları sabitlenince kumaş salınımı kalıyor mu?")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(OUT / "d4b_ablation.png", dpi=110); plt.close(fig)

    # (2) Buğday şoku: 1 sınıf vs 3 sınıf
    for label, kw in (("1 sınıf", {}), ("3 sınıf", dict(classes=CLASSES_3))):
        base = run(seed=0, yield_sigma=0.0, **kw)
        sh = run(seed=0, yield_sigma=0.0, wheat_yield_overrides={5: 0.7}, **kw)
        h = next(i for i, d in enumerate(base["date"]) if d.year == 1565 and d.month == 7)
        win = slice(h, h + 365)
        res = {c: float(np.mean(sh[f"{c}_bought"][win]) / np.mean(base[f"{c}_bought"][win])) for c in GOODS}
        res["WHT_price"] = float(np.mean(sh["WHT_ask"][win]) / np.mean(base["WHT_ask"][win]))
        cm = monthly(sh["CLO_bought"][h:h + 400], sh["date"][h:h + 400])
        res["cloth_min_month_vs_normal"] = float(cm.min() / sh["normal_q"]["CLO"])
        if kw:
            for k in CLASS_NAMES:
                res[k] = {c: float(np.mean(sh[f"{k}_{c}"][win]) / max(np.mean(base[f"{k}_{c}"][win]), 1e-9))
                          for c in GOODS}
            summary["_series"] = None
            fig, ax = plt.subplots(figsize=(11, 4))
            rng = slice(h - 180, h + 730)
            for k in CLASS_NAMES:
                s30 = np.convolve(sh[f"{k}_CLO"], np.ones(30) / 30, mode="same")[rng]
                b30 = np.convolve(base[f"{k}_CLO"], np.ones(30) / 30, mode="same")[rng]
                ax.plot(sh["date"][rng], s30, lw=1, label=f"{k} (şok)")
                ax.plot(sh["date"][rng], b30, lw=0.7, ls=":", color=ax.lines[-1].get_color())
            ax.axvline(sh["date"][h], color="red", ls="--", lw=0.8)
            ax.set_ylabel("kumaş alımı (30g ort.)"); ax.legend(fontsize=8)
            ax.set_title("3 sınıf: buğday kıtlığında sınıflara göre kumaş alımı (noktalı: şoksuz)")
            fig.tight_layout(); fig.savefig(OUT / "d4b_cloth_by_class.png", dpi=110); plt.close(fig)
        summary["shock"][label] = res
    summary.pop("_series", None)

    # Kararlılık (10 seed, 3 sınıf)
    exploded, vols = 0, {c: [] for c in GOODS}
    for s in range(10):
        r = run(seed=s, classes=CLASSES_3)
        for c in GOODS:
            p = r[f"{c}_ask"]
            if p.max() > 10 * np.median(p):
                exploded += 1
                break
            m = monthly(p, r["date"])[12:]
            vols[c].append(float(np.std(np.diff(np.log(m))) * np.sqrt(12)))
    summary["stability"] = {"exploded": f"{exploded}/10", **{f"{c}_vol": float(np.median(v)) for c, v in vols.items()}}

    a, b = run(seed=7, classes=CLASSES_3), run(seed=7, classes=CLASSES_3)
    summary["determinism_same_seed"] = bool(np.array_equal(a["WHT_ask"], b["WHT_ask"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
