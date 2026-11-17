"""Experiment D5b2 (diagnostic): where, when and why prices explode.
Run (repo root): python3 experiments/d5b2_diag_explode.py SETUP SEED   e.g. B 0
Report (Turkish): docs/experiments/D5b2.md

(Original notes in Turkish below.)

D5b2 teşhis: patlamalar nerede, ne zaman, neden. Hangi pazar/mal 50× referansı aşıyor; o pazarda
kapan fiyatı, dükkân req_price'ı, stokçu stoğu, kapan'a gelen arz. Kullanım: python3 experiments/d5b2_diag_explode.py B 0
"""
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from d5b_diversity import BASE  # noqa: E402
from d5b2_factorial import SETUPS  # noqa: E402
from d5b_diversity import SETUPS as D5B  # noqa: E402
SETUPS = {**{k.split()[0]: v for k, v in D5B.items()}, **SETUPS}
from sim.world5 import D5Config, D5World, GOODS5  # noqa: E402

name, seed = sys.argv[1], int(sys.argv[2])
w = D5World(D5Config(seed=seed, **BASE, **SETUPS[name]))
import datetime as dt
from sim.world5 import START_DATE  # noqa: E402
end = dt.date(START_DATE.year + w.cfg.years, START_DATE.month, START_DATE.day)
st = {k: [] for k in w.markets}
while w.date < end:
    w.step()
    for k, mk in w.markets.items():
        ms = [m for m in w.merchants if m.state == "selling" and m.loc == k[0] and m.good == k[1]]
        st[k].append((sum(s.stock for s in mk.shops), np.mean([s.req_price for s in mk.shops]) if mk.shops else np.nan,
                      len(mk.shops), sum(x.stock for x in mk.storers), len(ms), sum(m.qty for m in ms),
                      w.kapan_volume.get(k, 0.0)))
r = {k: (np.array(v) if k != "date" else v) for k, v in w.log.items()}
for (p, g) in w.markets:
    ret = np.array(r[f"{p}_{g}_retail"], dtype=float) / GOODS5[g].ref
    kap = np.array(r[f"{p}_{g}_kapan"], dtype=float) / GOODS5[g].ref
    if not np.any(ret > 50):
        print(f"{p}_{g}: max perakende {np.nanmax(ret):.1f}×")
        continue
    d0 = int(np.argmax(ret > 50))
    print(f"*** {p}_{g}: ilk >50× gün {d0} (yıl {d0/365:.2f}); max {np.nanmax(ret):.0f}×")
    for d in range(max(0, d0 - 120), d0 + 1, 10):
        a = st[(p, g)][d]
        print(f"   gün {d}: perakende {ret[d]:.1f}× kapan {kap[d]:.1f}× | dükkân stok {a[0]:.0f} req {a[1]/GOODS5[g].ref:.1f}× n={a[2]}"
              f" | stokçu {a[3]:.0f} | satıcı tüccar {a[4]} ({a[5]:.0f}) | kapan hacmi(kümülatif) {a[6]:.0f}")
