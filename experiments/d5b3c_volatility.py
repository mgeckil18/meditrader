"""Experiment D5b3c (diagnostic): why voyage returns are so volatile (decomposition per voyage).
Run (repo root): python3 experiments/d5b3c_volatility.py [N_SEEDS]
Report (Turkish): docs/experiments/D5b3c.md

(Original notes in Turkish below.)

D5b3c teşhis: sefer getirisi neden bu kadar oynak? (sd %40-90, seferlerin ~%10'u −%50'nin altında)

Her seferi (son 5 yıl) bileşenlerine ayırır:
  roi          satış geliri / birim maliyet − 1 (D5b3b-c'deki tanım; geçim gideri dahil)
  roi_nl       geçim gideri geri eklenmiş (ölçüm gürültüsü mü?)
  rerouted     satış, planlanan hedef dışında bir limanda
  dur, wait    toplam süre; yol dışındaki (satış bekleme) süre
  crowd        aynı hedef-mala kalkıştan önceki 20 / sonraki 5 gün içinde kalkan rakip kargo (hedefin günlük talebi cinsinden)
  p_arr        varış günündeki kapan fiyatı / kalkış günündeki hedef kapan fiyatı (yolda fiyat ne oldu)
  fill         ambar doluluğu (q × hacim / kapasite)
  fc_err       gerçekleşen birim gelir / beklenen birim gelir
Ayrıca sermaye ağırlıklı ve zaman payı: sefer getirisi yüksekken yıllık getiri neden ~0?
Kullanım: python3 experiments/d5b3c_volatility.py [seed sayısı]   Çıktı: experiments/out/d5b3c/volatility.json
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5b_diversity import BASE  # noqa: E402
from d5b3c_finance import SETUPS  # noqa: E402
from sim.world5 import D5Config, D5World, GOODS5  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b3c"
LAST = 5 * 365


def run(seed):
    w = D5World(D5Config(seed=seed, **BASE, **SETUPS["OS"]))
    r = w.run()
    cfg = w.cfg
    kap = {k: np.array(r[f"{k[0]}_{k[1]}_kapan"], dtype=float) for k in w.markets}
    deps = {}
    for day, o, d, g, q, lvl in r["departures"]:
        deps.setdefault((d, g), []).append((day, q))
    rows = []
    for day0, day1, g, o, d, q, exp_net, uc, real, lvl, loc, *_ in w.voy_log:
        if day0 < LAST or q <= 0 or uc <= 0:
            continue
        travel = w._voyage(o, d)
        dur = max(day1 - day0, 1)
        roi = real / uc - 1
        roi_nl = (real + cfg.living_cost * dur / q) / uc - 1
        dem = w.demand_L[d][g]
        crowd = sum(qq for dd, qq in deps.get((d, g), []) if day0 - 20 <= dd <= day0 + 5) - q
        a = min(int(day0 + travel), len(kap[(d, g)]) - 1)
        p_arr = kap[(d, g)][a] / max(kap[(d, g)][day0], 1e-9)
        rows.append(dict(g=g, route=f"{o}>{d}", lvl=lvl, roi=roi, roi_nl=roi_nl, rerouted=loc != d,
                         dur=dur, wait=dur - travel, crowd=max(crowd, 0.0) / max(dem, 1e-9),
                         p_arr=p_arr, fill=q * GOODS5[g].bulk / cfg.capacity, fc_err=real / max(exp_net, 1e-9),
                         cap=q * uc))
    # Zaman payı: tüccar-günlerinin ne kadarı alımda / yolda / satışta
    fs = np.array(r["frac_selling"][LAST:], dtype=float)
    fleet = float(np.mean(np.array(r["n_npc"][LAST:], dtype=float)))
    return seed, rows, float(np.mean(fs)), fleet


def describe(rows, label):
    a = lambda k: np.array([x[k] for x in rows], dtype=float)  # noqa: E731
    roi, roi_nl, cap = a("roi"), a("roi_nl"), a("cap")
    return {
        "label": label, "n": len(rows),
        "roi_mean": float(roi.mean()), "roi_median": float(np.median(roi)), "roi_sd": float(roi.std()),
        "roi_p10": float(np.quantile(roi, 0.1)), "loss_frac": float((roi < 0).mean()), "deep_loss_frac": float((roi < -0.5).mean()),
        "roi_capw": float((roi * cap).sum() / cap.sum()),
        "roi_nl_sd": float(roi_nl.std()), "roi_nl_p10": float(np.quantile(roi_nl, 0.1)), "deep_loss_nl": float((roi_nl < -0.5).mean()),
        "rerouted": float(a("rerouted").mean()), "wait_median": float(np.median(a("wait"))),
        "crowd_median": float(np.median(a("crowd"))), "p_arr_median": float(np.median(a("p_arr"))),
        "fill_median": float(np.median(a("fill"))), "fc_err_median": float(np.median(a("fc_err"))),
        "cap_frac_median": float(np.median(cap)) / 240_000, "cap_frac_mean": float(cap.mean()) / 240_000,
    }


def main(n):
    with Pool(n) as pool:
        res = pool.map(run, range(n))
    allr = [x for _, rows, _, _ in res for x in rows]
    roi = np.array([x["roi"] for x in allr])
    fleet = float(np.mean([f for *_, f in res]))
    out = {"frac_selling": float(np.mean([f for _, _, f, _ in res])), "fleet": fleet,
           "voyages_per_ship_year": len(allr) / len(res) / 5 / fleet,
           "all": describe(allr, "bütün seferler"),
           "deep": describe([x for x in allr if x["roi"] < -0.5], "derin zarar (< −%50)"),
           "loss": describe([x for x in allr if -0.5 <= x["roi"] < 0], "zarar (−%50 … 0)"),
           "win": describe([x for x in allr if x["roi"] >= 0], "kâr"),
           "big_win": describe([x for x in allr if x["roi"] >= 1.0], "büyük kâr (≥ %100)")}
    for g in ("WHT", "OIL", "PEP"):
        sub = [x for x in allr if x["g"] == g]
        out[f"good_{g}"] = describe(sub, g) if sub else None
    for L in (0, 1, 2):
        out[f"lvl_{L}"] = describe([x for x in allr if x["lvl"] == L], f"düzey {L}")
    for lo, hi in ((0, 0.25), (0.25, 0.5), (0.5, 0.9), (0.9, 1.01)):
        sub = [x for x in allr if lo <= x["fill"] < hi]
        out[f"fill_{lo}-{hi}"] = describe(sub, f"doluluk {lo}-{hi}") if len(sub) > 10 else None
    cr = np.array([x["crowd"] for x in allr])
    q1, q2 = np.quantile(cr, [1 / 3, 2 / 3])
    out["crowd_low"] = describe([x for x in allr if x["crowd"] <= q1], f"kalabalık ≤ {q1:.1f} gün")
    out["crowd_high"] = describe([x for x in allr if x["crowd"] >= q2], f"kalabalık ≥ {q2:.1f} gün")
    out["corr_roi"] = {k: float(np.corrcoef(roi, [float(x[k]) for x in allr])[0, 1])
                       for k in ("crowd", "p_arr", "fill", "wait", "rerouted", "fc_err")}
    (OUT / "volatility.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    for k, v in out.items():
        print(k, json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
