"""Experiment D5b3d: per-voyage lender pricing, ruin risk in equity, ship costs.
Run (repo root): python3 experiments/d5b3d_lender_entry.py YEARS [SETUP,...]
Report (Turkish): docs/experiments/D5b3d.md

(Original notes in Turkish below.)

Deney D5b3d: sefer bazlı alacaklı (K-023) + öz sermayede batma riski ve gemi masrafı (K-024).
Kullanıcı notu: tasarımlar kesin değil, deneyle sınanıyor.

  D'   D5b3c'nin D'si + ölçüm düzeltmesi (sefer getirisi geçim/gemi giderinden arındırılmış; risk sermayeye göre)
  V    D' + sefer bazlı alacaklı (Rialto: başvurular + kamuya açık bilgi; sıralı fiyatlama; credit rationing; sinyal)
  VR   V + giriş ve kalma kararı kamuya açık iflas sıklığını tartar
  VS   V + gemi masrafı (günde 40 ⚠️, sermayenin yılda ~%6'sı)
  VRS  V + ikisi
Sorular: alacaklı senet + marjı kazanıyor mu? Kalabalık ve oynaklık azalıyor mu? Getiri hedefe (~%8) yaklaşıyor mu?
Kullanım: python3 experiments/d5b3d_lender_entry.py 10 [kurulum,...]    Rapor: docs/experiments/D5b3d.md
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import d5b3c_finance as C  # noqa: E402
from d5b_diversity import BASE  # noqa: E402
from sim.world5 import D5Config, D5World, GOODS5  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b3d"
OUT.mkdir(parents=True, exist_ok=True)
D1 = dict(C.SETUPS["D"], record_net_overhead=True)
V = dict(D1, loan_pricing="voyage")
SETUPS = {
    "D'": D1,
    "V": V,
    "VR": dict(V, entry_ruin=True),
    "VS": dict(V, ship_cost_day=40.0),
    "VRS": dict(V, entry_ruin=True, ship_cost_day=40.0),
}
SEEDS = range(5)
TAG = ""
LAST = 5 * 365


def run(args):
    name, seed = args
    C.SETUPS = {**C.SETUPS, name: SETUPS[name]}
    _, _, out = C.run((name, seed))           # D5b3c metrikleri (aynı dünya, aynı seed)
    w = C.LAST_WORLD
    cfg = w.cfg
    out["rationed"] = w.rationed
    ll = [x for x in w.loan_log if x[0] >= LAST + w.t0_day and x[9] is not None]
    out["pd_pred_mean"] = float(np.mean([x[9] for x in ll])) if ll else float("nan")
    out["calib_mean"] = float(np.mean(list(w.lender_calib.values()))) if w.lender_calib else float("nan")
    out["ruin_price_end"] = w._ruin_price() if cfg.entry_ruin else float("nan")
    # Oynaklık ve kalabalık (D5b3c T2 ölçütleri; marj geçim gideri hariç)
    deps = {}
    for day, o, d, g, q, lvl in w.departures:
        deps.setdefault((d, g), []).append((day, q))
    rows = []
    for x in w.voy_log:
        day0, day1, g, o, d, q, exp_net, uc, real, lvl, loc, margin = x
        if day0 < LAST + w.t0_day or q <= 0 or uc <= 0:
            continue
        crowd = sum(qq for dd, qq in deps.get((d, g), []) if day0 - 20 <= dd <= day0 + 5) - q
        rows.append((margin, max(crowd, 0.0) / max(w.demand_L[d][g], 1e-9), q * GOODS5[g].bulk / cfg.capacity, q * uc))
    mg = np.array([r[0] for r in rows])
    cap = np.array([r[3] for r in rows])
    out["voy_n"] = len(rows)
    out["margin_sd"], out["margin_capw"] = float(mg.std()), float((mg * cap).sum() / cap.sum())
    out["deep_loss"], out["loss_frac"] = float((mg < -0.5).mean()), float((mg < 0).mean())
    out["crowd_median"] = float(np.median([r[1] for r in rows]))
    out["fill_median"] = float(np.median([r[2] for r in rows]))
    out["cap_frac_mean"] = float(cap.mean() / cfg.capital)
    fleet = out["fleet_last"]
    out["voy_per_ship_year"] = len(rows) / 5 / max(fleet, 1.0)
    # D5b3d T1: sermaye-yıl ağırlıklı toplam getiri (batanlar dahil). Ömür boyu getiri medyanı kısa ömürlü
    # başarısız girişlerle çarpık; "ticarete konan sermaye ne kazanıyor" sorusunun ölçütü bu
    end = w.day
    ppl = [(m, end, m.net_worth()) for m in w.merchants if not m.is_player] + [g for g in w.gone if not g[0].is_player]
    # D5b3g: snapshot'tan başlayan koşuda ölçüm snapshot anından (v0, t0); yeni girenler için start_capital, born_day
    pnl = np.array([v + m.divs - (m.v0 or m.start_capital) for m, d_, v in ppl])
    capy = np.array([(m.v0 or m.start_capital) * max((d_ - max(m.born_day, m.t0)) / 365.0, 1 / 365) for m, d_, v in ppl])
    out["agg_return"] = float(pnl.sum() / capy.sum())
    out["neg_share"] = float(np.mean([lr < 0 for lr in [(max(v + m.divs, 1.0) / m.start_capital) ** (1 / max((d_ - m.born_day) / 365.0, 0.5)) - 1 for m, d_, v in ppl]]))
    srt = np.sort(pnl)[::-1]
    out["top10_pnl_share"] = float(srt[: max(1, len(srt) // 10)].sum() / max(srt[srt > 0].sum(), 1.0))
    # Brüt-ömür boyu getiri farkı (D5b3c T2'de açıklanamadı): kaba brüt tahmin
    overhead = (cfg.living_cost + cfg.ship_cost_day) * 365 / cfg.capital
    out["gross_est"] = out["margin_capw"] * out["cap_frac_mean"] * out["voy_per_ship_year"] - overhead
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
        for k in ("ret_median", "agg_return", "lender_ann", "debt_bankruptcies", "fleet_last", "gross_est"):
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
