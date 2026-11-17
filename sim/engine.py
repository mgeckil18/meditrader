"""D1 engine: one port, one good, urban demand + shopkeepers + storers (presets V0-V3, F, G, H).

(Original notes in Turkish below.)

D1 motoru: tek liman, tek mal, kitle + dükkâncılar (spec §3, §6).

Günlük sıra: hasat → kırsal arz → kentsel talep → dükkâncılar arası takas →
fiyat güncellemesi → bozulma ve giderler → kayıt → muhasebe kontrolü.
"""
import datetime as dt
from dataclasses import dataclass, field

import numpy as np

from .ledger import Ledger
from .model import RuralSupply, Shopkeeper, Storer, UrbanDemand
from .rng import RngStreams

START_DATE = dt.date(1560, 3, 1)


@dataclass
class D1Config:
    seed: int = 0
    years: int = 10
    ref_price: float = 100.0            # soldo / birim (yer tutucu ölçek)
    population: int = 100_000
    need_per_capita_year: float = 2.0
    elasticity: float = -0.4
    supply_surplus: float = 1.04        # bozulmayı karşılayacak kadar fazla hasat
    harvest_month: int = 7
    yield_sigma: float = 0.15           # yıllık verim şoku (log ölçek)
    yield_overrides: dict = field(default_factory=dict)   # {yıl_indeksi: çarpan}
    spoilage_per_day: float = 0.0005    # dükkân stoğu: ≈ %1.5 / ay
    farm_spoilage_per_day: float = 0.0005
    n_shopkeepers: int = 3
    target_days: float = 30.0           # dükkâncıların toplam hedef stoku (gün olarak talep)
    margin: float = 0.10
    kappa: float = 0.02
    max_daily_move: float = 0.03
    backlog_carry: float = 0.5
    interdealer: bool = True
    price_rule: str = "linear"
    room_mult: float = 1.5
    anchor: float = 0.0
    farmer_adaptive: bool = False
    ref_budget_share: float | None = None
    max_budget_share: float = 0.6
    withdraw_rate: float = 0.0
    farm_supply_elasticity: float = 1.0
    # Hasat haberine beklenti tepkisi (D1e, SS-5): dükkâncılar hasat büyüklüğünü
    # öğrenince fiyatı talep esnekliğinin ima ettiği yöne bu ağırlıkla sıçratır.
    harvest_news_weight: float = 0.0
    good: str = "GRN"                   # D4: ortak defterde mallar ayrı izlenir
    continuous_supply: bool = False     # D4: hasadı olmayan, sürekli üretilen mal (ör. kumaş)
    continuous_pace_fix: bool = True    # D4b: sürekli üretimde satış hızı sabit ufka göre (artifact düzeltmesi)
    rent_turnover_share: float | None = None   # D5: kira = normal günlük ciro × bu pay (None: sabit 50)
    thin_guard: float = 0.0                    # D5: ince pazar koruması (bkz. Shopkeeper.thin_guard)
    external_wholesale: bool = False           # D5a: toptan işlemler dışarıdaki kapan'da
    # D1f: köylünün kendi tüketimi ve stokçular
    self_share: float = 0.0             # normal hasattan köylünün kendine ayırdığı pay
    self_compress_min: float = 0.8
    n_storers: int = 0
    storer_capital_days: float = 60.0   # stokçu sermayesi: kaç günlük kent ihtiyacının değeri
    storer_capacity_days: float = 120.0
    storer_margin: float = 0.08
    storer_fair_memory: float = 60.0
    storer_normal_memory: float = 730.0
    storer_carry: float = 0.0
    storer_normal_mode: str = "ema"
    # Yerine koyma maliyeti (D1f): stoğu azalan dükkâncı, toptan pazarda kendi
    # teklifinden yüksek işlem görürse fiyatını günde bu oranla ona yaklaştırır.
    replacement_cost_rate: float = 0.0
    excess_supply_rate: float = 0.0     # D1g: RC'nin aşağı yönlü simetriği
    prop_gain: float = 0.0              # D1g: PI kontrolün oransal kazancı
    farmer_front_load: float = 0.0      # D1g: hasat sonrası nakit ihtiyacı


# v0: ilk yazılan kurallar (hiperenflasyon üretti; bkz. docs/experiments/D1.md)
V0 = dict()
# v1: D1 teşhisinden sonraki düzeltmeler
V1 = dict(price_rule="log", room_mult=2.0, farmer_adaptive=True,
          farm_spoilage_per_day=0.0002, supply_surplus=1.05)
