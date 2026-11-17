"""D2-D3b: two ports and travelling merchants, information delay, entry and exit.

(Original notes in Turkish below.)

D2: iki liman (İskenderiye üretici → İstanbul tüketici) ve gezgin tüccarlar.

Her limanda D1 serisinin son modeli (ön ayar H) çalışır. Tüccarlar İskenderiye'de
dükkâncılardan alır, gemiyle İstanbul'a taşır, oradaki dükkâncılara satar ve boş döner.
Bilgi bu deneyde ANLIK ve küreseldir (bilgi gecikmesi D3'ün konusu).

Yarışan yuva: tüccar karar kuralı (docs/experiments/README.md):
  greedy   açgözlü arbitraj: İstanbul'un bugünkü fiyatı varışta da geçerli sanılır
  dp       Doran-Parberry: varış fiyatı için kendi işlemlerinden öğrenilen inanç aralığı
  utility  fayda tabanlı: yoldaki rakip kargoyu ve kendi fiyat etkisini hesaba katar,
           risk iştahı ve sermaye getirisi beklentisi kişiliğe göre değişir
"""
import datetime as dt
from dataclasses import dataclass, field

import numpy as np

from .engine import H, START_DATE, D1Config, D1Sim
from .ledger import Ledger
from .rng import RngStreams

GOOD = "GRN"


@dataclass
class D2Config:
    seed: int = 0
    years: int = 10
    kappa: float = 0.01
    # Limanlar (ölçek yer tutucu; ⚠️ tarihsel değil)
    ale_population: int = 50_000
    ale_supply: float = 2.1          # İskenderiye kendi ihtiyacının 2.1 katını pazara getirir
    ale_harvest_month: int = 5       # Mısır hasadı ilkbahar ⚠️
    ist_population: int = 100_000
    ist_supply: float = 0.5          # İstanbul ihtiyacının yarısını kendi üretir
    ist_harvest_month: int = 7
    yield_sigma: float = 0.15
    ale_yield_overrides: dict = field(default_factory=dict)
    # Taşıma (yer tutucu; ⚠️)
    freight_per_unit: float = 8.0    # navlun, soldo/birim (referans fiyatın %8'i)
    customs: float = 0.03            # İstanbul'da satış değerinin %3'ü
    voyage_days: float = 14.0        # yaz; kış (Kas-Şub) 1.5 katı
    voyage_sigma: float = 0.25
    loss_summer: float = 0.015       # sefer başına batma/korsan olasılığı
    loss_winter: float = 0.05
    # Tüccarlar
    n_merchants: int = 15
    rule: str = "utility"            # greedy | dp | utility | none
    capacity: float = 2000.0
    capital_mult: float = 1.2        # sermaye = kapasite × referans fiyat × bu çarpan
    living_cost: int = 30
    add_player_bot: bool = True      # NPC'lerle aynı kısıtlarda, açgözlü kuralla oynayan "oyuncu"
    player_rule: str = "greedy"
    # D3: bilgi ve beklenti
    info_mode: str = "instant"       # instant | ship | rumor
    expect_mode: str = "last"        # last | dist | revert
    p_hear: float = 0.3              # söylenti: limana gelen haberi bir tüccarın bir günde duyma olasılığı
    vol_annual: float = 0.4          # fiyat oynaklığı varsayımı (bilgi eskime hızı)
    sigma_source: float = 0.03       # gemi haberinin kendi belirsizliği
    revert_days: float = 60.0        # eski bilginin olağan fiyata dönüş zaman sabiti
    aware_lambda: float = 0.0        # rakip kargo farkındalığı: beklenen fiyat ∝ (gelecek kargo / normal ithalat)^(−λ)
    add_informed_bot: bool = False   # anlık bilgi alan ikinci oyuncu botu: bilginin değeri
    # D3b: senete bağlı serbest giriş-çıkış
    free_entry: bool = False
    bond_rate: float = 0.04          # devlet senedi yıllık getirisi
    risk_premium: float = 0.04       # yeni tüccarın senedin üstünde istediği pay
    entry_alpha: float = 1.0         # aylık giriş yoğunluğu: N × alpha × (fazla getiri)
    exit_prob: float = 0.25          # senedin altında kalan tüccarın her ay çıkma olasılığı
    max_merchants: int = 120
    entry_mode: str = "proportional"  # proportional | pool
    entry_pool: float = 1.0           # pool: ayda en fazla beklenen yeni tüccar
    dividends: bool = False          # ihtiyaç fazlası nakdi sahibine çek


