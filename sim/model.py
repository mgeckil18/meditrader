"""D1 agents: demand pools and shopkeepers.

(Original notes in Turkish below.)

D1 kapsamındaki varlıklar: kitle havuzları ve dükkâncılar (spec §2.4, §2.5, §6.1-6.3)."""
import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class UrbanDemand:
    """Kentsel talep havuzu: şehir nüfusunun tüketimi. Ajan değil, bir dağılım."""
    population: int
    need_per_capita_year: float
    ref_price: float
    elasticity: float            # negatif; tahıl ≈ -0.4
    backlog_carry: float = 0.5   # karşılanmayan ihtiyacın ertesi güne devreden payı
    backlog_cap_days: float = 30.0
    backlog: float = 0.0
    # Bütçe kısıtı (None = yok, v0/v1). Referans fiyatta tahıla giden gelir payı ve
    # kıtlıkta tahıla ayrılabilecek azami pay.
    ref_budget_share: float | None = None
    max_budget_share: float = 0.6

    @property
    def daily_need(self) -> float:
        return self.population * self.need_per_capita_year / 365.0

    @property
    def daily_income(self) -> float:
        return self.daily_need * self.ref_price / self.ref_budget_share

    def wanted_at(self, price: float, base: float) -> float:
        """Bu fiyat seviyesinde kitlenin toplam almak istediği miktar.

        Bütçe kısıtı varsa harcama gelirin azami payını aşamaz: yüksek fiyatlarda
        talep birim esnek (−1) hale gelir ve fiyatı sınırlar.
        """
        q = base * (price / self.ref_price) ** self.elasticity
        if self.ref_budget_share is not None:
            q = min(q, self.max_budget_share * self.daily_income / price)
        return q


@dataclass
class RuralSupply:
    """Kırsal arz havuzu: hasatı tutan ve yıl boyunca satan köylüler."""
    annual_capacity: float
    harvest_month: int
    ref_price: float
    floor_price: float           # bu fiyatın altında satmazlar
    supply_elasticity: float = 1.0
    stock: float = 0.0
    adaptive_ref: bool = False    # True: referansı sabit değil, kendi fiyat hafızaları
    ref_memory_days: float = 180.0
    expected_price: float = 0.0
    # Köylünün kendi tüketimi (D1f, framework A8). self_share: normal hasattan
    # köylünün kendine (yiyecek + tohumluk) ayırdığı pay. Kötü hasatta bu pay en
    # fazla self_compress_min oranına kadar kısılabilir (az yerler ama yerler).
    self_share: float = 0.0
    self_compress_min: float = 0.8
    own_daily: float = 0.0        # bu hasat yılı için günlük kendi tüketimi
    # Hasat sonrası nakit ihtiyacı (D1g): vergi, kira ve borç vadeleri hasada denk gelir.
    # Satış hızı sezon başında (1+front_load) katı, sezon sonunda (1−front_load) katı.
    front_load: float = 0.0

    def __post_init__(self):
        self.expected_price = self.ref_price

    def set_own_consumption(self, shock: float):
        own_year = self.annual_capacity * self.self_share * min(1.0, max(self.self_compress_min, shock))
        self.own_daily = own_year / 365.0

    def sellable(self, days_to_harvest: int) -> float:
        """Stoktan, hasata kadar kendi yiyeceklerini ayırdıktan sonra kalan."""
        return max(0.0, self.stock - self.own_daily * days_to_harvest)

    def offered_at(self, price: float, days_to_harvest: int) -> float:
        """Bu fiyatta bugün satmak istedikleri toplam miktar.

        Satılabilir stoğu kalan güne yayarlar; fiyat beklentilerinin üstündeyse
        hızlanır, altındaysa tutarlar.
        """
        avail = self.sellable(days_to_harvest)
        if price < self.floor_price or avail <= 0:
            return 0.0
        pace = self._pace(avail, days_to_harvest)
        ref = self.expected_price if self.adaptive_ref else self.ref_price
        factor = (price / ref) ** self.supply_elasticity
        return min(avail, pace * min(3.0, max(0.2, factor)))

    # Sürekli üretilen mallarda (D4b): satış hızı hasada kalan güne değil, sabit bir stok
    # eritme ufkuna göre. Aksi halde üretici "Ocak'ta hasat var" gibi davranıp yıllık bir
    # salınım yaratıyordu (artifact, D4b ablasyonu).
    continuous_horizon: float = 0.0

    def _pace(self, avail: float, days_to_harvest: int) -> float:
        if self.continuous_horizon > 0:
            return avail / self.continuous_horizon
        season_pos = 1 - days_to_harvest / 365.0
        return avail / max(1, days_to_harvest) * (1 + self.front_load * (1 - 2 * season_pos))

    def price_for(self, qty: float, days_to_harvest: int) -> float | None:
        """offered_at'in tersi: köylünün bugün tam olarak `qty` satmayı kabul edeceği fiyat.

        D1g fazla arz sinyali için: köylü sattığından fazlasını satmak isteseydi,
        bu miktarı hangi fiyata razı olurdu?
        """
        avail = self.sellable(days_to_harvest)
        if avail <= 0 or self.supply_elasticity <= 0:
            return None
        pace = self._pace(avail, days_to_harvest)
        factor = min(3.0, max(0.2, qty / pace))
        ref = self.expected_price if self.adaptive_ref else self.ref_price
        return max(self.floor_price, ref * factor ** (1.0 / self.supply_elasticity))

    def observe(self, price: float):
        """Uyarlamalı beklenti (01 §7): beklentiyi gözlenen fiyata doğru yavaşça kaydır."""
        if self.adaptive_ref:
            self.expected_price += (price - self.expected_price) / self.ref_memory_days


