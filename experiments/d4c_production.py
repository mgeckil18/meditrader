"""Experiment D4c: production chain (wool -> coarse and fine cloth), producer pools, wages.
Run (repo root): python3 experiments/d4c_production.py   (~3 min)
Report (Turkish): docs/experiments/D4c.md

(Original notes in Turkish below.)

Deney D4c: üretim zinciri (yün → kaba ve ince kumaş), üretici havuzları, ücretler.

Testler (docs/design/production-chains.md):
  T1  Zengin geliri +%20 (1565'ten itibaren): ince kumaş ↑ → yün ↑ → kaba kumaş da pahalanır mı?
  T2  Buğday hasadı −%30 (Aşama 1, sabit ücret): kaba kumaş üretimi ↓, yün ↓, ince kumaş korunur mu?
  T3  Yün kırkımı −%30: iki kumaş da pahalanır mı, kaba daha çok mu?
  T4  Buğday −%30, Aşama 2 (ücretler orta ve yoksulun gelirine bağlı): Labrousse çarpanı?
Kullanım:  python3 experiments/d4c_production.py   (~3 dk)
Rapor:     docs/experiments/D4c.md
"""
import json
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.d2_two_ports import monthly  # noqa: E402
from sim.production import D4cConfig, D4cWorld  # noqa: E402

OUT = ROOT / "experiments" / "out" / "d4c"
OUT.mkdir(parents=True, exist_ok=True)

TESTS = {
    "T1 zengin geliri +%20": (dict(rich_income_shock={y: 1.2 for y in range(5, 10)}), (1565, 3)),
    "T2 buğday −%30 (sabit ücret)": (dict(yield_overrides={"WHT": {5: 0.7}}), (1565, 7)),
    "T3 yün −%30": (dict(yield_overrides={"WOL": {5: 0.7}}), (1565, 5)),
    "T4 buğday −%30 (içsel ücret)": (dict(yield_overrides={"WHT": {5: 0.7}}, wages_endogenous=True), (1565, 7)),
}


def run(**kw):
    return D4cWorld(D4cConfig(**kw)).run()


def idx(r, ym):
    return next(i for i, d in enumerate(r["date"]) if (d.year, d.month) == ym)


def ratios(base, sh, start):
    win = slice(start, start + 365)
    f = lambda k: float(np.mean(sh[k][win]) / max(np.mean(base[k][win]), 1e-9))
    out = {
        "fiyat yün": f("WOL_ask"), "fiyat kaba": f("CLC_ask"), "fiyat ince": f("CLF_ask"),
        "fiyat buğday": f("WHT_ask"),
        "üretim kaba": f("CLC_prod"), "üretim ince": f("CLF_prod"),
        "kaba tüketim yoksul": f("yoksul_CLC"), "kaba tüketim orta": f("orta_CLC"),
        "ince tüketim zengin": f("zengin_CLF"),
        "gelir yoksul": f("yoksul_income"), "gelir orta": f("orta_income"),
    }
    pm = monthly(sh["CLC_prod"][start:start + 400], sh["date"][start:start + 400])
    out["kaba üretim en kötü ay / normal"] = float(pm.min() / sh["normal_q"]["CLC"])
    return out


def main():
    summary = {"tests": {}}
    series = {}
    for name, (kw, ym) in TESTS.items():
        endo = kw.get("wages_endogenous", False)
        base = run(seed=0, yield_sigma=0.0, wages_endogenous=endo)
        sh = run(seed=0, yield_sigma=0.0, **kw)
        start = idx(base, ym)
        summary["tests"][name] = ratios(base, sh, start)
        series[name] = (base, sh, start)
        print(name, "ok")

    # Kararlılık: 10 seed, iki aşama
    summary["stability"] = {}
    for endo in (False, True):
        expl, vols = 0, {c: [] for c in ("WHT", "WOL", "CLC", "CLF")}
        caps = []
        for s in range(10):
            r = run(seed=s, wages_endogenous=endo)
            for c in vols:
                p = r[f"{c}_ask"]
                if p.max() > 10 * np.median(p):
                    expl += 1
                    break
                m = monthly(p, r["date"])[12:]
                vols[c].append(float(np.std(np.diff(np.log(m))) * np.sqrt(12)))
            caps.append(float(r["CLC_cap"][-1] / r["CLC_cap"][0]))
        summary["stability"]["içsel ücret" if endo else "sabit ücret"] = {
            "exploded": f"{expl}/10", **{f"{c}_vol": float(np.median(v)) for c, v in vols.items()},
            "kaba kapasite son/ilk (medyan)": float(np.median(caps))}

    # Grafik 1: test oranları
    keys = ["fiyat yün", "fiyat kaba", "fiyat ince", "üretim kaba", "üretim ince", "kaba tüketim yoksul"]
    fig, ax = plt.subplots(figsize=(13, 4.2))
    x = np.arange(len(keys))
    for j, name in enumerate(TESTS):
        ax.bar(x + (j - 1.5) * 0.2, [summary["tests"][name][k] for k in keys], 0.2, label=name)
    ax.set_xticks(x); ax.set_xticklabels(keys); ax.axhline(1, color="gray", lw=0.8)
    ax.set_ylabel("şoklu / şoksuz (12 ay)"); ax.legend(fontsize=8)
    ax.set_title("D4c: dört şokun zincir boyunca etkisi")
    fig.tight_layout(); fig.savefig(OUT / "d4c_tests.png", dpi=110); plt.close(fig)

    # Grafik 2: Labrousse çarpanı: T2 vs T4
    fig, axs = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True)
    for name, ls in (("T2 buğday −%30 (sabit ücret)", "-"), ("T4 buğday −%30 (içsel ücret)", "--")):
        base, sh, start = series[name]
        rng = slice(start - 180, start + 730)
        d = sh["date"][rng]
        sm = lambda a: np.convolve(a, np.ones(30) / 30, mode="same")[rng]
        axs[0].plot(d, sm(sh["CLC_prod"]) / sh["normal_q"]["CLC"], ls=ls, label=name)
        axs[1].plot(d, sm(sh["yoksul_CLC"]) / max(np.mean(base["yoksul_CLC"]), 1e-9), ls=ls, label=name)
        axs[2].plot(d, sh["yoksul_income"][rng] / base["yoksul_income"][rng], ls=ls, label=name)
    axs[0].set_ylabel("kaba kumaş üretimi / normal")
    axs[1].set_ylabel("yoksulun kaba kumaş alımı / normal")
    axs[2].set_ylabel("yoksul geliri / şoksuz")
    for ax in axs:
        ax.axhline(1, color="gray", lw=0.8); ax.legend(fontsize=8, loc="lower left")
        ax.axvline(series["T2 buğday −%30 (sabit ücret)"][1]["date"][series["T2 buğday −%30 (sabit ücret)"][2]],
                   color="red", ls=":", lw=0.8)
    fig.suptitle("Labrousse çarpanı: ücretler zanaatkârın gelirine bağlanınca kıtlık derinleşiyor mu?")
    fig.tight_layout(); fig.savefig(OUT / "d4c_labrousse.png", dpi=110); plt.close(fig)

    a, b = run(seed=7), run(seed=7)
    summary["determinism_same_seed"] = bool(np.array_equal(a["CLC_ask"], b["CLC_ask"]))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
