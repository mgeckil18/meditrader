"""Experiment D5b3f: entry diagnosis: why ships keep entering when realised returns are below the bond rate. Defines the setups (`cfg_of`) that later runs and the Rust core use.
Run (repo root): python3 experiments/d5b3f_entry_diag.py YEARS SETUP,...   e.g. 4 VRS,F
Report (Turkish): docs/experiments/D5b3f.md

(Original notes in Turkish below.)

Deney D5b3f: giriş teşhisi. Gerçekleşen getiri senedin altındayken neden yılda ~29 gemi giriyor ve filo küçülmüyor?

Davranış değiştirmez; yalnızca kayıt tutar (aynı seed'de giriş sayısı değişmemeli, kontrol: `check`).
Kayıtlar:
  - giriş: her ay, her liman için sicil (track), limanın "şu anki en iyi fırsatı" (public voy), inanç, alternatif,
    batma bedeli, ikna olan pay, beklenen giriş (lam), giriş
  - kalma: çıkış adayının inancı (kendi sicili + önündeki fırsat) ve kalıp kalmadığı
  - giren kuşağı: girişte gördükleri inanç ile gerçekleşen ömür getirisi
  - sefer: beklenen ve gerçekleşen net kâr (voy_log)
Kullanım: python3 experiments/d5b3f_entry_diag.py 4 VRS,F   Rapor: docs/experiments/D5b3f.md
"""
import json
import math
import os
import pathlib
import sys
from multiprocessing import Pool

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import d5b3e_crowd_ablation as E  # noqa: E402
from d5b3c_finance import BASE  # noqa: E402
from sim.world5 import D5Config, D5World  # noqa: E402

OUT = ROOT / "experiments" / "out" / os.environ.get("DIAG_OUT", "d5b3f")
OUT.mkdir(parents=True, exist_ok=True)
SETUPS = dict(E.SETUPS)
for _b in ("VRS", "F"):                     # D5b3f.2: düzeltme varyantları
    SETUPS[_b + "-cold"] = dict(SETUPS[_b], cold_track="neutral")
    SETUPS[_b + "-cold-nobonus"] = dict(SETUPS[_b], cold_track="neutral", entry_bonus=False)
    # D5b3g (K-029): W = snapshot başlangıcı; T = ortak eşik + sefer sonunda çıkış + bonus yok; A = batanlar dahil
    # kamu sicili + credibility, batma bedeli eşikte yok (kayıp sicilde)
    SETUPS[_b + "-W"] = dict(SETUPS[_b], warm_start=True)
    SETUPS[_b + "-WT"] = dict(SETUPS[_b + "-W"], hurdle_rule="common", exit_rule="voyage", entry_bonus=False)
    SETUPS[_b + "-WTA"] = dict(SETUPS[_b + "-WT"], public_track="aggregate", entry_ruin=False)
    # D5b3g.2: sönümleme ablation'ları (Claude): Dixit bandı vekili, yavaş giriş, daha güçlü credibility
    SETUPS[_b + "-WTA-band"] = dict(SETUPS[_b + "-WTA"], exit_premium=0.0)
    SETUPS[_b + "-WTA-slow"] = dict(SETUPS[_b + "-WTA"], entry_attention=0.005)
    SETUPS[_b + "-WTA-k36"] = dict(SETUPS[_b + "-WTA"], shrink_k=36.0)
    # D5b3g.3 (2026-10-30): U = kullanıcının 3 × 3 ay teyitli girişi; R = real options bandı (κ = 1); U + R
    SETUPS[_b + "-WTA-U"] = dict(SETUPS[_b + "-WTA"], entry_confirm=3, entry_confirm_gap=3)
    SETUPS[_b + "-WTA-R"] = dict(SETUPS[_b + "-WTA"], band_kappa=1.0)
    SETUPS[_b + "-WTA-UR"] = dict(SETUPS[_b + "-WTA-U"], band_kappa=1.0)
    # D5b3h (Ö1): credibility k veriden (Bühlmann-Straub)
    SETUPS[_b + "-WTA-UR-B"] = dict(SETUPS[_b + "-WTA-UR"], cred_rule="buhlmann")
    # R1 (K-030): bacak + bölge tehlikesi, dinamik korsan baskısı; S = gemi kaybı yenileme bedeli (¼ sermaye, vekil ⚠️)
    SETUPS[_b + "-WTA-UR-B-R1"] = dict(SETUPS[_b + "-WTA-UR-B"], hazard_model="leg")
    SETUPS[_b + "-WTA-UR-B-R1S"] = dict(SETUPS[_b + "-WTA-UR-B-R1"], ship_loss=60_000.0)
    # Ö3 (D5b3j, kullanıcı 2026-11-06): gemi piyasası; band (R) kalkar. -noU: teyitli giriş de kalkar (Ö5 ablation)
    SETUPS[_b + "-B-R1-O3"] = dict(SETUPS[_b + "-WTA-UR-B-R1"], ship_market=True, band_kappa=0.0)
    SETUPS[_b + "-B-R1-O3-noU"] = dict(SETUPS[_b + "-B-R1-O3"], entry_confirm=1)
