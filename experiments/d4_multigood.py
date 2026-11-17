"""Experiment D4: many goods, shared urban budget; demand-model tournament (LES + CES won).
Run (repo root): python3 experiments/d4_multigood.py   (~3 min)
Report (Turkish): docs/experiments/D4.md

(Original notes in Turkish below.)

Deney D4: çok mal ve ortak bütçe.

Sorular:
  S1  Buğday kıtlığı lüks malları (kumaş) vuruyor mu? (income effect; Labrousse tezi)
  S2  Buğday pahalanınca arpaya kayılıyor mu? (substitution effect)
  S3  Ortak bütçe yeni bir kararsızlık yaratıyor mu?

Yarışan yuva: talep yapısı (independent / LES / LES + CES). Parametreler varsayılan.
Kullanım:  python3 experiments/d4_multigood.py   (~3 dk)
Rapor:     docs/experiments/D4.md
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
from sim.multigood import D4Config, D4World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d4"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = range(10)
MODELS = ("independent", "les", "les_ces")
GOODS = ("WHT", "BRL", "OIL", "CLO")
NAMES = {"WHT": "buğday", "BRL": "arpa", "OIL": "zeytinyağı", "CLO": "kumaş"}


def run(**kw):
    w = D4World(D4Config(**kw))
    r = w.run()
    r["normal_q"] = w.normal_q
    r["income"] = w.income
    return r


def stability(r):
    out = {"exploded": False}
    for c in GOODS:
        p = r[f"{c}_ask"]
        if p.max() > 10 * np.median(p):
            out["exploded"] = True
        m = monthly(p, r["date"])[12:]
        out[f"{c}_vol"] = float(np.std(np.diff(np.log(m))) * np.sqrt(12))
        out[f"{c}_price"] = float(np.mean(p[365:]))
    # Mallar arası bağ: aylık buğday fiyatı ile aylık kumaş alımı arasındaki korelasyon
    wp = monthly(r["WHT_ask"], r["date"])[12:]
    cq = monthly(r["CLO_bought"], r["date"])[12:]
    bp = monthly(r["BRL_ask"], r["date"])[12:]
    out["corr_wheatprice_clothqty"] = float(np.corrcoef(np.log(wp), cq)[0, 1])
    out["corr_wheatprice_barleyprice"] = float(np.corrcoef(np.log(wp), np.log(bp))[0, 1])
    out["spend_share"] = float(np.mean(r["spend"][365:]) / r["income"])
    return out


def shock(model):
    base = run(seed=0, demand=model, yield_sigma=0.0)
    sh = run(seed=0, demand=model, yield_sigma=0.0, wheat_yield_overrides={5: 0.7})
    h = next(i for i, d in enumerate(base["date"]) if d.year == 1565 and d.month == 7)
    win = slice(h, h + 365)
    res = {}
    for c in GOODS:
        res[c] = {
            "price": float(np.mean(sh[f"{c}_ask"][win]) / np.mean(base[f"{c}_ask"][win])),
            "qty": float(np.mean(sh[f"{c}_bought"][win]) / np.mean(base[f"{c}_bought"][win])),
            "spend": float(np.mean(sh[f"{c}_spend"][win]) / np.mean(base[f"{c}_spend"][win])),
        }
    return res, base, sh, h


def main():
    summary = {}
    for model in MODELS:
        rows = [stability(run(seed=s, demand=model)) for s in SEEDS]
        agg = {"exploded": f"{sum(r['exploded'] for r in rows)}/{len(rows)}"}
        for k in rows[0]:
            if k != "exploded":
                agg[k] = float(np.median([r[k] for r in rows]))
        res, _, _, _ = shock(model)
        summary[model] = {"stability": agg, "shock": res}
        print(model, "ok")

    # Şok tepkisi: fiyat ve miktar oranları
    fig, axs = plt.subplots(1, 2, figsize=(13, 4))
    x = np.arange(len(GOODS))
    for j, model in enumerate(MODELS):
        res = summary[model]["shock"]
        axs[0].bar(x + (j - 1) * 0.27, [res[c]["price"] for c in GOODS], 0.27, label=model)
        axs[1].bar(x + (j - 1) * 0.27, [res[c]["qty"] for c in GOODS], 0.27, label=model)
    for ax, t in zip(axs, ("Fiyat (şoklu / şoksuz)", "Kentin aldığı miktar (şoklu / şoksuz)")):
        ax.set_xticks(x); ax.set_xticklabels([NAMES[c] for c in GOODS]); ax.axhline(1, color="gray", lw=0.8)
        ax.set_title(t); ax.legend()
    fig.suptitle("Buğday hasadı %30 eksik (1565): 12 aylık ortalama etkiler")
    fig.tight_layout(); fig.savefig(OUT / "d4_shock_bars.png", dpi=110); plt.close(fig)

    # LES+CES şok zaman serisi
    _, base, sh, h = shock("les_ces")
    fig, axs = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    rng = slice(h - 365, h + 3 * 365)
    d = base["date"][rng]
    for ax, c, lab in ((axs[0], "WHT", "buğday fiyatı"), (axs[1], "BRL", "arpa fiyatı")):
        ax.plot(d, base[f"{c}_ask"][rng], color="gray", lw=0.8, label="şoksuz")
        ax.plot(d, sh[f"{c}_ask"][rng], lw=0.9, label="buğday şoku")
        ax.set_ylabel(lab); ax.legend(loc="upper left")
    bq = np.convolve(base["CLO_bought"], np.ones(30) / 30, mode="same")[rng]
    sq = np.convolve(sh["CLO_bought"], np.ones(30) / 30, mode="same")[rng]
    axs[2].plot(d, bq, color="gray", lw=0.8, label="şoksuz")
    axs[2].plot(d, sq, lw=0.9, label="buğday şoku")
    axs[2].set_ylabel("kumaş alımı (30g ort.)"); axs[2].legend(loc="upper left")
    for ax in axs:
        ax.axvline(base["date"][h], color="red", ls="--", lw=0.8)
    fig.suptitle("LES + CES: buğday kıtlığı arpaya ve kumaşa nasıl yayılıyor?")
    fig.tight_layout(); fig.savefig(OUT / "d4_les_ces_series.png", dpi=110); plt.close(fig)

    a, b = run(seed=7, demand="les_ces"), run(seed=7, demand="les_ces")
    summary["determinism_same_seed"] = bool(np.array_equal(a["WHT_ask"], b["WHT_ask"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
