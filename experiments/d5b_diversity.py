"""Experiment D5b: merchant diversity (level-k, imitation, overconfidence) and rumours of rival loadings.
Run (repo root): python3 experiments/d5b_diversity.py   (~4 min)
Report (Turkish): docs/experiments/D5b.md

(Original notes in Turkish below.)

Deney D5b: tüccar çeşitliliği ve rakip yüklemelerinin söylentiyle yayılması (K-014).

Soru: Homojen ve rakiplerinden habersiz tüccarlar en kârlı nişe sürü hâlinde koşuyor (D5, D5a3: yüklü 23 gemiden 19'u yağ).
Çeşitlilik (düşünme derinliği, taklit, servete bağlı risk, aşırı güven, ağ genişliği) ve "X, Y'ye Z yükledi" söylentisi
bu herding'i tamponluyor mu (El Farol / minority game), yoksa taklit çağlayan mı doğuruyor?
Kurulum: D5a3'ün dünyası (REL perakende + fiyat keşfi) + biber (İskenderiye'den, değerli ve küçük hacimli niş).
  H0  homojen, düzey 0, rakip bilgisi yok (önceki deneylerin tüccarı)
  H1  homojen, hepsi düzey 1, rakip bilgisi var
  D   çeşitli kişilikler + rakip bilgisi
  DN  D, taklit kapalı (ablasyon: çağlayanın kaynağı taklit mi?)
Kullanım:  python3 experiments/d5b_diversity.py   (~4 dk)
Rapor:     docs/experiments/D5b.md
"""
import json
import pathlib
import sys
from collections import Counter
from multiprocessing import Pool

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5a3_discovery import VARIANTS  # noqa: E402
from sim.world5 import CUSTOMS, FREIGHT_PER_BULK_DAY, GOODS5, D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b"
OUT.mkdir(parents=True, exist_ok=True)
BASE = dict(ports=["VEN", "COR", "ALE"], goods=["WHT", "OIL", "PEP"], years=10, wholesale=True,
            direct_farm_buying=False, dock_sales=False, recapitalize=False, share_depth=False,
            **VARIANTS["REL+PD"])
SETUPS = {
    "H0 homojen": dict(),
    "H1 homojen düzey 1": dict(rival_info=True, homog_level=1),
    "D çeşitli": dict(rival_info=True, diversity=True),
    "DN çeşitli taklitsiz": dict(rival_info=True, diversity=True, imitation_on=False),
}
ROUTES = {"WHT": ("ALE", "VEN"), "OIL": ("COR", "VEN"), "PEP": ("ALE", "VEN")}
SEEDS = range(5)
LAST = slice(-1825, None)
Y0 = 1565


def lifetime_return(m, end_day, value):
    years = max((end_day - m.born_day) / 365.0, 0.5)
    return (max(value + m.divs, 1.0) / m.start_capital) ** (1 / years) - 1


