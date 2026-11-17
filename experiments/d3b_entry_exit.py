"""Experiment D3b: free entry and exit tied to the bond rate (does zero excess profit emerge?).
Run (repo root): python3 experiments/d3b_entry_exit.py   (~6 min)
Report (Turkish): docs/experiments/D3b.md

(Original notes in Turkish below.)

Deney D3b: senete bağlı serbest giriş-çıkış.

Soru: Kullanıcının çerçevesi (Y10b) "baz ticaret = senet + risk primi; rekabetçi dengede
ekstra kâr yok" serbest giriş-çıkışla kendiliğinden oluşuyor mu? Tüccar nüfusu dengeye mi
oturuyor, döngü mü yapıyor? Başlangıç sayısından bağımsız mı (yol bağımsızlığı)?

Sabit: D3'ün en iyi bilgi kurulumu (C4: söylenti + dağılım + olağana dönüş), açgözlü çekirdek.
Yarışan yuva: giriş dinamiği.
  sabit           tüccar sayısı sabit (D3, kontrol)
  orantılı        giriş ∝ mevcut tüccar sayısı × fazla getiri (Doran-Parberry meslek değiştirme)
  havuz-1, havuz-3  giriş dışarıdan sınırlı akış: ayda en fazla ~1 / ~3 yeni tüccar

Kullanım:  python3 experiments/d3b_entry_exit.py   (~6 dk)
Rapor:     docs/experiments/D3b.md
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

OUT = ROOT / "experiments" / "out" / "d3b"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = range(5)
YEARS = 20
N0S = (5, 15, 40)
C4 = dict(rule="aware", player_rule="aware", aware_lambda=0.0, add_informed_bot=True,
          info_mode="rumor", expect_mode="revert", dividends=True, years=YEARS)
STRUCTS = {
    "sabit": dict(free_entry=False),
    "orantılı": dict(free_entry=True, entry_mode="proportional"),
    "havuz-1": dict(free_entry=True, entry_mode="pool", entry_pool=1.0, exit_prob=0.1),
    "havuz-3": dict(free_entry=True, entry_mode="pool", entry_pool=3.0, exit_prob=0.1),
}


def run_world(**kw):
    w = D2World(D2Config(**C4, **kw))
    r = w.run()
    r["ledger"] = w.ledger
    r["capital"] = int(w.cfg.capacity * 100 * w.cfg.capital_mult)
    return r


def metrics(r, n0):
    last = slice(-10 * 365, None)
    n = r["n_npc"].astype(float)
    L = r["ledger"]
    ale_last = float(r["ale_ask"][-1])
    npc = [m for m in r["merchants"] if not m.is_player]
    # Sektör getirisi: hayatta kalanlar yanılgısı olmadan, tüm tüccar sermayesinin yıllık getirisi
    money_in = n0 * r["capital"] + L.money_in.get("from_bonds", 0) + L.money_in.get("merchant_entry", 0)
    # Kâr payları defterden alınır: çıkan tüccarların daha önce çektiği paylar da sayılır.
    bot_divs = sum(m.divs for m in r["merchants"] if m.is_player)
    money_out = (L.money_out.get("to_bonds", 0) + L.money_out.get("merchant_exit", 0)
                 + L.money_out.get("merchant_dividends", 0) - bot_divs
                 + sum(m.net_worth(ale_last) for m in npc))
    deployed = max(np.mean(n), 1.0) * r["capital"]
    sector = (money_out - money_in) / deployed / YEARS * 100
    bots = [m for m in r["merchants"] if m.is_player]
    ret = lambda m: (((m.net_worth(ale_last) + m.divs) / m.start_capital) ** (1 / YEARS) - 1) * 100
    plain = [b for b in bots if not b.informed][0]
    inf = [b for b in bots if b.informed][0]
    return dict(
        n_mean=float(np.mean(n[last])), n_cv=float(np.std(n[last]) / max(np.mean(n[last]), 1e-9)),
        n_min=float(np.min(n[last])), n_max=float(np.max(n[last])),
        survivor_return=float(np.mean(r["trailing_median"][last]) * 100),
        sector_return=float(sector),
        player_return=ret(plain), informed_return=ret(inf),
        opp_days_pct=float(np.mean(r["margin_now"][last] > 0.10) * 100),
        ist_shortage=float(np.mean(r["ist_shortage"][last]) * 100),
        entries_per_year=r["entries"] / YEARS, exits_per_year=r["exits"] / YEARS,
        bankruptcies_per_year=r["bankruptcies"] / YEARS,
    )


def main():
    summary, series = {}, {}
    for sname, sk in STRUCTS.items():
        for n0 in N0S:
            rows = []
            for seed in SEEDS:
                r = run_world(seed=seed, n_merchants=n0, **sk)
                rows.append(metrics(r, n0))
                if seed == 1:
                    series[(sname, n0)] = (r["date"], r["n_npc"], r["trailing_median"])
            summary[f"{sname} | N0={n0}"] = {k: float(np.median([x[k] for x in rows])) for k in rows[0]}
            print(sname, n0, "ok")

    fig, axs = plt.subplots(len(STRUCTS) - 1, 1, figsize=(11, 9), sharex=True)
    for ax, sname in zip(axs, [s for s in STRUCTS if s != "sabit"]):
        for n0 in N0S:
            d, n, _ = series[(sname, n0)]
            ax.plot(d, n, lw=0.9, label=f"başlangıç N={n0}")
        ax.set_title(f"Giriş yapısı: {sname} (seed 1)"); ax.set_ylabel("NPC tüccar sayısı"); ax.legend(loc="upper right")
    fig.tight_layout(); fig.savefig(OUT / "d3b_population.png", dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4))
    names = list(STRUCTS)
    x = np.arange(len(names))
    for j, k in enumerate(("sector_return", "player_return", "informed_return")):
        ax.bar(x + (j - 1) * 0.27, [summary[f"{s} | N0=15"][k] for s in names], 0.27,
               label={"sector_return": "sektör (tüm tüccarlar)", "player_return": "oyuncu botu",
                      "informed_return": "bilgili oyuncu botu"}[k])
    ax.axhline(4, color="gray", ls="--", lw=0.8); ax.text(len(names) - 0.6, 4.4, "senet %4", fontsize=8)
    ax.axhline(8, color="gray", ls=":", lw=0.8); ax.text(len(names) - 0.6, 8.4, "senet + risk %8", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylabel("yıllık getiri %"); ax.legend()
    ax.set_title("Getiriler (başlangıç N=15, 20 yıl, 5 seed medyanı)")
    fig.tight_layout(); fig.savefig(OUT / "d3b_returns.png", dpi=110); plt.close(fig)

    a = run_world(seed=7, n_merchants=15, **STRUCTS["havuz-1"])
    b = run_world(seed=7, n_merchants=15, **STRUCTS["havuz-1"])
    summary["determinism_same_seed"] = bool(np.array_equal(a["ist_bid"], b["ist_bid"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