@dataclass
class Shopkeeper:
    """Dükkâncı: yerel, istikrarlı, sabit marjlı perakendeci (framework §4).

    Fiyatı stoka göre yavaşça kayan bir orta fiyat (mid) etrafında, sabit bir
    spread ile ilan eder. Marjı oynatarak kâr maksimize etmez; spekülasyon yapmaz.
    """
    id: str
    cash: int
    stock: float
    target: float
    capacity: float
    margin: float                  # toplam spread (ör. 0.10 = %10)
    mid: float
    avg_cost: float
    kappa: float = 0.02            # stok sapmasına günlük fiyat tepkisi
    max_daily_move: float = 0.03
    min_markup: float = 0.02       # normal stokta maliyetin altına satmaz
    rent: int = 50                 # günlük sabit gider (soldo)
    price_rule: str = "linear"     # "linear" (v0) | "log" (simetrik)
    room_mult: float = 1.5         # hedef stoğun kaç katına kadar alım yapar
    anchor: float = 0.0            # fiyat hafızasına doğru günlük çekim (0 = yok)
    memory_days: float = 365.0
    memory_price: float = 0.0
    # İşletme sermayesinin üstündeki nakdin günlük çekilen payı (sahibin tüketimi).
    withdraw_rate: float = 0.0
    working_capital_mult: float = 3.0

    # "cover" kuralı: stoğun kaç günlük müşteri talebine yettiği (v3)
    target_cover_days: float = 30.0
    request_memory_days: float = 14.0
    request_rate: float = 0.0     # müşterilerin bu dükkâna günlük talep ettiği miktarın ortalaması
    requests_today: float = 0.0

    def cover_ratio(self) -> float:
        cover = self.stock / max(self.request_rate, 1e-9)
        return cover / self.target_cover_days

    # D5: ince pazar koruması. Müşteri talebi normalin çok altındaysa (fiyat çok yüksek ya da
    # pazar ölü) stok sıfır olsa bile fiyat yukarı itilmez: müşterisi olmayan dükkâncı fiyat artırmaz.
    thin_guard: float = 0.0          # >0: normal talebin bu oranının altında sinyal nötr
    normal_request: float = 0.0

    def signal_ratio(self) -> float:
        """Fiyat kuralının baktığı oran: 1 = istenen stok seviyesi."""
        if self.price_rule == "cover":
            if self.thin_guard > 0 and self.request_rate < self.thin_guard * self.normal_request:
                return max(1.0, self.cover_ratio()) if self.stock > 0 else 1.0
            return self.cover_ratio()
        return self.stock_ratio

    def end_of_day_requests(self):
        self.request_rate += (self.requests_today - self.request_rate) / self.request_memory_days
        self.requests_today = 0.0

    def withdrawal(self) -> int:
        excess = self.cash - self.working_capital_mult * self.target * self.mid
        return int(excess * self.withdraw_rate) if excess > 0 else 0


    # PI kontrol (D1g): `mid` integral bileşendir (uzun dönem seviyeyi yavaşça bulur);
    # ilan edilen fiyat buna ek olarak BUGÜNKÜ kıtlığa anında tepki verir (oransal bileşen).
    # Sadece integral kullanmak mevsim dalgasını ~çeyrek dalga geciktiriyordu (D1g bulgusu).
    prop_gain: float = 0.0

    # D5a2 (K-016): rekabetçi perakende. "lerner": ilan fiyatı = yerine koyma maliyeti × (1 + marj)
    # × kıtlık çarpanı; marjı dünya, dükkânın müşteri payından (logit rekabet) hesaplar.
    pricing: str = "mid"
    cost_ref: float = 0.0          # yerine koyma maliyeti (açık toptan fiyatın kısa ortalaması)
    markup: float = 0.0
    req_price: float = 0.0         # request_rate'in gözlendiği fiyat düzeyi (aynı hafızayla)
    share: float = 0.0             # kent müşterilerinin bu dükkâna yönelen payı (atalet ile değişir)
    op_profit: float = 0.0         # bu ayın işletme kârı (satış − yerine koyma maliyeti − geçim − kira)
    withdrawn: float = 0.0         # sahibin çektiği toplam (getiri ölçümü için)

    def __post_init__(self):
        self.memory_price = self.mid

    @property
    def stock_ratio(self) -> float:
        return self.stock / self.target

    def scarcity_factor(self) -> float:
        if self.prop_gain <= 0:
            return 1.0
        r = min(self.room_mult, max(1.0 / self.room_mult, self.signal_ratio()))
        return r ** (-self.prop_gain)

    def quote(self) -> float:
        """İlan edilen orta fiyat = integral (mid) × oransal kıtlık çarpanı."""
        return self.mid * self.scarcity_factor()

    def ask(self) -> float:
        if self.pricing == "lerner":
            return self.cost_ref * (1 + self.markup) * self.scarcity_factor()
        a = self.quote() * (1 + self.margin / 2)
        swollen = (self.cover_ratio() if self.price_rule == "cover" else self.stock_ratio) >= 1.5
        if not swollen:   # stok şişmediyse zararına satmaz
            a = max(a, self.avg_cost * (1 + self.min_markup))
        return a

    def bid(self) -> float:
        if self.pricing == "lerner":   # en az asgari marjla satabileceğinden fazlasını ödemez
            return self.ask() / (1 + self.min_markup)
        return self.quote() * (1 - self.margin / 2)

    def mid_for_bid(self, bid: float) -> float:
        """Teklifin `bid` olması için integral bileşenin alması gereken değer."""
        return bid / ((1 - self.margin / 2) * self.scarcity_factor())

    def desired_stock(self) -> float:
        if self.price_rule == "cover":
            return self.target_cover_days * self.request_rate
        return self.target

    def buy_room(self, price: float) -> float:
        room = min(self.room_mult * self.desired_stock(), self.capacity) - self.stock
        affordable = self.cash / price if price > 0 else 0.0
        return max(0.0, min(room, affordable))

    def receive(self, qty: float, cost: int):
        total_value = self.avg_cost * self.stock + cost
        self.stock += qty
        if self.stock > 0:
            self.avg_cost = total_value / self.stock

    def update_mid(self):
        """Stok hedefin üstündeyse fiyatı indir, altındaysa artır (stoka dayalı el yordamı).

        "linear": hareket = −κ(oran−1). Oran [0, room_mult] aralığında olduğundan
        yukarı tepki aşağıdan güçlüdür → asimetrik mandal (D1 v0 bulgusu).
        "log": hareket = −κ·ln(oran), oran [1/room_mult, room_mult] ile sınırlı → simetrik.
        """
        if self.price_rule in ("log", "cover"):
            ratio = self.cover_ratio() if self.price_rule == "cover" else self.stock_ratio
            r = min(self.room_mult, max(1.0 / self.room_mult, ratio))
            move = -self.kappa * math.log(r)
        else:
            move = -self.kappa * (self.stock_ratio - 1.0)
        if self.anchor > 0:
            move += self.anchor * math.log(self.memory_price / self.mid)
        move = max(-self.max_daily_move, min(self.max_daily_move, move))
        self.mid *= 1.0 + move
        self.memory_price += (self.mid - self.memory_price) / self.memory_days


