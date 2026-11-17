# Üretim Zincirleri ve Üretici Havuzları (öneri)
> Durum: **tasarım önerisi** (2026-10-23), kullanıcıyla tartışılacak. Henüz kod yok.
> İlgili: [D4b B3](../experiments/D4b.md), [consumer-profiles](../research/history/consumer-profiles-16c.md), framework İ8, A9, K-004

## Kullanıcının tespiti

1. Zenginin kumaşı ile fakirin kumaşı farklı mallar; ayrılmalı.
2. Ama **hammaddeleri belli ölçüde ortak.** Bu, iki malı birbirinden bağımsız iki mal olarak ayırmaktan farklı bir dinamik yaratmalı.
3. Modelde hammadde, ara mamul ve son ürün ayrımı yok; olmalı. Bu da bir **üretici sınıfı** gerektiriyor.
4. Üreticiler tüccarlar gibi bireysel ajanlar olmayabilir.

## Şu anki durum

Modelde üretim zinciri yok. Kumaş D4'te "sürekli üretilen" bir mal: girdisi yok, işçisi yok, kapasitesi sabit, sanki köylünün hasadı gibi kendiliğinden ortaya çıkıyor. Kentin geliri de dışsal (yoktan geliyor; A9 açık).

## Önerilen yapı

### 1. Mal sınıflandırması

| Tür | Örnekler (ilk dilim) | Nereden gelir |
|---|---|---|
| **Hammadde** | Yün, ham ipek, pamuk, şap (alum), boya maddeleri (woad, kermes) | Kırsal arz havuzları (mevcut model), madenler (şap: devlet tekeli) |
| **Ara mamul** | İplik | *İlk aşamada atlanır*: eğirme, dokuma ile birleşik sayılır |
| **Son ürün** | **Kaba yünlü kumaş** (yoksul, orta), **ince yünlü kumaş** (zengin), ipekli kumaş (zengin) | Üretici havuzları (yeni) |

### 2. Reçeteler (Leontief, sabit girdi oranları) ⚠️ yer tutucu

| Ürün | Yün | Şap + boya | İşgücü (gün) | Not |
|---|---|---|---|---|
| Kaba yünlü (1 top) | 1,0 | 0 | 1 | Yerel yün, az işlem |
| İnce yünlü (1 top) | 1,5 | 0,2 | 4 | Daha çok ve daha iyi yün, boyama, apre (finishing) |
| İpekli (1 top) | — (ham ipek 1,0) | 0,2 | 6 | Ayrı hammadde |

**Ortak hammaddenin yarattığı fark (kullanıcının 2. noktası):** Kaba ve ince kumaş aynı yün havuzundan beslenir.
- Zenginlerin ince kumaş talebi artarsa yün fiyatı yükselir ve **kaba kumaş da pahalanır**: yoksul, zenginin modasının bedelini öder.
- Kıtlıkta kaba kumaş talebi çökerse yün ucuzlar ve **ince kumaş üreticisi kazanır.**
- Tarihsel bir ayrıntı ⚠️: İnce kumaş genelde ithal kaliteli yünle (İspanya, İngiltere), kaba kumaş yerel yünle yapılırdı. Yani "belli ölçüde ortak." İleride iki yün kalitesi arasında kısmi ikame (CES) eklenebilir. İlk aşamada tek yün yeterli.

### 3. Üretici havuzları (kullanıcının 4. noktası)

Üreticiler **bireysel ajan değil, havuz** (İ8: kitleler havuzla temsil edilir). Her kentte her ürün için bir "üretim sektörü": çok sayıda küçük atölye, lonca ustası ve işçinin toplamı.

Bir havuzun durumu:
```
kapasite        (top/gün; yavaşça değişir: işçi göçü, lonca girişi)
kullanım oranı  (0-1; kâr marjına göre ayarlanır)
girdi stokları  (yün, şap...)
ürün stoku
nakit
reçete          (girdi/ürün oranları, işgücü/ürün)
ücret           (işçi başına günlük)
```

Günlük davranış:
1. **Girdi alımı:** Hedef üretim için gereken girdileri dükkâncılardan veya toptancılardan alır (tüccarlar gibi bir alıcı; mevcut pazar mekanizması).
2. **Üretim:** Kullanım oranı × kapasite kadar üretir (girdiler yetiyorsa).
3. **Satış:** Ürünü kendi dükkâncılarına satar. Satış davranışı köylü arz havuzuna benzer; tek fark, rezervasyon fiyatının **birim maliyet** (girdiler + ücret) olması.
4. **Karar:** Beklenen marj = (ürün fiyatı − girdi maliyeti − ücret) / ürün fiyatı. Marj pozitifse kullanım oranı artar, negatifse azalır. Ayar, D1'deki dersle **seviye + yavaş düzeltme** (PI) olarak yapılır; saf integral değil.
5. **Kapasite:** Uzun süre yüksek kullanım + kâr → kapasite yavaşça artar; uzun süre düşük kullanım → azalır (pork cycle bekleriz; fenomen, korunur).

**Neden havuz:** Kumaş sektörü binlerce küçük birimden oluşuyordu; büyük sayılar yasası bireysel kararları düzleştirir. Bireysel ajan maliyeti (yüzlerce atölye × her gün) gereksiz.

