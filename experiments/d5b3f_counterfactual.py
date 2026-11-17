"""Experiment D5b3f (counterfactual): expected entry with parts of the belief changed, on recorded inputs.
Run (repo root): python3 experiments/d5b3f_counterfactual.py
Report (Turkish): docs/experiments/D5b3f.md

(Original notes in Turkish below.)

D5b3f karşı-olgusal: kaydedilen giriş girdileriyle, inancın parçaları değiştirilince beklenen giriş (lam) ne olurdu?
Davranış simüle edilmez (filo geri besleme yok); yalnızca aynı ayların girdileriyle giriş akışı ayrıştırılır."""
import json, math, pathlib, statistics as st
OUT = pathlib.Path(__file__).resolve().parents[1] / "experiments" / "out" / "d5b3f"
RP, SIG, ATT = 0.04, 0.5, 0.02

def conv(x, extra):
    if x <= 0:
        return 0.0
    z = (math.log(x) - math.log(RP + extra)) / SIG
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

for name in ["VRS", "F"]:
    tot = {}
    for f in sorted(OUT.glob(f"{name}_*.json")):
        r = json.load(open(f))
        E = [x for x in r["elog"] if x["track"] is not None]
        tr = [x["track"] for x in E]
        mu = sum(tr) / len(tr)
        # 12 aylık hareketli ortalama sicil (liman sayısı kadar kayıt/ay)
        P = len({x["p"] for x in E}); w = 12 * P
        sm = [sum(tr[max(0, i - w + 1):i + 1]) / len(tr[max(0, i - w + 1):i + 1]) for i in range(len(tr))]
        for key, fn in {
            "kaydedilen k": lambda x, i: x["k"],
            "gerçek lam": lambda x, i: ATT * x["pool_units"] * conv(x["belief"] - x["alt"], x["ruin"]),
            "bonus yok": lambda x, i: ATT * x["pool_units"] * conv(x["track"] - x["alt"], x["ruin"]),
            "sicil 12 ay ort. + bonus": lambda x, i: ATT * x["pool_units"] * conv(sm[i] + x["belief"] - x["track"] - x["alt"], x["ruin"]),
            "sicil 12 ay ort., bonus yok": lambda x, i: ATT * x["pool_units"] * conv(sm[i] - x["alt"], x["ruin"]),
            "sicil = koşu ortalaması, bonus yok": lambda x, i: ATT * x["pool_units"] * conv(mu - x["alt"], x["ruin"]),
        }.items():
            tot.setdefault(key, []).append(sum(fn(x, i) for i, x in enumerate(E)) / (len(E) / P / 12))
        tot.setdefault("sicil sd (aylar arası)", []).append(st.pstdev(tr))
        tot.setdefault("sicil ort.", []).append(mu)
    print(name)
    for k, v in tot.items():
        print(f"  {k:36s} {sum(v)/len(v):8.3f}  (yıllık, seed ort.)" if "sicil" not in k or "+" in k or "bonus" in k else f"  {k:36s} {sum(v)/len(v):8.3f}")
