"""D5: full slice (ports, goods, urban classes, production, merchants, delayed information, entry/exit). Reference engine for the Rust core.

(Original notes in Turkish below.)

D5: tam dilim. 6 liman, 9 mal, sınıflı kentler, üretim zinciri, çok mallı tüccarlar,
gecikmeli bilgi (C4), serbest giriş-çıkış (havuz). Önceki deneylerin yuvaları bir arada.

Her (liman, mal) çifti kendi D1 pazar motorunu (ön ayar H) çalıştırır; kentin alımı sınıflı
LES + CES talebiyle (D4b), kumaş üretimi üretici havuzlarıyla (D4c), limanlar arası ticaret
çok mallı tüccarlarla (D2-D3b genellemesi) yapılır. Tüm yer tutucu sayılar ⚠️.
"""
import dataclasses
import functools
import datetime as dt
import math
from dataclasses import dataclass, field

import numpy as np

from .engine import H, START_DATE, D1Config, D1Sim
from .ledger import Ledger
from .production import ProducerPool, Recipe
from .rng import RngStreams

POOR_INCOME_YEAR = 250.0
WAGE = 2.5
CUSTOMS = 0.03
FREIGHT_PER_BULK_DAY = 0.6
LOSS_PER_DAY_SUMMER = 0.001
LOSS_PER_DAY_WINTER = 0.003
# R1 (K-030; risk-model.md): bacak başına tehlike. Değerler Claude seçimi ⚠️, maritime-risk-16c.md'deki örüntülere göre:
# mesafe değil bölge belirleyici, korsan payı ≥ %50, kış etkisi bölgesel (Levant'ta yok). Bölge: (kış çarpanı, sakin korsan olasılığı)
REGIONS = {"ADR": (3.0, 0.003), "OTR": (2.0, 0.008), "AEG": (2.0, 0.010), "STR": (2.0, 0.002), "LEV": (1.0, 0.010)}
EDGE_REGIONS = {("VEN", "RAG"): ("ADR",), ("RAG", "COR"): ("OTR",), ("VEN", "COR"): ("ADR", "OTR"),
                ("COR", "CHI"): ("AEG",), ("CHI", "IST"): ("STR",), ("CHI", "ALE"): ("LEV",), ("COR", "ALE"): ("LEV",)}
NAT_PER_EDGE = 0.004              # yazın bacak başına doğal kayıp (fırtına, kaza) ⚠️
CORSAIR_RHO, CORSAIR_SIGMA = 0.8, 0.25     # korsan baskısı: aylık log-AR(1) ⚠️
CORSAIR_JUMP_P, CORSAIR_JUMP = 0.05, 1.0   # seyrek sıçrama (bir filo bölgeye gelir; söylentiyle fiyatlanır) ⚠️


@dataclass
class G5:
    ref: float
    bulk: float
    kind: str            # harvest | continuous | produced
    harvest_month: int = 7
    self_share: float = 0.0


GOODS5 = {
    "WHT": G5(100, 1.0, "harvest", 7, 0.4),
    "BRL": G5(60, 1.0, "harvest", 6, 0.4),
    "OIL": G5(150, 1.0, "harvest", 11, 0.2),
    "WIN": G5(80, 1.0, "harvest", 9, 0.2),
    "WOL": G5(10, 0.6, "harvest", 5, 0.1),
    "ALM": G5(50, 0.3, "continuous"),
    "PEP": G5(400, 0.05, "continuous"),
    "CLC": G5(22, 0.3, "produced"),
    "CLF": G5(60, 0.3, "produced"),
}
CONSUMER_CATS = ["CER", "OIL", "WIN", "CLC", "CLF", "PEP"]

# Sınıf şablonu (consumer-profiles-16c §4, kumaş ikiye ayrılmış, şarap ve biber eklenmiş)
CLASS_TEMPLATE = {
    "zengin": dict(rel=12.0, shares=dict(CER=0.08, OIL=0.03, WIN=0.05, CLC=0.01, CLF=0.14, PEP=0.04),
                   subs=dict(CER=0.3, OIL=0.3), wheat=0.95),
    "orta": dict(rel=3.0, shares=dict(CER=0.20, OIL=0.06, WIN=0.06, CLC=0.07, CLF=0.03, PEP=0.01),
                 subs=dict(CER=0.6, OIL=0.4), wheat=0.85),
    "yoksul": dict(rel=1.0, shares=dict(CER=0.35, OIL=0.07, WIN=0.06, CLC=0.06, CLF=0.0, PEP=0.0),
                   subs=dict(CER=0.85, OIL=0.5), wheat=0.70),
}
WAGE_SHARES = {"zengin": 0.0, "orta": 0.3, "yoksul": 0.7}


@dataclass
class P5:
    pop: int
    classes: tuple       # zengin, orta, yoksul nüfus payları
    wine_factor: float = 1.0


PORTS5 = {
    "VEN": P5(170_000, (0.10, 0.20, 0.70)),
    "IST": P5(450_000, (0.06, 0.24, 0.70), wine_factor=0.3),
    "ALE": P5(40_000, (0.05, 0.20, 0.75), wine_factor=0.2),
    "RAG": P5(30_000, (0.12, 0.23, 0.65)),
    "COR": P5(18_000, (0.08, 0.20, 0.72)),
    "CHI": P5(15_000, (0.10, 0.20, 0.70)),
}
EDGES = [("VEN", "RAG", 8), ("RAG", "COR", 5), ("VEN", "COR", 12), ("COR", "CHI", 9),
         ("CHI", "IST", 4), ("CHI", "ALE", 8), ("COR", "ALE", 14)]

# Arz planı: liman → kendine yeterlilik oranı (s) ya da ("X", ağırlık) = ihracatçı
SUPPLY = {
    "WHT": dict(VEN=0.4, IST=0.6, RAG=0.1, COR=0.4, CHI=0.3, ALE=("X", 1.0)),
    "BRL": dict(VEN=0.6, IST=0.8, RAG=0.3, COR=0.6, CHI=0.5, ALE=("X", 1.0)),
    "OIL": dict(VEN=0.0, IST=0.3, RAG=0.5, ALE=0.2, COR=("X", 0.6), CHI=("X", 0.4)),
    "WIN": dict(VEN=0.2, IST=0.5, RAG=0.5, ALE=0.0, COR=("X", 0.5), CHI=("X", 0.5)),
    "WOL": dict(VEN=0.3, IST=("X", 1.0)),
    "ALM": dict(VEN=1.0),
    "PEP": dict(ALE=("X", 1.0)),
}
RECIPES5 = {"CLC": Recipe({"WOL": 1.0}, 4.0), "CLF": Recipe({"WOL": 1.5, "ALM": 0.2}, 12.0)}
# Kumaş üretim planı: hangi havuz hangi limanların talebini karşılar
POOL_PLAN = {
    ("VEN", "CLF"): ["VEN", "IST", "ALE", "RAG", "COR", "CHI"],
    ("VEN", "CLC"): ["VEN", "RAG", "COR", "CHI"],
    ("IST", "CLC"): ["IST", "ALE"],
}


def shortest_days():
    names = list(PORTS5)
    d = {(a, b): (0 if a == b else math.inf) for a in names for b in names}
    for a, b, w in EDGES:
        d[(a, b)] = d[(b, a)] = w
    for k in names:
        for i in names:
            for j in names:
                if d[(i, k)] + d[(k, j)] < d[(i, j)]:
                    d[(i, j)] = d[(i, k)] + d[(k, j)]
    return d


def route_legs(d):
    """En kısa yolun bacakları (kenarlar, sıralı anahtar EDGE_REGIONS'taki gibi)."""
    names = list(PORTS5)
    edge = {}
    for a, b, w in EDGES:
        edge[(a, b)] = edge[(b, a)] = (a, b)
    out = {}
    for a in names:
        for b in names:
            if a == b:
                continue
            path, cur = [], a
            while cur != b:
                nxt = next(n for n in names if (cur, n) in edge and abs(d[(cur, b)] - d[(cur, n)] - d[(n, b)]) < 1e-9)
                path.append(edge[(cur, nxt)])
                cur = nxt
            out[(a, b)] = path
    return out


@functools.lru_cache(maxsize=None)
def corsair_norm(n=200_000):
    """Korsan çarpanının ortalamasını 1 yapan bölen: süreç sabit bir rastgele akışla uzun süre koşulur (deterministik)."""
    r = np.random.default_rng(12345)
    eps, jump = r.normal(size=n), r.random(n) < CORSAIR_JUMP_P
    x, tot = 0.0, 0.0
    for i in range(n):
        x = CORSAIR_RHO * x + CORSAIR_SIGMA * eps[i] + (CORSAIR_JUMP if jump[i] else 0.0)
        tot += math.exp(x)
    return tot / n


@dataclass
class D5Config:
    seed: int = 0
    years: int = 10
    kappa: float = 0.01
    yield_sigma: float = 0.15
    yield_overrides: dict = field(default_factory=dict)   # {(liman, mal): {yıl: çarpan}}
    wages_endogenous: bool = False
    n_merchants: int | None = None   # None: gereken filodan türetilir (başlangıç koşulu tutarlılığı)
    capacity: float = 2000.0
    capital: int = 240_000
    living_cost: int = 30
    p_hear: float = 0.3
    vol_annual: float = 0.4
    revert_days: float = 60.0
    hurdle: float = 0.05
    free_entry: bool = True
    entry_pool: float | None = None  # None: gereken filonun ayda %5'i
    exit_prob: float = 0.1
    bond_rate: float = 0.04
    risk_premium: float = 0.04
    max_merchants: int = 300
    add_bots: bool = True
    direct_farm_buying: bool = True   # D5: ihracatçı tüccar doğrudan üreticiden alabilir (caricatori)
    depth_days: float = 30.0          # D5: hedef pazarın kaç günlük tüketimi kadar mal götürülür
    reroute_after: int = 15           # D5: satamayan tüccar bu kadar gün sonra başka limanı değerlendirir
    share_depth: bool = True          # D5: pazar derinliğinden yoldaki ve bekleyen rakip kargo düşülür
    dock_sales: bool = True           # D5: tüccar iskelede kent alıcılarına doğrudan satabilir
    recapitalize: bool = True         # D5: likidite tuzağındaki dükkâncı ve havuza yeni sermaye girer
    wholesale: bool = False           # D5a: kurumsal toptan pazar (kapan), K-013
    kapan_fee: float = 0.01           # kapan resmi (işlem değerinin payı)
    retail_rule: str = "pull"         # D5a2: "pull" (D5a mekanik çekiş) | "none" | "compete" (K-016)
    retail_beta: float = 12.0         # logit fiyat duyarlılığı (arama maliyeti ↓ → β ↑); Bertrand: β → ∞
    retail_inertia_days: float = 30.0 # müşteri payının yeni hedefe yaklaşma süresi (switching cost)
    retail_cost_days: float = 3.0     # yerine koyma maliyeti = açık toptan fiyatın bu kadar günlük ortalaması
    market_elasticity: float = 0.7    # pazar talebinin fiyat esnekliği (Lerner formülünde, yer tutucu)
    markup_min: float = 0.02
    markup_max: float = 0.5
    retail_entry: bool = False        # perakende giriş-çıkışı (D3b mekanizması, aylık)
    max_shops: int = 12
    price_discovery: bool = False     # D5a3: işlemsiz günde açık fiyat = en yüksek alış teklifi; rafı boş dükkân teklifini yükseltir
    shop_living_cost: int = 0
    # D5b (K-014): tüccar çeşitliliği ve rakip yüklemelerinin söylentiyle yayılması
    rival_info: bool = False          # "X, Y'ye Z yükledi" söylentisi (limanda duyulur, gemiyle taşınır)
    diversity: bool = False           # kişilikler dağılımdan çekilir; False: herkes homog_level, taklit 0
    homog_level: int = 0
    imitation_on: bool = True         # ablasyon: taklit eğilimi kapalı
    l0_counts_rivals: bool = False    # D5b3e E1 ablasyon: düzey 0 da duyduğu rakip yüklerini sayar (düzey 1 gibi)
    ch_tau: float = 1.5               # Camerer-Ho-Chong: düşünme derinliği ~ Poisson(τ), 2'de kesilir
    load_memory_days: int = 60        # duyulan bir yüklemenin "hâlâ pazara inecek" sayıldığı süre
    # D5b2: dört yuva (faktöriyel deney)
    visibility: bool = False          # G: limandaki alımlar açık (kim, ne, ne kadar; hedef söylenti), kapan hacmi görünür
    forward: bool = False             # B: kendi kargosunun fiyat etkisi + ileriye bakan beklenti (hasat haberi, mevsim)
    forward_fund: bool = True         # D5b2 ablasyonu: False = B'nin yalnızca kendi-etki kısmı (beklenti C4 kalır)
    forward_impact: bool = True       # D5b2 ablasyonu: False = B'nin yalnızca ileriye bakan beklenti kısmı
    sell_decision: bool = False       # S: her gün sat / bekle / rota değiştir; bekleme maliyeti açık
    liquidity: bool = False           # L: stokçu bütün mallarda, envantere göre teklif kaydırma
    storer_shade: float = 0.3
    season_carry: float = 0.1         # B: hasat mallarında sezon içi beklenen fiyat artışı (stokçunun carry'siyle aynı)
    # D5b3 (K-020): kararlı başlangıç, fırsata ve sermayeye bağlı giriş, colleganza
    entry_rule: str = "realized"      # "opportunity": liman sermaye havuzu × kamuya açık fırsat (price current)
    spinup_years: float = 0.0         # >0: ön koşuyla kararlı filo bulunur, asıl koşu o filoyla başlar
    pool_mult: float = 6.0            # toplam yatırılabilir sermaye = pool_mult × gereken filo × sermaye ⚠️ (nüfusa göre bölünür)
    entry_attention: float = 0.02     # potansiyel yatırımcı birimlerinin ayda ilgilenen payı ⚠️
    investor_sigma: float = 0.5       # yatırımcıların istediği risk priminin log-normal dağılımı (medyan risk_premium) ⚠️
    entry_lag_days: tuple = (30, 60)  # gemi bulma ve donatma
    opp_weight: float = 0.25          # colleganza: sefer getirisi inancı = w × tüccarın tahmini + (1−w) × geçmiş colleganza getirisi ⚠️
    invest_horizon: float = 3.0       # yeni tüccar / kalma kararı: sicil + (bu seferin kârı / sermaye) / H yıl ⚠️
    entry_smooth_months: int = 12     # yeni tüccar kalıcı fırsata bakar: kamu getirisinin son N ay ortalaması ⚠️
    colleganza: bool = False          # mevcut tüccara yatırımcı sermayesi (Venedik colleganza'sı)
    colleg_share: float = 0.75        # kârın yatırımcıya giden payı (tek taraflı colleganza: stans 3/4) ⚠️
    colleg_max_frac: float = 0.05     # tek sözleşmede havuzun en çok payı ⚠️
    reputation: str = "none"          # D5b3b (K-021): "user" = hacim × kâr oranı × kârlı işlem oranı; "cred" = credibility
    colleg_month_frac: float = 0.10   # D5b3b: limanın ayda colleganza'ya ayırdığı sermaye (havuzun payı) ⚠️
    rep_k: float = 5.0                # cred: nüfus ortalamasına çekme gücü (sefer sayısı cinsinden) ⚠️
    rep_lambda: float = 1.0           # cred: belirsizlik indirimi (standart hata sayısı) ⚠️
    rep_window: int = 730             # cred: sicil penceresi (gün); "user" 365 gün ⚠️
    # D5b3c (K-022): hibrit finansman. Kullanıcı notu: kesin değil, deneyle sınanıyor
    debt: bool = False                # likidite için vadeli borç (liman havuzundan; "tersine senet")
    loan_type: str = "plain"          # "plain": kargo batsa da borç ödenir; "sea": deniz ödüncü, kargo batarsa borç düşer
    loan_lev: float = 1.0             # kaldıraç sınırı: borç ≤ loan_lev × özsermaye (K-022)
    loan_premium: float = 0.04        # kredi primi (senedin üstü); alacaklının öğrendiği beklenen kayıp ayrıca eklenir ⚠️
    ruin_weight: float = 1.0          # batma korkusunun karar ağırlığı ("hassas denge"); 0 = ablasyon ⚠️
    colleg_mode: str = "reputation"   # "verified": colleganza yalnızca denetlenebilir, düşük riskli rota-mal çiftinde (K-022)
    colleg_ports: tuple = ("VEN",)    # denetlenebilir: sözleşmenin kayıtlı olduğu ana liman (tüccarın home'u; devlet gözetimi) ⚠️
    colleg_min_n: int = 8             # rota-mal: son 1 yılda en az bu kadar sefer (gözlenmiş olmalı) ⚠️
    colleg_max_loss: float = 0.35     # rota-mal: son 1 yılda zararlı sefer oranı en çok ⚠️ (0,15'te hiç rota yok: D5b3c.1)
    colleg_beta: float = 20.0         # yatırımcı öğrenmesi: bütçe payı = azami × logistic(β × (colleganza getirisi − senet)) ⚠️
    # D5b3d (K-023, K-024). Kullanıcı notu: kesin değil, deneyle sınanıyor
    record_net_overhead: bool = False # ölçüm düzeltmesi: sefer getirisi geçim/gemi giderinden arındırılır; risk sermayeye göre (D5b3c T2)
    loan_pricing: str = "learned"     # "learned" (D5b3c: öğrenilmiş ortalama kayıp) | "voyage" (K-023: alacaklının sefer beklentisi)
    lender_markup: float = 0.02       # alacaklının senet üstü istediği getiri (yıllık) ⚠️
    lender_rr: float = 0.5            # temerrütte geri alınan pay (beklenti) ⚠️
    lender_pd_max: float = 0.25       # bu temerrüt olasılığının üstünde borç verilmez (credit rationing) ⚠️
    lender_signal_w: float = 0.5      # düzey ≥ 1 tüccar, faizin ima ettiği beklentiye bu ağırlıkla yaklaşır ⚠️
    entry_ruin: bool = False          # K-024: giriş ve kalma kararı kamuya açık iflas sıklığını tartar
    entry_ruin_weight: float = 1.0    # ⚠️
    cold_track: str = "opportunity"   # D5b3f: sicil henüz yokken (koşunun ilk yılı) giriş inancı. "opportunity": ham fırsat
                                      # (eski); "neutral": sicil = senet + risk primi (fazla getiri yok sayılır)
    entry_bonus: bool = True          # D5b3f: giriş inancına "şu anki en iyi fırsat" bonusu eklenir mi (kalma kararı etkilenmez)
    # K-029 (D5b3g): giriş-çıkış kuralının düzeltilmesi; gelecek hafta literatürle doğrulanacak
    warm_start: bool = False          # başlangıç = uzun ön koşudan nesnel kuralla seçilmiş an (snapshot)
    warm_years: int = 10              # snapshot ön koşusunun süresi
    warm_min_years: int = 8           # an bu yıldan sonra aranır
    warm_n: int = 3                   # farklı ön koşu sayısı; koşu seed % warm_n numaralı snapshot'tan başlar
    warm_dir: str = ""                # boş: experiments/out/snapshots
    hurdle_rule: str = "lognormal"    # "common": giriş ve çıkış eşiği herkes için senet + risk primi; heterojenlik yalnızca hız ⚠️ eşik düzeltilecek
    exit_rule: str = "monthly"        # "voyage": çıkış kararı her seferin sonunda (aylık kontrol + %10 olasılık kalkar)
    public_track: str = "survivor_median"   # "aggregate": batanlar ve çıkanlar dahil toplam sermaye getirisi (son 12 ay)
    exit_premium: float | None = None # D5b3g ablation: çıkış eşiği = senet + bu (None: risk_premium; 0: Dixit bandı vekili, batık gemi) ⚠️
    entry_confirm: int = 1            # D5b3g U (kullanıcı önerisi): aday tüccar bu kadar değerlendirmenin hepsinde eşiği aşarsa girer
    entry_confirm_gap: int = 3        # değerlendirmeler arası ay (3 değerlendirme × 3 ay = 6 aylık süreç)
    band_kappa: float = 0.0           # D5b3g R (Claude; Dixit 1989): giriş eşiği + κσ, çıkış eşiği − κσ; σ = kamu sicilinin son 24 aylık sd ⚠️
    shrink_k: float = 9.0             # kişisel beklenti = w·kendi sicili + (1 − w)·kamu, w = n / (n + k); n: son 12 aydaki sefer ⚠️
    cred_rule: str = "fixed"          # Ö1: "buhlmann" = k veriden (Bühlmann-Straub; aylık öz sermaye getirileri, son 12 ay)
    hazard_model: str = "daily"       # R1 (K-030): "leg" = bacak + bölge tehlikesi, dinamik korsan baskısı; "daily" = eski
    ship_loss: float = 0.0            # R1: gemi kaybolunca ödenen yenileme bedeli (Ö3'e kadar geçici vekil) ⚠️
    # Ö3 (D5b3j; kullanıcı kararı 2026-11-06): gemi piyasası. Gemi alınıp satılan, yaşlanan, batınca giden bir varlık.
    # Giriş = ikinci el gemi almak ya da tersaneye ısmarlamak; çıkış = gemiyi satılığa çıkarmak. Değerleme Tobin's q:
    # gemiye biçilen değer = yerine koyma değeri + beklenen fazla getirinin ufuk boyunca bugünkü değeri. Değerler ⚠️
    ship_market: bool = False
    ship_price: float = 120_000.0     # yeni gemi bedeli (tersane) ⚠️ sermayenin yarısı; ölçek araştırmasıyla düzeltilecek
    ship_life: float = 15.0           # gemi ömrü (yıl); değer doğrusal olarak söküm değerine iner ⚠️
    ship_scrap: float = 0.1           # söküm (kereste) değeri, yeni bedelin payı ⚠️
    yard_days: int = 180              # tersanede yapım süresi ⚠️
    yard_rate: float = 0.4            # tersane kapasitesi: yılda (son 5 yıl ortalama) filonun bu payı kadar gemi ⚠️
    foreign_premium: float | None = 0.25   # dışarıdan hazır gemi almak: yeni bedel × (1 + bu), hemen (Lane 1934: 16. yy
                                      # ortasında yasağa rağmen dışarıdan gemi alınıyordu) ⚠️ None = kapalı
    layup_cost_day: float = 10.0      # satılığa çıkmış, bağlı geminin bekleme masrafı ⚠️
    layup_max_days: int = 365         # bu kadar satılamayan gemi sökülür ⚠️
    rebuy_min_cash: float = 0.5       # gemisini kaybeden tüccar, gemi aldıktan sonra en az bu kadar sermaye (× capital) kalıyorsa alır ⚠️
    ship_cost_day: float = 0.0        # K-024: gemi masrafı + amortisman (günlük, boşta da ödenir) ⚠️
    budget_bids: bool = True          # D5b3: dükkân teklifi nakdiyle sınırlı; batan dükkân kapanır (son dükkân da) — False = eski
    dust_lot: float = 1.0             # D5b2: bundan az kalan kargo fire sayılır (Zeno artifact'ı düzeltmesi); 0 = D5-D5b davranışı
    # D5b3e (K-026, K-027). Kullanıcı notu: kesin değil, deneyle sınanıyor
    network: bool = False             # E2: muhabir ağı; ağdaki limanda taze bilgi (mektup), dışında komisyon
    net_init_k: int = 1               # başlangıçta ana limana ek muhabir limanı sayısı (yakın limanlar olası)
    commission: float = 0.025         # ağ dışı limanda alış ve satışta komisyoncu payı ⚠️ (Claude seçti; arşivle düzeltilecek)
    net_learn_n: int = 3              # bir limanda bu kadar satış → orada muhabir edinilir
    net_cap: int = 5                  # ağın azami liman sayısı (muhabir tutmak emek ister) ⚠️
    letter_every: int = 7             # muhabir mektubu sıklığı (gün); gecikme = mektubun deniz yolu süresi
    houses: bool = False              # E3: büyük sermayeli tüccarın birden çok gemisi (ortak kasa, ortak bilgi, kendi kargosunu sayar)
    house_share: float = 0.3          # başlangıç filosunda evlere ait gemi payı ⚠️
    house_sizes: tuple = (2, 3, 4)    # ev başına gemi sayısı (eşit olasılık) ⚠️
    house_pool: bool = True           # E3 ayrıştırma: ortak kasa (False = her gemi kendi nakdi)
    house_internal: bool = True       # E3 ayrıştırma: ev kendi kargosunu tam sayar (False = rakip gibi)
    ports: list | None = None         # D5a: liman alt kümesi
    goods: list | None = None         # D5a: mal alt kümesi