YEARS = int(os.environ.get("YEARS", 6))


class DiagWorld(D5World):
    def __init__(self, cfg):
        self.elog, self.slog, self.xlog, self.born = [], [], [], {}
        self._in_entry = False
        super().__init__(cfg)

    def _entry_signal(self, p, r_bar):
        belief, alt, conv = super()._entry_signal(p, r_bar)
        self._sig[p] = dict(track=self._public_track(), voy=self._public_voy, belief=belief, alt=alt, conv=conv,
                            ruin=self._ruin_price(), pool_units=self.pool[p] / self.cfg.capital,
                            route=self._public_route,
                            n_here=sum(1 for m in self.merchants if not m.is_player and m.loc == p and m.state == "buying"))
        return belief, alt, conv

    def _entry_opportunity(self, r):
        self._sig, n0 = {}, len(self.entry_log)
        self._in_entry = True
        try:
            super()._entry_opportunity(r)
        finally:
            self._in_entry = False
        for day, p, r_exp, k, belief in self.entry_log[n0:]:
            sg = self._sig[p]
            self.elog.append(dict(day=day, p=p, r_exp=r_exp, k=k, lam=self.cfg.entry_attention * sg["pool_units"] * sg["conv"], **sg))

    def _belief(self, r_opp, voyage_frac, track):
        b = super()._belief(r_opp, voyage_frac, track)
        if not self._in_entry and track is not None and self.day > 0:
            self.slog.append(dict(day=self.day, track=track, voy=voyage_frac, belief=b,
                                  bar=self.cfg.bond_rate, ruin=self._ruin_price()))
        return b

    def _exit_decision(self, m):
        e = self._own_expect(m)
        super()._exit_decision(m)
        if e is not None:
            self.xlog.append(dict(day=self.day, e=e, pub=self._public_track(), retire=m.retire,
                                  n=sum(1 for x in m.record if self.day - x[0] <= 365)))

    def _new_merchant(self, port, rng, capital=None):
        m = super()._new_merchant(port, rng, capital)
        if self.day > 0:
            # girişte görülen inanç: o limanın son kaydı
            last = [x for x in self.elog if x["p"] == port]
            self.born[m.id] = (m, self.day, last[-1]["belief"] if last else None)
        return m


def _agg(w):
    """Toplam sermaye getirisi (K-025; d5b3d_lender_entry ile aynı tanım, batanlar dahil, tüm koşu)"""
    end = w.day
    ppl = [(m, end, m.net_worth()) for m in w.merchants if not m.is_player] + [g for g in w.gone if not g[0].is_player]
    pnl = sum(v + m.divs - (m.v0 or m.start_capital) for m, d_, v in ppl)
    capy = sum((m.v0 or m.start_capital) * max((d_ - max(m.born_day, m.t0)) / 365.0, 1 / 365) for m, d_, v in ppl)
    return pnl / capy


def _returns(w):
    """Ö0: tüccar başına toplam sermaye getirisi (öz sermaye; batanlar ve çıkanlar dahil, t0'dan sonra).
    Döner: [(yıllık getiri, sermaye-yıl, yerleşik mi, yıl)]. Yerleşik = snapshot anında var olan tüccar."""
    end = w.day
    val = getattr(w, "_ship_R", lambda m: 0.0)
    ppl = ([(m, end, m.equity() + val(m)) for m in w.merchants if not m.is_player]
           + [(m, d_, v + m.exit_ship) for m, d_, v in w.gone if not m.is_player])     # Ö3: gemi yerine koyma değeriyle
    out = []
    for m, d_, v in ppl:
        v0 = m.v0 or m.start_capital
        yrs = max((d_ - max(m.born_day, m.t0)) / 365.0, 1 / 365)
        out.append(((v + m.divs - v0) / (v0 * yrs), v0 * yrs, m.born_day <= w.t0_day, yrs))
    return out


