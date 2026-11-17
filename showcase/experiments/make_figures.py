"""Builds the English figures of the showcase from experiment outputs.

Inputs (produced by the experiment scripts; experiments/out/ is not in the repo):
  experiments/out/d2/summary.json    python3 experiments/d2_two_ports.py
  experiments/out/d3/summary.json    python3 experiments/d3_information.py
  experiments/out/d3b/summary.json   python3 experiments/d3b_entry_exit.py
  experiments/out/d4b/summary.json   python3 experiments/d4b_classes.py
  experiments/out/m2/{PF,MX,MW}_*.json   bash core/tools/run_m.sh PF   (and MX, MW; Rust core)

Run (repo root): python3 showcase/experiments/make_figures.py
Writes showcase/experiments/img/*.png and prints the numbers used, so the pages can quote them.
Figures whose inputs are missing are skipped with a note.
"""
import json
import pathlib
import statistics as st

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments" / "out"
IMG = pathlib.Path(__file__).resolve().parent / "img"

# validated default categorical palette (light surface), fixed order
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e6e5e0"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y",
    "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.8, "legend.frameon": False, "text.color": INK,
})


def load(rel):
    p = OUT / rel
    if not p.exists():
        print(f"skip: {p.relative_to(ROOT)} missing")
        return None
    return json.loads(p.read_text())


def med(v):
    """Summary values are either a number or [median, low, high] across seeds."""
    return v[0] if isinstance(v, list) else v


def bars(ax, labels, series, width=0.36, whiskers=True):
    n = len(series)
    for i, (name, vals, color) in enumerate(series):
        xs = [x + (i - (n - 1) / 2) * (width + 0.02) for x in range(len(labels))]
        ys = [med(v) for v in vals]
        ax.bar(xs, ys, width, color=color, label=name, edgecolor="white", linewidth=2)
        if whiskers and all(isinstance(v, list) for v in vals):
            ax.errorbar(xs, ys, yerr=[[y - v[1] for y, v in zip(ys, vals)], [v[2] - y for y, v in zip(ys, vals)]],
                        fmt="none", ecolor=MUTED, elinewidth=1, capsize=2)
    ax.set_xticks(range(len(labels)), labels)
    ax.tick_params(axis="x", length=0)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(IMG / name, dpi=150)
    plt.close(fig)
    print("wrote", (IMG / name).relative_to(ROOT))


def fig_rules():
    d = load("d2/summary.json")
    if not d:
        return
    ns = (5, 15, 40)
    rules = [("greedy", "Greedy", C1), ("dp", "Doran-Parberry belief range", C2), ("utility", "Utility AI", C3)]
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, key, title in ((axs[0], "opp_days_pct", "Days with a profitable opportunity (%)"),
                           (axs[1], "player_return", "Return of a greedy player bot (% / year)")):
        for r, name, color in rules:
            ys = [med(d[f"{r}_N{n}"][key]) for n in ns]
            ax.plot(ns, ys, color=color, linewidth=2, marker="o", markersize=6, label=name)
        ax.set_xticks(ns)
        ax.set_xlabel("number of NPC merchants")
        ax.set_title(title)
        ax.grid(axis="x", visible=False)
    axs[1].legend(loc="center right", title="NPC decision rule", title_fontsize=9)
    print("D2 player return", {r: [round(med(d[f"{r}_N{n}"]["player_return"]), 1) for n in ns] for r, _, _ in rules})
    save(fig, "instant-information.png")


def fig_information():
    d2, d3 = load("d2/summary.json"), load("d3/summary.json")
    if not (d2 and d3):
        return
    keys = ["C0 anlık / son", "C1 gemi / son", "C2 söylenti / son", "C3 söylenti / dağılım",
            "C4 söylenti / dağılım+dönüş"]
    labels = ["Instant\n(C0)", "Ship news\n(C1)", "Rumour\n(C2)", "Rumour +\nspread (C3)",
              "Rumour + spread\n+ reversion (C4)"]
    opp = {n: [d3[f"{k} | N{n}"]["opp_days_pct"] for k in keys] for n in (15, 40)}
    val = {n: [d3[f"{k} | N{n}"]["info_value"] for k in keys] for n in (15, 40)}
    print("D3 opportunity days %", {n: [round(med(v), 1) for v in opp[n]] for n in opp})
    print("D3 value of information (pts/yr)", {n: [round(med(v), 1) for v in val[n]] for n in val})
    print("D2 greedy opportunity days %", [round(med(d2[f"greedy_N{n}"]["opp_days_pct"]), 1) for n in (5, 15, 40)])
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    bars(axs[0], labels, [("15 merchants", opp[15], C1), ("40 merchants", opp[40], C2)])
    axs[0].set_title("Days with a profitable opportunity (%)")
    axs[0].text(0.99, 0.97, "median of 10 seeds; whiskers: 10th-90th percentile", transform=axs[0].transAxes, ha="right",
                va="top", fontsize=8, color=MUTED)
    axs[0].legend(loc="upper left")
    bars(axs[1], labels, [("15 merchants", val[15], C1), ("40 merchants", val[40], C2)], whiskers=False)
    axs[1].set_title("Value of information (pts of return / year)")
    axs[1].text(0.01, 0.97, "informed bot minus same-information bot; median of 10 seeds", transform=axs[1].transAxes,
                va="top", fontsize=8, color=MUTED)
    axs[1].axhline(0, color=MUTED, linewidth=0.8)
    for ax in axs:
        ax.tick_params(axis="x", labelsize=8)
    save(fig, "information-delay.png")


