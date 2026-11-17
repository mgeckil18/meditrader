"""D4c: production chain (raw material -> final good), producer pools, wages.

(Original notes in Turkish below.)

D4c: üretim zinciri. Hammadde → son ürün, üretici havuzları, ücretler.

Tasarım: docs/design/production-chains.md

Mallar:
  Tüketim:   WHT buğday, BRL arpa, OIL zeytinyağı, CLC kaba yünlü kumaş, CLF ince yünlü kumaş
  Hammadde:  WOL yün (kırsal havuz, kırkım Mayıs), ALM şap + boya (dışsal sürekli arz)
Üretim (Leontief reçeteler, ⚠️ yer tutucu):
  CLC = 1,0 yün + 4 işgünü
  CLF = 1,5 yün + 0,2 şap/boya + 12 işgünü
Üreticiler bireysel ajan değil, kent başına ürün başına bir havuz (İ8).

Ücret aşamaları:
  Aşama 1 (wages_endogenous=False): ücretler sistemden çıkar (yutak); kent geliri dışsal ve sabit.
  Aşama 2 (wages_endogenous=True): ücretler orta ve yoksul sınıfın gelirine eklenir; üretim
           kısılınca zanaatkârın geliri düşer (Labrousse çarpanı).
"""
import dataclasses
import datetime as dt
from dataclasses import dataclass, field

import numpy as np

from .engine import H, START_DATE, D1Config, D1Sim
from .ledger import Ledger
from .multigood import POOR_INCOME_YEAR, ClassSpec

WAGE = 2.5          # soldo / işgünü (yoksul hanenin geliriyle tutarlı ölçek ⚠️)


@dataclass
class Good:
    code: str
    ref_price: float
    kind: str                     # "harvest" | "continuous" | "produced"
    consumer: bool = True
    elasticity: float = -0.5
    harvest_month: int = 7
    self_share: float = 0.0
    n_storers: int = 0
    q_per_capita: float = 0.0     # kalibrasyonda doldurulur


@dataclass
class Recipe:
    inputs: dict                  # {girdi kodu: birim ürün başına miktar}
    labor: float                  # birim ürün başına işgünü


RECIPES = {
    "CLC": Recipe({"WOL": 1.0}, 4.0),
    "CLF": Recipe({"WOL": 1.5, "ALM": 0.2}, 12.0),
}


def default_goods():
    return [
        Good("WHT", 100.0, "harvest", harvest_month=7, self_share=0.4, n_storers=2),
        Good("BRL", 60.0, "harvest", harvest_month=6, self_share=0.4, n_storers=1),
        Good("OIL", 150.0, "harvest", harvest_month=11, self_share=0.2, n_storers=1),
        Good("WOL", 10.0, "harvest", consumer=False, harvest_month=5, self_share=0.1, n_storers=1),
        Good("ALM", 50.0, "continuous", consumer=False),
        Good("CLC", 22.0, "produced"),
        Good("CLF", 60.0, "produced"),
    ]


CLASSES_C = [
    ClassSpec("zengin", 0.10, 12.0, {"CER": 0.08, "OIL": 0.03, "CLC": 0.01, "CLF": 0.14},
              {"CER": 0.3, "OIL": 0.3, "CLC": 0.0, "CLF": 0.0}, 0.95),
    ClassSpec("orta", 0.20, 3.0, {"CER": 0.20, "OIL": 0.06, "CLC": 0.07, "CLF": 0.03},
              {"CER": 0.6, "OIL": 0.4, "CLC": 0.0, "CLF": 0.0}, 0.85),
    ClassSpec("yoksul", 0.70, 1.0, {"CER": 0.35, "OIL": 0.07, "CLC": 0.06, "CLF": 0.0},
              {"CER": 0.85, "OIL": 0.5, "CLC": 0.0, "CLF": 0.0}, 0.70),
]
WAGE_SHARES = {"zengin": 0.0, "orta": 0.3, "yoksul": 0.7}   # ücretlerin sınıflara dağılımı


@dataclass
class ProducerPool:
    """Bir kentte bir ürünün üretim sektörü (çok sayıda atölye ve işçinin toplamı)."""
    good: str
    recipe: Recipe
    capacity: float               # birim/gün
    cash: int
    util: float = 0.85
    output: float = 0.0
    inputs: dict = field(default_factory=dict)
    input_days: float = 30.0      # hedef girdi stoku (gün)
    margin_target: float = 0.08
    util_speed: float = 0.05      # kullanım oranının hedefe günlük yaklaşma hızı
    util_hist: list = field(default_factory=list)
    divs: int = 0

    def rate(self) -> float:
        return self.capacity * self.util

    def unit_cost(self, in_prices: dict) -> float:
        return sum(q * in_prices[g] for g, q in self.recipe.inputs.items()) + self.recipe.labor * WAGE


