"""Experiment D3: information delay: does it keep arbitrage opportunities alive?
Run (repo root): python3 experiments/d3_information.py   (~4 min)
Report (Turkish): docs/experiments/D3.md

(Original notes in Turkish below.)

Deney D3: bilgi gecikmesi. Fırsatları canlı tutuyor mu?

Tüccar kuralı: açgözlü çekirdek (D2 kontrol kuralı); değişen tek şey bilgi ve beklenti yuvası.
  Bilgi:    instant (kontrol) | ship (dönen gemi İstanbul fiyatını getirir, limanda herkes duyar)
            | rumor (aynı haber, ama her tüccar her gün %30 olasılıkla duyar)
  Beklenti: last (son gözlem doğru kabul edilir) | dist (yaşla genişleyen log-normal dağılım,
            temkinli tüccar kötü uca bakar) | revert (dist + eski bilgi olağan fiyata döner)

Ek ölçüm: anlık bilgi alan "bilgili oyuncu botu" ile NPC'lerle aynı bilgideki bot arasındaki
getiri farkı = bilginin değeri.

Kullanım:  python3 experiments/d3_information.py   (~4 dk)
Rapor:     docs/experiments/D3.md
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
from experiments.d2_two_ports import agg, metrics, monthly  # noqa: E402
from sim.world import D2Config, D2World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d3"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = range(10)
NS = (15, 40)
CASES = {
    "C0 anlık / son": dict(info_mode="instant", expect_mode="last"),
    "C1 gemi / son": dict(info_mode="ship", expect_mode="last"),
    "C2 söylenti / son": dict(info_mode="rumor", expect_mode="last"),
    "C3 söylenti / dağılım": dict(info_mode="rumor", expect_mode="dist"),
    "C4 söylenti / dağılım+dönüş": dict(info_mode="rumor", expect_mode="revert"),
}
BASE = dict(rule="aware", player_rule="aware", aware_lambda=0.0, add_informed_bot=True)


def run(**kw):
    return D2World(D2Config(**BASE, **kw)).run()


def metrics3(r):
    m = metrics(r)
    ale_last = float(r["ale_ask"][-1])
    bots = [x for x in r["merchants"] if x.is_player]
    ret = lambda x: ((x.net_worth(ale_last) / x.start_capital) ** 0.1 - 1) * 100
    plain = [b for b in bots if not b.informed]
    inf = [b for b in bots if b.informed]
    m["player_return"] = ret(plain[0]) if plain else np.nan
    m["informed_return"] = ret(inf[0]) if inf else np.nan
    m["info_value"] = m["informed_return"] - m["player_return"]
    ages = [a for x in r["merchants"] if not x.is_player for a in x.decision_ages]
    m["info_age_days"] = float(np.mean(ages)) if ages else 0.0
    return m


def main():
    summary = {}
    for name, case in CASES.items():
        for n in NS:
            summary[f"{name} | N{n}"] = agg([metrics3(run(seed=s, n_merchants=n, **case)) for s in SEEDS])
            print(name, n, "ok")

    # İskenderiye'de %30 eksik hasat → İstanbul'a etkisi
    summary["shock"] = {}
    fig, ax = plt.subplots(figsize=(11, 4))
    for name in ("C0 anlık / son", "C2 söylenti / son", "C4 söylenti / dağılım+dönüş"):
        case = CASES[name]
        base = run(seed=0, yield_sigma=0.0, **case)
        shock = run(seed=0, yield_sigma=0.0, ale_yield_overrides={5: 0.7}, **case)
        ratio = monthly(shock["ist_bid"], shock["date"]) / monthly(base["ist_bid"], base["date"])
        months = sorted({(d.year, d.month) for d in base["date"]})
        hm = months.index((1565, 5))
        summary["shock"][name] = [round(float(x), 2) for x in ratio[hm:hm + 15]]
        ax.plot(range(-3, 15), ratio[hm - 3:hm + 15], "-o", ms=3, label=name)
    ax.axvline(0, color="red", ls="--", lw=0.8); ax.axhline(1, color="gray", lw=0.8)
    ax.set_xlabel("İskenderiye hasadından sonraki ay"); ax.set_ylabel("İstanbul fiyatı / şoksuz")
    ax.set_title("İskenderiye'de %30 eksik hasat → İstanbul (N=15)"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "d3_shock.png", dpi=110); plt.close(fig)

    # Fiyat serileri (N=15, seed 1)
    fig, axs = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True)
    for ax, name in zip(axs, ("C0 anlık / son", "C2 söylenti / son", "C4 söylenti / dağılım+dönüş")):
        r = run(seed=1, **CASES[name])
        ax.plot(r["date"], r["ist_bid"], lw=0.8, label="İstanbul (toptan)")
        ax.plot(r["date"], r["ale_ask"], lw=0.8, label="İskenderiye (dükkân satış)")
        ax.set_title(name + ", N=15"); ax.set_ylabel("soldo"); ax.legend(loc="upper left")
    fig.tight_layout(); fig.savefig(OUT / "d3_prices.png", dpi=110); plt.close(fig)

    # Özet çubuk grafik: fırsat günleri ve getiriler
    names = list(CASES)
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))
    x = np.arange(len(names))
    for j, n in enumerate(NS):
        g = lambda k: [summary[f"{nm} | N{n}"][k][0] for nm in names]
        axs[0].bar(x + (j - 0.5) * 0.38, g("opp_days_pct"), 0.38, label=f"N={n}")
        axs[1].bar(x + (j - 0.5) * 0.38, g("player_return"), 0.38, label=f"N={n}")
        axs[2].bar(x + (j - 0.5) * 0.38, g("info_value"), 0.38, label=f"N={n}")
    for ax, t in zip(axs, ("Fırsat açık günler %", "Oyuncu botu getiri %/yıl (NPC ile aynı bilgi)",
                          "Bilginin değeri: bilgili bot − bot (puan)")):
        ax.set_xticks(x); ax.set_xticklabels([nm.split(" ", 1)[0] for nm in names])
        ax.set_title(t, fontsize=10); ax.axhline(0, color="gray", lw=0.8); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "d3_summary.png", dpi=110); plt.close(fig)

    a, b = run(seed=7, **CASES["C4 söylenti / dağılım+dönüş"]), run(seed=7, **CASES["C4 söylenti / dağılım+dönüş"])
    summary["determinism_same_seed"] = bool(np.array_equal(a["ist_bid"], b["ist_bid"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