def _is_winter(d: dt.date) -> bool:
    return d.month in (11, 12, 1, 2)


@dataclass
class Merchant:
    id: str
    rule: str
    cash: int
    capacity: float
    is_player: bool = False
    informed: bool = False           # anlık bilgi (D3 bilgili bot)
    obs_price: float = 100.0         # İstanbul fiyatı hakkındaki en yeni bilgi
    obs_day: int = 0
    obs_history: list = field(default_factory=list)
    heard: set = field(default_factory=set)
    decision_ages: list = field(default_factory=list)
    state: str = "buying"            # buying | sailing | selling
    location: str = "ALE"
    dest: str = ""
    arrive_day: int = -1
    cargo: float = 0.0
    cost_basis: float = 0.0          # kargonun toplam maliyeti (alış + navlun)
    wait: int = 0
    # kişilik (utility)
    risk_aversion: float = 1.0
    hurdle_year: float = 0.2
    # Doran-Parberry inanç aralığı (İstanbul satış fiyatı için)
    belief_lo: float = 90.0
    belief_hi: float = 120.0
    # muhasebe
    start_capital: int = 0
    trips: int = 0
    losses: int = 0
    born_day: int = 0
    divs: int = 0                    # toplam çekilen kâr payı
    marks: list = field(default_factory=list)   # aylık (gün, net servet + kâr payı)

    def net_worth(self, ale_price: float) -> float:
        if self.cargo <= 0:
            return float(self.cash)
        return self.cash + self.cargo * (self.cost_basis / self.cargo if self.state != "buying" else ale_price)