@dataclass
class M5:
    id: str
    cash: int
    capacity: float
    is_player: bool = False
    informed: bool = False
    state: str = "buying"
    loc: str = "VEN"
    dest: str = ""
    arrive_day: int = -1
    good: str = ""
    qty: float = 0.0
    cost_basis: float = 0.0
    plan: tuple | None = None
    wait: int = 0
    risk_aversion: float = 1.0
    obs: dict = field(default_factory=dict)       # (liman, mal) → (fiyat, gün)
    hist: dict = field(default_factory=dict)      # (liman, mal) → [fiyatlar]
    heard: set = field(default_factory=set)
    born_day: int = 0
    start_capital: int = 0
    divs: int = 0
    marks: list = field(default_factory=list)
    # D5b kişiliği
    level: int = 0
    imitation: float = 0.0
    overconf: float = 1.0
    p_hear: float = 0.3
    dara: bool = False
    known_loads: dict = field(default_factory=dict)   # yük id → (köken, hedef, mal, miktar, gün[, tüccar])
    w_fund: float = 0.0               # D5b2 (B): beklentide temel (haber) bilginin ağırlığı; kalanı fiyat geçmişi
    hnews: dict = field(default_factory=dict)         # (liman, mal) → (hasat oranı, gün)
    seen_buys: list = field(default_factory=list)     # D5b2 (G): limanda gördüğü alımlar (tüccar, liman, mal, miktar, gün)
    reservation: float = 0.0          # D5b2 (S): bugünkü asgari satış fiyatı
    harbor: dict = field(default_factory=dict)        # (liman, mal) → (satış bekleyen kargo, gözlem günü)
    home: str = ""                    # D5b3: sermayesinin geldiği liman (çıkışta ve temettüde havuza döner)
    colleg: tuple | None = None       # D5b3: (yatırımcı sermayesi, liman, sözleşme anındaki nakit, gün)
    record: list = field(default_factory=list)        # D5b3b: sicil (bitiş günü, getiri, hacim, kâr, süre)
    debt: tuple | None = None         # D5b3c: (anapara, liman, yıllık faiz, gün)
    debt_lost: bool = False           # D5b3c: borçlu seferde kargo battı (deniz ödüncünde borç düşer)
    broke: bool = False               # D5b3c: borcunu ödeyemedi → battı, hiçbir faaliyet yapamaz, denklemden çıkar
    network: set = field(default_factory=set)         # D5b3e E2: muhabiri olan limanlar (ana liman dahil); ev üyeleri aynı kümeyi paylaşır
    net_count: dict = field(default_factory=dict)     # E2: liman → oradaki satış sayısı
    house: str = ""                   # D5b3e E3: ait olduğu ticaret evi (büyük tüccar); boş = tek gemili
    emarks: list = field(default_factory=list)        # D5b3g: aylık öz sermaye + temettü (borç ve colleganza sermayesi hariç)
    retire: bool = False              # D5b3g: sefer sonunda çıkmaya karar verdi; limanda boşalınca çıkar
    v0: float = 0.0                   # D5b3g: ölçüm başlangıcındaki değer (snapshot'tan gelenler; 0 = start_capital)
    t0: int = -1                      # D5b3g: ölçüm başlangıç günü (−1 = born_day)
    ship: int | None = None           # Ö3: geminin yapım günü; None = gemisi yok (batmış, sökülmüş ya da ısmarlanmış)
    on_order: int = -1                # Ö3: kendi ısmarladığı geminin teslim günü (−1 = yok)
    exit_ship: float = 0.0            # Ö3: çıkışta satılığa çıkan geminin yerine koyma değeri (sicil hesabı için)

    def net_worth(self) -> float:
        return float(self.cash) + (self.cost_basis if self.qty > 0 else 0.0)

    def equity(self) -> float:
        """D5b3g: öz sermaye. net_worth borç ve colleganza sermayesini de içeriyor (marks bu yüzden kaldıraçla şişiyordu)."""
        out = self.net_worth()
        if self.debt is not None:
            out -= self.debt[0]
        if self.colleg is not None:
            out -= self.colleg[0]
        return out


