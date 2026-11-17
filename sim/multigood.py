"""D4: one port, many goods, shared urban budget (LES + CES demand).

(Original notes in Turkish below.)

D4: tek liman, çok mal, ortak kent bütçesi.

Her mal kendi D1 motorunda (ön ayar H) yaşar: köylü/üretici, dükkâncılar, stokçular.
Kentin alımı ise ortak bir talep modeliyle yapılır (yarışan yuva: talep yapısı):

  independent  her malın kendi esnek talebi ve bütçe sınırı (D1 modeli; kontrol)
  les          Linear Expenditure System (Stone 1954): önce subsistence miktarları,
               kalan gelir sabit marjinal paylarla bölünür → income effect
  les_ces      LES kategoriler üzerinde (tahıl, yağ, kumaş, diğer) + tahıl içinde
               buğday/arpa CES ikamesi (two-stage budgeting) → substitution effect
"""
import dataclasses
import datetime as dt
from dataclasses import dataclass, field

import numpy as np

from .engine import H, START_DATE, D1Config, D1Sim
from .ledger import Ledger


@dataclass
class GoodSpec:
    code: str
    q_per_capita: float          # normal yıllık tüketim (kişi başı)
    ref_price: float
    elasticity: float            # sadece "independent" modelde
    harvest_month: int = 7
    self_share: float = 0.4
    n_storers: int = 2
    continuous: bool = False
    subsistence: float = 0.0     # LES: kişi başı yıllık zorunlu miktar


GOODS = [
    GoodSpec("WHT", 1.4, 100.0, -0.4, harvest_month=7, self_share=0.4, n_storers=2, subsistence=1.0),
    GoodSpec("BRL", 0.6, 60.0, -0.5, harvest_month=6, self_share=0.4, n_storers=1, subsistence=0.4),
    GoodSpec("OIL", 0.3, 150.0, -0.6, harvest_month=11, self_share=0.2, n_storers=1, subsistence=0.1),
    GoodSpec("CLO", 0.05, 800.0, -1.2, harvest_month=1, self_share=0.0, n_storers=0, continuous=True,
             subsistence=0.0),
]


@dataclass
class ClassSpec:
    """Kent sınıfı (D4b; bkz. docs/research/history/consumer-profiles-16c.md §4)."""
    name: str
    pop_share: float
    income_rel: float                 # kişi başı gelir, yoksul = 1
    shares: dict                      # referans fiyatlarda bütçe payları: CER, OIL, CLO (kalan = diğer)
    subsistence: dict                 # normal miktarın zorunlu kısmı: CER, OIL, CLO
    wheat_value_share: float          # tahıl harcamasında buğdayın payı (kalan arpa)


CLASSES_3 = [
    ClassSpec("zengin", 0.10, 12.0, {"CER": 0.08, "OIL": 0.03, "CLO": 0.15},
              {"CER": 0.3, "OIL": 0.3, "CLO": 0.0}, 0.95),
    ClassSpec("orta", 0.20, 3.0, {"CER": 0.20, "OIL": 0.06, "CLO": 0.10},
              {"CER": 0.6, "OIL": 0.4, "CLO": 0.0}, 0.85),
    ClassSpec("yoksul", 0.70, 1.0, {"CER": 0.35, "OIL": 0.07, "CLO": 0.06},
              {"CER": 0.85, "OIL": 0.5, "CLO": 0.0}, 0.70),
]
POOR_INCOME_YEAR = 250.0              # yoksul kişi başı yıllık gelir, soldo (ölçek yer tutucu ⚠️)


@dataclass
class D4Config:
    seed: int = 0
    years: int = 10
    kappa: float = 0.01
    population: int = 100_000
    yield_sigma: float = 0.15
    demand: str = "les_ces"      # independent | les | les_ces
    food_share_of_income: float = 0.6   # referans fiyatlarda modellenen 4 malın gelirdeki payı
    ces_sigma: float = 2.0       # buğday-arpa ikame esnekliği
    wheat_yield_overrides: dict = field(default_factory=dict)
    classes: list | None = None   # D4b: sınıflı talep (les_ces her sınıf için)
    freeze_cereal: bool = False   # D4b ablasyonu: bütçe kararında tahıl fiyatları referansta sabit