def fig_entry():
    d = load("d3b/summary.json")
    if not d:
        return
    structs = [("havuz-1", "Slow entry\n(~1/month)"), ("havuz-3", "Moderate entry\n(~3/month)"),
               ("orantılı", "Herd entry\n(∝ current N)")]
    sector = [st.median(med(d[f"{k} | N0={n}"]["sector_return"]) for n in (5, 15, 40)) for k, _ in structs]
    surv = [st.median(med(d[f"{k} | N0={n}"]["survivor_return"]) for n in (5, 15, 40)) for k, _ in structs]
    print("D3b sector return", [round(x, 1) for x in sector], "survivors", [round(x, 1) for x in surv])
    fig, ax = plt.subplots(figsize=(8.8, 4))
    ax.axhspan(4, 8, color="#f1efe8", zorder=0)
    bars(ax, [l for _, l in structs], [("Sector return (all merchants, from the ledger)", sector, C1),
                                       ("Median return of survivors", surv, C2)])
    ax.set_title("Entry speed sets the rent  (shaded: bond 4% to bond + risk premium 8%)")
    ax.set_ylabel("% per year")
    ax.legend(loc="upper right")
    save(fig, "entry-speed.png")


def fig_artifact():
    d = load("d4b/summary.json")
    if not d:
        return
    a = d["ablation"]
    rows = [("1 sınıf, eski satış hızı | tahıl serbest", "Old code\ngrain free"),
            ("1 sınıf, eski satış hızı | tahıl sabit", "Old code\ngrain frozen"),
            ("1 sınıf | tahıl serbest", "Fixed\ngrain free"), ("1 sınıf | tahıl sabit", "Fixed\ngrain frozen")]
    vals = [med(a[k]["cloth_amp"]) for k, _ in rows]
    print("D4b cloth amplitude", [round(v, 2) for v in vals])
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.bar(range(4), vals, 0.5, color=[C2, C2, C1, C1], edgecolor="white", linewidth=2)
    for x, v in enumerate(vals):
        ax.text(x, v + 0.04, f"{v:.2f}", ha="center", fontsize=9, color=INK)
    ax.set_xticks(range(4), [l for _, l in rows])
    ax.tick_params(axis="x", length=0)
    ax.axhline(1, color=MUTED, linewidth=0.8)
    ax.set_ylim(0, 3.0)
    ax.set_title("Seasonal swing in cloth buying (peak month / trough month)")
    ax.text(1.5, 2.8, "freezing grain prices does not remove the swing: not a grain effect, so an artifact",
            ha="center", fontsize=8, color=MUTED)
    save(fig, "cloth-artifact.png")


def m_stats(name):
    """Same definitions as core/tools/an_loss.py: departures after warm-up (t0), fleet = mean of the
    last 120 days, loss = ships_lost; pooled over seeds."""
    fs = sorted((OUT / "m2").glob(f"{name}_[0-9].json"))
    if not fs:
        return None
    sea = lost = fy = 0.0
    for f in fs:
        d = json.loads(f.read_text())
        fl = d["fleet"]
        fy += st.mean(fl[-120:] if len(fl) > 120 else fl) * 10
        sea += sum(r[9] for r in d["dep_log"] if r[0] >= d["t0"] and len(r) > 9 and r[9])
        lost += d["ships_lost"]
    return sea / fy, 100 * lost / fy


def fig_tempo():
    runs = [("PF", "Cost package\n(PF)"), ("MX", "+ partial sale,\nmixed cargo (MX)"),
            ("MW", "+ weighing\nrate (MW)")]
    stats = [(lab, m_stats(n)) for n, lab in runs]
    if any(s is None for _, s in stats):
        print("skip: experiments/out/m2 runs missing")
        return
    print("M2 sea days / ship-year, annual loss %", [(lab.split()[0], round(s[0]), round(s[1], 1)) for lab, s in stats])
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, i, title, band, unit in ((axs[0], 0, "Days at sea per ship-year", (0, 80), "historical: < 80"),
                                     (axs[1], 1, "Ships lost per ship-year (%)", (4, 12), "historical: 4–12%")):
        vals = [s[i] for _, s in stats]
        ax.axhspan(*band, color="#f1efe8", zorder=0)
        ax.bar(range(len(vals)), vals, 0.5, color=C1, edgecolor="white", linewidth=2)
        for x, v in enumerate(vals):
            ax.text(x, v * 1.02, f"{v:.0f}", ha="center", fontsize=9)
        ax.set_xticks(range(len(vals)), [lab for lab, _ in stats])
        ax.tick_params(axis="x", length=0, labelsize=8)
        ax.set_title(f"{title}  (shaded: {unit})")
    save(fig, "port-time-tempo.png")


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    fig_rules()
    fig_information()
    fig_entry()
    fig_artifact()
    fig_tempo()