@dataclass
class D4cConfig:
    seed: int = 0
    years: int = 10
    kappa: float = 0.01
    population: int = 100_000
    yield_sigma: float = 0.15
    ces_sigma: float = 2.0
    wages_endogenous: bool = False
    yield_overrides: dict = field(default_factory=dict)      # {mal: {yıl: çarpan}}
    rich_income_shock: dict = field(default_factory=dict)    # {yıl_indeksi: çarpan}


class D4cWorld:
    def __init__(self, cfg: D4cConfig):
        self.cfg = cfg
        self.ledger = Ledger()
        self.date = START_DATE
        self.day = 0
        self.goods = {g.code: g for g in default_goods()}
        self.classes = [dataclasses.replace(k) for k in CLASSES_C]
        self.consumer_cats = ["CER"] + [c for c, g in self.goods.items()
                                        if g.consumer and c not in ("WHT", "BRL")]
        self._calibrate_quantities()
        self.ports: dict[str, D1Sim] = {}
        for i, g in enumerate(self.goods.values()):
            kw = dict(H, kappa=cfg.kappa, seed=cfg.seed, years=cfg.years, good=g.code,
                      population=cfg.population, need_per_capita_year=max(g.q_per_capita, 1e-6),
                      ref_price=g.ref_price, elasticity=g.elasticity,
                      harvest_month=g.harvest_month, self_share=g.self_share,
                      n_storers=g.n_storers,
                      yield_sigma=cfg.yield_sigma if g.kind == "harvest" else 0.0,
                      continuous_supply=g.kind == "continuous",
                      farmer_front_load=H.get("farmer_front_load", 0.0) if g.kind == "harvest" else 0.0,
                      yield_overrides=dict(cfg.yield_overrides.get(g.code, {})))
            if g.kind == "produced":
                kw["supply_surplus"] = 0.0          # arz yalnızca üretici havuzundan gelir
            self.ports[g.code] = D1Sim(D1Config(**kw), ledger=self.ledger, rng_salt=20 + i)
        self._calibrate_demand()
        self.pools = {}
        for c, rec in RECIPES.items():
            daily = self.normal_q[c]
            cap = daily / 0.85
            in_p = {g: self.goods[g].ref_price for g in rec.inputs}
            cost = sum(q * in_p[g] for g, q in rec.inputs.items()) + rec.labor * WAGE
            pool = ProducerPool(good=c, recipe=rec, capacity=cap, cash=int(60 * daily * cost))
            pool.inputs = {g: q * daily * pool.input_days for g, q in rec.inputs.items()}
            pool.output = daily * 10
            self.pools[c] = pool
        self.normal_wage_bill = sum(self.normal_q[c] * r.labor * WAGE for c, r in RECIPES.items())
        self.wage_bill_yday = self.normal_wage_bill
        self.ledger.start(self._money_total(), self._goods_totals())
        keys = ["date", "income"] + [f"{c}_{x}" for c in self.goods for x in ("ask", "bought")]
        keys += [f"{c}_{x}" for c in RECIPES for x in ("prod", "util", "cap", "margin")]
        keys += [f"{k.name}_{c}" for k in self.classes for c in self.goods if self.goods[c].consumer]
        keys += [f"{k.name}_income" for k in self.classes]
        self.log = {k: [] for k in keys}

    # --- kalibrasyon --------------------------------------------------------
    def _calibrate_quantities(self):
        n = self.cfg.population
        ref = {c: g.ref_price for c, g in self.goods.items()}
        tot = {c: 0.0 for c in self.goods}
        self.class_income_ref = {}
        for k in self.classes:
            Yk = k.pop_share * n * k.income_rel * POOR_INCOME_YEAR / 365.0
            self.class_income_ref[k.name] = Yk
            e = k.shares["CER"] * Yk
            tot["WHT"] += e * k.wheat_value_share / ref["WHT"]
            tot["BRL"] += e * (1 - k.wheat_value_share) / ref["BRL"]
            for cat in self.consumer_cats[1:]:
                tot[cat] += k.shares[cat] * Yk / ref[cat]
        # Girdi talebi reçetelerden
        for c, rec in RECIPES.items():
            for g, q in rec.inputs.items():
                tot[g] += q * tot[c]
        for c, g in self.goods.items():
            g.q_per_capita = tot[c] * 365.0 / n
        self.normal_q = {c: tot[c] for c in self.goods}

    def _calibrate_demand(self):
        ref = {c: g.ref_price for c, g in self.goods.items()}
        sig = self.cfg.ces_sigma
        self.cls = []
        for k in self.classes:
            Yk = self.class_income_ref[k.name]
            E = {cat: k.shares[cat] * Yk for cat in self.consumer_cats}
            a = {"WHT": k.wheat_value_share * ref["WHT"] ** (sig - 1),
                 "BRL": (1 - k.wheat_value_share) * ref["BRL"] ** (sig - 1)}
            P_ref = {"CER": 1.0, **{c: ref[c] for c in self.consumer_cats[1:]}}
            q_ref = {cat: E[cat] / P_ref[cat] for cat in self.consumer_cats}
            gamma = {cat: k.subsistence[cat] * q_ref[cat] for cat in self.consumer_cats}
            S = Yk - sum(P_ref[cat] * gamma[cat] for cat in self.consumer_cats)
            beta = {cat: (E[cat] - P_ref[cat] * gamma[cat]) / S for cat in self.consumer_cats}
            self.cls.append(dict(name=k.name, Y=Yk, a=a, gamma=gamma, beta=beta))

    # --- muhasebe -----------------------------------------------------------
    def _money_total(self) -> int:
        return sum(p._money_total() for p in self.ports.values()) + sum(p.cash for p in self.pools.values())

    def _goods_totals(self) -> dict:
        out = {}
        for p in self.ports.values():
            out.update(p._goods_totals())
        for c, pool in self.pools.items():
            out[c] += pool.output
            for g, q in pool.inputs.items():
                out[g] += q
        return out

    # --- talep --------------------------------------------------------------
    def _class_income(self, k: dict) -> float:
        Y = self.class_income_ref[k["name"]]
        yidx = self.date.year - START_DATE.year - (0 if self.date.month >= START_DATE.month else 1)
        if k["name"] == "zengin" and yidx in self.cfg.rich_income_shock:
            Y *= self.cfg.rich_income_shock[yidx]
        if self.cfg.wages_endogenous:
            share = WAGE_SHARES[k["name"]]
            Y += share * (self.wage_bill_yday - self.normal_wage_bill)
        return max(Y, 0.0)

    def _desired_by_class(self, p: dict) -> tuple[dict, dict]:
        sig = self.cfg.ces_sigma
        out, incomes = {}, {}
        for k in self.cls:
            Yk = self._class_income(k)
            incomes[k["name"]] = Yk
            den = sum(k["a"][c] * p[c] ** (1 - sig) for c in ("WHT", "BRL"))
            P = {"CER": den ** (1 / (1 - sig)), **{c: p[c] for c in self.consumer_cats[1:]}}
            S = Yk - sum(P[cat] * k["gamma"][cat] for cat in P)
            if S >= 0:
                E = {cat: P[cat] * k["gamma"][cat] + k["beta"][cat] * S for cat in P}
            else:
                f = Yk / max(sum(P[cat] * k["gamma"][cat] for cat in P), 1e-9)
                E = {cat: P[cat] * k["gamma"][cat] * f for cat in P}
            q = {c: E["CER"] * k["a"][c] * p[c] ** (1 - sig) / den / p[c] for c in ("WHT", "BRL")}
            for c in self.consumer_cats[1:]:
                q[c] = E[c] / p[c]
            out[k["name"]] = q
        return out, incomes

    def _buy_from_shops(self, port: D1Sim, qty: float, buyer_cash: float | None = None):
        """Dükkâncılardan en ucuzdan başlayarak al. buyer_cash verilirse nakitle sınırlı."""
        bought, paid = 0.0, 0
        for s in port._sorted_shops(lambda s: s.ask()):
            price = s.ask()
            request = max(0.0, qty - bought)
            s.requests_today += request
            q = min(request, s.stock)
            if buyer_cash is not None:
                q = min(q, max(0.0, (buyer_cash - paid) / price))
            if q <= 0:
                continue
            pay = int(round(q * price))
            s.cash += pay
            s.stock -= q
            bought += q
            paid += pay
        return bought, paid

    # --- üretici havuzları --------------------------------------------------
    def _pools_step(self):
        wage_bill = 0
        for c, pool in self.pools.items():
            out_port = self.ports[c]
            in_ask = {g: min(s.ask() for s in self.ports[g].shops) for g in pool.recipe.inputs}
            out_bid = float(np.mean([s.bid() for s in out_port.shops]))
            unit_cost = pool.unit_cost(in_ask)
            margin = (out_bid - unit_cost) / out_bid

            # 1) Üretim: kullanım × kapasite, girdiler ve ücret nakdi yettiği kadar
            q = pool.rate()
            for g, a in pool.recipe.inputs.items():
                q = min(q, pool.inputs[g] / a)
            q = min(q, max(0.0, pool.cash / (pool.recipe.labor * WAGE)))
            if q > 0:
                for g, a in pool.recipe.inputs.items():
                    pool.inputs[g] -= q * a
                    self.ledger.goods_sink(g, "production_input", q * a)
                pool.output += q
                self.ledger.goods_source(c, "production", q)
                wages = int(round(q * pool.recipe.labor * WAGE))
                pool.cash -= wages
                wage_bill += wages
                self.ledger.money_sink("wages", wages)

            # 2) Satış: dükkâncılara; stok şiştikçe maliyetin altına inmeye razı
            stock_days = pool.output / max(pool.rate(), 1e-9)
            reservation = unit_cost * (1.0 if stock_days < 15 else 0.85 if stock_days < 30 else 0.7)
            for s in out_port._sorted_shops(lambda s: s.bid(), reverse=True):
                price = s.bid()
                if price < reservation or pool.output <= 0:
                    break
                qty = min(pool.output, s.buy_room(price))
                if qty <= 0:
                    continue
                pay = int(round(qty * price))
                s.cash -= pay
                s.receive(qty, pay)
                pool.cash += pay
                pool.output -= qty

            # 3) Girdi alımı: hedef girdi stokuna kadar
            for g, a in pool.recipe.inputs.items():
                target = a * pool.rate() * pool.input_days
                need = max(0.0, target - pool.inputs[g])
                if need > 0:
                    got, paid = self._buy_from_shops(self.ports[g], need, buyer_cash=pool.cash * 0.5)
                    pool.inputs[g] += got
                    pool.cash -= paid

            # 4) Kullanım oranı: seviye (marj + stok) → hedef, yavaş yaklaşma (D1g dersi: PI)
            desired = 0.85 + 2.0 * (margin - pool.margin_target) - 0.02 * (stock_days - 10)
            desired = min(1.0, max(0.1, desired))
            pool.util += pool.util_speed * (desired - pool.util)
            pool.util_hist.append(pool.util)

            # 5) Kapasite (aylık): yüksek kullanım + kâr → büyür; düşük kullanım → küçülür
            if self.date.day == 1 and len(pool.util_hist) >= 90:
                u = float(np.mean(pool.util_hist[-90:]))
                if u > 0.92 and margin > pool.margin_target:
                    pool.capacity *= 1.01
                elif u < 0.6:
                    pool.capacity *= 0.99
            # Sahiplerin kâr çekimi: 90 günlük maliyetin üstündeki nakit
            excess = pool.cash - 90 * pool.rate() * unit_cost
            if excess > 0:
                d = int(excess * 0.01)
                pool.cash -= d
                pool.divs += d
                self.ledger.money_sink("producer_dividends", d)

            L = self.log
            L[f"{c}_prod"].append(q)
            L[f"{c}_util"].append(pool.util)
            L[f"{c}_cap"].append(pool.capacity)
            L[f"{c}_margin"].append(margin)
        self.wage_bill_yday = wage_bill

    # --- ana döngü ----------------------------------------------------------
    def step(self):
        pres = {c: port.step_pre() for c, port in self.ports.items()}
        self._pools_step()
        p = {c: min(pres[c]["asks"]) for c in self.ports}
        by_class, incomes = self._desired_by_class(p)
        results = {}
        for c, port in self.ports.items():
            g = self.goods[c]
            if g.consumer:
                want = sum(q[c] for q in by_class.values())
                b, paid = self._buy_from_shops(port, want)
                self.ledger.money_source("urban_consumers", paid)
                self.ledger.goods_sink(c, "consumption", b)
                for kname, q in by_class.items():
                    self.log[f"{kname}_{c}"].append(b * (q[c] / want if want > 0 else 0.0))
                need = self.normal_q[c]
                results[c] = (b, max(0.0, need - b) / need, paid / b if b > 0 else float("nan"))
            else:
                results[c] = (0.0, 0.0, float("nan"))
            self.log[f"{c}_bought"].append(results[c][0])
        for c, port in self.ports.items():
            port.step_post(pres[c], *results[c])
            self.log[f"{c}_ask"].append(port.log["ask_mean"][-1])
        self.log["date"].append(self.date)
        self.log["income"].append(sum(incomes.values()))
        for k, v in incomes.items():
            self.log[f"{k}_income"].append(v)
        self.ledger.check(self._money_total(), self._goods_totals())
        self.date += dt.timedelta(days=1)
        self.day += 1

    def run(self):
        end = dt.date(START_DATE.year + self.cfg.years, START_DATE.month, START_DATE.day)
        while self.date < end:
            self.step()
        out = {k: (np.array(v) if k != "date" else v) for k, v in self.log.items()}
        out["normal_q"] = self.normal_q
        return out