@dataclass
class Storer:
    """Stokçu / spekülatör (D1f): zamanlar arası arbitraj yapar.

    Hasat haberini alınca bu sezonun "adil fiyatını" tahmin eder (King-Davenant
    mantığı: pazara gelecek miktar ve talep esnekliği). Köylüden adil fiyatın
    altında alır, dükkâncılara adil fiyatın üstünde satar. Temelci bir ajandır:
    beklentisi o günkü fiyatı değil, arz haberini ve uzun dönem normal fiyatı izler.
    """
    id: str
    cash: int
    stock: float
    capacity: float
    margin: float = 0.08            # alış ile satış eşiği arasındaki toplam pay
    normal: float = 100.0           # uzun dönem "normal" TOPTAN fiyat hafızası
    normal_memory_days: float = 730.0
    fair: float = 100.0
    fair_memory_days: float = 60.0  # sezon içinde beklentiyi gözleme doğru düzeltme hızı (0 = düzeltme yok)
    max_fair_mult: float = 3.0
    carry_per_year: float = 0.0     # tutma maliyeti (faiz + bozulma): sezon içi beklenen fiyat artışı
    season_pos: float = 0.5         # hasattan bu yana geçen sezon payı (0-1); motor günceller
    withdraw_rate: float = 0.01
    working_capital: int = 0
    # "median" (D1g): normal fiyat = son N sezonun ortalama fiyatlarının medyanı.
    # Tek bir kıtlık yılı medyanı kirletmez (D1f B4), ama birkaç yıl gerçek seviyeyi öğretir.
    # "ema": eski yöntem (normal_memory_days ile üstel ortalama).
    normal_mode: str = "ema"
    normal_years: int = 7
    season_sum: float = 0.0
    season_n: int = 0
    season_history: list = field(default_factory=list)

    def on_harvest_news(self, marketable_ratio: float, elasticity: float):
        if self.normal_mode == "median" and self.season_n > 0:
            self.season_history.append(self.season_sum / self.season_n)
            self.season_history = self.season_history[-self.normal_years:]
            self.normal = float(np.median(self.season_history))
            self.season_sum, self.season_n = 0.0, 0
        mult = marketable_ratio ** (1.0 / elasticity)
        self.fair = self.normal * min(self.max_fair_mult, max(1 / self.max_fair_mult, mult))

    def observe(self, wholesale_price: float):
        """Toptan fiyatı gözler. Normal hafıza çok yavaş, sezon beklentisi daha hızlı öğrenir."""
        if self.normal_mode == "median":
            self.season_sum += wholesale_price
            self.season_n += 1
        else:
            self.normal += (wholesale_price - self.normal) / self.normal_memory_days
        if self.fair_memory_days > 0:
            self.fair += (wholesale_price - self.fair) / self.fair_memory_days

    def fair_today(self) -> float:
        """Sezon ortalaması `fair`; hasattan sonra düşük, hasat öncesi yüksek (tutma maliyeti kadar)."""
        return self.fair * (1 + self.carry_per_year * (self.season_pos - 0.5))

    # D5b2 (L): envantere göre teklif kaydırma (Ho & Stoll 1981): depo boşken teklifler yukarı,
    # doluyken aşağı kayar. 0 = kapalı.
    shade: float = 0.0

    def _inv_factor(self) -> float:
        if self.shade <= 0 or self.capacity <= 0:
            return 1.0
        return 1.0 - self.shade * (self.stock / self.capacity - 0.5)

    def bid(self) -> float:
        return self.fair_today() / (1 + self.margin / 2) * self._inv_factor()

    def sell_floor(self) -> float:
        return self.fair_today() * (1 + self.margin / 2) * self._inv_factor()

    def roll_continuous(self, months: int = 12):
        """D5b2 (L): hasadı olmayan mallarda "sezon" = ay; olağan fiyat = son 12 ayın ortalamalarının medyanı."""
        if self.season_n > 0:
            self.season_history.append(self.season_sum / self.season_n)
            self.season_history = self.season_history[-months:]
            self.normal = float(np.median(self.season_history))
            self.season_sum, self.season_n = 0.0, 0
            self.fair = self.normal

    def buy_room(self, price: float) -> float:
        return max(0.0, min(self.capacity - self.stock, self.cash / price if price > 0 else 0.0))

    def receive(self, qty: float, cost: int):
        self.stock += qty

    def withdrawal(self) -> int:
        excess = self.cash - self.working_capital
        return int(excess * self.withdraw_rate) if excess > 0 else 0