def metrics(w, r):
    out = {"exploded": False, "dearth": False, "runaway": False, "explode_last": False}
    for (p, g) in w.markets:
        ret = np.array(r[f"{p}_{g}_retail"], dtype=float) / GOODS5[g].ref
        kap = np.array(r[f"{p}_{g}_kapan"], dtype=float) / GOODS5[g].ref
        if np.nanmax(ret) > 50:
            out["exploded"] = True
        # D5b2: diğer metrikler gibi son 5 yıl (ısınma hariç; D5b2'de patlamaların çoğu ilk 2 yılda, küçük
        # başlangıç filosu + ilk yıl giriş yok)
        if np.nanmax(ret[LAST]) > 50:
            out["explode_last"] = True
        # D5b2: patlamayı ayır: kıtlık (toptan fiyat da 50× üstü) / perakende kaçışı (perakende toptanın 3× üstü)
        if np.nanmax(kap) > 50:
            out["dearth"] = True
        with np.errstate(invalid="ignore"):
            if np.nanmax(np.where(ret > 10, ret / kap, 0)) > 3:
                out["runaway"] = True
    # İthalatçı Venedik: ithalat / ihtiyaç, malsız günler, buğday zirvesi ve yarı aç günler
    for g in ("WHT", "OIL", "PEP"):
        own = {"WHT": 0.4, "OIL": 0.0, "PEP": 0.0}[g]
        imp = sum(q for (y, o, d, gg), q in r["flows"].items() if d == "VEN" and gg == g and y >= Y0) / 5
        out[f"imp_{g}"] = imp / (w.local_cons["VEN"][g] * (1 - own) * 365)
        ret = np.array(r[f"VEN_{g}_retail"], dtype=float)
        out[f"nosale_{g}"] = float(np.mean(~np.isfinite(ret[LAST])))
        src, dst = ROUTES[g]
        days = w.days[(src, dst)]
        ps = np.nanmedian(np.array(r[f"{src}_{g}_kapan"][LAST], dtype=float))
        pd = np.nanmedian(np.array(r[f"{dst}_{g}_kapan"][LAST], dtype=float))
        cost = FREIGHT_PER_BULK_DAY * GOODS5[g].bulk * days + pd * (CUSTOMS + 0.03)
        out[f"spread_{g}"] = float((pd - ps) / cost)
    ven = np.array(r["VEN_WHT_retail"], dtype=float)[LAST] / GOODS5["WHT"].ref
    out["VEN_WHT_max"] = float(np.nanmax(ven))
    cons = np.array(r["VEN_WHT_cons"][LAST]) / w.local_cons["VEN"]["WHT"]
    out["VEN_WHT_halfhungry"] = float(np.mean(cons < 0.5))
    # Herding: aylık kalkışların seçenekler (mal, hedef) arasındaki yoğunlaşması (değerle ağırlıklı HHI)
    by_month = {}
    for day, o, d, g, q, lvl in r["departures"]:
        if day < 365 * 5:
            continue
        mo = day // 30
        by_month.setdefault(mo, Counter())[(g, d)] += q * GOODS5[g].ref
    hhi = [sum((v / sum(c.values())) ** 2 for v in c.values()) for c in by_month.values() if sum(c.values()) > 0]
    out["hhi"] = float(np.median(hhi)) if hhi else float("nan")
    # Glut: 14 gün içinde aynı (hedef, mal) pazarına inen kargonun, 30 günlük tüketimi aşması (yılda kaç kez)
    arr = {}
    for day, o, d, g, q, lvl in r["departures"]:
        if day >= 365 * 5:
            arr.setdefault((d, g), []).append((day + w.days[(o, d)], q))
    gluts = 0
    for (d, g), lst in arr.items():
        lst.sort()
        depth = 30 * w.demand_L[d][g]
        k = 0
        while k < len(lst):
            win = [q for t, q in lst if lst[k][0] <= t < lst[k][0] + 14]
            if sum(win) > depth:
                gluts += 1
                k += len(win)
            else:
                k += 1
    out["gluts_per_year"] = gluts / 5
    out["frac_selling"] = float(np.mean(r["frac_selling"][LAST]))
    ms = [m for m in r["merchants"] if not m.is_player]
    out["trapped_end"] = sum(1 for m in ms if m.state == "selling" and m.wait > 180) / max(len(ms), 1)
    out["n_merchants"] = float(np.mean(r["n_npc"][LAST]))
    out["bankruptcies"] = r["bankruptcies"]
    # Mal karışımı: son 5 yılın kalkışlarının değer payları
    val = Counter()
    for day, o, d, g, q, lvl in r["departures"]:
        if day >= 365 * 5:
            val[g] += q * GOODS5[g].ref
    tot = sum(val.values()) or 1.0
    for g in ("WHT", "OIL", "PEP"):
        out[f"mix_{g}"] = val[g] / tot
    # Kişiliklere göre ömür boyu yıllık getiri (yaşayan + çıkan + batan: survivorship bias yok)
    end = w.day
    people = [(m, end, m.net_worth()) for m in r["merchants"] if not m.is_player] + list(r["gone"])
    rows = [(m.level, m.imitation, m.overconf, lifetime_return(m, day, v)) for m, day, v in people if not m.is_player]
    out["ret_median"] = float(np.median([x[3] for x in rows]))
    for lv in (0, 1, 2):
        xs = [x[3] for x in rows if x[0] == lv]
        out[f"ret_level{lv}"] = float(np.median(xs)) if xs else float("nan")
    if any(x[1] > 0 for x in rows):
        imit = np.array([x[1] for x in rows]); rets = np.array([x[3] for x in rows])
        out["ret_imit_hi"] = float(np.median(rets[imit >= np.median(imit)]))
        out["ret_imit_lo"] = float(np.median(rets[imit < np.median(imit)]))
        oc = np.array([x[2] for x in rows])
        out["ret_overconf"] = float(np.median(rets[oc < np.median(oc)]))      # daha aşırı güvenli yarı
        out["ret_cautious"] = float(np.median(rets[oc >= np.median(oc)]))
    return out


def run(args):
    name, seed = args
    w = D5World(D5Config(seed=seed, **BASE, **SETUPS[name]))
    r = w.run()
    if seed == 1:
        fig, axs = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
        for ax, g in zip(axs, ("WHT", "OIL", "PEP")):
            ref = GOODS5[g].ref
            for p in w.port_list:
                if (p, g) in w.markets:
                    ax.plot(r["date"], np.array(r[f"{p}_{g}_kapan"], dtype=float) / ref, lw=0.7, label=p)
            ax.set_yscale("log"); ax.set_ylabel(f"{g} kapan / ref"); ax.legend(loc="upper left")
        fig.suptitle(f"D5b — {name} (seed 1)")
        fig.tight_layout(); fig.savefig(OUT / f"d5b_{name.split()[0]}.png", dpi=110); plt.close(fig)
    return name, seed, metrics(w, r)


def main():
    with Pool(5) as pool:
        res = pool.map(run, [(n, s) for n in SETUPS for s in SEEDS])
    summary = {}
    for name in SETUPS:
        rows = [o for n, s, o in res if n == name]
        agg = {k: f"{sum(x[k] for x in rows)}/{len(rows)}" for k in ("exploded", "explode_last", "dearth", "runaway")}
        for k in rows[0]:
            if k not in ("exploded", "explode_last", "dearth", "runaway") and all(k in x for x in rows):
                agg[k] = float(np.nanmedian([x[k] for x in rows]))
        summary[name] = agg
        print(name, json.dumps(agg, ensure_ascii=False))
    a = D5World(D5Config(seed=7, **BASE, **SETUPS["D çeşitli"])).run()
    b = D5World(D5Config(seed=7, **BASE, **SETUPS["D çeşitli"])).run()
    summary["determinism_same_seed"] = bool(np.array_equal(a["VEN_WHT_kapan"], b["VEN_WHT_kapan"]))
    print("determinism", summary["determinism_same_seed"])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
