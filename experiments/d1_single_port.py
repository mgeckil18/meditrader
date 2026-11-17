"""Experiment D1: one port, one good (wheat), urban demand + 3 shopkeepers, no merchants.
Run (repo root): python3 experiments/d1_single_port.py
Report (Turkish): docs/experiments/D1.md

(Original notes in Turkish below.)

Deney D1: tek liman, tek mal (buğday), kitle + 3 dükkâncı, tüccar yok.

Kullanım:  python3 experiments/d1_single_port.py
Çıktılar:  experiments/out/d1/  (grafikler + summary.json)
Rapor:     docs/experiments/D1.md
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
from sim.engine import V0, V3, D1Config, D1Sim  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d1"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = range(20)
KD_TABLE = {0.1: 0.3, 0.2: 0.8, 0.3: 1.6, 0.4: 2.8, 0.5: 4.5}   # King-Davenant (01 §2)


def run(seed=0, **kw):
    return D1Sim(D1Config(seed=seed, **kw)).run()


def monthly_means(r):
    keys = [(d.year, d.month) for d in r["date"]]
    out, cur, buf = [], keys[0], []
    for k, p in zip(keys, r["ask_mean"]):
        if k != cur:
            out.append(np.mean(buf)); buf, cur = [], k
        buf.append(p)
    out.append(np.mean(buf))
    return np.array(out)


def metrics(r):
    p = r["ask_mean"]
    exploded = bool(p.max() > 10 * np.median(p))
    m = monthly_means(r)[12:]                       # ilk yıl ısınma
    mv = float(np.std(np.diff(np.log(m))) * np.sqrt(12))
    yrs = len(m) // 12
    seas = float(np.mean([m[i*12:(i+1)*12].max() / m[i*12:(i+1)*12].min() for i in range(yrs)]))
    disp = float(np.mean((r["ask_max"] - r["ask_min"]) / r["ask_mean"]))
    return dict(exploded=exploded, monthly_vol=mv, seasonal_ratio=seas,
                mean_price=float(p[365:].mean()), peak_over_median=float(p.max() / np.median(p)),
                shortage_pct=float(r["shortage"][365:].mean() * 100), shop_dispersion=disp)


def aggregate(rows):
    ok = [r for r in rows if not r["exploded"]]
    agg = {"exploded": f"{len(rows) - len(ok)}/{len(rows)}"}
    for k in ("monthly_vol", "seasonal_ratio", "mean_price", "peak_over_median",
              "shortage_pct", "shop_dispersion"):
        vals = [r[k] for r in ok]
        agg[k] = {"median": float(np.median(vals)), "p10": float(np.percentile(vals, 10)),
                  "p90": float(np.percentile(vals, 90))} if vals else None
    return agg


def plot_series(r, title, path, ylog=False):
    fig, ax = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    d = r["date"]
    ax[0].plot(d, r["ask_mean"], lw=0.8, label="ortalama satış fiyatı")
    ax[0].fill_between(d, r["ask_min"], r["ask_max"], alpha=0.25, label="dükkâncılar min-max")
    ax[0].axhline(100, color="gray", ls=":", lw=0.8)
    if ylog:
        ax[0].set_yscale("log")
    ax[0].set_ylabel("soldo / birim"); ax[0].legend(loc="upper left"); ax[0].set_title(title)
    ax[1].plot(d, r["shop_stock"], lw=0.8, label="dükkân stoku")
    ax[1].plot(d, r["rural_stock"] / 10, lw=0.8, label="köylü stoku / 10")
    ax[1].set_ylabel("birim"); ax[1].legend(loc="upper left")
    ax[2].plot(d, r["shortage"] * 100, lw=0.6, color="tab:red")
    ax[2].set_ylabel("kıtlık %")
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def main():
    summary = {}

    # D1-0: v0 başarısızlığı (kanıt)
    r = run(seed=1, **V0)
    plot_series(r, "D1 v0 — ilk kurallar (seed 1): hiperenflasyon", OUT / "d1_v0_seed1.png", ylog=True)
    summary["v0"] = aggregate([metrics(run(s, **V0)) for s in SEEDS])

    # D1-a: v3 κ taraması
    summary["v3_kappa"] = {}
    for kap in (0.003, 0.005, 0.01, 0.02):
        summary["v3_kappa"][kap] = aggregate([metrics(run(s, **V3, kappa=kap)) for s in SEEDS])
    for kap in (0.005, 0.02):
        plot_series(run(seed=1, **V3, kappa=kap), f"D1 v3, κ={kap} (seed 1)",
                    OUT / f"d1_v3_k{kap}_seed1.png")

    # Mevsim profili (v3, κ=0.005): ay ortalaması / yıl ortalaması
    prof = np.zeros(12)
    for s in SEEDS:
        m = monthly_means(run(s, **V3, kappa=0.005))[12:]
        for i in range(len(m) // 12):
            yr = m[i*12:(i+1)*12]
            prof += yr / yr.mean()
    prof /= len(SEEDS) * (len(m) // 12)
    months = ["Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara", "Oca", "Şub"]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(months, prof); ax.axhline(1, color="gray", lw=0.8)
    ax.set_ylim(prof.min() * 0.97, prof.max() * 1.02)
    ax.set_title("Mevsim profili (v3, κ=0.005; hasat Temmuz başı): ay / yıl ortalaması")
    fig.tight_layout(); fig.savefig(OUT / "d1_season_profile.png", dpi=110); plt.close(fig)
    summary["season_profile"] = dict(zip(months, prof.round(3).tolist()))

    # D1-b: King-Davenant testi — rastgele verim kapalı, 5. yılın hasadı düşük
    summary["king_davenant"] = {}
    for kap in (0.005, 0.01):
        base = run(seed=0, **V3, kappa=kap, yield_sigma=0.0)
        bp = base["ask_mean"]
        hidx = next(i for i, d in enumerate(base["date"]) if d.year == 1565 and d.month == 7)
        win = slice(hidx, hidx + 365)
        res = {}
        for short in KD_TABLE:
            r = run(seed=0, **V3, kappa=kap, yield_sigma=0.0, yield_overrides={5: 1 - short})
            rise = float(r["ask_mean"][win].mean() / bp[win].mean() - 1)
            peak = float(r["ask_mean"][win].max() / bp[win].mean() - 1)
            res[short] = {"mean_rise": rise, "peak_rise": peak, "kd": KD_TABLE[short]}
        summary["king_davenant"][kap] = res
    xs = list(KD_TABLE)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([x*100 for x in xs], [KD_TABLE[x]*100 for x in xs], "k--o", label="King-Davenant (1699)")
    for kap, res in summary["king_davenant"].items():
        ax.plot([x*100 for x in xs], [res[x]["mean_rise"]*100 for x in xs], "-o",
                label=f"sim κ={kap}: 12 ay ortalaması")
        ax.plot([x*100 for x in xs], [res[x]["peak_rise"]*100 for x in xs], ":^",
                label=f"sim κ={kap}: zirve")
    ax.set_xlabel("hasat eksiği %"); ax.set_ylabel("fiyat artışı %"); ax.legend()
    ax.set_title("Hasat şokuna fiyat tepkisi (P1)")
    fig.tight_layout(); fig.savefig(OUT / "d1_king_davenant.png", dpi=110); plt.close(fig)
    plot_series(run(seed=0, **V3, kappa=0.005, yield_sigma=0.0, yield_overrides={5: 0.7}),
                "D1 v3 κ=0.005 — 1565 hasadı %30 eksik (verim gürültüsü kapalı)",
                OUT / "d1_shock30.png")

    # D1-c: determinizm
    a, b = run(seed=7, **V3), run(seed=7, **V3)
    c = run(seed=8, **V3)
    summary["determinism"] = {
        "same_seed_identical": bool(np.array_equal(a["ask_mean"], b["ask_mean"])),
        "different_seed_differs": bool(not np.array_equal(a["ask_mean"], c["ask_mean"])),
    }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
