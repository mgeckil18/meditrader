"""Experiment D2: two ports, travelling merchants, instant information (law of one price).
Run (repo root): python3 experiments/d2_two_ports.py   (~4 min)
Report (Turkish): docs/experiments/D2.md

(Original notes in Turkish below.)

Deney D2: iki liman, tek mal, gezgin tüccarlar; bilgi ANLIK.

Sorular:
  S1  Taşıma, limanlar arası fiyat farkını taşıma maliyetine yaklaştırıyor mu (tek fiyat yasası)?
  S2  Fırsatlar yaşıyor mu, yoksa NPC tüccarlar hepsini yiyor mu (Bannerlord sorunu)?
  S3  Tüccar karar kuralları (greedy / dp / utility) bu sorulara nasıl farklı cevap veriyor?

Parametreler varsayılan; ince ayar yok (docs/experiments/README.md).
Kullanım:  python3 experiments/d2_two_ports.py   (~4 dk)
Rapor:     docs/experiments/D2.md
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
from sim.world import D2Config, D2World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d2"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = range(10)
RULES = ("greedy", "dp", "utility")
NS = (5, 15, 40)
OPP = 0.10          # "fırsat": tüm maliyetler sonrası %10'dan fazla beklenen marj


def run(**kw):
    return D2World(D2Config(**kw)).run()


def monthly(a, dates):
    keys = [(d.year, d.month) for d in dates]
    out, cur, buf = [], keys[0], []
    for k, v in zip(keys, a):
        if k != cur:
            out.append(np.nanmean(buf)); buf, cur = [], k
        buf.append(v)
    out.append(np.nanmean(buf))
    return np.array(out)


def run_lengths(mask):
    runs, n = [], 0
    for x in mask:
        if x:
            n += 1
        elif n:
            runs.append(n); n = 0
    if n:
        runs.append(n)
    return runs


def metrics(r, years=10):
    s = slice(365, None)
    ist, ale = r["ist_bid"], r["ale_ask"]
    exploded = bool(np.nanmax(ist) > 10 * np.nanmedian(ist) or np.nanmax(ale) > 10 * np.nanmedian(ale))
    mi, ma = monthly(ist, r["date"])[12:], monthly(ale, r["date"])[12:]
    opp = r["margin_now"][s] > OPP
    runs = run_lengths(opp)
    arr_m = monthly(r["arrivals"], r["date"])[12:]
    npc = [m for m in r["merchants"] if not m.is_player]
    npc_ret = [(m.net_worth(float(ale[-1])) / m.start_capital) ** (1 / years) - 1 for m in npc] if npc else []
    pl = [m for m in r["merchants"] if m.is_player]
    pl_ret = ((pl[0].net_worth(float(ale[-1])) / pl[0].start_capital) ** (1 / years) - 1) if pl else np.nan
    return dict(
        exploded=exploded,
        ist_shortage=float(np.mean(r["ist_shortage"][s]) * 100),
        ist_price=float(np.nanmean(ist[s])), ale_price=float(np.nanmean(ale[s])),
        ist_vol=float(np.nanstd(np.diff(np.log(mi))) * np.sqrt(12)),
        ale_vol=float(np.nanstd(np.diff(np.log(ma))) * np.sqrt(12)),
        spread_ratio=float(np.nanmedian(r["spread_ratio"][s])),
        opp_days_pct=float(opp.mean() * 100),
        opp_run_days=float(np.mean(runs)) if runs else 0.0,
        arrivals_cv=float(np.std(arr_m) / np.mean(arr_m)) if np.mean(arr_m) > 0 else np.nan,
        npc_return=float(np.median(npc_ret)) * 100 if npc_ret else np.nan,
        player_return=float(pl_ret) * 100,
        bankruptcies_per_year=r["bankruptcies"] / years,
    )


def agg(rows):
    ok = [x for x in rows if not x["exploded"]]
    out = {"exploded": f"{len(rows) - len(ok)}/{len(rows)}"}
    for k in rows[0]:
        if k == "exploded":
            continue
        vals = [x[k] for x in ok if not np.isnan(x[k])]
        out[k] = (float(np.median(vals)), float(np.percentile(vals, 10)), float(np.percentile(vals, 90))) if vals else None
    return out


def main():
    summary = {"none": agg([metrics(run(seed=s, rule="none")) for s in SEEDS])}
    for rule in RULES:
        for n in NS:
            summary[f"{rule}_N{n}"] = agg([metrics(run(seed=s, rule=rule, n_merchants=n)) for s in SEEDS])
            print(rule, n, "ok")

    # Kötü hasat: İskenderiye 1565 hasadı %30 eksik, verim gürültüsü kapalı, N=15
    summary["shock"] = {}
    fig, ax = plt.subplots(figsize=(11, 4))
    for rule in RULES:
        base = run(seed=0, rule=rule, yield_sigma=0.0)
        shock = run(seed=0, rule=rule, yield_sigma=0.0, ale_yield_overrides={5: 0.7})
        h = next(i for i, d in enumerate(base["date"]) if d.year == 1565 and d.month == 5)
        ratio = monthly(shock["ist_bid"], shock["date"]) / monthly(base["ist_bid"], base["date"])
        hm = next(i for i, d in enumerate(sorted({(d.year, d.month) for d in base["date"]})) if d == (1565, 5))
        summary["shock"][rule] = [round(float(x), 2) for x in ratio[hm:hm + 15]]
        ax.plot(range(-3, 15), ratio[hm - 3:hm + 15], "-o", ms=3, label=rule)
    ax.axvline(0, color="red", ls="--", lw=0.8); ax.axhline(1, color="gray", lw=0.8)
    ax.set_xlabel("İskenderiye hasadından sonraki ay"); ax.set_ylabel("İstanbul fiyatı / şoksuz")
    ax.set_title("İskenderiye'de %30 eksik hasat → İstanbul'a etkisi (N=15, anlık bilgi)"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "d2_shock.png", dpi=110); plt.close(fig)

    # Fiyat serileri, N=15, seed 1
    fig, axs = plt.subplots(4, 1, figsize=(11, 11), sharex=True)
    r = run(seed=1, rule="none")
    axs[0].plot(r["date"], r["ist_bid"], lw=0.8, label="İstanbul (toptan)")
    axs[0].plot(r["date"], r["ale_ask"], lw=0.8, label="İskenderiye (dükkân satış)")
    axs[0].set_title("Ticaret yok"); axs[0].set_yscale("log"); axs[0].legend(loc="upper left")
    for ax, rule in zip(axs[1:], RULES):
        r = run(seed=1, rule=rule)
        ax.plot(r["date"], r["ist_bid"], lw=0.8, label="İstanbul (toptan)")
        ax.plot(r["date"], r["ale_ask"], lw=0.8, label="İskenderiye (dükkân satış)")
        ax.set_title(f"Kural: {rule}, N=15"); ax.set_ylabel("soldo")
    fig.tight_layout(); fig.savefig(OUT / "d2_prices.png", dpi=110); plt.close(fig)

    # Fırsat ve getiri, N'e göre
    fig, axs = plt.subplots(1, 3, figsize=(14, 3.8))
    for rule in RULES:
        get = lambda k: [summary[f"{rule}_N{n}"][k][0] for n in NS]
        axs[0].plot(NS, get("opp_days_pct"), "-o", label=rule)
        axs[1].plot(NS, get("npc_return"), "-o", label=rule)
        axs[2].plot(NS, get("player_return"), "-o", label=rule)
    axs[0].set_title(f"Fırsat açık günler % (marj > %{int(OPP*100)})")
    axs[1].set_title("NPC tüccar yıllık getiri % (medyan)")
    axs[2].set_title("Oyuncu botu (greedy) yıllık getiri %")
    for ax in axs:
        ax.set_xlabel("NPC tüccar sayısı"); ax.axhline(0, color="gray", lw=0.8); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "d2_opportunity.png", dpi=110); plt.close(fig)

    a, b = run(seed=7, rule="utility"), run(seed=7, rule="utility")
    summary["determinism_same_seed"] = bool(np.array_equal(a["ist_bid"], b["ist_bid"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
