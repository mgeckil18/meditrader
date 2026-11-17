"""Experiment D1g: fixing the seasonal price pattern (symmetric, PI-type price adjustment).
Run (repo root): python3 experiments/d1g_symmetry.py   (~4 min)
Report (Turkish): docs/experiments/D1g.md

(Original notes in Turkish below.)

Deney D1g: Mevsim desenini düzeltmek (fiyat ayarında simetri ve faz).

D1f sonunda (F) şoksuz dünyada mevsim deseni tersti: en pahalı ay Ağustos.
Teşhis: dükkâncı fiyatı kıtlığın İNTEGRALİNE göre ayarlıyordu (çeyrek dalga gecikme)
ve köylü satışlarını sezona eşit yayıyordu (mevsimsel kıtlık sinyali yoktu).

Eklenenler (ablasyonla):
  fl  köylünün hasat sonrası nakit ihtiyacı (satışlar sezon başında yoğun)
  es  fazla arz sinyali (yerine koyma maliyetinin aşağı yönlü simetriği)
  P   PI kontrolün oransal bileşeni (bugünkü kıtlığa anında fiyat tepkisi)

Kullanım:  python3 experiments/d1g_symmetry.py   (~4 dk)
Rapor:     docs/experiments/D1g.md
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
from experiments.d1_single_port import KD_TABLE, aggregate, metrics, run  # noqa: E402
from experiments.d1f_storer import (MONTHS, harvest_index, kd_curve, season_profile,  # noqa: E402
                                    shock_response, storer_return)
from sim.engine import F, H, V3  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d1g"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = range(20)

FL, ES, P = dict(farmer_front_load=0.3), dict(excess_supply_rate=0.1), dict(prop_gain=0.2)
VARIANTS = {
    "A  V3 (D1)": V3,
    "F  D1f sonu": F,
    "F+fl": dict(F, **FL),
    "F+fl+P": dict(F, **FL, **P),
    "F+fl+es": dict(F, **FL, **ES),
    "G  F+fl+es+P": dict(F, **FL, **ES, **P),
    "H  F+fl+P(.1)+medyan": H,
}


def main():
    summary = {}
    profiles = {}
    for kap in (0.005, 0.01):
        summary[kap] = {}
        for name, v in VARIANTS.items():
            kw = dict(v, kappa=kap)
            agg = aggregate([metrics(run(s, **kw)) for s in SEEDS])
            p0 = season_profile(dict(kw, yield_sigma=0.0), seeds=range(1))
            row = {"agg": agg, "season_noshock": p0.round(3).tolist(),
                   "cheapest": MONTHS[int(p0.argmin())], "dearest": MONTHS[int(p0.argmax())],
                   "season_amplitude": float(p0.max() / p0.min())}
            if agg["monthly_vol"] is not None:
                row["shock"], _, _ = shock_response(kw)
                row["kd"] = kd_curve(kw)
                row["storer_annual_return"] = storer_return(kw) if v.get("n_storers") else None
            summary[kap][name] = row
            profiles[(kap, name)] = p0
            print(kap, name, "ok")

    kap = 0.01
    fig, ax = plt.subplots(figsize=(11, 4))
    names = ("A  V3 (D1)", "F  D1f sonu", "H  F+fl+P(.1)+medyan")
    w = 0.27
    for j, name in enumerate(names):
        ax.bar(np.arange(12) + (j - 1) * w, profiles[(kap, name)], width=w, label=name)
    ax.set_xticks(range(12)); ax.set_xticklabels(MONTHS); ax.axhline(1, color="gray", lw=0.8)
    ax.axvline(4 - 0.5, color="red", lw=0.8, ls="--")   # Temmuz başı hasat
    ax.set_ylim(0.75, 1.25); ax.legend()
    ax.set_title("Şoksuz mevsim profili, κ=0.01 (kesikli çizgi: hasat). Hedef: ucuz Ağu-Eyl, pahalı May-Haz")
    fig.tight_layout(); fig.savefig(OUT / "d1g_season.png", dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for name in ("F  D1f sonu", "H  F+fl+P(.1)+medyan"):
        _, base, shock = shock_response(dict(VARIANTS[name], kappa=kap))
        ax.plot(shock["date"], shock["ask_mean"], lw=1, label=f"{name} — %30 eksik hasat")
    ax.plot(base["date"], base["ask_mean"], color="gray", lw=0.8, ls=":", label="H — şoksuz")
    ax.axvline(base["date"][harvest_index(base)], color="red", lw=0.8, ls="--")
    ax.set_ylabel("soldo / birim"); ax.legend(loc="upper left")
    ax.set_title("1565 kötü hasadına tepki, κ=0.01")
    fig.tight_layout(); fig.savefig(OUT / "d1g_shock.png", dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    xs = list(KD_TABLE)
    ax.plot([x * 100 for x in xs], [KD_TABLE[x] * 100 for x in xs], "k--o", label="King-Davenant (1699)")
    for kp in (0.005, 0.01):
        for name in ("F  D1f sonu", "H  F+fl+P(.1)+medyan"):
            kd = summary[kp][name]["kd"]
            ax.plot([x * 100 for x in xs], [kd[x] * 100 for x in xs], "-o", ms=3, label=f"{name}, κ={kp}")
    ax.set_xlabel("hasat eksiği %"); ax.set_ylabel("12 ay ort. fiyat artışı %"); ax.legend(fontsize=8)
    ax.set_title("Hasat şokuna fiyat tepkisi")
    fig.tight_layout(); fig.savefig(OUT / "d1g_king_davenant.png", dpi=110); plt.close(fig)

    a, b = run(7, **H, kappa=0.01), run(7, **H, kappa=0.01)
    summary["determinism_same_seed"] = bool(np.array_equal(a["ask_mean"], b["ask_mean"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