def cfg_of(name, seed, years=YEARS):
    return D5Config(seed=seed, **{**BASE, **SETUPS[name], "years": years})


def run(args):
    name, seed = args
    w = DiagWorld(cfg_of(name, seed))
    w.run()
    cap = w.cfg.capital
    end = w.day
    gone_day = {m.id: d for (m, d, _) in w.gone}
    cohort = []
    for mid, (m, d0, bel) in w.born.items():
        d1 = gone_day.get(mid, end)
        life = max(d1 - d0, 1)
        val = m.marks[-1] if m.marks else m.net_worth() + m.divs
        if mid in gone_day and m.broke:
            val = 0.1 * m.start_capital
        cohort.append(dict(d0=d0, life=life, belief=bel, ret=(val / m.start_capital) ** (365 / max(life, 180)) - 1,
                           gone=mid in gone_day, broke=bool(m.broke)))
    vl = [x for x in w.voy_log if x[0] > 365 + w.t0_day]
    bias = [((x[6] - x[8]) * x[5], x[7] * x[5]) for x in vl if x[7] > 0]
    n = np.array(w.log["n_npc"], dtype=float)
    fleet = [float(n[i]) for i in range(0, len(n), 30)]
    out = dict(name=name, fleet=fleet, n_init=w.n_init, agg=_agg(w), seed=seed, entries=w.entries, exits=w.exits, bankruptcies=w.bankruptcies,
               elog=w.elog, slog=w.slog, xlog=w.xlog, cohort=cohort, t0=w.t0_day,
               pub_log=getattr(w, 'pub_log', []),
               voy_bias=sum(a for a, _ in bias) / max(sum(b for _, b in bias), 1),
               n_markets=len(w.markets), trailing_end=w.trailing_median, cap=cap,
               rets=_returns(w), cred_log=[x for x in getattr(w, 'cred_log', []) if x[0] >= w.t0_day],
               dep_log=getattr(w, 'dep_log', []),
               ship_log=[x for x in getattr(w, 'ship_log', []) if x[0] >= w.t0_day], ships_lost=getattr(w, 'ships_lost', 0),
               ship_ages=[(w.day - m.ship) / 365 for m in w.merchants if not m.is_player and m.ship is not None])
    with open(OUT / f"{name}_{seed}.json", "w") as f:
        json.dump(out, f, default=float)
    return name, seed, w.entries


def _snap(args):
    from sim.world5 import build_snapshot, snapshot_path
    n, k = args
    build_snapshot(cfg_of(n, 0), k)
    return n, k, open(snapshot_path(cfg_of(n, 0), k).with_suffix(".json")).read()


def check():
    """Kayıt davranışı değiştirmemeli: aynı seed'de giriş sayısı aynı (3 × 3, 2 yıl)."""
    a = DiagWorld(cfg_of("VRS", 1, years=2))
    a.run()
    b = D5World(cfg_of("VRS", 1, years=2))
    b.run()
    print("check entries", a.entries, b.entries, "exits", a.exits, b.exits)
    assert (a.entries, a.exits) == (b.entries, b.exits)


if __name__ == "__main__":
    if sys.argv[1] == "check":
        check()
        sys.exit()
    seeds = range(int(sys.argv[1]))
    names = sys.argv[2].split(",")
    jobs = [(n, s) for n in names for s in seeds if not (OUT / f"{n}_{s}.json").exists()]
    from sim.world5 import build_snapshot, snapshot_path
    snaps = sorted({(n, s % cfg_of(n, s).warm_n) for n, s in jobs if cfg_of(n, s).warm_start})
    snaps = [(n, k) for n, k in snaps if not snapshot_path(cfg_of(n, 0), k).exists()]
    if snaps:
        with Pool(int(os.environ.get("NPROC", 8)), maxtasksperchild=1) as pool:
            for res in pool.imap_unordered(_snap, snaps):
                print("snapshot", *res, flush=True)
    with Pool(int(os.environ.get("NPROC", 8)), maxtasksperchild=1) as pool:
        for res in pool.imap_unordered(run, jobs):
            print(*res, flush=True)