class D2World:
    def __init__(self, cfg: D2Config):
        self.cfg = cfg
        self.rng = RngStreams(cfg.seed)
        self.ledger = Ledger()
        self.day = 0
        self.date = START_DATE
        common = dict(H, kappa=cfg.kappa, seed=cfg.seed, years=cfg.years, yield_sigma=cfg.yield_sigma)
        common.pop("supply_surplus", None)   # her limanın kendi arzı var
        self.ale = D1Sim(D1Config(**common, population=cfg.ale_population,
                                  supply_surplus=cfg.ale_supply,
                                  harvest_month=cfg.ale_harvest_month,
                                  yield_overrides=dict(cfg.ale_yield_overrides)),
                         ledger=self.ledger, rng_salt=1)
        self.ist = D1Sim(D1Config(**common, population=cfg.ist_population,
                                  supply_surplus=cfg.ist_supply,
                                  harvest_month=cfg.ist_harvest_month),
                         ledger=self.ledger, rng_salt=2)
        self.ports = {"ALE": self.ale, "IST": self.ist}

        mrng = self.rng.get("merchants_init")
        capital = int(cfg.capacity * 100 * cfg.capital_mult)
        self.merchants: list[Merchant] = []
        self._next_id = 0
        n = cfg.n_merchants if cfg.rule != "none" else 0
        for _ in range(n):
            self.merchants.append(self._new_merchant(cfg.rule, capital, mrng))
        if cfg.add_player_bot and cfg.rule != "none":
            self.merchants.append(self._new_merchant(cfg.player_rule, capital, mrng, is_player=True))
        if cfg.add_informed_bot and cfg.rule != "none":
            b = self._new_merchant(cfg.player_rule, capital, mrng, is_player=True)
            b.informed = True
            self.merchants.append(b)
        self.news_board: list[tuple[int, float, int]] = []   # İskenderiye'deki haberler: (id, fiyat, gözlem günü)
        self._news_id = 0

        self.import_rate = 0.0       # İstanbul'a günlük ithalatın 30 günlük ortalaması (kamuya açık)
        # Uzun dönem ithalat ortalaması: tüccarların "İstanbul ne kadar ithalat emer" yapısal bilgisi
        self.import_rate_long = (cfg.ist_population * 2.0 / 365.0) * (1 - cfg.ist_supply)
        self.trailing_median = 0.0
        self.ledger.start(self._money_total(), self._goods_totals())
        self.log = {k: [] for k in ("date", "ale_ask", "ale_bid", "ist_ask", "ist_bid", "ist_shortage",
                                    "ale_shortage", "arrivals", "at_sea_cargo", "margin_now",
                                    "spread_ratio", "player_nw", "npc_nw_median", "informed_nw",
                                    "n_npc", "trailing_median")}

    # --- kurulum ve muhasebe ------------------------------------------------
    def _new_merchant(self, rule, capital, rng, is_player=False) -> Merchant:
        self._next_id += 1
        m = Merchant(id=f"m{self._next_id}", rule=rule, cash=capital, capacity=self.cfg.capacity,
                     is_player=is_player, start_capital=capital,
                     risk_aversion=float(rng.uniform(0.5, 1.5)),
                     hurdle_year=float(rng.uniform(0.1, 0.4)))
        p0 = 100.0 * float(rng.uniform(0.9, 1.3))
        m.belief_lo, m.belief_hi = 0.85 * p0, 1.15 * p0
        m.obs_price, m.obs_day = 100.0, self.day if hasattr(self, "day") else 0
        m.obs_history = [100.0]
        m.born_day = self.day if hasattr(self, "day") else 0
        return m

    def _money_total(self) -> int:
        return self.ale._money_total() + self.ist._money_total() + sum(m.cash for m in self.merchants)

    def _goods_totals(self) -> dict:
        return {GOOD: self.ale._goods_totals()[GOOD] + self.ist._goods_totals()[GOOD]
                + sum(m.cargo for m in self.merchants)}

    # --- piyasa yardımcıları ------------------------------------------------
    def _p_loss(self) -> float:
        return self.cfg.loss_winter if _is_winter(self.date) else self.cfg.loss_summer

    def _voyage_mean(self) -> float:
        return self.cfg.voyage_days * (1.5 if _is_winter(self.date) else 1.0)

    def _ist_best_bid(self) -> float:
        return max(s.bid() for s in self.ist.shops)

    def _ale_best_ask(self) -> float:
        return min(s.ask() for s in self.ale.shops)

    def _net_sale_value(self, price: float) -> float:
        """İstanbul'da birim satış fiyatından, gümrük ve beklenen kayıp sonrası kalan."""
        return price * (1 - self.cfg.customs) * (1 - self._p_loss()) - self.cfg.freight_per_unit

    # --- karar kuralları ----------------------------------------------------
    def _expected_ist(self, m: Merchant) -> float:
        """Tüccarın varışta İstanbul'da bekleyeceği fiyat (D3: bilgi ve beklenti yuvaları)."""
        cfg = self.cfg
        if cfg.info_mode == "instant" or m.informed:
            m.obs_price, m.obs_day = self._ist_best_bid(), self.day
        age = self.day - m.obs_day
        m.decision_ages.append(age)
        if cfg.expect_mode == "last":
            return m.obs_price
        h = age + self._voyage_mean()
        v = cfg.vol_annual ** 2 / 365.0
        sigma = float(np.sqrt(cfg.sigma_source ** 2 + v * h))
        log_med = np.log(m.obs_price)
        if cfg.expect_mode == "revert":
            normal = float(np.median(m.obs_history[-20:]))
            log_med = np.log(normal) + (log_med - np.log(normal)) * np.exp(-h / cfg.revert_days)
        z = -(m.risk_aversion - 0.5)          # temkinli tüccar dağılımın kötü ucuna bakar (0 ile -1σ)
        return float(np.exp(log_med + z * sigma))

    def _max_bid(self, m: Merchant) -> float:
        """Tüccarın İskenderiye'de ödemeye razı olduğu en yüksek birim fiyat."""
        cfg = self.cfg
        if m.rule == "aware":
            e = self._expected_ist(m)
            # Yoldaki rakip kargo limanda görülür (yerel bilgi, gecikmesiz). Varış penceresinde
            # gelecek toplam kargo, İstanbul'un aynı sürede normalde emdiği ithalatla kıyaslanır.
            # Oran 1'in altındaysa beklenti yükselir, üstündeyse düşer (simetrik, İ9).
            incoming = sum(x.cargo for x in self.merchants if x.state == "sailing" and x.dest == "IST")
            incoming += m.capacity - m.cargo
            window = self._voyage_mean() + 30.0
            ratio = incoming / (max(self.import_rate_long, 1.0) * window)
            e *= min(1.3, max(0.6, ratio ** (-cfg.aware_lambda)))
            return self._net_sale_value(e) / 1.05
        if m.rule == "greedy":
            return self._net_sale_value(self._ist_best_bid()) / 1.05
        if m.rule == "dp":
            e = float(self.rng.get(f"dp_{m.id}").uniform(m.belief_lo, m.belief_hi))
            return self._net_sale_value(e) / 1.05
        if m.rule == "utility":
            e0 = self._ist_best_bid()
            incoming = sum(x.cargo for x in self.merchants if x.state == "sailing" and x.dest == "IST")
            incoming += m.capacity - m.cargo
            absorb = max(self.import_rate, 1.0) * 30.0
            e = e0 * max(0.5, 1 - 0.3 * incoming / absorb)
            trip_days = 2 * self._voyage_mean() + 5
            hurdle = m.hurdle_year * trip_days / 365.0
            if m.cargo > 0:
                hurdle *= 0.7                       # atalet: yüklemeye başladıysa devam
            net = (e * (1 - cfg.customs) * (1 - self._p_loss() * m.risk_aversion)
                   - cfg.freight_per_unit)
            return net / (1 + hurdle)
        raise ValueError(m.rule)

    def _dp_update(self, m: Merchant, realized: float):
        """Doran-Parberry inanç güncellemesi: kendi satışının sonucundan öğren."""
        width = m.belief_hi - m.belief_lo
        if m.belief_lo <= realized <= m.belief_hi:
            m.belief_lo += 0.05 * width
            m.belief_hi -= 0.05 * width          # isabet: daralt
        else:
            mid = (m.belief_lo + m.belief_hi) / 2
            shift = realized - mid
            m.belief_lo += shift
            m.belief_hi += shift
            m.belief_lo -= 0.05 * width          # ıska: kaydır ve genişlet
            m.belief_hi += 0.05 * width
        if m.belief_hi - m.belief_lo < 2.0:
            mid = (m.belief_lo + m.belief_hi) / 2
            m.belief_lo, m.belief_hi = mid - 1.0, mid + 1.0

    # --- günlük adımlar -----------------------------------------------------
    def _arrivals(self) -> float:
        arrived = 0.0
        for m in self.merchants:
            if m.state == "sailing" and m.arrive_day == self.day:
                m.location = m.dest
                m.wait = 0
                if m.dest == "IST":
                    m.state = "selling"
                    arrived += m.cargo
                else:
                    m.state = "buying"
                    if m.obs_day > 0 or m.trips > 0:
                        self._news_id += 1
                        self.news_board.append((self._news_id, m.obs_price, m.obs_day))
                        m.heard.add(self._news_id)
        return arrived

    def _observe_ist(self, m: Merchant):
        m.obs_price, m.obs_day = self._ist_best_bid(), self.day
        m.obs_history.append(m.obs_price)
        m.obs_history = m.obs_history[-40:]

    def _sell_at_ist(self):
        for m in self.merchants:
            if m.state != "selling":
                continue
            self._observe_ist(m)
            if m.cargo > 0:
                unit_cost = m.cost_basis / m.cargo
                # Sabır: beklendikçe kabul edilen en düşük fiyat iner (en fazla maliyetin %50'si)
                reservation = unit_cost * max(0.5, 1.0 - 0.02 * m.wait)
                sold_value, sold_qty = 0, 0.0
                for s in self.ist._sorted_shops(lambda s: s.bid(), reverse=True):
                    price = s.bid()
                    if price < reservation or m.cargo <= 0:
                        break
                    qty = min(m.cargo, s.buy_room(price))
                    if qty <= 0:
                        continue
                    pay = int(round(qty * price))
                    duty = int(round(pay * self.cfg.customs))
                    s.cash -= pay
                    s.receive(qty, pay)
                    m.cash += pay - duty
                    self.ledger.money_sink("customs", duty)
                    m.cost_basis -= unit_cost * qty
                    m.cargo -= qty
                    sold_value += pay
                    sold_qty += qty
                if sold_qty > 0:
                    self.import_today += sold_qty
                    if m.rule == "dp":
                        self._dp_update(m, sold_value / sold_qty)
                m.wait += 1
            if m.cargo <= 1e-9:
                m.cargo, m.cost_basis = 0.0, 0.0
                self._depart(m, "IST", "ALE")

    def _buy_at_ale(self):
        order = self.rng.get("merchant_order").permutation(len(self.merchants))
        for i in order:
            m = self.merchants[i]
            if m.state != "buying":
                continue
            max_bid = self._max_bid(m)
            for s in self.ale._sorted_shops(lambda s: s.ask()):
                ask = s.ask()
                room = m.capacity - m.cargo
                if ask > max_bid or room <= 0:
                    break
                # Dükkâncı istenen stoğunun yarısını yerel müşterisine ayırır.
                avail = max(0.0, s.stock - 0.5 * s.desired_stock())
                want = min(room, m.cash / ask)
                s.requests_today += want             # ihracat talebi de dükkâncının talep sinyaline girer
                qty = min(want, avail)
                if qty <= 0:
                    continue
                pay = int(round(qty * ask))
                s.cash += pay
                s.stock -= qty
                m.cash -= pay
                m.cargo += qty
                m.cost_basis += pay
            m.wait += 1
            full = m.cargo >= 0.9 * m.capacity
            broke = m.cash < 100 * 50
            if m.cargo > 0 and (full or m.wait >= 7 or broke):
                self._depart(m, "ALE", "IST")

    def _hear_news(self):
        """İskenderiye'deki tüccarlar limana gelen haberleri öğrenir (gemi / söylenti)."""
        if self.cfg.info_mode == "instant":
            return
        r = self.rng.get("rumor")
        for m in self.merchants:
            if m.state != "buying":
                continue
            for nid, price, oday in self.news_board:
                if nid in m.heard:
                    continue
                if self.cfg.info_mode == "rumor" and r.random() >= self.cfg.p_hear:
                    continue
                m.heard.add(nid)
                if oday > m.obs_day:
                    m.obs_price, m.obs_day = price, oday
                    m.obs_history.append(price)
                    m.obs_history = m.obs_history[-40:]
        # 60 günden eski haberler unutulur
        self.news_board = [n for n in self.news_board if self.day - n[2] < 60]

    def _depart(self, m: Merchant, origin: str, dest: str):
        r = self.rng.get("voyage")
        days = max(3, int(round(self._voyage_mean() * float(np.exp(r.normal(0, self.cfg.voyage_sigma))))))
        lost = bool(r.random() < self._p_loss())     # boş dönüşte de çekilir: dizi kaymasın
        if m.cargo > 0:
            freight = int(round(self.cfg.freight_per_unit * m.cargo))
            freight = min(freight, m.cash)
            m.cash -= freight
            m.cost_basis += freight
            self.ledger.money_sink("freight", freight)
            m.trips += 1
            if lost:
                self.ledger.goods_sink(GOOD, "shipwreck", m.cargo)
                m.cargo, m.cost_basis = 0.0, 0.0
                m.losses += 1
        m.state, m.location, m.dest = "sailing", "sea", dest
        m.arrive_day = self.day + days
        m.wait = 0

    def _monthly(self):
        """D3b: kâr payı, getiri ölçümü, senete bağlı çıkış ve giriş (ayın ilk günü)."""
        cfg = self.cfg
        ale_p = self._ale_best_ask()
        working = 1.2 * cfg.capacity * ale_p
        for m in self.merchants:
            if cfg.dividends and m.state == "buying" and m.cargo <= 0 and m.cash > working:
                d = int(m.cash - working)
                m.cash -= d
                m.divs += d
                self.ledger.money_sink("merchant_dividends", d)
            m.marks.append((self.day, m.net_worth(ale_p) + m.divs))
            m.marks = m.marks[-13:]
        if not cfg.free_entry:
            return

        def trailing(m):
            if len(m.marks) < 13 or self.day - m.born_day < 365:
                return None
            return m.marks[-1][1] / max(m.marks[0][1], 1.0) - 1

        npc = [m for m in self.merchants if not m.is_player]
        rets = [r for r in (trailing(m) for m in npc) if r is not None]
        if rets:
            self.trailing_median = float(np.median(rets))
        r = self.rng.get("entry_exit")
        # Çıkış: senedin altında kalan, limanda boşta bekleyen tüccar parasını senede koyar.
        keep = []
        for m in self.merchants:
            t = trailing(m) if not m.is_player else None
            idle = m.state == "buying" and m.cargo <= 0
            if t is not None and idle and t < cfg.bond_rate and r.random() < cfg.exit_prob:
                self.ledger.money_sink("to_bonds", m.cash)
                self.exits += 1
                continue
            keep.append(m)
        self.merchants = keep
        # Giriş: aktif tüccarların medyan getirisi senet + risk priminin üstündeyse.
        excess = self.trailing_median - (cfg.bond_rate + cfg.risk_premium)
        n_npc = sum(1 for m in self.merchants if not m.is_player)
        if excess > 0 and n_npc < cfg.max_merchants:
            if cfg.entry_mode == "proportional":
                # Mevcut tüccar sayısıyla orantılı (Doran-Parberry'nin meslek değiştirme mantığı)
                lam = cfg.entry_alpha * max(n_npc, 3) * excess
            else:
                # "pool": giriş dışarıdan sınırlı bir akış (çıraklık, sermaye, ortaklık);
                # fazla getiri arttıkça ayda en fazla entry_pool kişiye kadar
                lam = cfg.entry_pool * min(1.0, excess / 0.10)
            k = int(r.poisson(lam))
            capital = int(cfg.capacity * 100 * cfg.capital_mult)
            mrng = self.rng.get("merchants_entry")
            for _ in range(min(k, cfg.max_merchants - n_npc)):
                new = self._new_merchant(cfg.rule, capital, mrng)
                self.merchants.append(new)
                self.ledger.money_source("from_bonds", new.cash)
                self.entries += 1

    def _upkeep(self):
        mrng = self.rng.get("merchants_entry")
        capital = int(self.cfg.capacity * 100 * self.cfg.capital_mult)
        ale_p = self._ale_best_ask()
        for idx, m in enumerate(self.merchants):
            c = min(self.cfg.living_cost, m.cash)
            m.cash -= c
            self.ledger.money_sink("merchant_living", c)
            # İflas: elinde mal yok, limanda ve bir yüklük alacak parası kalmamış
            if (not m.is_player and m.state == "buying" and m.cargo <= 0
                    and m.cash < 0.2 * m.capacity * ale_p):
                self.ledger.money_sink("merchant_exit", m.cash)
                self.bankruptcies += 1
                if self.cfg.free_entry:
                    self.merchants[idx] = None     # serbest girişte yerine otomatik kimse gelmez
                    continue
                new = self._new_merchant(m.rule, capital, mrng)
                self.ledger.money_source("merchant_entry", new.cash)
                self.merchants[idx] = new
        self.merchants = [m for m in self.merchants if m is not None]

    def step(self):
        self.import_today = 0.0
        arrived = self._arrivals()
        self._sell_at_ist()
        self._hear_news()
        self._buy_at_ale()
        self.ale.step()
        self.ist.step()
        self._upkeep()
        if self.date.day == 1:
            self._monthly()
        self.import_rate += (self.import_today - self.import_rate) / 30.0
        self.import_rate_long += (self.import_today - self.import_rate_long) / 365.0

        L = self.log
        ale_ask, ist_bid = self._ale_best_ask(), self._ist_best_bid()
        cost_unit = self.cfg.freight_per_unit + ist_bid * (self.cfg.customs + self._p_loss())
        L["date"].append(self.date)
        L["ale_ask"].append(self.ale.log["ask_mean"][-1])
        L["ale_bid"].append(self.ale.log["wholesale"][-1])
        L["ist_ask"].append(self.ist.log["ask_mean"][-1])
        L["ist_bid"].append(self.ist.log["wholesale"][-1])
        L["ist_shortage"].append(self.ist.log["shortage"][-1])
        L["ale_shortage"].append(self.ale.log["shortage"][-1])
        L["arrivals"].append(arrived)
        L["at_sea_cargo"].append(sum(m.cargo for m in self.merchants if m.state == "sailing"))
        L["margin_now"].append(self._net_sale_value(ist_bid) / ale_ask - 1)
        L["spread_ratio"].append((ist_bid - ale_ask) / cost_unit)
        players = [m for m in self.merchants if m.is_player]
        plain = [m for m in players if not m.informed]
        L["player_nw"].append(plain[0].net_worth(ale_ask) if plain else np.nan)
        inf = [m for m in players if m.informed]
        L["informed_nw"].append(inf[0].net_worth(ale_ask) if inf else np.nan)
        L["n_npc"].append(sum(1 for m in self.merchants if not m.is_player))
        L["trailing_median"].append(self.trailing_median)
        npc = [m.net_worth(ale_ask) for m in self.merchants if not m.is_player]
        L["npc_nw_median"].append(float(np.median(npc)) if npc else np.nan)

        self.ledger.check(self._money_total(), self._goods_totals())
        self.day += 1
        self.date += dt.timedelta(days=1)

    def run(self):
        self.bankruptcies = 0
        self.entries = 0
        self.exits = 0
        end = dt.date(START_DATE.year + self.cfg.years, START_DATE.month, START_DATE.day)
        while self.date < end:
            self.step()
        out = {k: (np.array(v) if k != "date" else v) for k, v in self.log.items()}
        out["bankruptcies"] = self.bankruptcies
        out["entries"] = self.entries
        out["exits"] = self.exits
        out["merchants"] = self.merchants
        return out