# v2: kent bütçesi + dükkâncı kâr çekimi + arz düzeltmesi; κ ayrıca taranır
V2 = dict(price_rule="log", room_mult=2.0, farm_spoilage_per_day=0.0002,
          supply_surplus=1.05, ref_budget_share=0.3, max_budget_share=0.6,
          withdraw_rate=0.01)
# v3: v2 + fiyat sinyali "stok / müşteri talebi" (kaç günlük satışa yeter)
V3 = dict(V2, price_rule="cover")
# D1f varyantları
SELF = dict(self_share=0.4)
STORER = dict(n_storers=2, storer_fair_memory=0.0)
RC = dict(replacement_cost_rate=0.1)
# D1f'nin en iyi varyantı (F) ve D1g simetrik sürümü
F = dict(V3, self_share=0.4, n_storers=2, storer_fair_memory=0.0, replacement_cost_rate=0.1,
         storer_normal_memory=7300, storer_carry=0.1)
G = dict(F, excess_supply_rate=0.1)
# D1g sonucu: tek limanlı modelin önerilen hali (κ=0.01 ile)
H = dict(F, farmer_front_load=0.3, prop_gain=0.1, storer_margin=0.04, storer_normal_mode="median")


class D1Sim:
    def __init__(self, cfg: D1Config, ledger: Ledger | None = None, rng_salt: int = 0):
        """`ledger` verilirse (çok limanlı dünya, D2) muhasebe dünya düzeyinde tutulur:
        bu liman kendi defterini başlatmaz ve kontrol etmez."""
        self.cfg = cfg
        self.rng = RngStreams(cfg.seed * 1000 + rng_salt if rng_salt else cfg.seed)
        self._own_ledger = ledger is None
        self.ledger = Ledger() if ledger is None else ledger
        self.day = 0
        self.date = START_DATE
        self.good = cfg.good

        self.urban = UrbanDemand(cfg.population, cfg.need_per_capita_year, cfg.ref_price,
                                 cfg.elasticity, backlog_carry=cfg.backlog_carry,
                                 ref_budget_share=cfg.ref_budget_share,
                                 max_budget_share=cfg.max_budget_share)
        need = self.urban.daily_need
        # Pazara gelen normal miktar hep aynı kalsın diye, köylü kendine ayırdığı kadar fazla üretir.
        self.rural = RuralSupply(annual_capacity=need * 365 * cfg.supply_surplus / (1 - cfg.self_share),
                                 harvest_month=cfg.harvest_month, ref_price=cfg.ref_price,
                                 floor_price=0.4 * cfg.ref_price,
                                 supply_elasticity=cfg.farm_supply_elasticity,
                                 adaptive_ref=cfg.farmer_adaptive,
                                 self_share=cfg.self_share,
                                 self_compress_min=cfg.self_compress_min,
                                 front_load=cfg.farmer_front_load)
        if cfg.continuous_supply and cfg.continuous_pace_fix:
            self.rural.continuous_horizon = 30.0
        self.rural.set_own_consumption(1.0)
        # Başlangıç: hasata kalan süre kadar köylü stoğu.
        self.rural.stock = self.rural.annual_capacity * self._days_to_harvest() / 365.0

        init_rng = self.rng.get("init")
        tgt = need * cfg.target_days / cfg.n_shopkeepers
        self.shops = []
        for i in range(cfg.n_shopkeepers):
            stock = tgt * init_rng.uniform(0.7, 1.3)
            mid = cfg.ref_price * init_rng.uniform(0.95, 1.05)
            self.shops.append(Shopkeeper(
                id=f"sk{i}", cash=int(2 * tgt * cfg.ref_price), stock=stock, target=tgt,
                capacity=3 * tgt, margin=cfg.margin, mid=mid,
                avg_cost=mid * (1 - cfg.margin / 2), kappa=cfg.kappa,
                max_daily_move=cfg.max_daily_move, price_rule=cfg.price_rule,
                room_mult=cfg.room_mult, anchor=cfg.anchor, withdraw_rate=cfg.withdraw_rate,
                target_cover_days=cfg.target_days, request_rate=need / cfg.n_shopkeepers,
                prop_gain=cfg.prop_gain))
            sk = self.shops[-1]
            sk.thin_guard, sk.normal_request = cfg.thin_guard, need / cfg.n_shopkeepers
            if cfg.rent_turnover_share is not None:
                sk.rent = max(1, int(cfg.rent_turnover_share * need / cfg.n_shopkeepers * cfg.ref_price))

        self.storers = []
        for i in range(cfg.n_storers):
            capital = int(need * cfg.storer_capital_days * cfg.ref_price / cfg.n_storers)
            self.storers.append(Storer(
                id=f"st{i}", cash=capital, stock=0.0,
                capacity=need * cfg.storer_capacity_days / cfg.n_storers,
                margin=cfg.storer_margin, normal=cfg.ref_price * (1 - cfg.margin / 2),
                fair=cfg.ref_price * (1 - cfg.margin / 2), fair_memory_days=cfg.storer_fair_memory,
                normal_memory_days=cfg.storer_normal_memory, carry_per_year=cfg.storer_carry,
                normal_mode=cfg.storer_normal_mode,
                withdraw_rate=cfg.withdraw_rate, working_capital=capital))

        if self._own_ledger:
            self.ledger.start(self._money_total(), self._goods_totals())
        self.log = {k: [] for k in ("date", "ask_mean", "ask_min", "ask_max", "bought",
                                    "need", "shortage", "shop_stock", "rural_stock",
                                    "shop_cash", "farm_volume", "vwap", "storer_stock",
                                    "storer_cash", "farm_price", "wholesale")}

    # --- yardımcılar -------------------------------------------------------
    def _money_total(self) -> int:
        return sum(s.cash for s in self.shops) + sum(s.cash for s in self.storers)

    def _goods_totals(self) -> dict:
        return {self.good: self.rural.stock + sum(s.stock for s in self.shops)
                + sum(s.stock for s in self.storers)}

    def _days_to_harvest(self) -> int:
        y = self.date.year
        h = dt.date(y, self.cfg.harvest_month, 1)
        if h <= self.date:
            h = dt.date(y + 1, self.cfg.harvest_month, 1)
        return (h - self.date).days

    def _sorted_shops(self, key, reverse=False, agents=None):
        # Eşit fiyatlarda sıra avantajını yok etmek için önce seed'li karıştır.
        agents = self.shops if agents is None else agents
        order = self.rng.get("market").permutation(len(agents))
        shuffled = [agents[i] for i in order]
        return sorted(shuffled, key=key, reverse=reverse)

    # --- alt adımlar --------------------------------------------------------
    def _harvest(self):
        if self.cfg.continuous_supply:
            qty = self.rural.annual_capacity / 365.0
            self.rural.stock += qty
            self.ledger.goods_source(self.good, "production", qty)
            return
        if self.date.month == self.cfg.harvest_month and self.date.day == 1:
            year_idx = self.date.year - START_DATE.year
            if year_idx in self.cfg.yield_overrides:
                shock = self.cfg.yield_overrides[year_idx]
            else:
                shock = float(np.exp(self.rng.get("harvest").normal(0, self.cfg.yield_sigma)))
            qty = self.rural.annual_capacity * shock
            self.rural.stock += qty
            self.ledger.goods_source(self.good, "harvest", qty)
            self.rural.set_own_consumption(shock)
            # Pazara gelecek miktarın normale oranı: köylü önce kendini doyurur.
            r = self.rural
            marketable = r.annual_capacity * shock - r.own_daily * 365
            normal = r.annual_capacity * (1 - r.self_share)
            if normal > 0:                                        # D5b2: limanda açık hasat haberi
                self.harvest_ratio = max(0.05, marketable / normal)
                self.harvest_day = self.day
            for st in (self.storers if normal > 0 else []):
                st.on_harvest_news(max(0.05, marketable / normal), self.cfg.elasticity)
            w = self.cfg.harvest_news_weight
            if w > 0:
                # Arz %x eksikse dengenin gerektirdiği fiyat ≈ shock^(1/esneklik) (King-Davenant mantığı)
                implied = shock ** (1.0 / self.cfg.elasticity)
                for s in self.shops:
                    s.mid *= implied ** w

    def _rural_sells(self) -> tuple[float, int]:
        dth = self._days_to_harvest()
        sold, revenue = 0.0, 0
        buyers = self.shops + self.storers
        for s in self._sorted_shops(lambda s: s.bid(), reverse=True, agents=buyers):
            price = s.bid()
            # offered_at bu fiyattaki toplam arz; daha yüksek teklif verenlere satılanı düş.
            qty = min(self.rural.offered_at(price, dth) - sold, s.buy_room(price), self.rural.stock)
            if qty <= 0:
                continue
            cost = int(round(qty * price))
            if cost > s.cash:
                continue
            s.cash -= cost
            s.receive(qty, cost)
            self.rural.stock -= qty
            sold += qty
            revenue += cost
            self.ledger.money_sink("rural_farmers", cost)
        self._excess_supply(sold, dth)
        return sold, revenue

    def _excess_supply(self, sold: float, dth: int):
        """Fazla arz sinyali (D1g): yerine koyma maliyetinin aşağı yönlü simetriği.

        Köylü en düşük teklifte bile bugün sattığından fazlasını satmak istediyse
        pazarda mal bolluğu var demektir. Stoğu dolu dükkâncılar, köylünün bu
        miktara razı olacağı fiyata doğru, RC ile aynı hızla teklifini indirir.
        """
        rate = self.cfg.excess_supply_rate
        if rate <= 0:
            return
        lowest_bid = min(s.bid() for s in self.shops)
        if self.rural.offered_at(lowest_bid, dth) <= sold * 1.05:
            return
        clearing = self.rural.price_for(sold, dth)
        if clearing is None:
            return
        for s in self.shops:
            if s.signal_ratio() > 1.0 and s.bid() > clearing:
                s.mid += rate * (s.mid_for_bid(clearing) - s.mid)

    def _storers_sell(self):
        """Stokçular, adil fiyatın üstünde teklif veren dükkâncılara satar."""
        for st in self.storers:
            for s in self._sorted_shops(lambda s: s.bid(), reverse=True):
                price = s.bid()
                if st.stock <= 0 or price < st.sell_floor():
                    break
                qty = min(st.stock, s.buy_room(price))
                if qty <= 0:
                    continue
                cost = int(round(qty * price))
                s.cash -= cost
                s.receive(qty, cost)
                st.cash += cost
                st.stock -= qty

    def _replacement_cost(self, farm_volume: float, farm_revenue: int):
        """Dükkâncının malı yeniden alabileceği en düşük toptan fiyat."""
        rate = self.cfg.replacement_cost_rate
        if rate <= 0:
            return
        sources = [st.sell_floor() for st in self.storers if st.stock > 0]
        if farm_volume > 0:
            sources.append(farm_revenue / farm_volume)
        if not sources:
            return
        rc = min(sources)
        for s in self.shops:
            if s.signal_ratio() < 1.0 and s.bid() < rc:
                s.mid += rate * (s.mid_for_bid(rc) - s.mid)

    def _urban_buys(self) -> tuple[float, float, float]:
        u = self.urban
        base = u.daily_need + u.backlog
        bought, paid = 0.0, 0
        for s in self._sorted_shops(lambda s: s.ask()):
            price = s.ask()
            request = max(0.0, u.wanted_at(price, base) - bought)
            s.requests_today += request    # karşılanamasa bile talep kaydedilir
            qty = min(request, s.stock)
            if qty <= 0:
                continue
            pay = int(round(qty * price))
            s.cash += pay
            s.stock -= qty
            bought += qty
            paid += pay
            self.ledger.money_source("urban_consumers", pay)
            self.ledger.goods_sink(self.good, "consumption", qty)
        unmet = max(0.0, base - bought)
        u.backlog = min(u.backlog_cap_days * u.daily_need, unmet * u.backlog_carry)
        shortage = max(0.0, u.daily_need - bought) / u.daily_need
        vwap = paid / bought if bought > 0 else float("nan")   # gerçekleşen işlem fiyatı
        return bought, shortage, vwap

    def _interdealer(self):
        """Dükkâncılar arası çağrılı açık artırma (spec §6.4)."""
        sellers = [s for s in self.shops if s.signal_ratio() > 1.3]
        buyers = [s for s in self.shops if s.signal_ratio() < 0.7]
        sellers.sort(key=lambda s: s.quote())
        buyers.sort(key=lambda s: s.quote(), reverse=True)
        while sellers and buyers:
            se, bu = sellers[0], buyers[0]
            if bu.quote() < se.quote():
                break
            price = (bu.quote() + se.quote()) / 2
            qty = min(se.stock - se.desired_stock(), bu.desired_stock() - bu.stock,
                      bu.cash / price)
            if qty <= 0:
                break
            cost = int(round(qty * price))
            bu.cash -= cost
            se.cash += cost
            se.stock -= qty
            bu.receive(qty, cost)
            if se.signal_ratio() <= 1.3:
                sellers.pop(0)
            if bu.signal_ratio() >= 0.7:
                buyers.pop(0)

    def _upkeep(self):
        for s in self.shops:
            loss = s.stock * self.cfg.spoilage_per_day
            s.stock -= loss
            self.ledger.goods_sink(self.good, "spoilage", loss)
            rent = min(s.rent, s.cash)
            s.cash -= rent
            self.ledger.money_sink("rent", rent)
            w = s.withdrawal()
            s.cash -= w
            s.withdrawn += w
            self.ledger.money_sink("owner_consumption", w)
        loss = self.rural.stock * self.cfg.farm_spoilage_per_day
        self.rural.stock -= loss
        self.ledger.goods_sink(self.good, "spoilage", loss)
        eat = min(self.rural.stock, self.rural.own_daily)
        self.rural.stock -= eat
        self.ledger.goods_sink(self.good, "farm_consumption", eat)
        for st in self.storers:
            loss = st.stock * self.cfg.farm_spoilage_per_day   # ambarcılar iyi saklar
            st.stock -= loss
            self.ledger.goods_sink(self.good, "spoilage", loss)
            w = st.withdrawal()
            st.cash -= w
            self.ledger.money_sink("owner_consumption", w)

    # --- ana döngü ----------------------------------------------------------
    def step(self):
        pre = self.step_pre()
        bought, shortage, vwap = self._urban_buys()
        self.step_post(pre, bought, shortage, vwap)

    def step_pre(self) -> dict:
        """Günün kentsel alımdan önceki kısmı (D4: ortak talep modeli araya girer)."""
        self._harvest()
        if self.cfg.external_wholesale:
            # D5a: köylü ve stokçu satışları dünya düzeyindeki toptan pazarda (kapan) yapılır
            return dict(farm_volume=0.0, farm_revenue=0, asks=[s.ask() for s in self.shops])
        farm_volume, farm_revenue = self._rural_sells()
        self._storers_sell()
        self._replacement_cost(farm_volume, farm_revenue)
        asks = [s.ask() for s in self.shops]   # kitlenin gördüğü fiyatlar
        return dict(farm_volume=farm_volume, farm_revenue=farm_revenue, asks=asks)

    def step_post(self, pre: dict, bought: float, shortage: float, vwap: float):
        """Günün kentsel alımdan sonraki kısmı."""
        farm_volume, farm_revenue, asks = pre["farm_volume"], pre["farm_revenue"], pre["asks"]
        wholesale = float(np.mean([s.bid() for s in self.shops]))
        season_pos = 1 - self._days_to_harvest() / 365.0
        self.rural.observe(wholesale)
        for st in self.storers:
            st.observe(wholesale)
            st.season_pos = season_pos
        if self.cfg.interdealer:
            self._interdealer()
        for s in self.shops:
            s.end_of_day_requests()
            s.update_mid()
        self._upkeep()

        L = self.log
        L["date"].append(self.date)
        L["ask_mean"].append(float(np.mean(asks)))
        L["ask_min"].append(min(asks))
        L["ask_max"].append(max(asks))
        L["bought"].append(bought)
        L["need"].append(self.urban.daily_need)
        L["shortage"].append(shortage)
        L["shop_stock"].append(sum(s.stock for s in self.shops))
        L["rural_stock"].append(self.rural.stock)
        L["shop_cash"].append(self._money_total())
        L["farm_volume"].append(farm_volume)
        L["vwap"].append(vwap)
        L["wholesale"].append(wholesale)
        L["storer_stock"].append(sum(s.stock for s in self.storers))
        L["storer_cash"].append(sum(s.cash for s in self.storers))
        L["farm_price"].append(farm_revenue / farm_volume if farm_volume > 0 else float("nan"))

        if self._own_ledger:
            self.ledger.check(self._money_total(), self._goods_totals())
        self.day += 1
        self.date += dt.timedelta(days=1)

    def run(self):
        end = dt.date(START_DATE.year + self.cfg.years, START_DATE.month, START_DATE.day)
        while self.date < end:
            self.step()
        return {k: np.array(v) if k != "date" else v for k, v in self.log.items()}
