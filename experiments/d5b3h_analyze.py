"""Experiment D5b3h (analysis): means and 95% confidence intervals across seeds; three return measures; pattern metrics.
Run (repo root): DIAG_OUT=d5b3h python3 experiments/d5b3h_analyze.py A,B,...
Report (Turkish): docs/experiments/D5b3h.md

(Original notes in Turkish below.)

D5b3h (Ö0) çözümleme: seed'ler arası ortalama ve %95 güven aralığı; üç getiri ölçüsü; örüntü ölçütleri.

Kullanım: DIAG_OUT=d5b3h python3 experiments/d5b3h_analyze.py A,B,...
Örüntü ölçütleri (pattern-oriented modeling; Grimm ve ark. 2005): tek bir hedef sayı yerine birden çok örüntü.
"""
import json
import math
import os
import pathlib
import statistics as st
import sys

OUT = pathlib.Path(__file__).resolve().parents[1] / "experiments" / "out" / os.environ.get("DIAG_OUT", "d5b3h")

# Student t, iki yönlü %95, df = 1..30
T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131,
       2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def skew(v):
    if len(v) < 3:
        return None
    m, s = st.mean(v), st.pstdev(v)
    return sum((x - m) ** 3 for x in v) / len(v) / s ** 3 if s > 0 else None


