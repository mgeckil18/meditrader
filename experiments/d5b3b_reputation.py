"""Experiment D5b3b: colleganza contracts with reputation (skill vs luck).
Run (repo root): python3 experiments/d5b3b_reputation.py YEARS   e.g. 10
Report (Turkish): docs/experiments/D5b3b.md

(Original notes in Turkish below.)

Deney D5b3b: colleganza + itibar (K-021).

Soru: D5b3'te itibarsız colleganza adverse selection yüzünden yatırımcıya sözleşme başına −%17/−%19 kaybettirdi.
Yatırımcılar tüccarları siciline göre sıralayıp seçerse ne olur? İki skor yarışır:
  user  kullanıcı önerisi: bir yıllık işlem hacmi × kâr oranı × kârlı işlem oranı
  cred  Claude önerisi: credibility (Bühlmann 1967); sefer getirisi ortalaması nüfus ortalamasına çekilir,
        belirsizlik kadar indirilir
Sermaye bütçesi sınırlı (ayda havuzun %10'u); yeni tüccar girişinde yatırımcının alternatifi colleganza getirisi.
Ayrıca: sicil, sonraki sözleşmenin getirisini tahmin ediyor mu (Spearman)? Kullanıcı hipotezi: itibar,
serbest girişe kendiliğinden friction getirebilir.
Kullanım: python3 experiments/d5b3b_reputation.py 10    Rapor: docs/experiments/D5b3b.md
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

OUT = ROOT / "experiments" / "out" / "d5b3b"
OUT.mkdir(parents=True, exist_ok=True)
OS = dict(D3["OCS"], colleganza=False)
SETUPS = {
    "OS": OS,
    "OCS-itibarsız": D3["OCS"],
    "OCS-user": dict(D3["OCS"], reputation="user"),
    "OCS-cred": dict(D3["OCS"], reputation="cred"),
    "OCS-gate": dict(D3["OCS"], reputation="gate"),   # ablasyon: user kapısı, rastgele sıralama
}
TAG = ""
SEEDS = range(5)


def spearman(a, b):
    if len(a) < 10:
        return float("nan")
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def run(args):
    name, seed = args
    w = D5World(D5Config(seed=seed, **BASE, **SETUPS[name]))
    r = w.run()
    out = metrics(w, r)
    n = np.array(r["n_npc"], dtype=float)
    out["fleet_start"], out["fleet_last"] = float(n[0]), float(np.mean(n[-1825:]))
    out["track_last_mean"] = float(np.mean(np.array(r["track"], dtype=float)[-1825:]))
    out["entries"], out["exits"], out["bankruptcies_n"] = r["entries"], r["exits"], r["bankruptcies"]
    cc = [c for c in w.colleg_contracts if c[0] >= 5 * 365]                 # son 5 yıl
    out["colleg_n"] = len(cc)
    cap = sum(c[3] for c in cc)
    out["colleg_ret_capw"] = sum(c[2] * c[3] for c in cc) / cap if cap else float("nan")
    capd = sum(c[3] * c[4] for c in cc)
    out["colleg_ann"] = sum(c[2] * c[3] for c in cc) / capd * 365 if capd else float("nan")
    out["colleg_loss_frac"] = float(np.mean([c[2] < 0 for c in cc])) if cc else float("nan")
    for L in (0, 1, 2):
        sub = [c for c in cc if c[1] == L]
        out[f"colleg_share_lvl{L}"] = len(sub) / len(cc) if cc else float("nan")
    sc = [(c[5], c[2]) for c in cc if c[5] is not None]
    out["spearman_score_ret"] = spearman([x[0] for x in sc], [x[1] for x in sc])
    # Sicil kalıcı mı? Her tüccarın ilk yarı / ikinci yarı sefer getirisi (son 5 yıl), en az 4'er sefer
    halves = []
    for m in r["merchants"] + [g[0] for g in r["gone"]]:
        rec = [x for x in m.record if x[0] >= 5 * 365]
        if len(rec) >= 8:
            k = len(rec) // 2
            halves.append((np.mean([x[1] for x in rec[:k]]), np.mean([x[1] for x in rec[k:]])))
    out["persistence"] = spearman([h[0] for h in halves], [h[1] for h in halves])
    out["persistence_n"] = len(halves)
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
        agg["colleg_ret_capw_seeds"] = [round(x["colleg_ret_capw"], 3) for x in rows]
        summary[name] = agg
        print(name, json.dumps(agg, ensure_ascii=False), flush=True)
    (OUT / f"summary{TAG}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        SEEDS = range(int(sys.argv[1]))
    if len(sys.argv) > 2:                          # ör. "OCS-gate" → yalnız bu kurulumlar, ayrı özet dosyası
        SETUPS = {k: SETUPS[k] for k in sys.argv[2].split(",")}
        TAG = "_" + sys.argv[2].replace(",", "_")
    main()
