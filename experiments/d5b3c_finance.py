"""Experiment D5b3c: hybrid merchant finance: own cash, debt, sea loan, colleganza.
Run (repo root): python3 experiments/d5b3c_finance.py YEARS [SETUP,...]
Report (Turkish): docs/experiments/D5b3c.md

(Original notes in Turkish below.)

Deney D5b3c: hibrit tüccar finansmanı (K-022). Kullanıcı notu: tasarım kesin değil, deneyle sınanıyor.

Nakdi gemisini doldurmaya yetmeyen tüccar üç yol arasında seçer: kendi nakdiyle gitmek, liman havuzundan vadeli
borç (faiz = senet + prim + alacaklının öğrendiği beklenen kayıp; kaldıraç ≤ 1; ödeyemeyen batar ve silinir),
ya da yalnızca denetlenebilir ve düşük riskli rota-mal çiftinde colleganza (bütçe, limanın gerçekleşen colleganza
getirisine göre öğrenilir). Seçim: beklenen servet − risk cezası − batma korkusu ("hassas denge").
  OS          taban (D5b3: spin-up + fırsata bağlı giriş, finansman yok)
  D           borç (kargo batsa da ödenir)
  D-sea       deniz ödüncü (kargo batarsa borç düşer; alacaklı deniz riskini taşır)
  D-korkusuz  D, batma korkusu kapalı (ruin_weight = 0; ablasyon)
  DC          D + denetlenebilir colleganza + yatırımcı öğrenmesi
Kullanım: python3 experiments/d5b3c_finance.py 10 [kurulum,...]    Rapor: docs/experiments/D5b3c.md
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5b_diversity import BASE, metrics  # noqa: E402
from d5b3_entry import SETUPS as D3  # noqa: E402
from sim.world5 import D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b3c"
OUT.mkdir(parents=True, exist_ok=True)
OS = dict(D3["OCS"], colleganza=False)
D = dict(OS, debt=True)
SETUPS = {
    "OS": OS,
    "D": D,
    "D-sea": dict(D, loan_type="sea"),
    "D-korkusuz": dict(D, ruin_weight=0.0),
    "DC": dict(D, colleganza=True, colleg_mode="verified"),
}
SEEDS = range(5)
TAG = ""
LAST = 5 * 365
LAST_WORLD = None


def run(args):
    name, seed = args
    global LAST_WORLD
    w = D5World(D5Config(seed=seed, **{**BASE, **SETUPS[name]}))   # kurulum BASE alanlarını ezebilir (D5b3e tam harita)
    r = w.run()
    LAST_WORLD = w                             # D5b3d ek metrikleri için
    out = metrics(w, r)
    n = np.array(r["n_npc"], dtype=float)
    out["fleet_start"], out["fleet_last"] = float(n[0]), float(np.mean(n[-1825:]))
    out["track_last_mean"] = float(np.mean(np.array(r["track"], dtype=float)[-1825:]))
    out["entries"], out["exits"], out["bankruptcies_n"] = r["entries"], r["exits"], r["bankruptcies"]
    out["debt_bankruptcies"] = w.debt_bankruptcies
    # Alacaklı tarafı (son 5 yıl)
    ll = [x for x in w.loan_log if x[0] >= LAST + w.t0_day]
    out["loans_n"] = len(ll)
    capd = sum(x[2] * x[3] for x in ll)
    out["lender_ann"] = sum(x[4] - x[2] for x in ll) / capd * 365 if capd else float("nan")
    out["loan_rate_ann"] = float(np.mean([(x[5] / x[2] - 1) * 365 / x[3] for x in ll])) if ll else float("nan")
    out["default_frac"] = float(np.mean([x[7] for x in ll])) if ll else float("nan")
    out["lost_frac"] = float(np.mean([x[8] for x in ll])) if ll else float("nan")
    for L in (0, 1, 2):
        sub = [x for x in ll if x[6] == L]
        out[f"default_lvl{L}"] = float(np.mean([x[7] for x in sub])) if sub else float("nan")
    # Tüccar kararı: kim borçlanıyor? (son 5 yıl, finansman kararı verilen her plan)
    fl = [x for x in w.fin_log if x[0] >= LAST + w.t0_day]
    out["fin_decisions"] = len(fl)
    for ch in ("debt", "colleg", "none"):
        out[f"choice_{ch}"] = float(np.mean([x[4] == ch for x in fl])) if fl else float("nan")
    for L in (0, 1, 2):
        sub = [x for x in fl if x[1] == L]
        out[f"debt_rate_lvl{L}"] = float(np.mean([x[4] == "debt" for x in sub])) if sub else float("nan")
        out[f"lev_lvl{L}"] = float(np.mean([x[5] for x in sub if x[4] == "debt"])) if any(x[4] == "debt" for x in sub) else float("nan")
    if fl:
        g = np.array([x[2] for x in fl])
        lo, hi = np.quantile(g, [1 / 3, 2 / 3])
        out["debt_rate_ra_low"] = float(np.mean([x[4] == "debt" for x in fl if x[2] <= lo]))
        out["debt_rate_ra_high"] = float(np.mean([x[4] == "debt" for x in fl if x[2] >= hi]))
        out["debt_rate_new"] = float(np.mean([x[4] == "debt" for x in fl if x[3] == 0])) if any(x[3] == 0 for x in fl) else float("nan")
        out["debt_rate_rec"] = float(np.mean([x[4] == "debt" for x in fl if x[3] >= 5])) if any(x[3] >= 5 for x in fl) else float("nan")
    # Colleganza (son 5 yıl)
    cc = [c for c in w.colleg_contracts if c[0] >= LAST + w.t0_day]
    out["colleg_n"] = len(cc)
    cap = sum(c[3] for c in cc)
    out["colleg_ret_capw"] = sum(c[2] * c[3] for c in cc) / cap if cap else float("nan")
    capd = sum(c[3] * c[4] for c in cc)
    out["colleg_ann"] = sum(c[2] * c[3] for c in cc) / capd * 365 if capd else float("nan")
    out["colleg_loss_frac"] = float(np.mean([c[2] < 0 for c in cc])) if cc else float("nan")
    out["colleg_routes"] = len(w.colleg_routes)
    out["colleg_share_end"] = w.colleg_share_now if w.colleg_share_now is not None else float("nan")
    out["pool_end"] = float(sum(w.pool.values()))
    return name, seed, out


def main():
    with Pool(min(20, len(SETUPS) * len(SEEDS))) as pool:
        res = pool.map(run, [(n, s) for n in SETUPS for s in SEEDS])
    summary = {}
    for name in SETUPS:
        rows = [o for n, s, o in res if n == name]
        agg = {k: f"{sum(x[k] for x in rows)}/{len(rows)}" for k in ("exploded", "explode_last", "dearth", "runaway")}
        for k in rows[0]:
            if k not in agg and all(k in x for x in rows):
                agg[k] = float(np.nanmedian([x[k] for x in rows]))
        for k in ("ret_median", "lender_ann", "debt_bankruptcies", "fleet_last"):
            agg[k + "_seeds"] = [round(x[k], 3) for x in rows]
        summary[name] = agg
        print(name, json.dumps(agg, ensure_ascii=False), flush=True)
    (OUT / f"summary{TAG}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        SEEDS = range(int(sys.argv[1]))
    if len(sys.argv) > 2:
        SETUPS = {k: SETUPS[k] for k in sys.argv[2].split(",")}
        TAG = "_" + sys.argv[2].replace(",", "_")
    main()