def cycle_period(f):
    """Filonun baskın döngü süresi (ay): ortalaması çıkarılmış serinin otokorelasyonunda, ilk negatif değerden
    sonraki ilk yerel tepe. Döngü yoksa None."""
    n = len(f)
    m = st.mean(f)
    x = [v - m for v in f]
    v0 = sum(a * a for a in x)
    if v0 == 0:
        return None
    acf = [sum(x[i] * x[i + L] for i in range(n - L)) / v0 for L in range(n // 2)]
    neg = next((L for L, a in enumerate(acf) if a < 0), None)
    if neg is None:
        return None
    for L in range(neg + 1, len(acf) - 1):
        if acf[L] >= acf[L - 1] and acf[L] >= acf[L + 1] and acf[L] > 0:
            return L
    return None


def per_run(r):
    t0 = r.get("t0", 0)
    yrs = (len(r["fleet"]) - 1) / 12
    fleet = r["fleet"]
    fm = st.mean(fleet)
    rets = r["rets"]
    rets = [x[:3] for x in rets]
    W = sum(w for _, w, _ in rets)
    agg_eq = sum(x * w for x, w, _ in rets) / W
    inc = [(x, w) for x, w, i in rets if i]
    ent = [(x, w) for x, w, i in rets if not i]
    pub = [x[1] for x in r["pub_log"] if x[0] >= t0 and x[1] is not None]
    cred = r.get("cred_log", [])
    ks = [x[1] for x in cred]
    ship_yrs = fm * yrs
    o = dict(
        agg_old=r["agg"],
        agg_eq=agg_eq,
        agg_incumbent=sum(x * w for x, w in inc) / max(sum(w for _, w in inc), 1e-9),
        agg_entrant=sum(x * w for x, w in ent) / max(sum(w for _, w in ent), 1e-9) if ent else None,
        public_track_mean=st.mean(pub) if pub else None,
        entrant_ret_median=st.median([x for x, _ in ent]) if ent else None,
        ret_skew=skew([x for x, _, _ in rets]),
        ret_frac_neg=sum(1 for x, _, _ in rets if x < 0) / len(rets),
        entry_rate=r["entries"] / ship_yrs,
        exit_rate=r["exits"] / ship_yrs,
        bankr_rate=r["bankruptcies"] / ship_yrs,
        fleet_mean=fm,
        fleet_cv=st.pstdev(fleet) / fm,
        fleet_peak_trough=max(fleet) / max(min(fleet), 1),
        cycle_months=cycle_period(fleet),
    )
    dl = r.get("dep_log", [])
    if dl:                                  # R1: gerçekleşen deniz kaybı örüntüleri
        lost = [x for x in dl if x[3]]
        win = [x for x in dl if x[5] in (11, 12, 1, 2)]
        o["loss_rate"] = len(lost) / len(dl)
        o["loss_corsair_share"] = sum(1 for x in lost if x[4] == "corsair") / len(lost) if lost else None
        o["winter_dep_share"] = len(win) / len(dl)
        o["loss_rate_winter"] = sum(1 for x in win if x[3]) / len(win) if win else None
        o["voyages_per_ship_year"] = len(dl) / ship_yrs
    sl = r.get("ship_log", [])
    if sl:                                  # Ö3: gemi piyasası örüntüleri
        px = [x[1] for x in sl]
        o["ship_px_mean"] = st.mean(px)
        o["ship_px_cv"] = st.pstdev(px) / st.mean(px) if st.mean(px) > 0 else None
        o["ship_px_min"], o["ship_px_max"] = min(px), max(px)
        o["ships_listed_mean"] = st.mean(x[2] for x in sl)
        o["ship_trades_per_yr"] = sum(x[3] for x in sl) / yrs
        o["newbuild_per_yr"] = sum(x[4] + x[5] for x in sl) / yrs
        o["foreign_per_yr"] = sum(x[12] for x in sl) / yrs if len(sl[0]) > 12 else None
        o["scrap_per_yr"] = sum(x[7] + x[8] for x in sl) / yrs
        o["rebuy_exit_per_yr"] = sum(x[10] for x in sl) / yrs
        o["yard_queue_days"] = st.mean(x[9] for x in sl)
        o["ships_lost_per_ship_yr"] = r.get("ships_lost", 0) / ship_yrs
        pubm = {x[0]: x[1] for x in r["pub_log"] if x[1] is not None}
        pairs = [(x[1], pubm[x[0]]) for x in sl if x[0] in pubm]
        if len(pairs) > 3:                  # fiyat kamu siciline (getiri beklentisine) ne kadar bağlı
            a, b = zip(*pairs)
            ma, mb = st.mean(a), st.mean(b)
            va, vb = st.pstdev(a), st.pstdev(b)
            o["corr_px_track"] = sum((x - ma) * (y - mb) for x, y in pairs) / len(pairs) / (va * vb) if va * vb > 0 else None
        if r.get("ship_ages"):
            o["ship_age_mean"] = st.mean(r["ship_ages"])
    if ks:
        o["cred_k_inf_frac"] = sum(1 for k in ks if math.isinf(k)) / len(ks)
        fin = [k for k in ks if not math.isinf(k)]
        o["cred_Z12_median"] = st.median([12 / (12 + k) if not math.isinf(k) else 0.0 for k in ks])
        o["cred_k_median_finite"] = st.median(fin) if fin else None
        kq = [x[5] for x in cred if len(x) > 5]
        o["cred_kq_inf_frac"] = sum(1 for k in kq if k is None or math.isinf(k)) / len(kq) if kq else None
    return o


def ci(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    m = st.mean(v)
    if len(v) < 2:
        return m, None, len(v)
    h = T95[min(len(v) - 1, 30) - 1] * st.stdev(v) / math.sqrt(len(v))
    return m, h, len(v)


def summarize(name):
    d, _, n = name.rpartition(":")         # "dizin:kurulum" başka bir deneyin çıktısını karşılaştırmak için
    root = OUT.parent / d if d else OUT
    runs = [json.load(open(f)) for f in sorted(root.glob(f"{n}_*.json"))]
    if not runs:
        return None
    P = [per_run(r) for r in runs]
    keys = list(dict.fromkeys(k for p in P for k in p))
    return {k: ci([p.get(k) for p in P]) for k in keys}


def fmt(c):
    if c is None:
        return "-"
    m, h, n = c
    if h is None:
        return f"{m:.3f}"
    return f"{m:.3f}±{h:.3f}"


if __name__ == "__main__":
    names = sys.argv[1].split(",")
    res = {n: summarize(n) for n in names}
    keys = list(dict.fromkeys(k for v in res.values() if v for k in v))
    seeds = {n: (max(c[2] for c in v.values() if c) if v else 0) for n, v in res.items()}
    print(f"{'':24s}" + "".join(f"{n + ' (' + str(seeds[n]) + ')':>20s}" for n in names))
    for k in keys:
        print(f"{k:24s}" + "".join(f"{fmt(res[n].get(k)) if res[n] else '-':>20s}" for n in names))
    json.dump({n: v for n, v in res.items()}, open(OUT / f"summary_{'_'.join(x.replace(':', '-') for x in names)}.json", "w"), indent=1, default=str)
