"""Experiment D5b2 (extra ablation): the two parts of B (own price impact vs forward expectation) separately.
Run (repo root): python3 experiments/d5b2_split_b.py YEARS   e.g. 10
Report (Turkish): docs/experiments/D5b2.md

(Original notes in Turkish below.)

D5b2 ek ablasyon: B'nin iki parçası ayrı. Bimp = yalnızca kendi kargosunun fiyat etkisi (miktar ızgarası),
Bfund = yalnızca ileriye bakan temel beklenti. Soru: B'li kurulumlarda ısınma kıtlığı hangi parçadan?
Kullanım: python3 experiments/d5b2_split_b.py 10    Rapor: docs/experiments/D5b2.md
"""
import json
import sys
from multiprocessing import Pool

import d5b2_factorial as F

S = F.SETUPS
F.SETUPS = {
    "Bimp": dict(S["B"], forward_fund=False),
    "GBSL·imp": dict(S["GBSL"], forward_fund=False),
}
# Bfund: kendi etkisi kapalı ama temel beklenti açık. _impact yalnızca forward'a bakıyor, o yüzden
# yalnızca-temel kurulumu ayrı bayrak gerektirir → forward_impact
F.SETUPS["Bfund"] = dict(S["B"], forward_impact=False)
F.SETUPS["GBSL·fund"] = dict(S["GBSL"], forward_impact=False)

if __name__ == "__main__":
    F.SEEDS = range(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
    F.OUT = F.OUT.parent / "d5b2_splitB"
    F.OUT.mkdir(parents=True, exist_ok=True)
    F.main()