class D5World:
    def __init__(self, cfg: D5Config):
        self.cfg = cfg
        self.rng = RngStreams(cfg.seed)
        self.ledger = Ledger()
        self.day = 0
        self.date = START_DATE
        self.days = shortest_days()
        self.legs = route_legs(self.days)
        self._corsair_x = {k: 0.0 for k in REGIONS}
        self._corsair_z = corsair_norm()
        self.corsair = {k: 1.0 / self._corsair_z for k in REGIONS}
        self.dep_log = []                 # R1: (gün, kalkış, varış, kayıp, neden, ay) — yüklü her kalkış
        self.port_list = list(cfg.ports or PORTS5)
        self.good_list = list(cfg.goods or GOODS5)
        self.kapan_price = {}
        self.kapan_quote = {}                    # D5a2: işlem olmasa da görülen en ucuz teklif
        self.kapan_bid = {}                      # D5a3: günün en yüksek alış teklifi
        self.kapan_traded = {}                   # D5a3: son kapan oturumunda işlem oldu mu
        self._plan()
        self._build_markets()
        if cfg.retail_rule == "compete":
            for (p, g), mk in self.markets.items():
                for sk in mk.shops:
                    sk.pricing, sk.share = "lerner", 1.0 / len(mk.shops)
                    sk.cost_ref = sk.mid * (1 - sk.margin / 2)
                    sk.req_price = sk.mid
                self._set_markups(mk)
        self.shop_exits = 0
        self._build_pools()
        self._build_demand()
        self.required_fleet = self._required_fleet()
        self.n_init = cfg.n_merchants if cfg.n_merchants is not None else int(round(self.required_fleet))
        self.spinup_fleet = None
        if cfg.spinup_years > 0 and cfg.n_merchants is None and not cfg.warm_start:
            self.n_init = self.spinup_fleet = self._spinup()
        # D5b3: limanın price current'ı (kamuya açık, gemilerle gelen haberlerden; bayat)
        self.current = {p: {k: (GOODS5[k[1]].ref, -60) for k in self.markets} for p in self.port_list}
        self.current_hist = {p: {k: [GOODS5[k[1]].ref] for k in self.markets} for p in self.port_list}
        pops = {p: PORTS5[p].pop for p in self.port_list}
        tot = sum(pops.values())
        self.pool = {p: cfg.pool_mult * self.required_fleet * cfg.capital * pops[p] / tot for p in self.port_list}
        self.pending = []                 # (gün, liman, rota[, gemi yapım günü]): donatılmakta olan yeni gemiler
        self.ship_list = []               # Ö3: satılığa çıkmış (bağlı) gemiler: dict(built, owner, day)
        self.ship_px = 1.0                # Ö3: ikinci el gemi fiyatı / yerine koyma değeri (price current; son işlem ya da teklif)
        self.yard_next = 0                # Ö3: tersanenin bir sonraki boş teslim günü (kuyruk)
        self.ship_log = []                # Ö3: aylık piyasa kaydı
        self.ships_lost = 0
        self.colleg_n = self.colleg_in = self.colleg_out = 0
        self._track_known = False
        self.voy_log = []                 # teşhis: (kalkış, bitiş, mal, köken, hedef, miktar, beklenen, maliyet, gerçekleşen, düzey, satış limanı)
        self.colleg_ann = None            # D5b3b: colleganza yatırımcısının yıllıklaştırılmış getirisi (EMA)
        self.colleg_contracts = []        # D5b3b: (gün, düzey, getiri, yıllık, skor)
        self.colleg_requests = []
        self.colleg_budget = {}
        self.pop_roi = None               # D5b3b: (medyan sefer getirisi, sd, medyan süre), son 1 yıl
        self.colleg_track = None          # D5b3: colleganza seferlerinin gerçekleşen getirisi (EMA)
        self.entry_log = []               # (gün, liman, beklenen getiri, giriş sayısı)
        self.entry_pool = cfg.entry_pool if cfg.entry_pool is not None else 0.05 * self.required_fleet
        self.merchants: list[M5] = []
        self._next = 0
        mrng = self.rng.get("merchants_init")
        ports = list(self.port_list)
        for _ in range(self.n_init):
            self.merchants.append(self._new_merchant(ports[int(mrng.integers(len(ports)))], mrng))
        if cfg.ship_market:
            self._init_ships(self.rng.get("ships_init"))
        self.bid_snap = {k: [] for k in self.markets}    # D5b3e E2: haftalık (gün, en iyi teklif); mektuplar buradan
        self.commissions = 0
        self.n_houses = 0
        if cfg.houses:
            self._form_houses(self.rng.get("houses"))
        if cfg.add_bots:
            for informed in (False, True):
                b = self._new_merchant("VEN", mrng)
                b.is_player, b.informed = True, informed
                self.merchants.append(b)
        self.news = {p: [] for p in self.port_list}      # liman → [(id, köken, gün, {mal: fiyat})]
        self.loads = {p: {} for p in self.port_list}     # D5b: liman → {yük id: (köken, hedef, mal, miktar, gün)}
        self.harbor_news = {p: [] for p in self.port_list}
        self.port_buys = {p: [] for p in self.port_list}
        self.hnews_board = {p: [] for p in self.port_list}   # D5b2 (B): gemilerin getirdiği hasat haberleri     # D5b2 (G): (tüccar, liman, mal, miktar, gün)
        self.kapan_today = {}                                # D5b2 (G): (liman, mal) → bugünkü işlem hacmi   # D5b: liman → [(haber id, {(liman, mal): (miktar, gün)})]
        self._load_id = 0
        self.departures = []                             # D5b: (gün, köken, hedef, mal, miktar, düzey)
        self.gone = []                                   # D5b: çıkan / batan tüccarlar (kişilik getirisi için)
        self._news_id = 0
        self.flows = {}                          # (yıl, köken, hedef, mal) → miktar
        self.trailing_median = 0.0
        self.entries = self.exits = self.bankruptcies = self.reroutes = 0
        self.debt_bankruptcies = 0        # D5b3c: borcunu ödeyemeyip silinen tüccar
        self.loan_log = []                # D5b3c: (kapanış, liman, anapara, gün, ödenen, borç, düzey, temerrüt, kargo battı)
        self.fin_log = []                 # D5b3c: (gün, düzey, risk tutumu, sicil sayısı, seçim, borç/özsermaye)
        self.loan_el = {}                 # D5b3c: liman → alacaklının öğrendiği yıllık beklenen kayıp
        self.colleg_routes = set()        # D5b3c: colleganza'ya uygun (köken, hedef, mal)
        self.route_stats = {}             # D5b3c: (köken, hedef, mal) → (n, zararlı payı, ort. getiri, medyan süre)
        self.colleg_share_now = None      # D5b3c: yatırımcı öğrenmesi, havuzun aylık colleganza payı
        self.lender_book = {}             # D5b3d: liman → [(gün, hedef, mal, miktar, tüccar)] verilen borçların seferleri
        self.lender_calib = {}            # D5b3d: liman → gerçekleşen / tahmin edilen temerrüt oranı
        self.ruin_days = []               # D5b3d: iflas günleri (kamuya açık: "banca rotta")
        self.rationed = 0                 # D5b3d: alacaklının reddettiği teklifler
        self.shop_entries = self.pool_investments = 0
        self.ledger.start(self._money_total(), self._goods_totals())
        self.log = {"date": [], "n_npc": [], "best_margin": [], "bot_nw": [], "inf_nw": [], "frac_selling": []}
        self.kapan_volume = {}
        for (p, g) in self.markets:
            self.log[f"{p}_{g}_ask"] = []
            self.log[f"{p}_{g}_kapan"] = []
            self.log[f"{p}_{g}_retail"] = []
        for p in self.port_list:
            for k in CLASS_TEMPLATE:
                self.log[f"{p}_{k}_income"] = []
            for g in ("CLC", "CLF", "WHT"):
                self.log[f"{p}_{g}_cons"] = []
        for key in self.pools:
            self.log[f"{key[0]}_{key[1]}_prod"] = []
        self.agg_hist = []                # D5b3g: aylık toplam sermaye getirisi (batanlar ve çıkanlar dahil)
        self.public_agg = None            # D5b3g: son 12 ayın toplamı (yıllık); kamuya açık sicil
        self._prev_val = {}
        self._gone_seen = 0
        self.t0_day = 0
        self.start_date = START_DATE
        if cfg.warm_start:
            self._load_warm()

    # --- K-029 snapshot ------------------------------------------------------
    def _load_warm(self):
        import pickle
        k = self.cfg.seed % self.cfg.warm_n
        path = snapshot_path(self.cfg, k)
        if not path.exists():
            build_snapshot(self.cfg, k)
        with open(path, "rb") as f:
            snap = pickle.load(f)
        cfg = self.cfg
        self.__dict__.update(snap.__dict__)
        self.cfg = cfg
        self.rng = RngStreams(cfg.seed)
        if cfg.ship_market and not hasattr(self, "ship_list"):    # gemisiz eski snapshot: gemi ekle
            self.ship_list, self.ship_px, self.yard_next, self.ship_log, self.ships_lost = [], 1.0, 0, [], 0
        if cfg.ship_market and all(m.ship is None for m in self.merchants if not m.is_player):
            self._init_ships(self.rng.get("ships_init"))
        self._rebase()

    def _rebase(self):
        """Ölçüm bu andan başlar: kayıtlar ve sayaçlar sıfırlanır; dünya durumu (tüccarlar, pazarlar, sicil, batma geçmişi) kalır."""
        self.t0_day, self.start_date = self.day, self.date
        self.log = {k: [] for k in self.log}
        self.voy_log, self.departures, self.loan_log, self.fin_log, self.gone = [], [], [], [], []
        self.dep_log = []
        self.ship_log = []
        self.colleg_contracts = []
        self._gone_seen = 0                    # pub_log kalır: R bandının σ'sı için durum
        self.flows, self.kapan_volume = {}, {}
        for name in ("entries", "exits", "bankruptcies", "reroutes", "debt_bankruptcies", "shop_entries",
                     "pool_investments", "shop_exits", "rationed", "commissions", "ships_lost"):
            if isinstance(getattr(self, name, None), (int, float)):
                setattr(self, name, 0)
        self.n_init = sum(1 for m in self.merchants if not m.is_player)
        for m in self.merchants:
            m.v0, m.t0 = self._value(m), self.day

    def _snapshot_bytes(self) -> bytes:
        import pickle
        keep = {k: getattr(self, k) for k in ("log", "voy_log", "departures", "loan_log", "fin_log", "gone",
                                               "colleg_contracts", "flows", "_gone_seen", "dep_log", "ship_log")}
        try:
            self.log = {k: [] for k in self.log}
            for k in ("voy_log", "departures", "loan_log", "fin_log", "gone", "colleg_contracts", "dep_log", "ship_log"):
                setattr(self, k, [])
            self.flows = {}
            self._gone_seen = 0
            return pickle.dumps(self, protocol=5)
        finally:
            for k, v in keep.items():
                setattr(self, k, v)

    # --- kalibrasyon --------------------------------------------------------
    def _class_income(self, port: str) -> dict:
        P = PORTS5[port]
        return {k: share * P.pop * CLASS_TEMPLATE[k]["rel"] * POOR_INCOME_YEAR / 365.0
                for k, share in zip(CLASS_TEMPLATE, P.classes)}

    def _class_shares(self, port: str, k: str) -> dict:
        sh = dict(CLASS_TEMPLATE[k]["shares"])
        sh["WIN"] *= PORTS5[port].wine_factor
        return sh

    def _plan(self):
        """Her limanın yerel normal tüketimi, havuz üretim planları, girdi ihtiyacı ve arz kapasitesi."""
        ref = {g: GOODS5[g].ref for g in GOODS5}
        L = {p: {g: 0.0 for g in GOODS5} for p in self.port_list}
        self.income_ref = {}
        for p in self.port_list:
            inc = self._class_income(p)
            self.income_ref[p] = inc
            for k, Yk in inc.items():
                sh = self._class_shares(p, k)
                w = CLASS_TEMPLATE[k]["wheat"]
                L[p]["WHT"] += sh["CER"] * Yk * w / ref["WHT"]
                L[p]["BRL"] += sh["CER"] * Yk * (1 - w) / ref["BRL"]
                for c in ("OIL", "WIN", "CLC", "CLF", "PEP"):
                    L[p][c] += sh[c] * Yk / ref[c]
        self.local_cons = {p: dict(L[p]) for p in self.port_list}
        # Havuz planları
        self.pool_target = {}
        for (p, g), served in POOL_PLAN.items():
            if p not in self.port_list or g not in self.good_list:
                continue
            self.pool_target[(p, g)] = sum(self.local_cons[q][g] for q in served if q in self.port_list)
        need_in = {p: {g: 0.0 for g in GOODS5} for p in self.port_list}
        for (p, g), out in self.pool_target.items():
            for inp, a in RECIPES5[g].inputs.items():
                need_in[p][inp] += a * out
        for p in self.port_list:
            for g in ("WOL", "ALM"):
                L[p][g] = need_in[p][g]
        self.demand_L = L
        # Arz kapasiteleri
        self.supply = {p: {g: 0.0 for g in GOODS5} for p in self.port_list}
        for g, plan in SUPPLY.items():
            if g not in self.good_list:
                continue
            deficit = 0.0
            exporters = {}
            for p in self.port_list:
                v = plan.get(p, 0.0)
                if isinstance(v, tuple):
                    exporters[p] = v[1]
                else:
                    self.supply[p][g] = v * L[p][g]
                    deficit += (1 - v) * L[p][g]
            wsum = sum(exporters.values()) or 1.0          # mevcut ihracatçılar arasında normalize
            for p, w in exporters.items():
                self.supply[p][g] = L[p][g] + w / wsum * deficit

    def _build_markets(self):
        cfg = self.cfg
        self.markets: dict[tuple, D1Sim] = {}
        i = 0
        for p in self.port_list:
            P = PORTS5[p]
            for g, spec in ((g, GOODS5[g]) for g in self.good_list):
                demand = self.demand_L[p][g]
                supply = self.supply[p][g]
                pool = (p, g) in self.pool_target
                if demand <= 0 and supply <= 0 and not pool:
                    continue
                need = max(demand, 0.05 * supply, 1.0)     # pazar ölçeği (ihracatçıda en az arzın %5'i)
                surplus = 1.05 * supply / need if supply > 0 else 0.0
                harvest = spec.kind == "harvest" and supply > 0
                kw = dict(H, kappa=cfg.kappa, seed=cfg.seed, years=cfg.years, good=g,
                          population=P.pop, need_per_capita_year=need * 365.0 / P.pop,
                          ref_price=spec.ref, harvest_month=spec.harvest_month,
                          self_share=spec.self_share if harvest else 0.0,
                          n_storers=(2 if g in ("WHT", "BRL") else 1) if harvest else (1 if cfg.liquidity else 0),
                          supply_surplus=surplus,
                          yield_sigma=cfg.yield_sigma if harvest else 0.0,
                          continuous_supply=spec.kind == "continuous" and supply > 0,
                          farmer_front_load=H.get("farmer_front_load", 0.0) if harvest else 0.0,
                          yield_overrides=dict(cfg.yield_overrides.get((p, g), {})),
                          rent_turnover_share=0.001, thin_guard=0.05,
                          external_wholesale=cfg.wholesale)
                self.markets[(p, g)] = D1Sim(D1Config(**kw), ledger=self.ledger, rng_salt=100 + i)
                if cfg.liquidity:
                    for st in self.markets[(p, g)].storers:
                        st.shade = cfg.storer_shade
                        if not harvest:              # arzı olmayan (ithalatçı) pazarlar da aylık medyanla
                            st.normal_mode = "median"
                i += 1

    def _build_pools(self):
        self.pools = {}
        for (p, g), out in self.pool_target.items():
            rec = RECIPES5[g]
            cost = sum(a * GOODS5[i].ref for i, a in rec.inputs.items()) + rec.labor * WAGE
            pool = ProducerPool(good=g, recipe=rec, capacity=out / 0.85, cash=int(60 * out * cost))
            pool.inputs = {i: a * out * pool.input_days for i, a in rec.inputs.items()}
            pool.output = out * 10
            self.pools[(p, g)] = pool
        self.normal_wage = {p: 0.0 for p in self.port_list}
        for (p, g), out in self.pool_target.items():
            self.normal_wage[p] += out * RECIPES5[g].labor * WAGE
        self.wage_yday = dict(self.normal_wage)

    def _build_demand(self):
        sig = 2.0
        ref = {g: GOODS5[g].ref for g in GOODS5}
        self.cls = {}
        for p in self.port_list:
            out = []
            for k, Yk in self.income_ref[p].items():
                sh = self._class_shares(p, k)
                subs = CLASS_TEMPLATE[k]["subs"]
                w = CLASS_TEMPLATE[k]["wheat"]
                E = {cat: sh[cat] * Yk for cat in CONSUMER_CATS}
                a = {"WHT": w * ref["WHT"] ** (sig - 1), "BRL": (1 - w) * ref["BRL"] ** (sig - 1)}
                P_ref = {"CER": 1.0, **{c: ref[c] for c in CONSUMER_CATS[1:]}}
                gamma = {cat: subs.get(cat, 0.0) * E[cat] / P_ref[cat] for cat in CONSUMER_CATS}
                S = Yk - sum(P_ref[c] * gamma[c] for c in CONSUMER_CATS)
                beta = {cat: (E[cat] - P_ref[cat] * gamma[cat]) / S for cat in CONSUMER_CATS}
                out.append(dict(name=k, a=a, gamma=gamma, beta=beta))
            self.cls[p] = out

    def _required_fleet(self) -> float:
        """İthalat açıklarını en yakın kaynaktan taşımak için gereken tüccar sayısı (kaba)."""
        bulk_days = 0.0
        for g, spec in ((g, GOODS5[g]) for g in self.good_list):
            for p in self.port_list:
                if spec.kind == "produced":
                    srcs = [k[0] for k, served in POOL_PLAN.items()
                            if k in self.pool_target and k[1] == g and p in served]
                    if not srcs or srcs[0] == p:
                        continue
                    deficit = self.local_cons[p][g]
                else:
                    srcs = [q for q in self.port_list if isinstance(SUPPLY.get(g, {}).get(q), tuple)]
                    deficit = max(0.0, self.demand_L[p][g] - self.supply[p][g])
                if deficit <= 0 or not srcs or p in srcs:
                    continue
                d = min(self.days[(e, p)] for e in srcs)
                bulk_days += deficit * spec.bulk * (2 * d + 8)
        return bulk_days / self.cfg.capacity / 0.7

    # --- muhasebe -----------------------------------------------------------
    def _money_total(self) -> int:
        return (sum(m._money_total() for m in self.markets.values())
                + sum(pl.cash for pl in self.pools.values()) + sum(m.cash for m in self.merchants))

    def _goods_totals(self) -> dict:
        out = {g: 0.0 for g in self.good_list}
        for m in self.markets.values():
            for g, v in m._goods_totals().items():
                out[g] += v
        for (p, g), pl in self.pools.items():
            out[g] += pl.output
            for i, q in pl.inputs.items():
                out[i] += q
        for m in self.merchants:
            if m.qty > 0:
                out[m.good] += m.qty
        return out

    # --- yardımcılar --------------------------------------------------------
    def _winter(self) -> bool:
        return self.date.month in (11, 12, 1, 2)

    def _voyage(self, a: str, b: str) -> float:
        return self.days[(a, b)] * (1.5 if self._winter() else 1.0)

    def _p_loss(self, days: float, a: str | None = None, b: str | None = None, actual: bool = False) -> float:
        """Sefer başına kayıp olasılığı. R1 ("leg"): rotanın bacakları boyunca doğal tehlike (bölgenin kış çarpanıyla)
        ve korsan tehlikesi birleşir. actual=True: bugünkü korsan baskısıyla (gerçek çekiliş); değilse uzun dönem
        ortalaması (tüccar bölgenin olağan riskini bilir, bugünkü şoku bilmez; R2'de öğrenmeyle değişecek)."""
        if self.cfg.hazard_model != "leg" or a is None or b is None:
            pd = LOSS_PER_DAY_WINTER if self._winter() else LOSS_PER_DAY_SUMMER
            return 1 - (1 - pd) ** days
        return 1 - math.prod(1 - h for h in self._leg_hazards(a, b, actual)[0])

    def _leg_hazards(self, a, b, actual=False):
        """Rotanın bacak tehlikeleri: ([birleşik], [(doğal, korsan)])."""
        w = self._winter()
        out, parts = [], []
        for e in self.legs[(a, b)]:
            regs = EDGE_REGIONS[e]
            nat = NAT_PER_EDGE * (max(REGIONS[r][0] for r in regs) if w else 1.0)
            cor = 1 - math.prod(1 - REGIONS[r][1] * (self.corsair[r] if actual else 1.0) for r in regs)
            parts.append((nat, cor))
            out.append(1 - (1 - nat) * (1 - cor))
        return out, parts

    def _corsair_step(self):
        """Aylık korsan baskısı: bölge başına log-AR(1) + seyrek sıçrama; çarpanın uzun dönem ortalaması 1."""
        r = self.rng.get("corsair")
        for k in REGIONS:
            x = CORSAIR_RHO * self._corsair_x[k] + CORSAIR_SIGMA * r.normal()
            if r.random() < CORSAIR_JUMP_P:
                x += CORSAIR_JUMP
            self._corsair_x[k] = x
            self.corsair[k] = math.exp(x) / self._corsair_z

    def _best_bid(self, p, g):
        if self.cfg.wholesale:
            if self.cfg.price_discovery and not self.kapan_traded.get((p, g), True) and (p, g) in self.kapan_bid:
                return self.kapan_bid[(p, g)]       # son oturumda işlem yok: satıcının alabileceği, en yüksek alış teklifi
            return self.kapan_price.get((p, g), GOODS5[g].ref)
        return max(s.bid() for s in self.markets[(p, g)].shops)

    def _best_ask(self, p, g):
        if self.cfg.wholesale:
            return self.kapan_price.get((p, g), GOODS5[g].ref) * (1 + self.cfg.kapan_fee)
        return min(s.ask() for s in self.markets[(p, g)].shops)

    def _new_merchant(self, port, rng, capital=None) -> M5:
        self._next += 1
        cap = capital or self.cfg.capital
        m = M5(id=f"m{self._next}", cash=cap, capacity=self.cfg.capacity, loc=port,
               risk_aversion=float(rng.uniform(0.5, 1.5)), born_day=self.day, start_capital=cap)
        cfg = self.cfg
        m.p_hear, m.level = cfg.p_hear, cfg.homog_level
        if cfg.diversity:
            # Düşünme derinliği: Camerer, Ho & Chong (2004) Poisson(τ), 2'de kesilmiş
            m.level = min(2, int(rng.poisson(cfg.ch_tau)))
            m.imitation = float(rng.beta(2, 5)) if cfg.imitation_on else 0.0
            m.overconf = float(np.exp(rng.normal(-0.2, 0.3)))     # <1: belirsizliği küçümser (Odean 1998)
            m.p_hear = float(np.clip(cfg.p_hear * np.exp(rng.normal(0, 0.5)), 0.05, 0.9))   # ağ genişliği
            m.dara = True
            m.w_fund = float(rng.beta(2, 2)) if cfg.forward else 0.0     # Brock & Hommes (1998): fundamentalist ↔ chartist
        elif cfg.forward:
            m.w_fund = 0.5
        m.home = port
        if cfg.network:
            m.network = self._initial_network(port, rng)
        for (p, g) in self.markets:     # genel bilgi: referans fiyatlar, eski
            m.obs[(p, g)] = (GOODS5[g].ref, self.day - 60)
            m.hist[(p, g)] = [GOODS5[g].ref]
        if cfg.entry_rule == "opportunity" and hasattr(self, "current"):   # D5b3: limanın price current'ını bilir
            for k in self.markets:
                m.obs[k] = self.current[port][k]
                m.hist[k] = list(self.current_hist[port][k][-20:])
            if cfg.rival_info and hasattr(self, "loads"):
                m.known_loads = dict(self.loads[port])
        return m

    # --- D5b3e: muhabir ağı (E2) ve çok gemili tüccar (E3), K-026/K-027 ------------------
    def _initial_network(self, home: str, rng) -> set:
        """Ana liman + yakınlığa ağırlıklı net_init_k muhabir limanı (Trivellato; Datini şubeleri)."""
        others = [q for q in self.port_list if q != home]
        w = np.array([1.0 / max(self._voyage(home, q), 1.0) for q in others])
        k = min(self.cfg.net_init_k, len(others))
        pick = rng.choice(len(others), size=k, replace=False, p=w / w.sum()) if k > 0 else []
        return {home} | {others[i] for i in pick}

    def _comm(self, m: M5, p: str) -> float:
        """Ağ dışı limanda komisyoncu payı (E2)."""
        return self.cfg.commission if self.cfg.network and p not in m.network else 0.0

    def _form_houses(self, rng):
        """E3 (K-027): başlangıç filosunun house_share'i 2-4 gemili evlerde toplanır. Ev tek bir tüccardır: üyeler
        başkanın kişiliğini, bilgisini, ağını ve kasasını paylaşır. Toplam gemi sayısı değişmez."""
        free = [m for m in self.merchants if not m.is_player]
        rng.shuffle(free)
        target, used, h = int(round(self.cfg.house_share * len(free))), 0, 0
        while used < target and len(free) - used >= 2:
            size = int(min(rng.choice(self.cfg.house_sizes), len(free) - used))
            grp = free[used: used + size]
            used += size
            h += 1
            head = grp[0]
            net = set().union(*(x.network for x in grp)) if self.cfg.network else set()
            for x in grp:
                x.house = f"h{h}"
                x.home = head.home
                for a in ("level", "imitation", "overconf", "p_hear", "w_fund", "risk_aversion"):
                    setattr(x, a, getattr(head, a))
                x.network = net                       # aynı küme nesnesi: ev ağı ortak
                x.net_count = head.net_count
        self.n_houses = h

    def _house_members(self) -> dict:
        hs = {}
        for x in self.merchants:
            if x.house and not x.broke:
                hs.setdefault(x.house, []).append(x)
        return hs

    def _house_pool(self):
        """E3: ortak kasa. Borcu ya da colleganza'sı açık olmayan üyelerin nakdi eşitlenir: bir geminin zararı
        diğerlerini de etkiler (K-027)."""
        for mem in self._house_members().values():
            el = [x for x in mem if x.debt is None and x.colleg is None]
            if len(el) < 2:
                continue
            tot = sum(x.cash for x in el)
            each = tot // len(el)
            new = [each] * len(el)
            new[0] += tot - each * len(el)
            for x, c in zip(el, new):
                v = getattr(x, "voy", None)
                if v is not None:            # ölçüm: kasa transferi sefer getirisine sayılmasın
                    x.voy = v[:5] + (v[5] + c - x.cash,) + v[6:]
                x.cash = c

    def _house_share_info(self):
        """E3: ev içi mektuplaşma; her (liman, mal) için en taze gözlem bütün üyelere geçer (aylık)."""
        for mem in self._house_members().values():
            if len(mem) < 2:
                continue
            for k in self.markets:
                best = max(mem, key=lambda x: x.obs[k][1])
                for x in mem:
                    if x is not best and x.obs[k][1] < best.obs[k][1]:
                        x.obs[k] = best.obs[k]
                        x.hist[k] = list(best.hist[k])

    def _letters(self):
        """E2: muhabir mektupları. Ağdaki her limandan, mektubun yol süresi kadar eski fiyat gelir. Seferdeki
        tüccar mektubu limana varınca okur (basitleştirme: seferde mektup yok)."""
        for k, snap in self.bid_snap.items():
            snap.append((self.day, self._best_bid(*k)))
            if len(snap) > 30:
                del snap[0]
        for m in self.merchants:
            if m.state == "sailing" or m.is_player:
                continue
            for q in m.network:
                if q == m.loc:
                    continue
                lag = self._voyage(q, m.loc)
                for (p, g) in self.markets:
                    if p != q:
                        continue
                    old = [x for x in self.bid_snap[(p, g)] if x[0] <= self.day - lag]
                    if not old:
                        continue
                    day, price = old[-1]
                    if day > m.obs[(p, g)][1]:
                        m.obs[(p, g)] = (price, day)
                        h = m.hist[(p, g)]
                        h.append(price)
                        if len(h) > 40:
                            del h[0]

    # --- D5b3: başlangıç, sermaye havuzu, kamuya açık fırsat, colleganza (K-020) ---------
    def _spinup(self) -> int:
        """Ön koşu: aynı dünya kısa süre koşulur; son 180 günün ortalama filosu asıl koşunun başlangıcı olur."""
        sub = D5World(dataclasses.replace(self.cfg, spinup_years=0.0))
        while sub.day < int(self.cfg.spinup_years * 365):
            sub.step()
        n = sub.log["n_npc"][-180:]
        return max(1, int(round(sum(n) / len(n))))

    def _update_current(self):
        for (p, g) in self.markets:
            self.current[p][(p, g)] = (self._best_bid(p, g), self.day)
            h = self.current_hist[p][(p, g)]
            h.append(self.current[p][(p, g)][0])
            if len(h) > 40:
                del h[0]

    def _ret_of(self, opt, capital: float, origin: str, asks: dict | None = None, extra_days: float = 0.0) -> float:
        """Seçeneğin yıllık getirisi: yolculuk kârı / sermaye × 365 / döngü süresi. Döngü = konumlanma +
        gidiş + dönüş + 3 gün + hedefte satış süresi (kargo / günlük talep). D5b3 duman testi: satış süresi
        sayılmayınca beklenen getiri yıllık %200-900 çıkıyor, gerçekleşen −%1'di."""
        _, g, d, max_bid, q = opt
        ask = asks[g] if asks else self._best_ask(origin, g)
        net = max_bid * (1 + self.cfg.hurdle)
        days = self._voyage(origin, d)
        T = extra_days + 2 * days + 3 + q / max(self.demand_L[d][g], 1e-9)
        frac = (net - ask) * q / max(capital, 1.0)
        self._last_voyage = (frac, T)                # sefer kârı / sermaye ve döngü süresi
        return frac * 365 / T

    def _best_from(self, m: M5, p: str):
        """m'nin bilgisiyle, p'deki bir geminin en iyi fırsatı: (yıllık getiri, sefer kârı / sermaye, rota).
        Başka limandan yükleme de sayılır; oraya boş gitme süresi döngüye eklenir (_reposition gibi)."""
        best, voy, route = -1.0, 0.0, None
        for q in self.port_list:
            asks = None if q == p else {g: m.obs[(q, g)][0] / (1 - 0.05) for (x, g) in self.markets if x == q}
            opts = self._options(m, q, asks)
            v = 0.0 if q == p else self._voyage(p, q)
            for o in opts:
                r_o = self._ret_of(o, max(m.cash, 1.0), q, asks, v)
                if r_o > best:
                    best, voy, route = r_o, self._last_voyage[0], (q, o[2], o[1])
        return best, voy, route

    def _public_return(self, p: str) -> float:
        """Limanda "genel bilinen" fırsat = limandaki tüccarların beklentilerinin medyanı (liman konuşması).
        Limanda 3'ten az tüccar varsa: price current'la temsilî düzey 1 tüccar. D5b3.2 teşhisi: temsilî tüccar
        bayat price current'la sefer başına %160'lık hayalet farklar görüyordu; tüccarların kendi beklentisi
        medyanı %11'di."""
        cfg = self.cfg
        here = [m for m in self.merchants if not m.is_player and m.loc == p and m.state == "buying"]
        if len(here) >= 3:
            vals = sorted((self._best_from(m, p) for m in here), key=lambda x: x[0])
            mid = vals[len(vals) // 2]
            self._public_voy, self._public_route = mid[1], mid[2]
            return mid[0]
        rep_m = M5(id="public", cash=cfg.capital, capacity=cfg.capacity, loc=p, start_capital=cfg.capital,
                   level=1, p_hear=cfg.p_hear)
        rep_m.obs = dict(self.current[p])
        rep_m.hist = {k: list(v[-20:]) for k, v in self.current_hist[p].items()}
        if cfg.rival_info:
            rep_m.known_loads = dict(self.loads[p])
        # Donatılmakta olan gemiler limanda görünür ve gidecekleri yer tahmin edilir (düzey 1; entry cobweb tamponu)
        for i, (_, pp, route, *_) in enumerate(self.pending):
            if pp == p and route is not None:
                rep_m.known_loads[("pend", i)] = (route[0], route[1], route[2], cfg.capacity / GOODS5[route[2]].bulk,
                                                  self.day, f"pend{i}")
        best, self._public_voy, self._public_route = self._best_from(rep_m, p)
        return best

    def _belief(self, r_opp: float, voyage_frac: float, track: float | None) -> float:
        """Çok yıllık karar (yeni tüccar, kalmak) için beklenen yıllık getiri. "Şu anki en iyi fırsat"
        ortalamayı abartır (optimizer's curse; Smith & Winkler 2006): en iyisi seçilen tahminler yukarı yanlıdır.
        D5b3 duman testi: fırsat tahmini yıllık %200-700, gerçekleşen −%5. Bu yüzden: sicil (herkesin bildiği
        gerçekleşen getiri) + bu seferin olağanüstü kârı ufka yayılmış. Sicil yoksa (ısınma) fırsat."""
        if track is None:
            return r_opp
        lag = sum(self.cfg.entry_lag_days) / 2         # fırsat, gemi donatılırken C4'teki hızla söner
        return track + max(0.0, voyage_frac) * math.exp(-lag / self.cfg.revert_days) / self.cfg.invest_horizon

    def _convinced(self, x: float, extra: float = 0.0) -> float:
        """Fazla getiri x'e ikna olan yatırımcı payı: istenen risk primi log-normal (medyan risk_premium).
        extra (K-024): batma riskinin bedeli medyana eklenir; risk tutumu dağılımı aynı log-normalle ölçeklenir."""
        if x <= 0:
            return 0.0
        z = (math.log(x) - math.log(self.cfg.risk_premium + extra)) / self.cfg.investor_sigma
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    def _entry_opportunity(self, r):
        cfg = self.cfg
        if cfg.reputation != "none":
            self._update_pop_roi()
            self.colleg_budget = {p: cfg.colleg_month_frac * self.pool[p] for p in self.port_list}
        if cfg.debt or (cfg.colleganza and cfg.colleg_mode == "verified"):
            self._update_pop_roi()
            self._update_finance()
        n = sum(1 for m in self.merchants if not m.is_player) + len(self.pending)
        ship_rows = []
        for p in self.port_list:
            self.pool[p] *= 1 + cfg.bond_rate / 12
            r_exp = self._public_return(p)
            # Kalıcı giriş kalıcı fırsata bakar (geçici kıtlık ayları colleganza'yla, sefer başına karşılanır)
            hist = [x[2] for x in self.entry_log if x[1] == p][-(cfg.entry_smooth_months - 1):] + [r_exp]
            r_bar = sum(max(0.0, x) for x in hist) / cfg.entry_smooth_months
            belief, alt, conv = self._entry_signal(p, r_bar)
            if cfg.ship_market:                       # Ö3: aday yatırımcılar gemi piyasasında alıcı olur; takas ay sonunda
                self._ship_candidates(p, r, belief, alt)
                ship_rows.append((p, r_exp, belief, self._public_route))
                continue
            if cfg.entry_confirm > 1:
                k = self._entry_candidates(p, r, belief - alt - cfg.risk_premium - self._band(), n)
            else:
                lam = cfg.entry_attention * self.pool[p] / cfg.capital * conv
                k = min(int(r.poisson(lam)), int(self.pool[p] // cfg.capital), max(0, cfg.max_merchants - n))
                for _ in range(k):
                    self.pool[p] -= cfg.capital
                    lo, hi = cfg.entry_lag_days
                    self.pending.append((self.day + int(r.integers(lo, hi + 1)), p, self._public_route))
            n += k
            self.entry_log.append((self.day, p, r_exp, k, belief))
        if cfg.ship_market:
            k = self._ship_clear(r, n, {row[0]: row[3] for row in ship_rows})
            for p, r_exp, belief, _ in ship_rows:
                self.entry_log.append((self.day, p, r_exp, k.get(p, 0), belief))

    def _public_track(self):
        if self.cfg.public_track == "aggregate":
            return self.public_agg
        return self.trailing_median if self._track_known else None

    def _entry_signal(self, p: str, r_bar: float):
        """Limandaki yatırımcının inancı, alternatifi ve ikna olan pay. K-029 "common": eşik = alternatif + risk primi
        herkes için; log-normal yalnızca eşiğin üstündeki fazlaya kaç yatırımcının ikna olduğunu (hızı) belirler."""
        cfg = self.cfg
        track = self._public_track()
        if track is None and cfg.cold_track == "neutral":
            track = cfg.bond_rate + cfg.risk_premium
        belief = self._belief(r_bar, self._public_voy if cfg.entry_bonus else 0.0, track)
        # D5b3b: yatırımcının alternatifi yalnızca senet değil; itibarlı tüccara colleganza'nın getirisi de
        alt = cfg.bond_rate
        if cfg.reputation != "none" and self.colleg_ann is not None:
            alt = max(alt, self.colleg_ann)
        if cfg.hurdle_rule == "common":
            conv = self._convinced(belief - alt - cfg.risk_premium - self._band())
        else:
            conv = self._convinced(belief - alt, self._ruin_price())
        return belief, alt, conv

    def _band(self) -> float:
        """D5b3g R: real options bandının yarı genişliği κσ (Dixit 1989; Dixit & Pindyck 1994). σ = kamu sicilinin
        son 24 aylık standart sapması; belirsiz dönemde bant genişler, yatırımcı bekler."""
        if self.cfg.band_kappa <= 0:
            return 0.0
        i = 1 if self.cfg.public_track == "aggregate" else 2
        v = [x[i] for x in getattr(self, "pub_log", [])[-24:] if x[i] is not None]
        if len(v) < 6:
            return 0.0
        return self.cfg.band_kappa * float(np.std(v))

    def _entry_candidates(self, p: str, r, exc: float, n: int) -> int:
        """D5b3g U (kullanıcı önerisi): eşiği aşan fırsata ikna olan yatırımcı aday olur; entry_confirm_gap ay arayla
        yeniden değerlendirir; entry_confirm değerlendirmenin hepsinde fazla getiri kendi priminin üstündeyse sermayeyi
        bağlar ve gemi donatılır. Bir değerlendirmede bile ikna olmazsa vazgeçer. Adaylar birbirini görmez.
        Kişisel prim ~ log-normal (medyan risk_premium), yani ilk değerlendirme eski kuralın ikna olan payıyla aynı."""
        cfg = self.cfg
        gap = cfg.entry_confirm_gap * 30 - 5
        cands = getattr(self, "candidates", [])
        keep, k = [], 0
        for c in cands:                              # (liman, kişisel prim, sonraki değerlendirme günü, kalan değerlendirme)
            if c[0] != p or c[2] > self.day:
                keep.append(c)
                continue
            if exc <= c[1]:
                continue                             # ikna olmadı, vazgeçti
            if c[3] > 1:
                keep.append((p, c[1], self.day + gap, c[3] - 1))
            elif self.pool[p] >= cfg.capital and n + k < cfg.max_merchants:
                self.pool[p] -= cfg.capital
                lo, hi = cfg.entry_lag_days
                self.pending.append((self.day + int(r.integers(lo, hi + 1)), p, self._public_route))
                k += 1
        if exc > 0:
            for _ in range(int(r.poisson(cfg.entry_attention * self.pool[p] / cfg.capital))):
                prem = cfg.risk_premium * math.exp(cfg.investor_sigma * r.standard_normal())
                if exc > prem:
                    keep.append((p, prem, self.day + gap, cfg.entry_confirm - 1))
        self.candidates = keep
        return k

    def _update_agg(self):
        """K-029: aylık toplam sermaye getirisi = Σ değer değişimi / Σ ay başı değer; değer = öz sermaye + temettü.
        Çıkan ve batanlar çıktıkları ayın içinde (çıkışta kalan nakitle) sayılır; yeni girenler giriş sermayesiyle başlar."""
        num = den = 0.0
        alive = [m for m in self.merchants if not m.is_player]
        for m in alive:
            vp = self._prev_val.get(m.id, m.start_capital)
            num += self._value(m) - vp
            den += vp
        for m, _, cash in self.gone[self._gone_seen:]:
            if m.is_player:
                continue
            vp = self._prev_val.get(m.id, m.start_capital)
            num += max(0.0, cash - (m.debt[0] if m.debt is not None else 0.0)) + m.divs + m.exit_ship - vp
            den += vp
        self._gone_seen = len(self.gone)
        self._prev_val = {m.id: self._value(m) for m in alive}
        if den > 0:
            self.agg_hist = (self.agg_hist + [num / den])[-12:]
        self.public_agg = sum(self.agg_hist) * 12 / len(self.agg_hist) if len(self.agg_hist) >= 3 else None

    def _own_expect(self, m: M5):
        """K-029: kişisel beklenti, kendi sicili ile kamu sicili arasında credibility ağırlığı (Bühlmann ⚠️)."""
        pub = self._public_track()
        if pub is None:
            return None
        own = None
        if m.house and self.cfg.houses:
            mem = [x for x in self.merchants if x.house == m.house and len(x.emarks) >= 4]
            if mem:
                span = min(len(x.emarks) for x in mem) - 1
                own = (sum(x.emarks[-1] for x in mem) / max(sum(x.emarks[-1 - span] for x in mem), 1.0) - 1) * 12 / span
        elif self.cfg.cred_rule == "buhlmann":
            r = self._mrets(m)
            k = getattr(self, "cred_k", None)
            if len(r) < 3 or k is None:
                return pub
            z = len(r) / (len(r) + k)                # Bühlmann: Z = n / (n + k), n = ay sayısı
            return z * 12 * sum(r) / len(r) + (1 - z) * pub
        elif len(m.emarks) >= 4:
            own = (m.emarks[-1] / max(m.emarks[0], 1.0) - 1) * 12 / (len(m.emarks) - 1)
        if own is None:
            return pub
        n = sum(1 for x in m.record if self.day - x[0] <= 365)
        w = n / (n + self.cfg.shrink_k)
        return w * own + (1 - w) * pub

    @staticmethod
    def _mrets(m: M5) -> list:
        e = m.emarks
        return [e[i] / e[i - 1] - 1 for i in range(1, len(e)) if e[i - 1] > 1.0]

    def _update_cred(self):
        """Ö1: Bühlmann-Straub (1970) credibility parametresi, yaşayan tüccarların aylık öz sermaye getirilerinden.
        X_it = i tüccarının t ayındaki getirisi; s² = E[süreç varyansı] (tüccar içi), a = Var[gerçek ortalamalar]
        (tüccarlar arası, gürültü payı düşülmüş). k = s² / a; a ≤ 0 ise kendi sicil bilgi taşımaz (Z = 0)."""
        ms = [m for m in self.merchants if not m.is_player and not m.house]
        est = self._buhlmann([self._mrets(m) for m in ms], 3)
        if est is None:
            return
        k, s2, a, I = est
        self.cred_k = k
        # sağlamlık kontrolü (karara girmez): çakışmayan çeyreklik getirilerle aynı tahmin; k birimi ay
        q = [[e[i] / e[i - 3] - 1 for i in range(len(e) - 1, 2, -3) if e[i - 3] > 1.0] for e in (m.emarks for m in ms)]
        eq = self._buhlmann(q, 2)
        kq = eq[0] * 3 if eq else None
        self.cred_log = getattr(self, "cred_log", []) + [(self.day, k, s2, a, I, kq)]

    @staticmethod
    def _buhlmann(R, nmin):
        """Bühlmann-Straub tahmincisi (eşit ağırlıklı gözlemler, farklı n_i): (k, s², a, I) ya da None."""
        R = [r for r in R if len(r) >= nmin]
        I = len(R)
        if I < 10:
            return None
        n = [len(r) for r in R]
        mb = [sum(r) / len(r) for r in R]
        N = sum(n)
        s2 = sum(sum((x - mb[i]) ** 2 for x in R[i]) for i in range(I)) / sum(k - 1 for k in n)
        xb = sum(n[i] * mb[i] for i in range(I)) / N
        a = (sum(n[i] * (mb[i] - xb) ** 2 for i in range(I)) - (I - 1) * s2) / (N - sum(k * k for k in n) / N)
        return (s2 / a if a > 0 else math.inf), s2, a, I

    def _exit_decision(self, m: M5):
        """K-029: sefer bitince: beklenti eşiğin altındaysa, açığa ikna olma olasılığıyla çıkmaya karar verir."""
        if self.cfg.ship_market and m.ship is None:
            return                                   # Ö3: gemisi yok; kararı gemi piyasasında verir
        e = self._own_expect(m)
        if e is None:
            return
        prem = self.cfg.risk_premium if self.cfg.exit_premium is None else self.cfg.exit_premium
        short = self.cfg.bond_rate + prem - self._band() - e
        if self.cfg.ship_market:                     # Ö3: kalmanın fırsat maliyeti gemiyi bugün satmaktır (batık maliyet)
            short -= self._sunk_term(m, self.cfg.bond_rate + prem)
        if short > 0 and self.rng.get("exit_voyage").random() < self._convinced(short):
            m.retire = True

    def _retire_flagged(self):
        """Çıkmaya karar veren tüccar limanda boşalınca çıkar (eski aylık çıkışla aynı muhasebe)."""
        hm = self._house_members() if self.cfg.houses else {}
        keep = []
        for m in self.merchants:
            if not (m.retire and m.state == "buying" and m.qty <= 0) or m.is_player:
                keep.append(m)
                continue
            self._settle(m)
            if m.broke:
                keep.append(m)
                continue
            mates = [x for x in hm.get(m.house, []) if x is not m and not x.retire] if m.house else []
            if mates:
                mates[0].cash += m.cash
                m.cash = 0
            self._to_pool(m, m.cash)
            self.ledger.money_sink("to_bonds", m.cash)
            self.exits += 1
            self._release_ship(m)
            self.gone.append((m, self.day, m.cash))
        self.merchants = keep

    def _ruin_price(self) -> float:
        """K-024: kamuya açık iflas sıklığı (son 1 yıl, filo başına; "banca rotta" herkesçe bilinir) × batmada
        kaybedilen pay (~%90 ⚠️) × ağırlık. Yeni girenin ve kalanın istediği ek getiri."""
        if not self.cfg.entry_ruin:
            return 0.0
        n = sum(1 for d in self.ruin_days if self.day - d <= 365)
        fleet = max(1, sum(1 for m in self.merchants if not m.is_player))
        return self.cfg.entry_ruin_weight * 0.9 * n / fleet

    def _activate_pending(self):
        if self.cfg.ship_market:
            for m in self.merchants:
                if 0 <= m.on_order <= self.day:      # Ö3: kendi ısmarladığı gemi teslim edildi
                    m.ship, m.on_order = m.on_order, -1
        if not self.pending:
            return
        mrng = self.rng.get("merchants_entry")
        keep = []
        for x in self.pending:
            if x[0] > self.day:
                keep.append(x)
                continue
            nm = self._new_merchant(x[1], mrng)
            if len(x) > 3:                           # Ö3: gemisiyle gelir; sicil değeri öz sermaye + yerine koyma değeri
                nm.ship = x[3]
                nm.v0 = self._value(nm)
                self._prev_val[nm.id] = nm.v0
            self.merchants.append(nm)
            self.ledger.money_source("from_investors", nm.cash)
            self.entries += 1
        self.pending = keep

    # --- Ö3: gemi piyasası (D5b3j) --------------------------------------------
    # Kökeni: öneri Claude (14-natural-entry-exit Ö3), kullanıcı öne çekti (2026-11-06). Değerleme Tobin's q (Tobin 1969;
    # Hayashi 1982 ⚠️): yatırım, gemiye biçilen değer yerine koyma maliyetini aşınca yapılır. Batık maliyet (yeni bedel ile
    # ikinci el ya da söküm değeri arasındaki fark) çıkışı geciktirir (Dixit 1989 ⚠️); band (R) yerine bu geçer.
    # İkinci el fiyatı aylık çağrılı pazarda oluşur (kapan'la aynı mantık); tersane kuyruğu yapım süresini uzatır.
    def _init_ships(self, rng):
        L = self.cfg.ship_life * 365
        for m in self.merchants:
            if not m.is_player and m.ship is None:
                m.ship = self.day - int(rng.uniform(0, L))      # yaşlar düzgün dağılımlı ⚠️

    def _ship_R(self, m: M5 | None = None, built: int | None = None) -> float:
        """Yerine koyma değeri: yeni bedel, ömür boyunca doğrusal olarak söküm değerine iner. Ismarlanan gemi bedeliyle."""
        cfg = self.cfg
        if built is None:
            if m is None or not cfg.ship_market or m.is_player:
                return 0.0
            if m.ship is None:
                return cfg.ship_price if m.on_order >= 0 else 0.0
            built = m.ship
        age = max(0.0, (self.day - built) / 365.0)
        return cfg.ship_price * max(cfg.ship_scrap, 1 - (1 - cfg.ship_scrap) * age / cfg.ship_life)

    def _value(self, m: M5) -> float:
        """Sicil değeri: öz sermaye + temettü + gemi (yerine koyma değeriyle; piyasa fiyatı sicile girmez)."""
        return m.equity() + m.divs + self._ship_R(m)

    def _annuity(self, r: float) -> float:
        """Fazla getirinin süreceği beklenen ufuk (invest_horizon yıl) boyunca bugünkü değer çarpanı."""
        H = self.cfg.invest_horizon
        return H if abs(r) < 1e-9 else (1 - (1 + r) ** -H) / r

    def _ship_worth(self, belief: float, r: float, R: float) -> float:
        """Tobin's q: geminin bu yatırımcıya değeri = R + (beklenen − istenen getiri) × (sermaye + R) × a(r, H)."""
        return R + (belief - r) * (self.cfg.capital + R) * self._annuity(r)

    def _yard_delivery(self) -> int:
        return max(self.day + self.cfg.yard_days, self.yard_next)

    def _new_surplus(self, belief: float, r: float) -> float:
        """Tersaneye ısmarlamanın artığı: bedel ısmarlarken ödenir, gemi kuyruk + yapım süresi sonra gelir."""
        P = self.cfg.ship_price
        d = math.exp(-r * (self._yard_delivery() - self.day) / 365.0)
        return d * self._ship_worth(belief, r, P) - P

    def _foreign_surplus(self, belief: float, r: float) -> float:
        """Dışarıdan hazır yeni gemi: primli ama beklemesiz."""
        f = self.cfg.foreign_premium
        if f is None:
            return -math.inf
        P = self.cfg.ship_price
        return self._ship_worth(belief, r, P) - (1 + f) * P

    def _listed_R(self) -> float:
        return float(np.mean([self._ship_R(built=x["built"]) for x in self.ship_list])) if self.ship_list else 0.0

    def _sale_value(self, R: float) -> float:
        return max(self.ship_px * R, self.cfg.ship_price * self.cfg.ship_scrap)

    def _sunk_term(self, m: M5, r: float) -> float:
        """Çıkış eşiğinin düzeltmesi: gemi bugün yerine koyma değerinin altında satılıyorsa, kalmak için gereken getiri o kadar
        düşer (batık maliyet); üstünde satılıyorsa yükselir (patlamada gemiyi satıp çıkmak)."""
        R = self._ship_R(m)
        if R <= 0:
            return 0.0
        return (R - self._sale_value(R)) / ((self.cfg.capital + R) * self._annuity(r))

    def _ship_surplus(self, belief: float, r: float) -> float:
        """Bugünkü fiyatlarla en iyi edinme yolunun artığı (ikinci el ya da tersane)."""
        best = max(self._new_surplus(belief, r), self._foreign_surplus(belief, r))
        if self.ship_list:
            R = self._listed_R()
            best = max(best, self._ship_worth(belief, r, R) - self._sale_value(R))
        return best

    def _ship_candidates(self, p: str, r, belief: float, alt: float):
        """Aday yatırımcılar (U ile aynı süreç; ölçüt gemi piyasasındaki artık). Teyidi biten aday bu ay alıcı olur."""
        cfg = self.cfg
        gap = cfg.entry_confirm_gap * 30 - 5
        keep = []
        buyers = getattr(self, "_ship_buyers", [])
        for c in getattr(self, "candidates", []):
            if c[0] != p or c[2] > self.day:
                keep.append(c)
                continue
            if self._ship_surplus(belief, alt + c[1]) <= 0:
                continue                             # ikna olmadı, vazgeçti
            if c[3] > 1:
                keep.append((p, c[1], self.day + gap, c[3] - 1))
            else:
                buyers.append(dict(kind="inv", p=p, r=alt + c[1], belief=belief))
        unit = cfg.capital + cfg.ship_price          # bir yatırım birimi = işletme sermayesi + gemi
        for _ in range(int(r.poisson(cfg.entry_attention * self.pool[p] / unit))):
            prem = cfg.risk_premium * math.exp(cfg.investor_sigma * r.standard_normal())
            if self._ship_surplus(belief, alt + prem) > 0:
                if cfg.entry_confirm > 1:
                    keep.append((p, prem, self.day + gap, cfg.entry_confirm - 1))
                else:
                    buyers.append(dict(kind="inv", p=p, r=alt + prem, belief=belief))
        self.candidates = keep
        self._ship_buyers = buyers

    def _ship_clear(self, rng, n: int, routes: dict) -> dict:
        """Aylık gemi piyasası: (1) yaşlanan gemiler sökülür, (2) bağlı gemilerin masrafı ve uzun bekleyenlerin sökümü,
        (3) alıcılar: teyidi biten yatırımcılar + gemisini kaybetmiş tüccarlar, (4) tek fiyatlı takas (çağrılı pazar),
        (5) eşleşmeyen ve tersaneden artık gören alıcı ısmarlar; gemisiz tüccar hiçbir yolu kârlı görmüyorsa çıkar."""
        cfg = self.cfg
        K, P, scrap = cfg.capital, cfg.ship_price, cfg.ship_price * cfg.ship_scrap
        L = cfg.ship_life * 365
        n_scrap = n_layup_scrap = 0
        for m in self.merchants:                     # (1) ömrünü dolduran gemi limanda sökülür
            if (not m.is_player and m.ship is not None and self.day - m.ship >= L and m.state == "buying"
                    and m.qty <= 0):
                m.ship = None
                m.cash += int(scrap)
                self.ledger.money_source("ship_scrap", int(scrap))
                n_scrap += 1
        keep = []
        for x in self.ship_list:                     # (2) bağlı gemi
            self.pool[x["owner"]] -= 30 * cfg.layup_cost_day
            if self.day - x["built"] >= L or self.day - x["day"] >= cfg.layup_max_days:
                self.pool[x["owner"]] += self._ship_R(built=x["built"]) if self.day - x["built"] >= L else scrap
                n_layup_scrap += 1
                continue
            keep.append(x)
        self.ship_list = keep
        buyers = getattr(self, "_ship_buyers", [])
        self._ship_buyers = []
        rp = cfg.bond_rate + cfg.risk_premium
        for m in self.merchants:                     # (3) gemisini kaybeden tüccar: kendi beklentisiyle yeniden alıcı
            if (not m.is_player and m.ship is None and m.on_order < 0 and m.state == "buying" and m.qty <= 0
                    and not m.retire and not m.broke):
                e = self._own_expect(m)
                buyers.append(dict(kind="own", m=m, r=rp, belief=e if e is not None else rp))
        Rbar = self._listed_R() if self.ship_list else P
        for b in buyers:
            sn = self._new_surplus(b["belief"], b["r"])
            sf = self._foreign_surplus(b["belief"], b["r"])
            b["new"], b["foreign"] = sn, sf
            sn = max(sn, sf)
            bid = self._ship_worth(b["belief"], b["r"], Rbar) - max(0.0, sn)    # ikinci ele en çok: tersaneye göre artık
            cash = (b["m"].cash - cfg.rebuy_min_cash * K) if b["kind"] == "own" else (self.pool[b["p"]] - K)
            b["bid"] = min(bid, cash) / Rbar
        bids = sorted(buyers, key=lambda b: -b["bid"])
        ships = sorted(self.ship_list, key=lambda x: scrap / self._ship_R(built=x["built"]))
        asks = [scrap / self._ship_R(built=x["built"]) for x in ships]
        k = 0
        while k < min(len(bids), len(asks)) and bids[k]["bid"] >= asks[k]:
            k += 1
        trades, new_inv, new_own, rebuy_exit, n_foreign = 0, 0, 0, 0, 0
        entries = {}
        if k > 0:                                    # (4) tek fiyat: k. alış ile k. satış arası, k+1. teklifleri dışlayan
            lo = max(asks[k - 1], bids[k]["bid"] if k < len(bids) else -math.inf)
            hi = min(bids[k - 1]["bid"], asks[k] if k < len(asks) else math.inf)
            self.ship_px = (lo + hi) / 2
        elif bids and asks:
            self.ship_px = max(bids[0]["bid"], cfg.ship_scrap)   # işlem yok: en iyi alış teklifi, söküm tabanlı (satış değeri zaten sökümle tabanlı)
        elif asks:
            self.ship_px = asks[0]
        elif bids:
            self.ship_px = max(bids[0]["bid"], cfg.ship_scrap)
        sold = set()
        for i in range(k):
            b, x = bids[i], ships[i]
            if b["kind"] == "inv" and n >= cfg.max_merchants:
                continue
            R = self._ship_R(built=x["built"])
            price = self.ship_px * R
            self.pool[x["owner"]] += price
            sold.add(id(x))
            trades += 1
            if b["kind"] == "own":
                m = b["m"]
                m.cash -= int(price)
                self.ledger.money_sink("ship_purchase", int(price))
                m.ship = x["built"]
                self._prev_val[m.id] = self._prev_val.get(m.id, m.start_capital) + R - int(price)   # alım sicile kazanç/kayıp yazmaz
            else:
                self.pool[b["p"]] -= K + price
                lo_, hi_ = cfg.entry_lag_days
                self.pending.append((self.day + int(rng.integers(lo_, hi_ + 1)), b["p"], routes.get(b["p"]), x["built"]))
                entries[b["p"]] = entries.get(b["p"], 0) + 1
                n += 1
        self.ship_list = [x for x in self.ship_list if id(x) not in sold]
        nl = self.log["n_npc"][-1825:]               # tersane, sektörün olağan büyüklüğüne göre boyutlanmış (son 5 yıl filo ortalaması)
        fleet = sum(nl) / len(nl) if nl else self.n_init
        gap = 365.0 / max(cfg.yard_rate * max(fleet, 1.0), 1e-9)
        PF = (1 + cfg.foreign_premium) * P if cfg.foreign_premium is not None else math.inf
        for b in bids[k:]:                           # (5) tersane, dışarıdan hazır gemi ya da vazgeçmek
            foreign = b["foreign"] > b["new"]
            cost = PF if foreign else P
            ok = max(b["new"], b["foreign"]) > 0
            if b["kind"] == "own":
                m = b["m"]
                if ok and m.cash - cost >= cfg.rebuy_min_cash * K:
                    m.cash -= int(cost)
                    if foreign:
                        self.ledger.money_sink("foreign_ships", int(cost))
                        m.ship = self.day
                        self._prev_val[m.id] = self._prev_val.get(m.id, m.start_capital) + P - int(cost)
                        n_foreign += 1
                    else:
                        d = self._yard_delivery()
                        self.yard_next = d + gap
                        self.ledger.money_sink("shipbuilding", int(cost))
                        m.on_order = int(d)
                        self._prev_val[m.id] = self._prev_val.get(m.id, m.start_capital) + P - int(cost)
                        new_own += 1
                else:
                    m.retire = True                  # gemisiz ve yeniden almaya değmiyor: sermaye senede döner
                    rebuy_exit += 1
            elif ok and self.pool[b["p"]] >= K + cost and n < cfg.max_merchants:
                self.pool[b["p"]] -= K + cost
                if foreign:
                    lo_, hi_ = cfg.entry_lag_days
                    d = self.day + int(rng.integers(lo_, hi_ + 1))
                    self.pending.append((d, b["p"], routes.get(b["p"]), self.day))
                    n_foreign += 1
                else:
                    d = self._yard_delivery()
                    self.yard_next = d + gap
                    self.pending.append((int(d), b["p"], routes.get(b["p"]), int(d)))
                    new_inv += 1
                entries[b["p"]] = entries.get(b["p"], 0) + 1
                n += 1
        self.ship_log.append((self.day, self.ship_px, len(self.ship_list), trades, new_inv, new_own, len(buyers),
                              n_scrap, n_layup_scrap, max(0, self.yard_next - self.day), rebuy_exit,
                              sum(1 for b in buyers if b["kind"] == "own"), n_foreign))
        return entries

    def _release_ship(self, m: M5):
        """Çıkan ya da batan tüccarın gemisi satılığa çıkar (sahibi: ana limanın yatırımcıları)."""
        if not self.cfg.ship_market or m.is_player:
            return
        built = m.ship if m.ship is not None else (m.on_order if m.on_order >= 0 else None)
        if built is None:
            return
        m.exit_ship = self._ship_R(built=built)
        self.ship_list.append(dict(built=built, owner=m.home if m.home in self.pool else self.port_list[0], day=self.day))
        m.ship, m.on_order = None, -1

    def _to_pool(self, m: M5, amount: float):
        if self.cfg.entry_rule == "opportunity" and m.home in self.pool:
            self.pool[m.home] += amount

    def _colleganza(self, m: M5, opts):
        """Nakdi gemisini doldurmaya yetmeyen tüccara limanın yatırımcıları sermaye verir, fırsat onları
        ikna ederse (aynı eşik dağılımı). Tek taraflı colleganza: kârın colleg_share'i yatırımcıya, zarar
        yatırımcının sermayesinden (Lane 1973; González de Lara 2008 ⚠️)."""
        cfg = self.cfg
        score, g, d, max_bid, q_max = opts[0]
        ask = self._best_ask(m.loc, g)
        room = m.capacity / GOODS5[g].bulk - q_max
        if room <= 1 or m.cash / ask > q_max * 1.05:          # nakit değil derinlik/kapasite bağlıyor
            return opts
        self._ret_of(opts[0], q_max * ask, m.loc)
        frac, T = self._last_voyage                  # tüccarın bu sefer için tahmini (kendi sermayesine göre)
        if self.colleg_track is not None:            # limanın colleganza deneyimi (gerçekleşen sefer getirisi)
            frac = cfg.opp_weight * frac + (1 - cfg.opp_weight) * self.colleg_track
        x = frac * 365 / T - cfg.bond_rate
        r = self.rng.get("colleganza")
        if r.random() >= self._convinced(x):
            return opts
        c = int(min(room * ask, cfg.colleg_max_frac * self.pool.get(m.loc, 0.0)))
        if c < 0.05 * cfg.capital:
            return opts
        self.pool[m.loc] -= c
        m.cash += c
        self.ledger.money_source("colleganza_in", c)
        m.colleg = (c, m.loc, m.cash, self.day)
        self.colleg_n += 1
        self.colleg_in += c
        return self._options(m, m.loc) or opts

    # --- D5b3c: hibrit finansman (K-022) ------------------------------------------------
    def _update_finance(self):
        """Aylık: (1) alacaklının beklenen kaybı (öğrenme), (2) colleganza'ya uygun rota-mal çiftleri,
        (3) yatırımcı öğrenmesi: colleganza bütçesi, limanın gerçekleşen colleganza getirisine göre."""
        cfg = self.cfg
        recent = [x for x in self.loan_log if self.day - x[0] <= 365]
        for p in self.port_list + [None]:
            sub = [x for x in recent if p is None or x[1] == p]
            if len(sub) >= 5:                        # sefer başına kayıp oranı (temerrüt + deniz ödüncünde batan kargo)
                self.loan_el[p] = sum(max(0.0, x[5] - x[4]) for x in sub) / sum(x[2] for x in sub)
        if cfg.loan_pricing == "voyage":           # alacaklı kendi tahmin yanlılığını defterinden öğrenir
            for p in self.port_list:
                sub = [x for x in recent if x[1] == p and x[9] is not None]
                if len(sub) >= 10:
                    self.lender_calib[p] = min(3.0, max(0.5, (sum(x[7] for x in sub) + 1) / (sum(x[9] for x in sub) + 1)))
                self.lender_book[p] = [x for x in self.lender_book.get(p, []) if x[0] >= self.day - cfg.load_memory_days]
        stats = {}
        for x in self.voy_log:
            if self.day - x[1] <= 365:
                r = x[11] if cfg.record_net_overhead else x[8] / max(x[7], 1e-9) - 1
                stats.setdefault((x[3], x[4], x[2]), []).append((r, x[1] - x[0]))
        self.route_stats = {k: (len(v), float(np.mean([r < 0 for r, _ in v])), float(np.mean([r for r, _ in v])),
                                float(np.median([t for _, t in v])), float(np.std([r for r, _ in v])))
                            for k, v in stats.items()}
        self.colleg_routes = {k for k, (n, lf, mu, _, _) in self.route_stats.items()
                              if n >= cfg.colleg_min_n and lf <= cfg.colleg_max_loss and mu > 0}
        if cfg.colleganza and cfg.colleg_mode == "verified":
            rc = [x for x in self.colleg_contracts if self.day - x[0] <= 365]          # son 1 yılın deneyimi
            capd = sum(x[3] * x[4] for x in rc)
            self.colleg_ann = sum(x[2] * x[3] for x in rc) / capd * 365 if capd > 0 and len(rc) >= 5 else None
            x = 0.0 if self.colleg_ann is None else self.colleg_ann - cfg.bond_rate   # deneyim yoksa nötr (yeniden dener)
            self.colleg_share_now = cfg.colleg_month_frac / (1 + math.exp(-cfg.colleg_beta * x))
            self.colleg_budget = {p: self.colleg_share_now * self.pool[p] for p in self.port_list}

    def _loan_terms(self, p: str, days: float, d: str | None = None):
        """(yıllık faiz, sefer başına kayıp primi). Prim alacaklının öğrendiği kayıp oranı; deneyim yoksa
        önsel: deniz ödüncünde rotanın batma olasılığı, düz borçta %2 ⚠️."""
        prior = self._p_loss(days, p, d) if self.cfg.loan_type == "sea" else 0.02
        el = self.loan_el.get(p, self.loan_el.get(None, prior))
        if self.cfg.loan_type == "sea":
            el = max(el, prior)
        return self.cfg.bond_rate + self.cfg.loan_premium, el

    def _own_view(self, m: M5, frac: float, deploy: float = 1.0):
        """Tüccarın sefer getirisi inancı: kendi tahmini (frac), kendi siciliyle güncellenir (learning from
        experience; Malmendier & Nagel 2016). Sicil k sefer ağırlığında. σ: kendi sicili, yoksa nüfus.
        record_net_overhead: sicil kargo marjıdır (geçim gideri hariç); sermaye getirisine kargonun sermayedeki
        payıyla (deploy) çevrilir. Yoksa D5b3c davranışı (birim getiri doğrudan sermaye getirisi sayılır)."""
        cfg = self.cfg
        rec = [x[1] for x in m.record if self.day - x[0] <= cfg.rep_window]
        n = len(rec)
        if cfg.record_net_overhead:
            frac = frac / max(deploy, 1e-6)          # ex-ante sermaye getirisi → kargo marjı
        mu = (cfg.rep_k * frac + n * float(np.mean(rec))) / (cfg.rep_k + n) if n else frac
        if n >= 5:
            sd = float(np.std(rec))
        else:
            sd = self.pop_roi[1] if self.pop_roi is not None else 0.2
        sd = max(0.02, sd * m.overconf)
        if cfg.record_net_overhead:
            return mu * deploy, sd * deploy, n
        return mu, sd, n

    def _deploy(self, opt, K: float, p: str) -> float:
        return min(1.0, opt[4] * self._best_ask(p, opt[1]) / max(K, 1.0))

    def _lender_view(self, p: str, opt, K: float):
        """K-023: alacaklının sefer beklentisi (sermaye getirisi μ, σ). Bilgisi: price current (bayat), limanda
        görülen yüklemeler, kendisine yapılan önceki başvurular (sıralı fiyatlama: kalabalık). Tahmin yöntemi
        düzey 2 tüccarınkine benzer (çapalama + kalabalık + kendi kargosunun etkisi); daha iyi tahmin etmez."""
        cfg = self.cfg
        _, g, d, _, q = opt
        travel = self._voyage(p, d)
        price, oday = self.current[p][(d, g)]
        hist = self.current_hist[p][(d, g)]
        normal = float(np.median(hist[-20:]))
        h = (self.day - oday) + travel
        e0 = math.exp(math.log(normal) + (math.log(max(price, 1e-9)) - math.log(normal)) * math.exp(-h / cfg.revert_days))
        since = self.day - cfg.load_memory_days
        seen, crowd = set(), 0.0
        for day, dd, gg, qq, mid in self.lender_book.get(p, []):
            if day >= since and dd == d and gg == g:
                crowd += qq
                seen.add(mid)
        for v in self.loads.get(p, {}).values() if hasattr(self, "loads") else []:
            if v[1] == d and v[2] == g and v[4] >= since and (len(v) < 6 or v[5] not in seen):
                crowd += v[3]
        depth0 = cfg.depth_days * self.demand_L[d][g]
        e = e0 * depth0 / (depth0 + crowd + q)
        net = e * (1 - CUSTOMS) * (1 - self._p_loss(travel, p, d)) - FREIGHT_PER_BULK_DAY * GOODS5[g].bulk * travel
        ask = self._best_ask(p, g)
        margin = net / ask - 1
        st = self.route_stats.get((p, d, g))
        sd = st[4] if st is not None and st[0] >= 8 else (self.pop_roi[1] if self.pop_roi is not None else 0.3)
        dep = min(1.0, q * ask / max(K, 1.0))
        return margin * dep, max(0.02, sd) * dep

    def _lender_quote(self, p: str, opt, K: float, b: float, T: float):
        """Sefer bazlı faiz: alacaklı beklenen geri ödemesi senet + marj olacak şekilde fiyatlar.
        borç = b × taban / (1 − PD × (1 − RR) − kayıp); PD = P(sermaye getirisi < borç / K − 1). Yoksa None
        (credit rationing). Dönüş: (yıllık zaman faizi, sefer başına risk primi, PD, alacaklının μ'sü)."""
        cfg = self.cfg
        mu, sd = self._lender_view(p, opt, K)
        travel = self._voyage(p, opt[2])
        i_ann = cfg.bond_rate + cfg.lender_markup
        base = 1 + i_ann * T / 365
        lost = self._p_loss(travel, p, opt[2])
        calib = self.lender_calib.get(p, 1.0)
        owed, pd = b * base, 0.0
        for _ in range(4):
            z = (owed / K - 1 - mu) / sd
            pd = min(1.0, calib * 0.5 * (1 + math.erf(z / math.sqrt(2))) + (lost if cfg.loan_type == "plain" else 0.0))
            denom = 1 - pd * (1 - cfg.lender_rr) - (lost if cfg.loan_type == "sea" else 0.0)
            if pd > cfg.lender_pd_max or denom <= 0.05:
                return None
            owed = b * base / denom
        return i_ann, owed / b - base, pd, mu

    def _finance(self, m: M5, opts):
        """Nakdi gemisini doldurmaya yetmeyen tüccar: borç almak, colleganza ya da kendi nakdiyle gitmek.
        Seçim, beklenen servet − risk cezası (Arrow-Pratt yaklaşımı: γ/2 × Var / servet) − batma korkusu
        (ruin_weight × γ × P(batma) × özsermaye) ile tartılır ("hassas denge", K-022)."""
        cfg = self.cfg
        _, g, d, max_bid, q_max = opts[0]
        ask = self._best_ask(m.loc, g)
        room = m.capacity / GOODS5[g].bulk - q_max
        if room <= 1 or m.cash / ask > q_max * 1.05:          # nakit değil derinlik/kapasite bağlıyor
            return opts
        cash = float(m.cash)
        gamma = self._risk(m)
        p, pool = m.loc, self.pool.get(m.loc, 0.0)
        self._ret_of(opts[0], cash, p)
        mu0, sd0, n_rec = self._own_view(m, self._last_voyage[0], self._deploy(opts[0], cash, p))
        best = ("none", cash * (1 + mu0) - 0.5 * gamma * (sd0 * cash) ** 2 / cash, 0, opts, None)
        if cfg.debt:
            b_max = min(cfg.loan_lev * cash, room * ask, cfg.colleg_max_frac * pool)
            for f in (0.25, 0.5, 0.75, 1.0):
                b = int(b_max * f)
                if b < 0.05 * cfg.capital:
                    continue
                m.cash = cash + b
                o2 = self._options(m, p)
                m.cash = int(cash)
                if not o2:
                    continue
                K = cash + b
                self._ret_of(o2[0], K, p)
                frac, T = self._last_voyage
                mu, sd, _ = self._own_view(m, frac, self._deploy(o2[0], K, p))
                if cfg.loan_pricing == "voyage":
                    q = self._lender_quote(p, o2[0], K, b, T)
                    if q is None:                     # alacaklı bu sefere borç vermiyor (credit rationing)
                        self.rationed += 1
                        continue
                    i_ann, prem, pd_l, mu_l = q
                    if m.level >= 1:                  # faiz bir sinyal: düzey ≥ 1 tüccar alacaklının beklentisine yaklaşır
                        mu = (1 - cfg.lender_signal_w) * mu + cfg.lender_signal_w * mu_l
                else:
                    i_ann, prem = self._loan_terms(p, self._voyage(p, o2[0][2]), o2[0][2])
                    pd_l = None
                owed = b * (1 + i_ann * T / 365 + prem)
                z = (owed / K - 1 - mu) / sd
                p_ruin = 0.5 * (1 + math.erf(z / math.sqrt(2)))
                if cfg.loan_type == "plain":                  # kargo batarsa borç yine ödenir: kesin batma
                    p_ruin = min(1.0, p_ruin + self._p_loss(self._voyage(p, o2[0][2]), p, o2[0][2]))
                U = K * (1 + mu) - owed - 0.5 * gamma * (sd * K) ** 2 / cash - cfg.ruin_weight * gamma * p_ruin * cash
                if U > best[1]:
                    best = ("debt", U, b, o2, (i_ann, prem, pd_l))
        if cfg.colleganza and cfg.colleg_mode == "verified" and m.home in cfg.colleg_ports:
            hp = m.home                              # sözleşme ana limanda kayıtlı, sermaye oranın havuzundan
            c = int(min(room * ask, cfg.colleg_max_frac * self.pool.get(hp, 0.0), self.colleg_budget.get(hp, 0.0)))
            if c >= 0.05 * cfg.capital:
                m.cash = cash + c
                o2 = self._options(m, p)
                m.cash = int(cash)
                key = (p, o2[0][2], o2[0][1]) if o2 else None
                if key in self.colleg_routes:
                    n, lf, mu_r, dur, _ = self.route_stats[key]
                    x = cfg.colleg_share * mu_r * 365 / max(dur, 1.0) - cfg.bond_rate   # yatırımcı rotanın siciline bakar
                    if self.rng.get("colleganza").random() < self._convinced(x):
                        K = cash + c
                        self._ret_of(o2[0], K, p)
                        mu, sd, _ = self._own_view(m, self._last_voyage[0], self._deploy(o2[0], K, p))
                        U = (K * (1 + mu) - c - cfg.colleg_share * c * max(mu, 0.0)
                             - 0.5 * gamma * (sd * (K - 0.875 * c)) ** 2 / cash)
                        if U > best[1]:
                            best = ("colleg", U, c, o2, None)
        choice, _, amt, o2, terms = best
        self.fin_log.append((self.day, m.level, gamma, n_rec, choice, amt / cash))
        if choice == "debt":
            self.pool[p] -= amt
            m.cash += amt
            self.ledger.money_source("loan_in", amt)
            i_ann, prem, pd_l = terms
            m.debt = (amt, p, i_ann, self.day, prem)
            m.debt_pd = pd_l
            if cfg.loan_pricing == "voyage":         # alacaklı bu seferi biliyor: sonraki başvurularda kalabalık
                self.lender_book.setdefault(p, []).append((self.day, o2[0][2], o2[0][1], o2[0][4], m.id))
            return o2
        if choice == "colleg":
            self.colleg_budget[m.home] -= amt
            self.pool[m.home] -= amt
            m.cash += amt
            self.ledger.money_source("colleganza_in", amt)
            m.colleg = (amt, m.home, m.cash, self.day)
            self.colleg_n += 1
            self.colleg_in += amt
            return o2
        return opts

    def _repay(self, m: M5):
        """Borç vadesi = sefer sonu. Ödeyemeyen tüccar batar (tam sorumluluk; K-022): bütün nakdi alacaklıya."""
        b, port, rate, day0, prem = m.debt
        days = max(self.day - day0, 1)
        owed = contract = b * (1 + rate * days / 365 + prem)
        if self.cfg.loan_type == "sea" and m.debt_lost:
            owed = 0.0                               # deniz ödüncü: kargo battı, alacaklı deniz riskini taşır
        paid = int(min(m.cash, math.ceil(owed)))
        m.cash -= paid
        self.pool[port] += paid
        self.ledger.money_sink("loan_out", paid)
        default = paid < owed - 1
        self.loan_log.append((self.day, port, b, days, paid, contract, m.level, default, m.debt_lost,
                              getattr(m, "debt_pd", None)))
        m.debt, m.debt_lost = None, False
        if default:
            m.broke = True

    # --- D5b3b: itibar (K-021) -------------------------------------------------------
    def _rep_score(self, m: M5):
        """(sıralama skoru, yatırımcının beklediği yıllık getiri) ya da None (sicil yok → sermaye yok)."""
        cfg = self.cfg
        if cfg.reputation in ("user", "gate"):
            # Kullanıcı önerisi: bir yıllık işlem hacmi × kâr oranı × kârlı işlem oranı
            rec = [x for x in m.record if self.day - x[0] <= 365]
            if not rec:
                return None
            V = sum(x[2] for x in rec)
            p = sum(x[3] for x in rec) / max(V, 1.0)
            w = sum(1 for x in rec if x[3] > 0) / len(rec)
            dur = float(np.median([x[4] for x in rec]))
            if cfg.reputation == "gate":             # D5b3b ablasyon: aynı kapı (kârlı sicil), sıralama rastgele
                return (self.rng.get("rep_gate").random() if V * p * w > 0 else 0.0), p * 365 / dur
            return V * p * w, p * 365 / dur
        # "cred": credibility (Bühlmann 1967; Bayes shrinkage). Sefer getirisi ortalaması, sefer sayısı arttıkça
        # tüccarın kendi siciline, azken nüfus ortalamasına yaslanır; belirsizlik kadar indirilir.
        if self.pop_roi is None:
            return None
        mu0, sd0, dur0 = self.pop_roi
        rec = [x for x in m.record if self.day - x[0] <= cfg.rep_window]
        n = len(rec)
        mean = float(np.mean([x[1] for x in rec])) if rec else 0.0
        E = (n * mean + cfg.rep_k * mu0) / (n + cfg.rep_k)
        lcb = E - cfg.rep_lambda * sd0 / math.sqrt(n + cfg.rep_k)
        dur = float(np.median([x[4] for x in rec])) if rec else dur0
        ann = lcb * 365 / max(dur, 1.0)
        return ann, ann

    def _update_pop_roi(self):
        rec = [x for x in self.voy_log if self.day - x[1] <= 365]
        if len(rec) >= 10:
            roi = np.array([x[11] if self.cfg.record_net_overhead else x[8] / max(x[7], 1e-9) - 1 for x in rec])
            self.pop_roi = (float(np.median(roi)), float(np.std(roi)), float(np.median([x[1] - x[0] for x in rec])))

    def _process_colleg_requests(self):
        """Limanın yatırımcıları günün colleganza taleplerini itibar skoruna göre yukarıdan aşağı sıralar;
        aylık bütçe bitene ya da kalan tüccarlar ikna edemeyene kadar sermaye verir."""
        cfg = self.cfg
        r = self.rng.get("colleganza")
        by_port = {}
        for m in self.colleg_requests:
            sc = self._rep_score(m)
            if sc is not None and m.plan is not None and m.colleg is None:
                by_port.setdefault(m.loc, []).append((sc, m))
        self.colleg_requests = []
        for p, reqs in by_port.items():
            for (score, exp_ann), m in sorted(reqs, key=lambda x: -x[0][0]):
                if score <= 0 or r.random() >= self._convinced(exp_ann - cfg.bond_rate):
                    continue
                g, d, max_bid, q_max = m.plan
                ask = self._best_ask(p, g)
                room = m.capacity / GOODS5[g].bulk - q_max
                if room <= 1 or m.cash / ask > q_max * 1.05:
                    continue
                c = int(min(room * ask, cfg.colleg_max_frac * self.pool.get(p, 0.0), self.colleg_budget.get(p, 0.0)))
                if c < 0.05 * cfg.capital:
                    continue
                self.colleg_budget[p] -= c
                self.pool[p] -= c
                m.cash += c
                self.ledger.money_source("colleganza_in", c)
                m.colleg = (c, p, m.cash, self.day)
                m.colleg_score = score
                self.colleg_n += 1
                self.colleg_in += c
                opts = self._options(m, p)
                if opts:
                    _, g, d, max_bid, q_max = opts[0]
                    m.plan = (g, d, max_bid, q_max)

    def _settle(self, m: M5):
        """Yolculuk bitti (kargo tükendi): colleganza hesabı kapanır; teşhis kaydı."""
        v = getattr(m, "voy", None)
        if v is not None:
            day0, g, q, exp_net, unit_cost, cash0, o, d, lvl = v
            realized = (m.cash - cash0) / max(q, 1e-9)        # birim başına (navlun sonrası) gerçekleşen gelir
            # D5b3d ölçüm düzeltmesi: geçim ve gemi gideri seferin değil tüccarın gideri; küçük partide birim başına
            # şişip getiriyi bozuyordu (D5b3c T2: derin zararların ~%40'ı)
            margin = (realized + getattr(m, "voy_overhead", 0) / max(q, 1e-9)) / max(unit_cost, 1e-9) - 1
            self.voy_log.append((day0, self.day, g, o, d, q, exp_net, unit_cost, realized, lvl, m.loc, margin))
            roi = margin if self.cfg.record_net_overhead else realized / max(unit_cost, 1e-9) - 1
            m.record.append((self.day, roi, unit_cost * q, (realized - unit_cost) * q, max(self.day - day0, 1)))
            m.record = [x for x in m.record if self.day - x[0] <= max(self.cfg.rep_window, 365)]
            m.voy = None
            if self.cfg.exit_rule == "voyage" and self.cfg.free_entry and not m.is_player:
                self._exit_decision(m)
            if self.cfg.network and m.loc not in m.network:       # E2: tekrar eden ticaret muhabir kazandırır
                m.net_count[m.loc] = m.net_count.get(m.loc, 0) + 1
                if m.net_count[m.loc] >= self.cfg.net_learn_n and len(m.network) < self.cfg.net_cap:
                    m.network.add(m.loc)
        if m.debt is not None:
            self._repay(m)
        if m.colleg is None:
            return
        c, port, k0, _ = m.colleg
        rho = m.cash / max(k0, 1.0) - 1
        pay = c * (1 + rho * self.cfg.colleg_share) if rho > 0 else c * (1 + rho)
        ret = pay / max(c, 1.0) - 1                  # yatırımcının gerçekleşen sefer getirisi
        self.colleg_track = ret if self.colleg_track is None else 0.9 * self.colleg_track + 0.1 * ret
        dur = max(self.day - m.colleg[3], 1)
        self.colleg_contracts.append((self.day, m.level, ret, c, dur, getattr(m, "colleg_score", None)))
        # Yatırımcının yıllık getirisi = son bir yılın colleganza kârı / (sermaye × gün) × 365. Sözleşme başına
        # getiriyi kendi süresiyle yıllıklaştırmak kısa sözleşmelerde patlıyordu (D5b3b duman: %541).
        recent = [x for x in self.colleg_contracts if self.day - x[0] <= 365]
        cap_days = sum(x[3] * x[4] for x in recent)
        self.colleg_ann = sum(x[2] * x[3] for x in recent) / cap_days * 365 if cap_days > 0 and len(recent) >= 5 else None
        pay = int(max(0.0, min(pay, m.cash)))
        m.cash -= pay
        self.pool[port] += pay
        self.ledger.money_sink("colleganza_out", pay)
        self.colleg_out += pay
        m.colleg = None

    def _expect(self, m: M5, p: str, g: str, travel: float) -> float:
        """C4 beklentisi: yaşla genişleyen log-normal dağılım + olağan fiyata (medyan) dönüş."""
        if m.informed:
            return self._best_bid(p, g)
        price, oday = m.obs[(p, g)]
        h = (self.day - oday) + travel
        sigma = math.sqrt(0.03 ** 2 + self.cfg.vol_annual ** 2 / 365.0 * h) * m.overconf
        normal = float(np.median(m.hist[(p, g)][-20:]))
        log_med = math.log(normal) + (math.log(price) - math.log(normal)) * math.exp(-h / self.cfg.revert_days)
        return math.exp(log_med - (self._risk(m) - 0.5) * sigma)

    def _expect_fwd(self, m: M5, p: str, g: str, travel: float) -> float:
        """D5b2 (B): beklenti = w × temel projeksiyon + (1−w) × fiyat geçmişi (C4) (Brock & Hommes 1998).
        Temel projeksiyon: olağan fiyat × hasat haberinin ima ettiği çarpan (King-Davenant) × varış günündeki
        mevsim etkisi. Hasat haberi limanda açık, uzağa gemiyle ve söylentiyle gider."""
        c4 = self._expect(m, p, g, travel)
        if not self.cfg.forward or not self.cfg.forward_fund or m.w_fund <= 0 or m.informed:
            return c4
        normal = float(np.median(m.hist[(p, g)][-20:]))
        F = normal
        if GOODS5[g].kind == "harvest":
            mk = self.markets[(p, g)]
            hn = m.hnews.get((p, g))
            if hn is not None and self.day - hn[1] < 365:
                F *= min(3.0, max(1 / 3, hn[0] ** (1.0 / mk.cfg.elasticity)))
            dth = (mk._days_to_harvest() - travel) % 365
            F *= 1 + self.cfg.season_carry * ((1 - dth / 365.0) - 0.5)
        price, oday = m.obs[(p, g)]
        h = (self.day - oday) + travel
        sigma = math.sqrt(0.03 ** 2 + self.cfg.vol_annual ** 2 / 365.0 * h) * m.overconf
        F *= math.exp(-(self._risk(m) - 0.5) * sigma)
        return m.w_fund * F + (1 - m.w_fund) * c4

    def _impact(self, depth0: float, crowd: float, q_own: float) -> float:
        """Beklenen kalabalığın (ve B açıksa kendi kargosunun) fiyat etkisi (birim esneklik ⚠️)."""
        own = self.cfg.forward and self.cfg.forward_impact
        return depth0 / (depth0 + crowd + (q_own if own else 0.0))

    def _risk(self, m: M5) -> float:
        """Servete bağlı risk tutumu (DARA; Arrow-Pratt): yoksullaşan tüccar temkinlenir; batma eşiğine
        yaklaşınca safety-first (Roy 1952). Zenginleşen daha az kaçınır."""
        if not m.dara:
            return m.risk_aversion
        w = max(m.net_worth(), 1.0) / m.start_capital
        ra = m.risk_aversion * min(3.0, max(0.5, w ** -0.5))
        if w < 0.4:
            ra += 1.0
        return ra

    def _waiting(self, p: str) -> dict:
        """Limanda satış bekleyen kargo (mal → miktar): limandaki herkes gemileri görür."""
        w = {}
        for x in self.merchants:
            if x.state == "selling" and x.loc == p and x.qty > 0:
                w[x.good] = w.get(x.good, 0.0) + x.qty
        return w

    def _observe(self, m: M5, p: str):
        if self.cfg.forward:                 # limanın hasat haberi limanda herkesçe bilinir
            for (q, g) in self.markets:
                mk = self.markets[(q, g)]
                if q == p and getattr(mk, "harvest_day", None) is not None:
                    m.hnews[(p, g)] = (mk.harvest_ratio, mk.harvest_day)
        if self.cfg.visibility:              # G: kapan'daki alımlar açık; hedefleri bilinmez
            since = self.day - self.cfg.load_memory_days
            m.seen_buys = [b for b in m.seen_buys if b[4] >= since] + \
                [b for b in self.port_buys.get(p, []) if b[0] != m.id and b[4] == self.day - 1]
        if self.cfg.rival_info:
            wt = self._waiting_cache[p]
            for (q, g) in self.markets:
                if q == p:
                    m.harbor[(p, g)] = (wt.get(g, 0.0), self.day)
        for (q, g) in self.markets:
            if q == p:
                b = self._best_bid(p, g)
                m.obs[(p, g)] = (b, self.day)
                h = m.hist[(p, g)]
                h.append(b)
                if len(h) > 40:
                    del h[0]

    # --- tüccar adımları ----------------------------------------------------
    def _committed(self) -> dict:
        """(hedef, mal) → yolda ya da hedefte satış bekleyen toplam kargo (basitleştirme: anlık bilinir)."""
        c = {}
        for x in self.merchants:
            if x.qty > 0 and x.state in ("sailing", "selling"):
                key = (x.dest if x.state == "sailing" else x.loc, x.good)
                c[key] = c.get(key, 0.0) + x.qty
        return c

    def _options(self, m: M5, origin: str, asks: dict | None = None):
        """(günlük kâr, mal, hedef, azami alış fiyatı, azami miktar) seçenekleri."""
        cfg = self.cfg
        opts = []
        committed = self._committed_cache if cfg.share_depth else {}
        for (p, g) in self.markets:
            if p != origin:
                continue
            ask = asks[g] if asks else self._best_ask(origin, g)
            spec = GOODS5[g]
            for d in self.port_list:
                if d == origin or (d, g) not in self.markets:
                    continue
                days = self._voyage(origin, d)
                e0 = self._expect_fwd(m, d, g, days)
                depth0 = cfg.depth_days * self.demand_L[d][g]
                crowd, bonus = self._rivals(m, d, g, depth0)
                depth = depth0 - committed.get((d, g), 0.0) - crowd
                q_max = min(m.capacity / spec.bulk, m.cash / ask, depth)
                if q_max < 1:
                    continue
                # B açıksa kendi kargosunun etkisi: en iyi miktar küçük bir ızgarada seçilir
                best = None
                for f in ((0.25, 0.5, 0.75, 1.0) if cfg.forward and cfg.forward_impact else (1.0,)):
                    q = q_max * f
                    e = e0 * self._impact(depth0, crowd, q)
                    net = e * (1 - CUSTOMS) * (1 - self._p_loss(days, origin, d)) - FREIGHT_PER_BULK_DAY * spec.bulk * days
                    if cfg.network:          # E2: ağ dışı limanda alışta ve satışta komisyon
                        net = net * (1 - self._comm(m, d)) / (1 + self._comm(m, origin))
                    margin = net / ask - 1 + bonus
                    if margin > cfg.hurdle:
                        score = margin * q * ask / (days + 3)
                        if best is None or score > best[0]:
                            best = (score, g, d, net / (1 + cfg.hurdle), q)
                if best is not None:
                    opts.append(best)
        opts.sort(key=lambda o: -o[0])
        return opts

    def _rivals(self, m: M5, d: str, g: str, depth0: float):
        """Duyulan rakip yüklemeleri (K-014). Düzey 0: yok sayar. Düzey 1: hepsi pazara inecek (kalabalık).
        Düzey 2: düzey 1'lerin kaçınacağını öngörür, yarısını sayar. Taklit: rakibin yüklemesini
        "onlar bir şey biliyor" diye çekicilik sinyali olarak da okur (Banerjee 1992; BHW 1992)."""
        if not self.cfg.rival_info or (not m.known_loads and not (m.house and self.cfg.house_internal)):
            return 0.0, 0.0
        since = self.day - self.cfg.load_memory_days
        mates = set()
        own = 0.0
        if m.house and self.cfg.house_internal:   # E3: evin kendi kargosu kesin bilinir ve tam sayılır; taklit çekimi yok
            for x in self.merchants:
                if x.house == m.house and x is not m:
                    mates.add(x.id)
                    if x.qty > 0 and x.good == g and ((x.state == "sailing" and x.dest == d)
                                                      or (x.state == "selling" and x.loc == d)):
                        own += x.qty
        known = sum(v[3] for v in m.known_loads.values() if v[1] == d and v[2] == g and v[4] >= since
                    and not (len(v) > 5 and v[5] in mates))
        if self.cfg.visibility and m.seen_buys:
            # G: gördüğü ama hedefini duymadığı alımlar, olası hedeflere pazar büyüklüğüyle dağıtılır
            known_ids = {v[5] for v in m.known_loads.values() if len(v) > 5}
            for mid, o, gg, q, day in m.seen_buys:
                if gg != g or mid in known_ids or o == d:
                    continue
                dests = [x for x in self.port_list if x != o and (x, g) in self.markets]
                tot = sum(self.demand_L[x][g] for x in dests) or 1.0
                known += q * self.demand_L[d][g] / tot
        q_h, day_h = m.harbor.get((d, g), (0.0, -1))
        if day_h >= since:
            known += q_h                       # limanda satılmayı bekleyen kargo (gözlenen ya da duyulan)
        if known <= 0:
            return own, 0.0
        if m.level == 0 and not self.cfg.l0_counts_rivals:
            crowd = 0.0
        else:
            crowd = 0.5 * known if m.level >= 2 else known
        bonus = m.imitation * 0.10 * min(1.0, known / depth0)
        return crowd + own, bonus

    def _merchant_buy(self, m: M5):
        if m.plan is None:
            opts = self._options(m, m.loc)
            if not opts:
                m.wait += 1
                if m.wait >= 7:
                    self._reposition(m)
                return
            _, g, d, max_bid, q_max = opts[0]
            m.plan = (g, d, max_bid, q_max)
        g, d, max_bid, q_max = m.plan
        spec = GOODS5[g]
        market = self.markets[(m.loc, g)]
        room = min(m.capacity / spec.bulk, q_max) - m.qty
        # 1) Doğrudan üreticiden (köylü / dışsal arz havuzu): dükkâncı teklifini biraz aşan fiyatla
        rural = market.rural
        if self.cfg.direct_farm_buying and rural.stock > 0 and room > 0:
            farm_price = max(s.bid() for s in market.shops) * 1.02
            if farm_price <= max_bid:
                key = (m.loc, g)
                offered = rural.offered_at(farm_price, market._days_to_harvest()) - self.farm_sold.get(key, 0.0)
                q = min(room, m.cash / farm_price, max(0.0, offered), rural.stock)
                if q > 0:
                    pay = int(round(q * farm_price))
                    rural.stock -= q
                    self.ledger.money_sink("rural_farmers", pay)
                    m.cash -= pay
                    m.qty += q
                    m.cost_basis += pay
                    m.good = g
                    room -= q
                    self.farm_sold[key] = self.farm_sold.get(key, 0.0) + q
        # 1b) Doğrudan üretici havuzundan (atölye / lonca deposu)
        pool = self.pools.get((m.loc, g))
        if self.cfg.direct_farm_buying and pool is not None and pool.output > 0 and room > 0:
            price = max(s.bid() for s in market.shops) * 1.02
            if price <= max_bid:
                q = min(room, m.cash / price, pool.output)
                if q > 0:
                    pay = int(round(q * price))
                    pool.output -= q
                    pool.cash += pay
                    m.cash -= pay
                    m.qty += q
                    m.cost_basis += pay
                    m.good = g
                    room -= q
        # 2) Dükkâncılardan
        for s in market._sorted_shops(lambda s: s.ask()):
            ask = s.ask()
            if ask > max_bid or room <= 0:
                break
            want = min(room, m.cash / ask)
            s.requests_today += want
            avail = max(0.0, s.stock - 0.5 * s.desired_stock())
            q = min(want, avail)
            if q <= 0:
                continue
            pay = int(round(q * ask))
            s.cash += pay
            s.stock -= q
            m.cash -= pay
            m.qty += q
            m.cost_basis += pay
            m.good = g
            room -= q
        m.wait += 1
        full = m.qty >= 0.9 * min(m.capacity / spec.bulk, q_max)
        if m.qty > 0 and (full or m.wait >= 5 or m.cash < 1000):
            self._depart(m, d)
        elif m.qty <= 0 and m.wait >= 7:
            m.plan = None
            self._reposition(m)

    def _reposition(self, m: M5):
        best, best_port = 0.0, None
        for q in self.port_list:
            if q == m.loc:
                continue
            asks = {g: m.obs[(q, g)][0] / (1 - 0.05) for (p, g) in self.markets if p == q}  # bid'den kaba ask tahmini
            opts = self._options(m, q, asks)
            if opts:
                score = opts[0][0] * 0.5 / (1 + self._voyage(m.loc, q) / 10)
                if score > best:
                    best, best_port = score, q
        if best_port:
            self._depart(m, best_port)
        m.wait = 0

    def _depart(self, m: M5, dest: str):
        r = self.rng.get("voyage")
        base = self._voyage(m.loc, dest)
        days = max(2, int(round(base * float(np.exp(r.normal(0, 0.25))))))
        lost = bool(r.random() < self._p_loss(days, m.loc, dest, actual=True))
        if m.qty > 0 and self._comm(m, m.loc) > 0 and getattr(m, "voy", None) is None:
            comm = int(min(round(m.cost_basis * self._comm(m, m.loc)), m.cash))   # E2: ağ dışında alış komisyonu
            m.cash -= comm
            m.cost_basis += comm
            self.ledger.money_sink("commission", comm)
            self.commissions += comm
        if m.qty > 0:
            freight = min(int(round(FREIGHT_PER_BULK_DAY * GOODS5[m.good].bulk * m.qty * days)), m.cash)
            m.cash -= freight
            m.cost_basis += freight
            self.ledger.money_sink("freight", freight)
            key = (self.date.year, m.loc, dest, m.good)
            self.flows[key] = self.flows.get(key, 0.0) + m.qty
            if hasattr(self, "_committed_cache"):
                ck = (dest, m.good)
                self._committed_cache[ck] = self._committed_cache.get(ck, 0.0) + m.qty
            if self.cfg.hazard_model == "leg":
                cause = None
                if lost:                          # neden: bacakların doğal ve korsan payıyla orantılı
                    parts = self._leg_hazards(m.loc, dest, actual=True)[1]
                    nat, cor = sum(x for x, _ in parts), sum(y for _, y in parts)
                    cause = "corsair" if self.rng.get("loss_cause").random() < cor / (nat + cor) else "wreck"
                self.dep_log.append((self.day, m.loc, dest, lost, cause, self.date.month))
            if lost:
                self.ledger.goods_sink(m.good, "shipwreck", m.qty)
                if self.cfg.ship_market and not m.is_player:   # Ö3: gemi varlık olarak gider
                    m.ship = None
                    self.ships_lost += 1
                elif self.cfg.ship_loss > 0:      # gemi de gider: yenileme bedeli (Ö3'e kadar vekil)
                    sl = int(min(self.cfg.ship_loss, m.cash))
                    m.cash -= sl
                    self.ledger.money_sink("ship_loss", sl)
                if m.debt is not None:
                    m.debt_lost = True
                m.qty, m.cost_basis = 0.0, 0.0
        if m.qty > 0:
            self.departures.append((self.day, m.loc, dest, m.good, m.qty, m.level))
            if self.cfg.rival_info:          # yükleme limanda görülür: söylenti olarak yayılır
                self._load_id += 1
                item = (m.loc, dest, m.good, m.qty, self.day, m.id)
                self.loads[m.loc][self._load_id] = item
                m.known_loads[self._load_id] = item
        # Gemi kalkış limanının fiyatlarını ve bildiği yükleme söylentilerini haber olarak taşır
        since = self.day - self.cfg.load_memory_days
        m.known_loads = {k: v for k, v in m.known_loads.items() if v[4] >= since}
        m.packet = (m.loc, self.day, {g: self._best_bid(p, g) for (p, g) in self.markets if p == m.loc})
        if self.cfg.forward:
            m.packet_hnews = dict(m.hnews)
        if self.cfg.rival_info:
            m.packet_harbor = dict(m.harbor)
        m.carried = dict(m.known_loads)
        if m.qty > 0 and m.plan is not None and getattr(m, "voy", None) is None:
            # Teşhis (D5b3): kalkışta beklenen birim net gelir ve o anki nakit; sefer bitince gerçekleşenle kıyas
            m.voy = (self.day, m.good, m.qty, m.plan[2] * (1 + self.cfg.hurdle), m.cost_basis / m.qty, m.cash,
                     m.loc, dest, m.level)
            m.voy_overhead = 0
        m.state, m.dest, m.arrive_day = "sailing", dest, self.day + days
        m.plan, m.wait = None, 0

    def _arrivals(self):
        for m in self.merchants:
            if m.state == "sailing" and m.arrive_day == self.day:
                origin, oday, prices = m.packet
                for k, v in getattr(m, "carried", {}).items():
                    self.loads[m.dest].setdefault(k, v)
                if self.cfg.forward:
                    self.hnews_board[m.dest].append((self._news_id, getattr(m, "packet_hnews", {})))
                if self.cfg.rival_info:     # liman haberleri: gemi, bildiği limanlardaki bekleyen kargoyu anlatır
                    self.harbor_news[m.dest].append((self._news_id, getattr(m, "packet_harbor", {})))
                self._news_id += 1
                self.news[m.dest].append((self._news_id, origin, oday, prices))
                m.heard.add(self._news_id)
                if hasattr(self, "current"):         # D5b3: haber limanın price current'ına girer
                    for g, price in prices.items():
                        if oday > self.current[m.dest][(origin, g)][1]:
                            self.current[m.dest][(origin, g)] = (price, oday)
                            h = self.current_hist[m.dest][(origin, g)]
                            h.append(price)
                            if len(h) > 40:
                                del h[0]
                m.loc, m.wait = m.dest, 0
                m.state = "selling" if m.qty > 0 else "buying"
                if m.qty <= 0:
                    self._settle(m)

    def _hear_loads(self):
        r = self.rng.get("load_rumor")
        since = self.day - self.cfg.load_memory_days
        for p in self.port_list:
            self.loads[p] = {k: v for k, v in self.loads[p].items() if v[4] >= since}
            self.harbor_news[p] = self.harbor_news[p][-50:]
        for m in self.merchants:
            if m.state == "sailing":
                continue
            for nid, hb in self.harbor_news[m.loc]:
                if ("h", nid) in m.heard or r.random() >= m.p_hear:
                    continue
                m.heard.add(("h", nid))
                for key, (q, day) in hb.items():
                    if key[0] != m.loc and day > m.harbor.get(key, (0.0, -1))[1]:
                        m.harbor[key] = (q, day)
        for m in self.merchants:
            if m.state == "sailing":
                continue
            for k, v in self.loads[m.loc].items():
                if k not in m.known_loads and r.random() < m.p_hear:
                    m.known_loads[k] = v

    def _hear(self):
        if self.cfg.rival_info:
            self._hear_loads()
        if self.cfg.forward:
            r = self.rng.get("hnews_rumor")
            for p in self.port_list:
                self.hnews_board[p] = self.hnews_board[p][-50:]
            for m in self.merchants:
                if m.state == "sailing":
                    continue
                for nid, hb in self.hnews_board[m.loc]:
                    if ("hn", nid) in m.heard or r.random() >= m.p_hear:
                        continue
                    m.heard.add(("hn", nid))
                    for key, (ratio, day) in hb.items():
                        if day > m.hnews.get(key, (1.0, -1))[1]:
                            m.hnews[key] = (ratio, day)
        r = self.rng.get("rumor")
        for m in self.merchants:
            if m.state == "sailing":
                continue
            for nid, origin, oday, prices in self.news[m.loc]:
                if nid in m.heard or r.random() >= m.p_hear:
                    continue
                m.heard.add(nid)
                for g, price in prices.items():
                    if oday > m.obs[(origin, g)][1]:
                        m.obs[(origin, g)] = (price, oday)
                        h = m.hist[(origin, g)]
                        h.append(price)
                        if len(h) > 40:
                            del h[0]
        for p in self.news:
            self.news[p] = [n for n in self.news[p] if self.day - n[2] < 90]

    def _merchant_sell(self, m: M5):
        market = self.markets[(m.loc, m.good)]
        unit = m.cost_basis / m.qty
        reservation = unit * max(0.2 if m.wait > 60 else 0.5, 1.0 - 0.02 * m.wait)
        for s in market._sorted_shops(lambda s: s.bid(), reverse=True):
            price = s.bid()
            if price < reservation or m.qty <= 0:
                break
            q = min(m.qty, s.buy_room(price))
            if q <= 0:
                continue
            pay = int(round(q * price))
            duty = int(round(pay * CUSTOMS))
            comm = int(round(pay * self._comm(m, m.loc)))      # E2: ağ dışı limanda komisyoncu
            s.cash -= pay
            s.receive(q, pay)
            m.cash += pay - duty - comm
            self.ledger.money_sink("customs", duty)
            if comm:
                self.ledger.money_sink("commission", comm)
                self.commissions += comm
            m.cost_basis -= unit * q
            m.qty -= q
        m.wait += 1
        if m.qty <= 1e-9:
            m.qty, m.cost_basis, m.good = 0.0, 0.0, ""
            m.state, m.wait = "buying", 0
            return
        if m.wait >= self.cfg.reroute_after and m.wait % 5 == 0:
            # Kargoyu başka bir limana götürmek, burada beklemekten iyi mi?
            here = max(s.bid() for s in market.shops)
            best, best_d = here * 1.1, None
            for d in self.port_list:
                if d == m.loc or (d, m.good) not in self.markets:
                    continue
                days = self._voyage(m.loc, d)
                room_d = self.cfg.depth_days * self.demand_L[d][m.good]
                if self.cfg.share_depth:
                    room_d -= self._committed_cache.get((d, m.good), 0.0)
                if m.qty > room_d:
                    continue
                e = self._expect(m, d, m.good, days)
                net = (e * (1 - CUSTOMS) * (1 - self._comm(m, d)) * (1 - self._p_loss(days, m.loc, d))
                       - FREIGHT_PER_BULK_DAY * GOODS5[m.good].bulk * days)
                if net > best:
                    best, best_d = net, d
            if best_d:
                self.reroutes += 1
                self._depart(m, best_d)

    # --- havuzlar ve kent talebi --------------------------------------------
    def _pools_step(self):
        wages = {p: 0.0 for p in self.port_list}
        for (p, g), pool in self.pools.items():
            in_ask = {i: self._best_ask(p, i) for i in pool.recipe.inputs}
            out_m = self.markets[(p, g)]
            out_bid = float(np.mean([s.bid() for s in out_m.shops]))
            unit_cost = pool.unit_cost(in_ask)
            margin = (out_bid - unit_cost) / out_bid
            q = pool.rate()
            for i, a in pool.recipe.inputs.items():
                q = min(q, pool.inputs[i] / a)
            q = max(0.0, min(q, pool.cash / (pool.recipe.labor * WAGE)))
            if q > 0:
                for i, a in pool.recipe.inputs.items():
                    pool.inputs[i] -= q * a
                    self.ledger.goods_sink(i, "production_input", q * a)
                pool.output += q
                self.ledger.goods_source(g, "production", q)
                w = int(round(q * pool.recipe.labor * WAGE))
                pool.cash -= w
                wages[p] += w
                self.ledger.money_sink("wages", w)
            stock_days = pool.output / max(pool.rate(), 1e-9)
            reservation = unit_cost * (1.0 if stock_days < 15 else 0.85 if stock_days < 30 else 0.7)
            pool.reservation = reservation
            for s in ([] if self.cfg.wholesale else out_m._sorted_shops(lambda s: s.bid(), reverse=True)):
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
            for i, a in ([] if self.cfg.wholesale else pool.recipe.inputs.items()):
                need = max(0.0, a * pool.rate() * pool.input_days - pool.inputs[i])
                if need > 0:
                    got, paid = self._buy(self.markets[(p, i)], need, cash=pool.cash * 0.5)
                    pool.inputs[i] += got
                    pool.cash -= paid
            desired = 0.85 + 2.0 * (margin - pool.margin_target) - 0.02 * (stock_days - 10)
            pool.util += pool.util_speed * (min(1.0, max(0.1, desired)) - pool.util)
            pool.util_hist.append(pool.util)
            if self.date.day == 1 and len(pool.util_hist) >= 90:
                u = float(np.mean(pool.util_hist[-90:]))
                if u > 0.92 and margin > pool.margin_target:
                    pool.capacity *= 1.01
                elif u < 0.6:
                    pool.capacity *= 0.99
            excess = pool.cash - 90 * pool.rate() * unit_cost
            if excess > 0:
                d = int(excess * 0.01)
                pool.cash -= d
                self.ledger.money_sink("producer_dividends", d)
            self.log[f"{p}_{g}_prod"].append(q)
        self.wage_yday = wages

    def _buy(self, market: D1Sim, qty: float, cash: float | None = None):
        bought, paid = 0.0, 0
        for s in market._sorted_shops(lambda s: s.ask()):
            price = s.ask()
            req = max(0.0, qty - bought)
            s.requests_today += req
            q = min(req, s.stock)
            if cash is not None:
                q = min(q, max(0.0, (cash - paid) / price))
            if q <= 0:
                continue
            pay = int(round(q * price))
            s.cash += pay
            s.stock -= q
            bought += q
            paid += pay
        return bought, paid

    def _buy_with_docks(self, port: str, g: str, qty: float):
        """Kent alıcıları en ucuzdan başlayarak dükkânlardan ve iskeledeki tüccarlardan alır."""
        market = self.markets[(port, g)]
        if self.cfg.retail_rule == "compete":
            return self._buy_compete(market, qty)
        if not self.cfg.dock_sales:
            return self._buy(market, qty)
        best_shop = min(s.ask() for s in market.shops)
        sellers = [("shop", s, s.ask()) for s in market._sorted_shops(lambda s: s.ask())]
        for m in self.merchants:
            if m.state == "selling" and m.loc == port and m.good == g and m.qty > 0:
                unit = m.cost_basis / m.qty
                floor = unit * max(0.2 if m.wait > 60 else 0.5, 1.0 - 0.02 * m.wait)
                sellers.append(("dock", m, max(floor, best_shop)))
        # Eşit fiyatta dükkân önce: iskele yalnızca dükkânların karşılayamadığı talebi karşılar.
        sellers.sort(key=lambda x: (x[2], 0 if x[0] == "shop" else 1))
        bought, paid = 0.0, 0
        for kind, who, price in sellers:
            req = max(0.0, qty - bought)
            if req <= 0:
                break
            if kind == "shop":
                who.requests_today += req
                q = min(req, who.stock)
            else:
                q = min(req, who.qty)
            if q <= 0:
                continue
            pay = int(round(q * price))
            if kind == "shop":
                who.cash += pay
                who.stock -= q
            else:
                duty = int(round(pay * CUSTOMS))
                unit = who.cost_basis / who.qty
                who.cash += pay - duty
                self.ledger.money_sink("customs", duty)
                who.cost_basis -= unit * q
                who.qty -= q
                if who.qty <= 1e-9:
                    who.qty, who.cost_basis, who.good = 0.0, 0.0, ""
                    who.state, who.wait = "buying", 0
                    self._settle(who)
            bought += q
            paid += pay
        return bought, paid

    def _urban(self, port: str, asks: dict) -> dict:
        """Limanın sınıflı talebi; her mal için (alınan, kıtlık, ort. fiyat)."""
        sig = 2.0
        p = {g: asks[g] for g in asks}
        want = {g: 0.0 for g in ("WHT", "BRL", "OIL", "WIN", "CLC", "CLF", "PEP")}
        for k in self.cls[port]:
            Y = self.income_ref[port][k["name"]]
            if self.cfg.wages_endogenous:
                Y += WAGE_SHARES[k["name"]] * (self.wage_yday[port] - self.normal_wage[port])
            Y = max(Y, 0.0)
            self.log[f"{port}_{k['name']}_income"].append(Y)
            den = sum(k["a"][c] * p[c] ** (1 - sig) for c in ("WHT", "BRL") if c in p)
            P = {"CER": den ** (1 / (1 - sig))}
            for c in CONSUMER_CATS[1:]:
                P[c] = p.get(c, math.inf)
            avail = [c for c in CONSUMER_CATS if P[c] < math.inf]
            S = Y - sum(P[c] * k["gamma"][c] for c in avail)
            if S >= 0:
                E = {c: P[c] * k["gamma"][c] + k["beta"][c] * S for c in avail}
            else:
                f = Y / max(sum(P[c] * k["gamma"][c] for c in avail), 1e-9)
                E = {c: P[c] * k["gamma"][c] * f for c in avail}
            for c in ("WHT", "BRL"):
                if c in p:
                    want[c] += E["CER"] * k["a"][c] * p[c] ** (1 - sig) / den / p[c]
            for c in avail[1:]:
                want[c] += E[c] / P[c]
        res = {}
        for g, q in want.items():
            if (port, g) not in self.markets:
                continue
            b, paid = self._buy_with_docks(port, g, q)
            self.ledger.money_source("urban_consumers", paid)
            self.ledger.goods_sink(g, "consumption", b)
            need = max(self.local_cons[port][g], 1e-9)
            res[g] = (b, max(0.0, need - b) / need, paid / b if b > 0 else float("nan"))
            if g in ("CLC", "CLF", "WHT"):
                self.log[f"{port}_{g}_cons"].append(b)
        for g in ("CLC", "CLF", "WHT"):
            if (port, g) not in self.markets:
                self.log[f"{port}_{g}_cons"].append(0.0)
        return res

    # --- aylık: kâr payı, giriş-çıkış ----------------------------------------
    def _monthly(self):
        cfg = self.cfg
        if cfg.liquidity:
            for (p, g), mk in self.markets.items():
                if GOODS5[g].kind != "harvest" or mk.rural.annual_capacity <= 0:
                    for st in mk.storers:
                        st.roll_continuous()
        for m in self.merchants:
            if (m.state == "buying" and m.qty <= 0 and m.cash > 1.2 * m.start_capital
                    and m.colleg is None and m.debt is None):   # D5b3c düzeltmesi: yatırımcı/alacaklı parası temettü olmaz
                d = int(m.cash - 1.2 * m.start_capital)
                m.cash -= d
                m.divs += d
                self.ledger.money_sink("merchant_dividends", d)
                self._to_pool(m, d)                  # D5b3: temettü yatırımcı sermayesine döner
            fin = m.colleg if m.colleg is not None else m.debt
            if fin is not None and m.state == "buying" and m.qty <= 0 and self.day - fin[3] > 30:
                self._settle(m)                      # D5b3: kullanılmayan sermaye geri döner
            m.marks.append(m.net_worth() + m.divs + self._ship_R(m))
            m.marks = m.marks[-13:]
            m.emarks.append(self._value(m))
            m.emarks = m.emarks[-13:]
        self._update_agg()
        self.pub_log = getattr(self, "pub_log", []) + [(self.day, self.public_agg, self.trailing_median)]
        if cfg.cred_rule == "buhlmann":
            self._update_cred()
        if cfg.hazard_model == "leg":
            self._corsair_step()
        if not cfg.free_entry:
            return

        hm = self._house_members() if cfg.houses else {}

        def trailing(m):
            if len(m.marks) < 13 or self.day - m.born_day < 365:
                return None
            if m.house and m.house in hm:            # E3: ortak kasada geminin tek başına getirisi anlamsız; ev getirisi
                mem = [x for x in hm[m.house] if len(x.marks) >= 13]
                return sum(x.marks[-1] for x in mem) / max(sum(x.marks[0] for x in mem), 1.0) - 1
            return m.marks[-1] / max(m.marks[0], 1.0) - 1

        rets = [t for t in (trailing(m) for m in self.merchants if not m.is_player) if t is not None]
        self._track_known = len(rets) >= 3
        if rets:
            self.trailing_median = float(np.median(rets))
        r = self.rng.get("entry_exit")
        keep = []
        exited = set()
        for m in self.merchants:
            t = trailing(m) if not m.is_player else None
            if (cfg.exit_rule == "monthly" and t is not None and m.state == "buying" and m.qty <= 0
                    and t < cfg.bond_rate and r.random() < cfg.exit_prob):
                if cfg.entry_rule == "opportunity":  # D5b3: önünde fırsat görüyorsa çıkmaz (beklenen getiri)
                    opts = self._options(m, m.loc)
                    nxt = (self._ret_of(opts[0], m.cash, m.loc), self._last_voyage[0]) if opts else (-1.0, 0.0)
                    stay_bar = cfg.bond_rate + self._risk(m) * self._ruin_price()   # K-024: kalmak da batma riskini tartar
                    if opts and self._belief(nxt[0], nxt[1], t) > stay_bar:
                        keep.append(m)
                        continue
                    self._settle(m)
                    if m.broke:                      # borcunu ödeyemedi: _upkeep denklemden çıkarır
                        keep.append(m)
                        continue
                    mates = [x for x in hm.get(m.house, []) if x is not m and x.id not in exited] if m.house else []
                    if mates:                        # E3: gemi elden çıkar, sermaye evde kalır
                        mates[0].cash += m.cash
                        m.cash = 0
                    self._to_pool(m, m.cash)
                self.ledger.money_sink("to_bonds", m.cash)
                exited.add(m.id)
                self.exits += 1
                self._release_ship(m)
                self.gone.append((m, self.day, m.cash))
                continue
            keep.append(m)
        self.merchants = keep
        if cfg.entry_rule == "opportunity":
            self._entry_opportunity(r)
            return
        excess = self.trailing_median - (cfg.bond_rate + cfg.risk_premium)
        n = sum(1 for m in self.merchants if not m.is_player)
        if excess > 0 and n < cfg.max_merchants:
            k = int(r.poisson(self.entry_pool * min(1.0, excess / 0.10)))
            ports = list(self.port_list)
            mrng = self.rng.get("merchants_entry")
            for _ in range(min(k, cfg.max_merchants - n)):
                nm = self._new_merchant(ports[int(mrng.integers(len(ports)))], mrng)
                self.merchants.append(nm)
                self.ledger.money_source("from_bonds", nm.cash)
                self.entries += 1

    def _recapitalize(self):
        """Likidite tuzağı: nakdi ve stoğu tükenmiş dükkâncının yerine yeni sermayeli dükkâncı geçer;
        marjı olumlu ama nakdi bitmiş üretici havuzuna yeni yatırım gelir (aylık kontrol)."""
        for (p, g), mk in self.markets.items():
            for s in mk.shops:
                trapped_cash = s.cash < 0.1 * s.target * s.mid
                if trapped_cash and s.stock < 0.1 * s.target:
                    s.trapped = getattr(s, "trapped", 0) + 1
                else:
                    s.trapped = 0
                if s.trapped >= 1:          # bir ay boyunca tuzakta
                    fresh = int(2 * s.target * GOODS5[g].ref)
                    s.cash += fresh
                    s.mid = GOODS5[g].ref * (1 + 0.0)        # yeni dükkâncı olağan fiyattan başlar
                    s.avg_cost = s.mid * (1 - s.margin / 2)
                    s.trapped = 0
                    self.ledger.money_source("shop_entry", fresh)
                    self.shop_entries += 1
        for (p, g), pool in self.pools.items():
            in_ask = {i: self._best_ask(p, i) for i in pool.recipe.inputs}
            bid = float(np.mean([s.bid() for s in self.markets[(p, g)].shops]))
            margin = (bid - pool.unit_cost(in_ask)) / bid
            daily_cost = pool.rate() * pool.unit_cost(in_ask)
            if pool.cash < 10 * daily_cost and margin > pool.margin_target:
                fresh = int(60 * max(daily_cost, 1.0))
                pool.cash += fresh
                self.ledger.money_source("producer_investment", fresh)
                self.pool_investments += 1

    def _upkeep(self):
        keep = []
        for m in self.merchants:
            if m.broke:                              # D5b3c (K-022): borçtan batan tüccar oyundan silinir
                self.debt_bankruptcies += 1
                self.ruin_days.append(self.day)
                self._release_ship(m)
                self.gone.append((m, self.day, m.cash))
                continue
            c = min(self.cfg.living_cost, m.cash)
            m.cash -= c
            self.ledger.money_sink("merchant_living", c)
            sc = int(min(round(self.cfg.ship_cost_day), m.cash))
            if self.cfg.ship_market and not m.is_player and m.ship is None:
                sc = 0                               # Ö3: gemisi olmayan gemi masrafı ödemez
            if sc > 0:                               # K-024: mürettebat, bakım, amortisman; boşta da ödenir
                m.cash -= sc
                self.ledger.money_sink("ship_costs", sc)
            if getattr(m, "voy", None) is not None:
                m.voy_overhead = getattr(m, "voy_overhead", 0) + c + sc
            if m.house and self.cfg.houses:          # E3: iflas evin toplam servetiyle ölçülür (kasa ortak)
                mem = [x for x in self.merchants if x.house == m.house and not x.broke]
                poor = sum(x.net_worth() for x in mem) < 0.1 * sum(x.start_capital for x in mem)
            else:
                poor = m.cash < 0.1 * m.start_capital
            if (not m.is_player and m.state == "buying" and m.qty <= 0 and poor):
                self.ledger.money_sink("merchant_exit", m.cash)
                self._to_pool(m, m.cash)
                self.ruin_days.append(self.day)
                self.bankruptcies += 1
                self._release_ship(m)
                self.gone.append((m, self.day, m.cash))
                continue
            keep.append(m)
        self.merchants = keep

    # --- D5a: kurumsal toptan pazar (kapan) -----------------------------------
    def _kapan(self, p: str, g: str):
        """Günlük toptan takas: tek fiyat (talep ve arz eğrilerinin kesişimi)."""
        cfg = self.cfg
        mk = self.markets[(p, g)]
        rural = mk.rural
        dth = mk._days_to_harvest()
        buys, sells = [], []                       # (fiyat, miktar, tür, nesne)
        if cfg.retail_rule == "compete":
            for s in mk.shops:
                buys.extend(self._shop_schedule(s))
        else:
            for s in mk.shops:
                b = s.bid()
                q = s.buy_room(b)
                if q > 0:
                    buys.append((b, q, "shop", s))
        for st in mk.storers:
            if st.stock > 0:
                sells.append((st.sell_floor(), st.stock, "storer", st))
            q = st.buy_room(st.bid())
            if q > 0:
                buys.append((st.bid(), q, "storer", st))
        for m in self.merchants:
            if m.loc != p:
                continue
            if m.state == "selling" and m.good == g and m.qty > 0:
                unit = m.cost_basis / m.qty
                res = unit * max(0.2 if m.wait > 60 else 0.5, 1.0 - 0.02 * m.wait)
                if cfg.sell_decision:
                    res = m.reservation
                sells.append((res, m.qty, "msell", m))
            elif m.state == "buying" and m.plan is not None and m.plan[0] == g:
                _, _, max_bid, q_max = m.plan
                q = min(min(m.capacity / GOODS5[g].bulk, q_max) - m.qty, m.cash / max_bid)
                if q > 0:
                    buys.append((max_bid, q, "mbuy", m))
        pool = self.pools.get((p, g))
        if pool is not None and pool.output > 0:
            sells.append((getattr(pool, "reservation", 0.0), pool.output, "pool", pool))
        for (pp, og), pl in self.pools.items():
            if pp == p and g in pl.recipe.inputs:
                a = pl.recipe.inputs[g]
                need = max(0.0, a * pl.rate() * pl.input_days - pl.inputs[g])
                maxp = 2.0 * GOODS5[g].ref
                q = min(need, pl.cash * 0.5 / maxp)
                if q > 0:
                    buys.append((maxp, q, "pinput", pl))
        farm = rural.stock > 0 and rural.annual_capacity > 0
        self.kapan_traded[(p, g)] = False
        if buys:
            self.kapan_bid[(p, g)] = max(pr for pr, _, _, _ in buys)
        if not buys or (not sells and not farm):
            return

        def S(price):
            v = rural.offered_at(price, dth) if farm else 0.0
            return v + sum(q for pr, q, _, _ in sells if pr <= price)

        def D(price):
            return sum(q for pr, q, _, _ in buys if pr >= price)

        lo = min([pr for pr, _, _, _ in sells] + ([rural.floor_price] if farm else []))
        hi = max(pr for pr, _, _, _ in buys)
        if hi < lo:
            self.kapan_quote[(p, g)] = lo          # kimse bu fiyatın altında satmıyor (açık bilgi)
            return
        if D(lo) <= S(lo):
            price = lo
        elif D(hi) >= S(hi):
            price = hi
        else:
            a_, b_ = lo, hi
            for _ in range(40):
                mid = (a_ + b_) / 2
                if D(mid) > S(mid):
                    a_ = mid
                else:
                    b_ = mid
            price = (a_ + b_) / 2
        dq, sq = D(price), S(price)
        V = min(dq, sq)
        if V <= 1e-9:
            return
        fb = V / dq
        # 1) Alıcı payları (yuvarlama ve nakit kısıtından sonra gerçekten alınan miktar)
        alloc = []
        for pr, q, kind, obj in buys:
            if pr < price:
                continue
            qq = q * fb
            cost = min(int(round(qq * price)), obj.cash)
            if cost <= 0:
                continue
            qq = min(qq, cost / price)
            alloc.append((kind, obj, qq, cost))
        delivered = sum(a[2] for a in alloc)
        if delivered <= 1e-9:
            return
        total_paid = 0
        for kind, obj, qq, cost in alloc:
            obj.cash -= cost
            total_paid += cost
            if kind in ("shop", "storer"):
                obj.receive(qq, cost)
            elif kind == "mbuy":
                obj.qty += qq
                obj.cost_basis += cost
                obj.good = g
                if cfg.visibility:
                    self.port_buys[p].append((obj.id, p, g, qq, self.day))
            elif kind == "pinput":
                obj.inputs[g] += qq
        # 2) Satıcı payları: teslim edilen miktar kadar, fiyat sırasıyla orantılı
        shares = []
        if farm:
            shares.append(["farm", rural.offered_at(price, dth), None])
        for pr, q, kind, obj in sells:
            if pr <= price:
                shares.append([kind, q, obj])
        avail = sum(x[1] for x in shares)
        fs = delivered / avail
        for x in shares:
            x[1] *= fs
        if farm and shares[0][1] > rural.stock:             # köylü stoğu yetmezse fark diğerlerine
            short = shares[0][1] - rural.stock
            shares[0][1] = rural.stock
            others = sum(x[1] for x in shares[1:]) or 1.0
            for x in shares[1:]:
                x[1] += short * x[1] / others
        qsum = sum(x[1] for x in shares) or 1.0
        paid_out = 0
        for idx, (kind, qq, obj) in enumerate(shares):
            proceeds = total_paid - paid_out if idx == len(shares) - 1 else int(total_paid * qq / qsum)
            paid_out += proceeds
            fee = int(round(proceeds * cfg.kapan_fee))
            self.ledger.money_sink("kapan_fee", fee)
            net = proceeds - fee
            if kind == "farm":
                rural.stock -= qq
                self.ledger.money_sink("rural_farmers", net)
            elif kind == "storer":
                obj.stock -= qq
                obj.cash += net
            elif kind == "msell":
                duty = int(round(net * CUSTOMS))
                self.ledger.money_sink("customs", duty)
                comm = int(round(net * self._comm(obj, p)))      # E2: ağ dışı limanda komisyoncu
                if comm:
                    self.ledger.money_sink("commission", comm)
                    self.commissions += comm
                unit = obj.cost_basis / obj.qty
                obj.cash += net - duty - comm
                obj.cost_basis -= unit * qq
                obj.qty -= qq
            elif kind == "pool":
                obj.output -= qq
                obj.cash += net
        V = delivered
        self.kapan_price[(p, g)] = price
        self.kapan_quote[(p, g)] = price
        self.kapan_traded[(p, g)] = True
        self.kapan_volume[(p, g)] = self.kapan_volume.get((p, g), 0.0) + V
        self.kapan_today[(p, g)] = V
        # Dükkâncı yerine koyma maliyeti = açık toptan fiyat, iki yönde de (İ9 simetri):
        # stok azken toptan pahalıysa yükselt, stok yeterliyken toptan ucuzsa indir.
        if cfg.retail_rule == "pull":
            for s in mk.shops:
                ratio = s.signal_ratio()
                if (ratio < 1.0 and s.bid() < price) or (ratio >= 1.0 and s.bid() > price):
                    s.mid += 0.1 * (s.mid_for_bid(price) - s.mid)

    # --- D5a2: rekabetçi perakende (K-016) ------------------------------------
    def _set_markups(self, mk: D1Sim):
        """Logit rekabette dükkânın karşılaştığı esneklik ε_i = β(1−s_i) + ε_pazar·s_i;
        Lerner kuralı μ_i = 1/(ε_i − 1) (Anderson, de Palma & Thisse 1992)."""
        cfg = self.cfg
        for s in mk.shops:
            eps = cfg.retail_beta * (1 - s.share) + cfg.market_elasticity * s.share
            mu = 1.0 / (eps - 1.0) if eps > 1.0 else cfg.markup_max
            s.markup = min(cfg.markup_max, max(cfg.markup_min, mu))

    def _retail_prices(self, p: str, g: str):
        mk = self.markets[(p, g)]
        q = self.kapan_quote.get((p, g))
        if q is not None:
            for s in mk.shops:
                s.cost_ref += (q - s.cost_ref) / self.cfg.retail_cost_days
                s.mid = s.cost_ref
        self._set_markups(mk)

    LEVELS = (0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5)

    def _shop_schedule(self, s):
        """Türetilmiş talep (derived demand): dükkân, müşterilerinin son haftalarda hangi fiyatta ne kadar
        istediğini bilir (request_rate, req_price). Toptan fiyat w'de hedef stok = 30 günlük satış × (w/ref)^−ε;
        ucuzsa en çok room_mult katına kadar stoklar. Gözlediği fiyat aralığının (ref) %50 üstünden
        fazlasını önermez: deneyimlemediği fiyatta müşterisinin alacağını bilmez. Kapan'a kademeli emir."""
        eps = self.cfg.market_elasticity
        base = s.target_cover_days * s.request_rate
        ref = s.req_price / (1 + s.markup)               # satış hızının gözlendiği maliyet düzeyi
        gaps = [max(0.0, min(s.room_mult * base, base * m ** (-eps)) - s.stock) for m in self.LEVELS]
        out = []
        for k, m in enumerate(self.LEVELS):
            q = gaps[k] - (gaps[k + 1] if k + 1 < len(gaps) else 0.0)
            if q > 1e-9:
                out.append((ref * m, q, "shop", s))
        if self.cfg.budget_bids:
            # Ödeyemeyeceği emri veremez (D5b3: nakitsiz dükkânın dev emri kapan'ı 5 yıl dondurdu).
            # En yüksek kademeden aşağı: kalan nakit ancak o fiyattan alınabilecek miktarı karşılar.
            left, capped = float(s.cash), []
            for pr, q, kind, obj in sorted(out, key=lambda x: -x[0]):
                q = min(q, left / max(pr, 1e-9))
                if q > 1e-9:
                    capped.append((pr, q, kind, obj))
                    left -= q * pr
            out = capped
        return out

    def _buy_compete(self, market: D1Sim, qty: float):
        """Müşteriler alışık oldukları dükkâna gider (pay); orada mal yoksa en ucuzdan aramaya başlar."""
        bought, paid = 0.0, 0
        unmet = 0.0
        for s in market.shops:
            req = qty * s.share
            s.requests_today += req
            q = min(req, s.stock)
            s.stocked_out = q < req - 1e-9
            s.unmet_frac = (req - q) / req if req > 0 else 0.0
            unmet += req - q
            if q > 0:
                pay = int(round(q * s.ask()))
                s.op_profit += pay - q * s.cost_ref
                s.cash += pay
                s.stock -= q
                bought += q
                paid += pay
        for s in market._sorted_shops(lambda s: s.ask()):
            if unmet <= 1e-9:
                break
            s.requests_today += unmet
            q = min(unmet, s.stock)
            if q <= 0:
                continue
            pay = int(round(q * s.ask()))
            s.op_profit += pay - q * s.cost_ref
            s.cash += pay
            s.stock -= q
            unmet -= q
            bought += q
            paid += pay
        return bought, paid

    def _update_shares(self, mk: D1Sim):
        """Payın hedefi: mal bulunan dükkânlar arasında logit (p_i^−β); atalet ile yaklaşılır."""
        cfg = self.cfg
        ok = [s for s in mk.shops if not getattr(s, "stocked_out", False)]
        if not ok:
            return
        pmin = min(s.ask() for s in ok)
        w = {id(s): (pmin / s.ask()) ** cfg.retail_beta for s in ok}
        tot = sum(w.values())
        for s in mk.shops:
            target = w.get(id(s), 0.0) / tot
            s.share += (target - s.share) / cfg.retail_inertia_days
            if not getattr(s, "stocked_out", False):      # müşterilerin gerçekten ödediği en yüksek fiyat (yavaşça unutulur)
                s.peak_paid = max(getattr(s, "peak_paid", 0.0) * (1 - 1 / 365), s.ask())
            if cfg.price_discovery and getattr(s, "stocked_out", False):
                # Tâtonnement: müşterileri eli boş dönen dükkâncı, bu fiyatta talebin arzı aştığını öğrenir.
                # Müşterilerinin son bir yılda ödediğini gördüğü en yüksek fiyatın üstüne çıkmaz.
                s.req_price = min(s.req_price * (1 + s.max_daily_move * s.unmet_frac),
                                  max(s.req_price, getattr(s, "peak_paid", s.req_price)))
            else:
                s.req_price += (s.ask() - s.req_price) / s.request_memory_days
        z = sum(s.share for s in mk.shops)
        for s in mk.shops:
            s.share /= z

    def _retail_entry_exit(self):
        """Aylık: perakende işletme getirisi senet + risk primini aşarsa yeni dükkân açılır (D3b mekanizması);
        senedin altında kalan dükkân kapanır. İşletme kârı = satış − yerine koyma maliyeti − geçim − kira
        (stok değer artışı sayılmaz: fiyat şişince sahte kâr görünmesin)."""
        cfg = self.cfg
        r = self.rng.get("shop_entry_exit")
        for (p, g), mk in self.markets.items():
            rets = []
            for s in mk.shops:
                s.marks = (getattr(s, "marks", []) + [s.op_profit])[-12:]
                s.op_profit = 0.0
                if len(s.marks) == 12:              # bir yıllık işletme kârı (mevsimsel boşluklar ortalanır)
                    capital = max(s.cash + s.stock * s.cost_ref, 1.0)
                    rets.append((s, sum(s.marks) / capital))
            if cfg.budget_bids:
                self._close_broke_shops(p, g, mk)
            if not rets:
                continue
            rets = [(s, x) for s, x in rets if s in mk.shops]
            if not rets:
                continue
            med = float(np.median([x for _, x in rets]))
            n = len(mk.shops)
            for s, ret in sorted(rets, key=lambda x: x[1]):
                if n > 1 and ret < cfg.bond_rate and r.random() < cfg.exit_prob:
                    self.ledger.money_sink("shop_exit", s.cash)
                    self.ledger.goods_sink(g, "shop_exit", s.stock)
                    mk.shops.remove(s)
                    self.shop_exits += 1
                    n -= 1
            z = sum(s.share for s in mk.shops)
            for s in mk.shops:
                s.share /= z
            excess = med - (cfg.bond_rate + cfg.risk_premium)
            if excess > 0 and n < cfg.max_shops and r.random() < min(1.0, excess / 0.10):
                t = mk.shops[0]
                # Yeni dükkânın henüz müşterisi yok: ilk stoğunu, ilk ay kazanmayı umduğu pay kadar alır
                # (yerleşik dükkânlar kadar değil; yoksa her giriş kente yeni talep eklenmiş gibi stok toplar).
                rr = float(np.mean([s.request_rate for s in mk.shops])) / (n + 1)
                cash = int(2 * t.target_cover_days * rr * (n + 1) * t.cost_ref) + 1
                ns = dataclasses.replace(t, id=f"sk{self.shop_entries}e", cash=cash, stock=0.0, share=0.0,
                                         request_rate=rr, requests_today=0.0, withdrawn=0.0, op_profit=0.0,
                                         req_price=float(np.mean([s.req_price for s in mk.shops])),
                                         avg_cost=t.cost_ref)
                ns.marks, ns.stocked_out = [], False
                mk.shops.append(ns)
                self.ledger.money_source("shop_entry", cash)
                self.shop_entries += 1

    def _close_broke_shops(self, p, g, mk):
        """D5b3: nakdi bir günlük satışını almaya, stoğu da bir birime yetmeyen dükkân bir ay böyle kalırsa
        kapanır (tek dükkân olsa da). Hiç dükkân kalmazsa yerine pazarın görünen fiyatıyla yenisi açılır."""
        quote = self.kapan_quote.get((p, g), GOODS5[g].ref)
        template = mk.shops[0] if mk.shops else None
        for s in list(mk.shops):
            day_need = max(s.share, 0.05) * self.demand_L[p][g] * quote
            broke = s.stock < 1.0 and s.cash < day_need
            s.broke_months = getattr(s, "broke_months", 0) + 1 if broke else 0
            if s.broke_months >= 1:
                self.ledger.money_sink("shop_exit", s.cash)
                self.ledger.goods_sink(g, "shop_exit", s.stock)
                mk.shops.remove(s)
                self.shop_exits += 1
        if not mk.shops and template is not None:
            cash = int(2 * template.target_cover_days * self.demand_L[p][g] * quote) + 1
            ns = dataclasses.replace(template, id=f"sk{self.shop_entries}r", cash=cash, stock=0.0, share=1.0,
                                     request_rate=self.demand_L[p][g], requests_today=0.0, withdrawn=0.0,
                                     op_profit=0.0, req_price=quote, cost_ref=quote, avg_cost=quote)
            ns.marks, ns.stocked_out, ns.broke_months = [], False, 0
            mk.shops.append(ns)
            self.ledger.money_source("shop_entry", cash)
            self.shop_entries += 1
        z = sum(x.share for x in mk.shops) or 1.0
        for x in mk.shops:
            x.share /= z

    def _sell_plan(self, m: M5):
        """D5b2 (S): satıcının günlük kararı (optimal stopping; McCall 1970'in satıcı tarafı).
        Burada kalmanın değeri = beklenen fiyat (kalabalık ve kendi kargosunun etkisiyle) − bekleme maliyeti ×
        satış süresi. Bekleme maliyeti = (kargonun değeri + gemiye bağlı sermaye) × (senet + risk primi).
        Başka limanın değeri = oradaki beklenen fiyat − navlun − yol + satış süresi boyunca bekleme maliyeti.
        Başka liman açıkça iyiyse rota değiştirir; değilse kapan'a "kalmanın değeri" kadar asgari fiyatla girer.
        Stokçu (L) ya da dükkânlar bu fiyatın üstünde teklif verirse satar: fırsat maliyeti zararına satışı doğurur."""
        cfg, g = self.cfg, m.good
        r_d = (cfg.bond_rate + cfg.risk_premium) / 365.0
        here = m.loc
        e_here = self._expect_fwd(m, here, g, 0)
        value = e_here * m.qty
        hold = (value + m.start_capital) * r_d / m.qty            # birim başına günlük bekleme maliyeti
        waiting = self._waiting_cache.get(here, {}).get(g, 0.0) if hasattr(self, "_waiting_cache") else 0.0
        rate = self.demand_L[here][g]
        if cfg.visibility:
            rate = max(self.kapan_today.get((here, g), 0.0), 0.1 * rate)   # G: kapan'da gerçekten satılan hacim
        depth0 = cfg.depth_days * self.demand_L[here][g]
        T_here = waiting / max(rate, 1e-9)
        p_here = e_here * self._impact(depth0, max(0.0, waiting - m.qty), m.qty if cfg.forward else 0.0)
        v_stay = p_here * (1 - CUSTOMS) * (1 - self._comm(m, here)) - hold * T_here
        best, best_d = v_stay * 1.05, None
        for d in self.port_list:
            if d == here or (d, g) not in self.markets:
                continue
            days = self._voyage(here, d)
            d0 = cfg.depth_days * self.demand_L[d][g]
            crowd, _ = self._rivals(m, d, g, d0)
            e = self._expect_fwd(m, d, g, days) * self._impact(d0, crowd, m.qty)
            T_d = days + (crowd + m.qty) / max(self.demand_L[d][g], 1e-9) / 2
            v = (e * (1 - CUSTOMS) * (1 - self._comm(m, d)) * (1 - self._p_loss(days, here, d))
                 - FREIGHT_PER_BULK_DAY * GOODS5[g].bulk * days - hold * T_d)
            if v > best:
                best, best_d = v, d
        if best_d is not None and m.wait >= 1:
            self.reroutes += 1
            self._depart(m, best_d)
            return
        m.reservation = max(0.0, v_stay / ((1 - CUSTOMS) * (1 - self._comm(m, here))))

    def _plan_merchant(self, m: M5):
        if m.plan is not None:
            return
        if m.broke:
            return
        if self.cfg.ship_market and m.ship is None and not m.is_player:
            return                                   # Ö3: gemisiz tüccar ticaret yapamaz
        opts = self._options(m, m.loc)
        verified = self.cfg.colleganza and self.cfg.colleg_mode == "verified"
        if opts and (self.cfg.debt or verified) and not m.is_player and m.colleg is None and m.debt is None:
            opts = self._finance(m, opts)
        elif opts and self.cfg.colleganza and not verified and not m.is_player and m.colleg is None:
            if self.cfg.reputation == "none":
                opts = self._colleganza(m, opts)
            else:
                self.colleg_requests.append(m)       # D5b3b: günün talepleri itibara göre sıralanır
        if opts:
            _, g, d, max_bid, q_max = opts[0]
            m.plan = (g, d, max_bid, q_max)

    def _after_kapan(self, m: M5):
        if m.state == "selling":
            if m.qty <= max(1e-9, self.cfg.dust_lot):
                if m.qty > 0:                    # orantılı paylaşımda kalan kırıntı: fire (Zeno artifact'ı, D5b2)
                    self.ledger.goods_sink(m.good, "lot_dust", m.qty)
                m.qty, m.cost_basis, m.good = 0.0, 0.0, ""
                m.state, m.wait = "buying", 0
                self._settle(m)
                return
            m.wait += 1
            if not self.cfg.sell_decision and m.wait >= self.cfg.reroute_after and m.wait % 5 == 0:
                here = self._best_bid(m.loc, m.good)
                best, best_d = here * 1.1, None
                for d in self.port_list:
                    if d == m.loc or (d, m.good) not in self.markets:
                        continue
                    days = self._voyage(m.loc, d)
                    depth0 = self.cfg.depth_days * self.demand_L[d][m.good]
                    if m.qty > depth0:
                        continue
                    e = self._expect(m, d, m.good, days)
                    crowd, _ = self._rivals(m, d, m.good, depth0)     # D5b: rota değiştirirken de rakipler
                    e *= depth0 / (depth0 + crowd)
                    net = (e * (1 - CUSTOMS) * (1 - self._comm(m, d)) * (1 - self._p_loss(days, m.loc, d))
                           - FREIGHT_PER_BULK_DAY * GOODS5[m.good].bulk * days)
                    if net > best:
                        best, best_d = net, d
                if best_d:
                    self.reroutes += 1
                    self._depart(m, best_d)
            return
        if m.state != "buying":
            return
        m.wait += 1
        if m.plan is None:
            if m.wait >= 7:
                self._reposition(m)
            return
        g, d, _, q_max = m.plan
        target = min(m.capacity / GOODS5[g].bulk, q_max)
        if m.qty > 0 and (m.qty >= 0.9 * target or m.wait >= 5 or m.cash < 1000):
            self._depart(m, d)
        elif m.qty <= 0 and m.wait >= 7:
            m.plan = None
            self._reposition(m)

    def _step_wholesale(self):
        self.farm_sold = {}
        if self.cfg.visibility:
            for p in self.port_list:
                self.port_buys[p] = [b for b in self.port_buys[p] if b[4] >= self.day - 1]
        self._arrivals()
        if self.cfg.entry_rule == "opportunity":
            self._activate_pending()
            self._update_current()
        if self.cfg.rival_info:
            self._waiting_cache = {p: self._waiting(p) for p in self.port_list}
        for m in self.merchants:
            if m.state != "sailing":
                self._observe(m, m.loc)
        self._hear()
        if self.cfg.network and self.day % self.cfg.letter_every == 0:
            self._letters()
        if self.cfg.houses and self.cfg.house_pool:
            self._house_pool()
        self._committed_cache = self._committed() if self.cfg.share_depth else {}
        if self.cfg.sell_decision:
            if not self.cfg.rival_info:
                self._waiting_cache = {p: self._waiting(p) for p in self.port_list}
            for m in list(self.merchants):
                if m.state == "selling" and m.qty > 0:
                    self._sell_plan(m)
        if self.cfg.exit_rule == "voyage":
            self._retire_flagged()
        for m in self.merchants:
            if m.state == "buying":
                self._plan_merchant(m)
        if self.colleg_requests:
            self._process_colleg_requests()
        pres = {key: mk.step_pre() for key, mk in self.markets.items()}
        self._pools_step()                         # üretim, kullanım, kapasite (ticaret kapan'da)
        compete = self.cfg.retail_rule == "compete"
        for (p, g) in self.markets:
            self._kapan(p, g)
            if compete:
                self._retail_prices(p, g)
        for m in list(self.merchants):
            self._after_kapan(m)
        results = {}
        for port in self.port_list:
            if compete:   # kent, müşterilerinin gerçekten gittiği dükkânların fiyatını görür
                asks = {g: sum(s.share * s.ask() for s in self.markets[(p, g)].shops)
                        for (p, g) in self.markets if p == port}
            else:
                asks = {g: min(s.ask() for s in self.markets[(p, g)].shops) for (p, g) in self.markets if p == port}
            results.update({(port, g): v for g, v in self._urban(port, asks).items()})
        if compete:
            for (p, g), mk in self.markets.items():
                self._update_shares(mk)
                for s in mk.shops:            # dükkâncının geçimi: sabit gider
                    c = min(self.cfg.shop_living_cost, s.cash)
                    s.op_profit -= self.cfg.shop_living_cost + s.rent
                    s.cash -= c
                    self.ledger.money_sink("shop_living", c)
        for key, mk in self.markets.items():
            b, sh, vw = results.get(key, (0.0, 0.0, float("nan")))
            mk.step_post(pres[key], b, sh, vw)
            self.log[f"{key[0]}_{key[1]}_ask"].append(mk.log["ask_mean"][-1])
            self.log[f"{key[0]}_{key[1]}_kapan"].append(self.kapan_price.get(key, GOODS5[key[1]].ref))
            self.log[f"{key[0]}_{key[1]}_retail"].append(vw)
        self._upkeep()
        if self.date.day == 1:
            self._monthly()
            if self.cfg.houses:
                self._house_share_info()
            if self.cfg.recapitalize:
                self._recapitalize()
            if compete and self.cfg.retail_entry:
                self._retail_entry_exit()
        self._log_common()

    def _log_common(self):
        L = self.log
        L["date"].append(self.date)
        L["n_npc"].append(sum(1 for m in self.merchants if not m.is_player))
        bots = [m for m in self.merchants if m.is_player]
        L["bot_nw"].append(next((b.net_worth() + b.divs for b in bots if not b.informed), np.nan))
        L["inf_nw"].append(next((b.net_worth() + b.divs for b in bots if b.informed), np.nan))
        ms = [m for m in self.merchants if not m.is_player]
        L["frac_selling"].append(sum(1 for m in ms if m.state == "selling") / max(len(ms), 1))
        L.setdefault("track", []).append(self.trailing_median)      # D5b3: herkesin bildiği gerçekleşen medyan getiri
        self.ledger.check(self._money_total(), self._goods_totals())
        self.day += 1
        self.date += dt.timedelta(days=1)

    # --- ana döngü ----------------------------------------------------------
    def step(self):
        if self.cfg.wholesale:
            return self._step_wholesale()
        self.farm_sold = {}
        self._arrivals()
        for m in self.merchants:
            if m.state != "sailing":
                self._observe(m, m.loc)
        self._hear()
        if self.cfg.network and self.day % self.cfg.letter_every == 0:
            self._letters()
        if self.cfg.houses and self.cfg.house_pool:
            self._house_pool()
        self._committed_cache = self._committed()
        order = self.rng.get("merchant_order").permutation(len(self.merchants))
        for i in order:
            m = self.merchants[i]
            if m.state == "selling":
                self._merchant_sell(m)
        for i in order:
            m = self.merchants[i]
            if m.state == "buying" and not m.retire:
                self._merchant_buy(m)
        pres = {key: mk.step_pre() for key, mk in self.markets.items()}
        self._pools_step()
        results = {}
        for port in self.port_list:
            asks = {g: min(pres[(p, g)]["asks"]) for (p, g) in self.markets if p == port}
            results.update({(port, g): v for g, v in self._urban(port, asks).items()})
        for key, mk in self.markets.items():
            b, sh, vw = results.get(key, (0.0, 0.0, float("nan")))
            mk.step_post(pres[key], b, sh, vw)
            self.log[f"{key[0]}_{key[1]}_ask"].append(mk.log["ask_mean"][-1])
        self._upkeep()
        if self.cfg.exit_rule == "voyage":
            self._retire_flagged()
        if self.date.day == 1:
            self._monthly()
            if self.cfg.houses:
                self._house_share_info()
            if self.cfg.recapitalize:
                self._recapitalize()
        for key in self.markets:
            self.log[f"{key[0]}_{key[1]}_kapan"].append(float("nan"))
        self._log_common()

    def run(self):
        sd = self.start_date
        end = dt.date(sd.year + self.cfg.years, sd.month, sd.day)
        while self.date < end:
            self.step()
        out = {k: (np.array(v) if k != "date" else v) for k, v in self.log.items()}
        out["flows"] = self.flows
        out["entries"], out["exits"], out["bankruptcies"] = self.entries, self.exits, self.bankruptcies
        out["reroutes"] = self.reroutes
        out["shop_entries"], out["pool_investments"] = self.shop_entries, self.pool_investments
        out["shop_exits"] = self.shop_exits
        out["kapan_volume"] = self.kapan_volume
        out["merchants"] = self.merchants
        out["gone"] = self.gone
        out["departures"] = self.departures
        return out


# --- K-029 snapshot yardımcıları --------------------------------------------
_NOT_IN_KEY = {"seed", "years", "warm_start", "warm_n", "warm_dir", "spinup_years"}
_KEY_IF_SET = {"hazard_model", "ship_loss", "ship_market", "ship_price", "ship_life", "ship_scrap", "yard_days",
               "yard_rate", "layup_cost_day", "layup_max_days", "rebuy_min_cash", "foreign_premium"}   # R1'den sonra eklenen alanlar: varsayılandaysa hash'e girmez (eski snapshot'lar geçerli)


def snapshot_path(cfg: D5Config, k: int):
    """Snapshot yapılandırmaya bağlı: ölçümü değiştirmeyen alanlar dışındaki her alan hash'e girer."""
    import hashlib
    import json
    import pathlib
    d = {f.name: getattr(cfg, f.name) for f in dataclasses.fields(cfg) if f.name not in _NOT_IN_KEY
         and not (f.name in _KEY_IF_SET and getattr(cfg, f.name) == f.default)}
    key = hashlib.sha1(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:12]
    root = pathlib.Path(cfg.warm_dir) if cfg.warm_dir else pathlib.Path(__file__).resolve().parents[1] / "experiments" / "out" / "snapshots"
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{key}_{k}.pkl"


def build_snapshot(cfg: D5Config, k: int):
    """Ön koşu (seed 1000 + k, warm_years yıl, soğuk başlangıç). warm_min_years'tan sonra her ay başı: filo son 5 yılın
    ortalamasına ±%5 yakın ve donatılan gemi filonun ≤ %2'si ise aday; son aday seçilir. Aday yoksa sapması en küçük an.
    Aynı anda birden çok süreç isterse biri üretir, ötekiler bekler (kilit dosyası)."""
    import json
    import os
    import time
    path = snapshot_path(cfg, k)
    lock = path.with_suffix(".lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        while not path.exists():
            time.sleep(10)
        return
    try:
        c = dataclasses.replace(cfg, warm_start=False, seed=1000 + k, years=cfg.warm_years, spinup_years=0.0)
        w = D5World(c)
        t_min = dt.date(START_DATE.year + cfg.warm_min_years, START_DATE.month, START_DATE.day)
        end = dt.date(START_DATE.year + cfg.warm_years, START_DATE.month, START_DATE.day)
        best, best_dev, best_ok, meta = None, float("inf"), False, {}
        while w.date < end:
            w.step()
            if w.date.day != 1 or w.date < t_min:
                continue
            n = w.log["n_npc"]
            mean5 = sum(n[-1825:]) / len(n[-1825:])
            dev = abs(n[-1] - mean5) / max(mean5, 1.0)
            pend = len(w.pending) / max(n[-1], 1)
            ok = dev <= 0.05 and pend <= 0.02
            if ok or (not best_ok and dev < best_dev):
                best, best_dev, best_ok = w._snapshot_bytes(), dev, ok
                meta = dict(date=str(w.date), fleet=n[-1], mean5=mean5, dev=dev, pending=len(w.pending), ok=ok,
                            public_agg=w.public_agg, seed=1000 + k)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            f.write(best)
        os.replace(tmp, path)
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(meta, f, default=float)
    finally:
        os.close(fd)
        os.remove(lock)

