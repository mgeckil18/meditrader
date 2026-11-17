"""Experiment D5b2: thin-market trap: factorial test of four mechanisms (visibility, forward expectation, sell decision, liquidity).
Run (repo root): python3 experiments/d5b2_factorial.py   (~10 min)
Report (Turkish): docs/experiments/D5b2.md

(Original notes in Turkish below.)

Deney D5b2: ince pazar tuzağı — dört mekanizmanın faktöriyel testi.

Soru: D5b'de bazı seed'lerde 15-25 tüccar Korfu'da biberle yıllarca bekliyor (ince pazar tuzağı). Kullanıcının
sezgisi: birden çok gerçek mekanizma birlikte çalışınca bu çözülmeli. Dört yuva, tek tek ve birlikte:
  G  görünürlük: limandaki alımlar açık (kim, ne, ne kadar; hedef söylenti), kapan hacmi görünür (kullanıcı)
  B  beklenti: kendi kargosunun fiyat etkisi + ileriye bakan bilgi: hasat haberi, mevsim (kullanıcı fikri; Claude)
  S  satış kararı: her gün sat / bekle / rota değiştir; bekleme maliyeti açık (kullanıcı fikri; Claude)
  L  likidite: stokçu bütün mallarda; envantere göre teklif kaydırma (kullanıcı fikri: depocu; Claude)
Kurulumlar: taban (D5b'nin D'si), her biri tek başına, hepsi, hepsi eksi biri. 10 kurulum × 5 seed.
Kullanım:  python3 experiments/d5b2_factorial.py   (~10 dk)
Rapor:     docs/experiments/D5b2.md
Not: ilk koşu (D5b2.2) dust_lot=0 ile yapıldı → out/d5b2/*_dust0.*; Zeno artifact'ı düzeltmesinden sonra dust_lot=1.
"""
import json
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5b_diversity import BASE, SETUPS as D5B, metrics  # noqa: E402
from sim.world5 import D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d5b2"
OUT.mkdir(parents=True, exist_ok=True)
D = D5B["D çeşitli"]
FLAGS = {"G": "visibility", "B": "forward", "S": "sell_decision", "L": "liquidity"}


def setup(on):
    return dict(D, **{FLAGS[k]: True for k in on})


SETUPS = {"taban": setup("")}
for k in "GBSL":
    SETUPS[k] = setup(k)
SETUPS["GBSL"] = setup("GBSL")
for k in "GBSL":
    SETUPS["GBSL−" + k] = setup("GBSL".replace(k, ""))
SEEDS = range(5)


def run(args):
    name, seed = args
    w = D5World(D5Config(seed=seed, **BASE, **SETUPS[name]))
    r = w.run()
    out = metrics(w, r)
    ms = [m for m in r["merchants"] if not m.is_player]
    out["trapped_n_end"] = sum(1 for m in ms if m.state == "selling" and m.wait > 180)
    out["cor_pep_end"] = sum(1 for m in ms if m.state == "selling" and m.loc == "COR" and m.good == "PEP")
    out["reroutes"] = r["reroutes"]
    n = np.array(r["n_npc"], dtype=float)
    out["fleet_y1"] = float(np.mean(n[:365]))
    out["fleet_last"] = float(np.mean(n[-1825:]))
    out["dust"] = sum(
        v for (g, k), v in w.ledger.goods_out.items() if k == "lot_dust")
    return name, seed, out


def main():
    with Pool(min(20, 2 * len(SEEDS))) as pool:
        res = pool.map(run, [(n, s) for n in SETUPS for s in SEEDS])
    summary = {}
    for name in SETUPS:
        rows = [o for n, s, o in res if n == name]
        agg = {**{k: f"{sum(x[k] for x in rows)}/{len(rows)}" for k in ("exploded", "explode_last", "dearth", "runaway")},
               "trapped_seeds": [x["trapped_n_end"] for x in rows],
               "cor_pep_seeds": [x["cor_pep_end"] for x in rows]}
        for k in rows[0]:
            if k not in ("exploded", "explode_last", "dearth", "runaway") and all(k in x for x in rows):
                agg[k] = float(np.nanmedian([x[k] for x in rows]))
        summary[name] = agg
        print(name, json.dumps(agg, ensure_ascii=False), flush=True)
    last = list(SETUPS)[-1]
    a = D5World(D5Config(seed=7, **BASE, **SETUPS[last])).run()
    b = D5World(D5Config(seed=7, **BASE, **SETUPS[last])).run()
    summary["determinism_same_seed"] = bool(np.array_equal(a["VEN_WHT_kapan"], b["VEN_WHT_kapan"]))
    print("determinism", summary["determinism_same_seed"])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        SEEDS = range(int(sys.argv[1]))
    main()
