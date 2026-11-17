"""Experiment D1f: D1 + peasant self-consumption + storer (intertemporal arbitrage) + replacement-cost signal.
Run (repo root): python3 experiments/d1f_storer.py
Report (Turkish): docs/experiments/D1f.md

(Original notes in Turkish below.)

Deney D1f: D1 + köylünün kendi tüketimi + stokçu (zamanlar arası arbitraj)
+ dükkâncının yerine koyma maliyeti sinyali.

Hipotezler:
  H1  Stokçu varken kötü hasata fiyat tepkisi anında gelir (D1'de ~1 yıl gecikiyordu).
  H2  Köylünün kendi tüketimi King-Davenant eğrisini tarihsel tabloya yaklaştırır.

Kullanım:  python3 experiments/d1f_storer.py
Çıktılar:  experiments/out/d1f/
Rapor:     docs/experiments/D1f.md
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
from experiments.d1_single_port import KD_TABLE, aggregate, metrics, monthly_means, run  # noqa: E402
from sim.engine import RC, SELF, STORER, V3  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d1f"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = range(20)
MONTHS = ["Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara", "Oca", "Şub"]

VARIANTS = {
    "A  V3 (D1 sonu)": V3,
    "B  +köylü tüketimi": dict(V3, **SELF),
    "C  +stokçu+RC (hafıza 2y)": dict(V3, **STORER, **RC, storer_normal_memory=730),
    "D  +stokçu+RC (hafıza 5y)": dict(V3, **STORER, **RC, storer_normal_memory=1825),
    "E  +köylü+stokçu+RC (5y)": dict(V3, **SELF, **STORER, **RC, storer_normal_memory=1825),
    "F  E + hafıza 20y + taşıma": dict(V3, **SELF, **STORER, **RC, storer_normal_memory=7300,
                                       storer_carry=0.1),
}


def harvest_index(r, year=1565):
    return next(i for i, d in enumerate(r["date"]) if d.year == year and d.month == 7)


def shock_response(kw):
    """%30 eksik hasat (1565), verim gürültüsü kapalı; normale oranlar."""
    base = run(0, **kw, yield_sigma=0.0)
    shock = run(0, **kw, yield_sigma=0.0, yield_overrides={5: 0.7})
    h = harvest_index(base)
    ratio = shock["ask_mean"] / base["ask_mean"]
    return {
        "month1": float(ratio[h + 30]), "month2": float(ratio[h + 60]),
        "month6": float(ratio[h + 180]), "month11": float(ratio[h + 330]),
        "peak_day": int(np.argmax(shock["ask_mean"][h:h + 400])),
        "year_after_next": float(ratio[h + 365:h + 730].mean()),   # kalıcılık
        "year_plus2": float(ratio[h + 730:h + 1095].mean()),
    }, base, shock


def kd_curve(kw):
    base = run(0, **kw, yield_sigma=0.0)
    h = harvest_index(base)
    win = slice(h, h + 365)
    return {s: float(run(0, **kw, yield_sigma=0.0, yield_overrides={5: 1 - s})["ask_mean"][win].mean()
                     / base["ask_mean"][win].mean() - 1) for s in KD_TABLE}


def season_profile(kw, seeds=range(8)):
    prof, n = np.zeros(12), 0
    for s in seeds:
        m = monthly_means(run(s, **kw))[12:]
        for i in range(len(m) // 12):
            yr = m[i * 12:(i + 1) * 12]
            prof += yr / yr.mean(); n += 1
    return prof / n


def storer_return(kw):
    """Stokçuların yıllıklandırılmış net servet getirisi (nakit + stok × toptan fiyat)."""
    rets = []
    for s in SEEDS:
        r = run(s, **kw)
        nw0 = r["storer_cash"][0] + r["storer_stock"][0] * r["wholesale"][0]
        nw1 = r["storer_cash"][-1] + r["storer_stock"][-1] * r["wholesale"][-1]
        if nw0 > 0:
            rets.append((nw1 / nw0) ** (1 / 10) - 1)
    return float(np.median(rets)) if rets else None


def main():
    summary = {}
    for kap in (0.005, 0.01):
        summary[kap] = {}
        for name, v in VARIANTS.items():
            kw = dict(v, kappa=kap)
            agg = aggregate([metrics(run(s, **kw)) for s in SEEDS])
            sr, _, _ = shock_response(kw)
            prof = season_profile(kw)
            summary[kap][name] = {
                "agg": agg, "shock": sr, "kd": kd_curve(kw),
                "cheapest": MONTHS[int(prof.argmin())], "dearest": MONTHS[int(prof.argmax())],
                "season_profile": prof.round(3).tolist(),
                "storer_annual_return": storer_return(kw) if v.get("n_storers") else None,
            }
            print(kap, name, "ok")

    # Grafikler (κ=0.005)
    kap = 0.005
    fig, ax = plt.subplots(figsize=(11, 4.5))
    for name in ("A  V3 (D1 sonu)", "F  E + hafıza 20y + taşıma"):
        _, base, shock = shock_response(dict(VARIANTS[name], kappa=kap))
        ax.plot(shock["date"], shock["ask_mean"], lw=1, label=f"{name} — %30 eksik hasat")
    ax.plot(base["date"], base["ask_mean"], color="gray", lw=0.8, ls=":", label="F — şoksuz")
    ax.axvline(base["date"][harvest_index(base)], color="red", lw=0.8, ls="--")
    ax.set_ylabel("soldo / birim"); ax.legend(loc="upper left")
    ax.set_title("1565 kötü hasadına tepki: D1 sonu (A) ve D1f (F), κ=0.005")
    fig.tight_layout(); fig.savefig(OUT / "d1f_shock_compare.png", dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    xs = list(KD_TABLE)
    ax.plot([x * 100 for x in xs], [KD_TABLE[x] * 100 for x in xs], "k--o", label="King-Davenant (1699)")
    for name in VARIANTS:
        kd = summary[kap][name]["kd"]
        ax.plot([x * 100 for x in xs], [kd[x] * 100 for x in xs], "-o", ms=3, label=name)
    ax.set_xlabel("hasat eksiği %"); ax.set_ylabel("12 ay ort. fiyat artışı %")
    ax.set_title("Hasat şokuna fiyat tepkisi, κ=0.005"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "d1f_king_davenant.png", dpi=110); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(13, 3.8), sharey=True)
    w = 0.38
    for ax, sigma, title in ((axs[0], None, "verim şokları açık (8 seed)"),
                             (axs[1], 0.0, "şoksuz (saf mevsim)")):
        for j, name in enumerate(("A  V3 (D1 sonu)", "F  E + hafıza 20y + taşıma")):
            kw = dict(VARIANTS[name], kappa=kap)
            prof = (summary[kap][name]["season_profile"] if sigma is None
                    else season_profile(dict(kw, yield_sigma=0.0), seeds=range(1)))
            ax.bar(np.arange(12) + (j - 0.5) * w, prof, width=w, label=name)
        ax.set_xticks(range(12)); ax.set_xticklabels(MONTHS); ax.axhline(1, color="gray", lw=0.8)
        ax.set_ylim(0.9, 1.1); ax.set_title(title)
    axs[0].legend(fontsize=8)
    fig.suptitle("Mevsim profili (hasat Temmuz başı), κ=0.005: ay / yıl ortalaması")
    fig.tight_layout(); fig.savefig(OUT / "d1f_season.png", dpi=110); plt.close(fig)

    a, b = run(7, **VARIANTS["E  +köylü+stokçu+RC (5y)"]), run(7, **VARIANTS["E  +köylü+stokçu+RC (5y)"])
    summary["determinism_same_seed"] = bool(np.array_equal(a["ask_mean"], b["ask_mean"]))

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