class D4World:
    def __init__(self, cfg: D4Config, continuous_pace_fix: bool = True):
        self.cfg = cfg
        self.ledger = Ledger()
        self.date = START_DATE
        # Kopya: sınıflı kalibrasyon miktarları değiştirir; ortak GOODS listesi bozulmamalı.
        self.specs = {g.code: dataclasses.replace(g) for g in GOODS}
        if cfg.classes:
            self._class_quantities()
        self.ports: dict[str, D1Sim] = {}
        for i, g in enumerate(self.specs.values()):
            kw = dict(H, kappa=cfg.kappa, seed=cfg.seed, years=cfg.years,
                      yield_sigma=0.0 if g.continuous else cfg.yield_sigma,
                      good=g.code, population=cfg.population, need_per_capita_year=g.q_per_capita,
                      ref_price=g.ref_price, elasticity=g.elasticity, harvest_month=g.harvest_month,
                      self_share=g.self_share, n_storers=g.n_storers,
                      continuous_supply=g.continuous, continuous_pace_fix=continuous_pace_fix,
                      farmer_front_load=0.0 if g.continuous else H.get("farmer_front_load", 0.0))
            if g.code == "WHT":
                kw["yield_overrides"] = dict(cfg.wheat_yield_overrides)
            self.ports[g.code] = D1Sim(D1Config(**kw), ledger=self.ledger, rng_salt=10 + i)
        if cfg.classes:
            self._calibrate_classes()
        else:
            self._calibrate()
        self.ledger.start(self._money_total(), self._goods_totals())
        self.log = {k: [] for k in ["date", "spend", "income"]
                    + [f"{c}_{x}" for c in self.specs for x in ("ask", "bought", "spend")]
                    + ([f"{k.name}_{c}" for k in cfg.classes for c in self.specs] if cfg.classes else [])}

    # --- kalibrasyon: referans fiyatlarda her model normal miktarları üretsin ----------
    def _calibrate(self):
        cfg = self.cfg
        n = cfg.population
        self.normal_q = {c: g.q_per_capita * n / 365.0 for c, g in self.specs.items()}   # günlük
        self.gamma = {c: g.subsistence * n / 365.0 for c, g in self.specs.items()}
        ref = {c: g.ref_price for c, g in self.specs.items()}
        spend_ref = sum(ref[c] * self.normal_q[c] for c in self.specs)
        self.income = spend_ref / cfg.food_share_of_income          # günlük kent geliri
        # LES (mal düzeyinde): β_i = p_i (q_i − γ_i) / S
        S = self.income - sum(ref[c] * self.gamma[c] for c in self.specs)
        self.beta = {c: ref[c] * (self.normal_q[c] - self.gamma[c]) / S for c in self.specs}
        # LES + CES: tahıl kategorisi (WHT, BRL) CES bileşik; diğerleri tek mallı kategori
        sig = cfg.ces_sigma
        e_w, e_b = ref["WHT"] * self.normal_q["WHT"], ref["BRL"] * self.normal_q["BRL"]
        s_w = e_w / (e_w + e_b)
        # Referans fiyatlarda bileşik fiyat 1 olacak şekilde CES ağırlıkları
        self.ces_a = {"WHT": s_w * ref["WHT"] ** (sig - 1), "BRL": (1 - s_w) * ref["BRL"] ** (sig - 1)}
        self.cereal_q_ref = e_w + e_b                               # bileşik birim (P=1'de harcama)
        cereal_gamma = (ref["WHT"] * self.gamma["WHT"] + ref["BRL"] * self.gamma["BRL"])   # bileşik birim
        self.cat_gamma = {"CER": cereal_gamma, "OIL": self.gamma["OIL"], "CLO": self.gamma["CLO"]}
        S2 = self.income - (cereal_gamma * 1.0 + ref["OIL"] * self.gamma["OIL"] + ref["CLO"] * self.gamma["CLO"])
        self.cat_beta = {"CER": (self.cereal_q_ref - cereal_gamma) / S2,
                         "OIL": ref["OIL"] * (self.normal_q["OIL"] - self.gamma["OIL"]) / S2,
                         "CLO": ref["CLO"] * (self.normal_q["CLO"] - self.gamma["CLO"]) / S2}

    # --- D4b: sınıflı talep -------------------------------------------------
    def _class_quantities(self):
        """Sınıf bütçe paylarından malların normal kişi başı miktarlarını türet."""
        cfg = self.cfg
        n = cfg.population
        ref = {c: g.ref_price for c, g in self.specs.items()}
        tot = {c: 0.0 for c in self.specs}
        self.class_income = {}
        for k in cfg.classes:
            Yk = k.pop_share * n * k.income_rel * POOR_INCOME_YEAR / 365.0     # günlük
            self.class_income[k.name] = Yk
            e_cer = k.shares["CER"] * Yk
            tot["WHT"] += e_cer * k.wheat_value_share / ref["WHT"]
            tot["BRL"] += e_cer * (1 - k.wheat_value_share) / ref["BRL"]
            tot["OIL"] += k.shares["OIL"] * Yk / ref["OIL"]
            tot["CLO"] += k.shares["CLO"] * Yk / ref["CLO"]
        for c, g in self.specs.items():
            g.q_per_capita = tot[c] * 365.0 / n

    def _calibrate_classes(self):
        cfg = self.cfg
        ref = {c: g.ref_price for c, g in self.specs.items()}
        self.normal_q = {c: g.q_per_capita * cfg.population / 365.0 for c, g in self.specs.items()}
        self.income = sum(self.class_income.values())
        sig = cfg.ces_sigma
        self.cls = []
        for k in cfg.classes:
            Yk = self.class_income[k.name]
            E = {cat: k.shares[cat] * Yk for cat in ("CER", "OIL", "CLO")}
            # Tahıl bileşiği: referansta bileşik fiyat 1 → bileşik miktar = harcama
            a = {"WHT": k.wheat_value_share * ref["WHT"] ** (sig - 1),
                 "BRL": (1 - k.wheat_value_share) * ref["BRL"] ** (sig - 1)}
            q_ref = {"CER": E["CER"], "OIL": E["OIL"] / ref["OIL"], "CLO": E["CLO"] / ref["CLO"]}
            P_ref = {"CER": 1.0, "OIL": ref["OIL"], "CLO": ref["CLO"]}
            gamma = {cat: k.subsistence[cat] * q_ref[cat] for cat in q_ref}
            S = Yk - sum(P_ref[cat] * gamma[cat] for cat in q_ref)
            beta = {cat: (E[cat] - P_ref[cat] * gamma[cat]) / S for cat in q_ref}
            self.cls.append(dict(name=k.name, Y=Yk, a=a, gamma=gamma, beta=beta))

    def _desired_by_class(self, p: dict) -> dict:
        sig = self.cfg.ces_sigma
        out = {}
        for k in self.cls:
            den = sum(k["a"][c] * p[c] ** (1 - sig) for c in ("WHT", "BRL"))
            P = {"CER": den ** (1 / (1 - sig)), "OIL": p["OIL"], "CLO": p["CLO"]}
            S = k["Y"] - sum(P[cat] * k["gamma"][cat] for cat in P)
            if S >= 0:
                E = {cat: P[cat] * k["gamma"][cat] + k["beta"][cat] * S for cat in P}
            else:
                f = k["Y"] / sum(P[cat] * k["gamma"][cat] for cat in P)
                E = {cat: P[cat] * k["gamma"][cat] * f for cat in P}
            q = {c: E["CER"] * k["a"][c] * p[c] ** (1 - sig) / den / p[c] for c in ("WHT", "BRL")}
            q["OIL"] = E["OIL"] / p["OIL"]
            q["CLO"] = E["CLO"] / p["CLO"]
            out[k["name"]] = q
        return out

    def _money_total(self) -> int:
        return sum(p._money_total() for p in self.ports.values())

    def _goods_totals(self) -> dict:
        out = {}
        for p in self.ports.values():
            out.update(p._goods_totals())
        return out

    # --- talep modelleri ----------------------------------------------------
    def _cereal_index(self, p: dict) -> float:
        sig = self.cfg.ces_sigma
        tot = sum(self.ces_a[c] * p[c] ** (1 - sig) for c in ("WHT", "BRL"))
        return tot ** (1 / (1 - sig))

    def _desired(self, p: dict) -> dict:
        """Bugünkü fiyatlarda kentin her maldan almak istediği miktar (günlük)."""
        model, Y = self.cfg.demand, self.income
        if model == "les":
            S = Y - sum(p[c] * self.gamma[c] for c in self.specs)
            if S >= 0:
                return {c: self.gamma[c] + self.beta[c] * S / p[c] for c in self.specs}
            k = Y / sum(p[c] * self.gamma[c] for c in self.specs)   # gelir zorunluları bile karşılamıyor
            return {c: self.gamma[c] * k for c in self.specs}
        if model == "les_ces":
            P = {"CER": self._cereal_index(p), "OIL": p["OIL"], "CLO": p["CLO"]}
            S = Y - sum(P[k] * self.cat_gamma[k] for k in P)
            if S >= 0:
                E = {k: P[k] * self.cat_gamma[k] + self.cat_beta[k] * S for k in P}
            else:
                k_ = Y / sum(P[k] * self.cat_gamma[k] for k in P)
                E = {k: P[k] * self.cat_gamma[k] * k_ for k in P}
            sig = self.cfg.ces_sigma
            den = sum(self.ces_a[c] * p[c] ** (1 - sig) for c in ("WHT", "BRL"))
            out = {c: E["CER"] * self.ces_a[c] * p[c] ** (1 - sig) / den / p[c] for c in ("WHT", "BRL")}
            out["OIL"] = E["OIL"] / p["OIL"]
            out["CLO"] = E["CLO"] / p["CLO"]
            return out
        raise ValueError(model)

    def _buy(self, port: D1Sim, qty: float) -> tuple[float, int]:
        bought, paid = 0.0, 0
        for s in port._sorted_shops(lambda s: s.ask()):
            price = s.ask()
            request = max(0.0, qty - bought)
            s.requests_today += request
            q = min(request, s.stock)
            if q <= 0:
                continue
            pay = int(round(q * price))
            s.cash += pay
            s.stock -= q
            bought += q
            paid += pay
            self.ledger.money_source("urban_consumers", pay)
            self.ledger.goods_sink(port.good, "consumption", q)
        return bought, paid

    def step(self):
        pres = {c: port.step_pre() for c, port in self.ports.items()}
        results = {}
        if self.cfg.demand == "independent":
            for c, port in self.ports.items():
                results[c] = port._urban_buys()
            spends = {c: (results[c][0] * results[c][2] if results[c][0] > 0 else 0.0) for c in self.ports}
        else:
            p = {c: min(pres[c]["asks"]) for c in self.ports}
            if self.cfg.freeze_cereal:          # ablasyon: bütçe kararında tahıl fiyatı referansta
                p_dec = dict(p, WHT=self.specs["WHT"].ref_price, BRL=self.specs["BRL"].ref_price)
            else:
                p_dec = p
            if self.cfg.classes:
                by_class = self._desired_by_class(p_dec)
                want = {c: sum(q[c] for q in by_class.values()) for c in self.ports}
            else:
                want = self._desired(p_dec)
            spends = {}
            for c, port in self.ports.items():
                b, paid = self._buy(port, want[c])
                if self.cfg.classes:
                    for kname, q in by_class.items():
                        share = q[c] / want[c] if want[c] > 0 else 0.0
                        self.log[f"{kname}_{c}"].append(b * share)
                need = self.normal_q[c]
                results[c] = (b, max(0.0, need - b) / need, paid / b if b > 0 else float("nan"))
                spends[c] = paid
        for c, port in self.ports.items():
            port.step_post(pres[c], *results[c])

        L = self.log
        L["date"].append(self.date)
        L["income"].append(self.income)
        L["spend"].append(sum(spends.values()))
        for c, port in self.ports.items():
            L[f"{c}_ask"].append(port.log["ask_mean"][-1])
            L[f"{c}_bought"].append(results[c][0])
            L[f"{c}_spend"].append(spends[c])
        self.ledger.check(self._money_total(), self._goods_totals())
        self.date += dt.timedelta(days=1)

    def run(self):
        end = dt.date(START_DATE.year + self.cfg.years, START_DATE.month, START_DATE.day)
        while self.date < end:
            self.step()
        return {k: (np.array(v) if k != "date" else v) for k, v in self.log.items()}