**K-004 ile uyum:** Oyuncu ileride kendi atölyesini kurarsa o atölye **bireysel bir ajan** olur, ama havuzla aynı kuralları kullanır (aynı reçete, aynı pazar). Havuz NPC sektörünü temsil eder.

### 4. Getirdiği diğer şeyler (kullanıcının 3. noktası)

| Getirdiği | Neden | Öneri |
|---|---|---|
| **İşgücü ve ücretler** | Üretim işçi ister. İşçiler kentin orta ve yoksul sınıfıdır. | **Aşama 1:** ücret dışsal ve sabit; kent geliri değişmez. **Aşama 2:** ücretler kent sınıflarının gelirine eklenir (içsel gelir). |
| **Labrousse çarpanı** (Aşama 2) | Kıtlık → kaba kumaş talebi düşer → üretim kısılır → zanaatkâr geliri düşer → talep daha da düşer. Labrousse'un tezinin asıl mekanizması bu. | Güçlü bir pozitif geri besleme. Sönümlü mü yoksa çöküş mü yaratıyor, mutlaka test edilmeli (Y16). |
| **Para devresinin kısmen kapanması** (A9) | Ücretler üreticiden kente akar; kent gelirinin bir kısmı içsel olur. | Aşama 2 ile birlikte. |
| **Kalite dereceleri** | Kaba ve ince ayrımı, yün kalitesi | İlk aşamada ürün düzeyinde; hammadde kalitesi sonra |
| **Loncalar** (kurumlar) | Venedik Arte della Lana: kalite kuralları, kapasite ve giriş sınırları | Düzey 1 kurum kuralı: kapasite artış sınırı, asgari kalite. Giriş engelleri rant yaratır (literatür: Bain 1956; D3b'de simülasyonda yeniden üretildi). |
| **Putting-out (Verlagssystem)** | Tarihsel olarak tüccar-girişimci (lanaiolo) yünü alır, eğiricilere ve dokumacılara dağıtır, kumaşı satar. | **Oyuncu için büyük bir fırsat:** tüccardan girişimciye geçiş yolu. Sonraki aşama. |
| **Ara mamuller (iplik)** | Eğirme çoğunlukla kırsalda, kadın emeğiyle | Şimdilik atlanır |
| **Diğer zincirler** | Ham ipek → ipekli; pamuk → fustian; tahıl → un → ekmek (fırıncılar); zeytin → yağ | İlk deneyde sadece yün → kaba ve ince kumaş. Diğerleri aynı yapıyla eklenir. |

## Riskler

1. **Yeni geri besleme döngüleri:** Girdi fiyatı ↔ ürün fiyatı ↔ kullanım oranı; Aşama 2'de gelir ↔ talep. D1'deki dersler (asimetri, integral gecikmesi, likidite sarmalı) burada da geçerli.
2. **Kapsam büyümesi:** Her zincir yeni mallar, havuzlar ve kalibrasyon getirir. Önce tek zincir.
3. **Kalibrasyon:** Reçeteler ve ücretler tarihsel veri ister (Venedik ve Floransa yün sanayisi literatürü: Mola, Rapp, Goldthwaite ⚠️).

## Deney önerisi: D4c (D5'ten önce)

**Kurulum:** D4b dünyası (3 sınıf) + yün (hammadde, kırsal havuz) + şap/boya (dışsal arz) + kaba ve ince kumaş üretici havuzları.

| Test | Beklenen (fenomen) |
|---|---|
| T1: Zengin talebi +%20 (moda şoku) | İnce kumaş fiyatı ↑, **yün fiyatı ↑, kaba kumaş fiyatı ↑** (ortak hammadde etkisi) |
| T2: Buğday şoku %30 (Aşama 1, sabit ücret) | Kaba kumaş talebi ve üretimi ↓, yün fiyatı ↓, ince kumaş üretimi ~sabit veya ↑ |
| T3: Yün arz şoku (koyun hastalığı, −%30) | İki kumaş da pahalanır; kaba kumaş daha çok etkilenir (girdi payı yüksek) |
| T4: Aşama 2 (içsel ücret) + buğday şoku | Labrousse çarpanı: kaba kumaş çöküşü T2'den derin mi? Sönümlü mü, çöküş mü? |
| Kararlılık | Patlama yok; kapasite döngüleri (pork cycle) sınırlı |

## Deney sonucu (D4c)

Kullanıcı önerileri kabul etti (tek yün, iki ücret aşaması ardışık, iplik atlandı). [D4c](../experiments/D4c.md): T1-T3 beklenen yönlerde; üretici havuzları kararlı. Labrousse çarpanı kapalı tek kentte zayıf, çünkü sektör yalnızca yerel tüketim için üretiyor → ihracatlı dünya (D5) gerekli.

## Kullanıcıya sorular (cevaplandı)

1. **Yün:** İlk aşamada tek yün mü (önerim), yoksa baştan iki kalite mi (yerel / ithal kaliteli)?
2. **Ücretler:** Aşama 1 (dışsal) ve Aşama 2 (içsel) aynı deneyde mi (önerim: evet, ardışık iki adım olarak), yoksa Aşama 2 sonraya mı?
3. **Ara mamul (iplik):** Şimdilik atlamak uygun mu?
