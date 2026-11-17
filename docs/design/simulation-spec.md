# Simülasyon Spesifikasyonu (v0, ilk dilim)
> Durum: **taslak v0**. Her şey tartışmaya açık. Sayıların çoğu yer tutucu (⚠️).
> Son güncelleme: 2026-10-22
> Format: ODD protokolü (Overview, Design concepts, Details). Bkz. [06 §2](../research/simulation/06-validation-and-tuning.md)
> İlgili: [framework](framework.md), [information-model](information-model.md), [determinism](determinism.md), [00-sentez](../research/simulation/00-synthesis.md), S-006

## Değişiklik günlüğü (deneylerden öğrenilenler)

| Tarih | Kaynak | Değişiklik |
|---|---|---|
| 2026-10-22 | [D1](../experiments/D1.md) | §6.3 dükkâncı fiyat sinyali: stok/hedef yerine **stok / müşteri talebi** (kaç günlük satışa yeter), logaritmik ve simetrik tepki. Eski kural mandal ve likidite sarmalı üretiyordu. |
| 2026-10-22 | D1 | §6.1 kent havuzuna **bütçe kısıtı** (gelir = para musluğu); SS-1'e ilk cevap |
| 2026-10-22 | D1 | §6.11 dükkâncı **kâr çekimi** (para yutağı) |
| 2026-10-22 | D1 | §9 κ en kritik parametre; çalışma aralığı 0,005-0,01 |
| 2026-10-22 | D1 | §2.5 **yeni rol adayı: stokçu / spekülatör.** Kötü hasata anında tepki ancak zamanlar arası arbitrajla mümkün |
| 2026-10-22 | D1 | §6.5 uyarlamalı beklentiler fiyatı kovalamamalı (yavaş + sınırlı veya çapalı) |
| 2026-10-22 | [D1f](../experiments/D1f.md) | §6.2 köylü önce kendini doyurur (kendi tüketimi, kıtlıkta en fazla %20 kısılır) → King-Davenant dışbükeyliği kendiliğinden çıkıyor |
| 2026-10-22 | D1f | §2.5 **stokçu rolü** eklendi (temelci, toptan fiyat, hasat haberi → adil fiyat; tutma maliyeti) |
| 2026-10-22 | D1f | §6.3 dükkâncıya **yerine koyma maliyeti** sinyali; ⚠️ şu an asimetrik, mevsim desenini ters çeviriyor → simetrik yeniden tasarım (D1g) |
| 2026-10-22 | D1f | §6.5 "normal fiyat" hafızası aykırı yıllara dayanıklı olmalı (kıtlık hafızayı kirletip yapay taban oluşturuyor) |
| 2026-10-22 | D1f | §7 ajan başarısı nakitle değil **net servetle** ölçülür |
| 2026-10-22 | [D1g](../experiments/D1g.md) | §6.3 dükkâncı fiyat kuralı **PI**: integral (stok/talep, κ≈0,01) + oransal (bugünkü kıtlık, P≈0,1; P≥0,5 kararsız). Sadece integral çeyrek dalga gecikme yaratıyordu. |
| 2026-10-22 | D1g | §6.2 köylünün **hasat sonrası nakit ihtiyacı** (satışlar sezon başında yoğun): mevsim deseninin asıl kaynağı |
| 2026-10-22 | D1g | §6.5 stokçunun normal fiyatı = **son 7 sezonun medyanı** (kirlenmeye dayanıklı, öğrenebilir) |
| 2026-10-22 | D1g | Fazla arz sinyali reddedildi (oynaklık artırıyor, fayda yok) |
| 2026-10-22 | D1g | **Tek limanlı modelin önerilen hali: ön ayar `H`, κ=0,01.** D2 bunun üzerine kurulur. |
| 2026-10-23 | [D2](../experiments/D2.md) | §6.5 tüccar kuralı adayı: **açgözlü çekirdek + rakip kargo farkındalığı**, yüksek getiri beklentisi yok. DP (gürültülü) ve yüksek eşikli fayda kuralı fırsatı verimsizlikle yaratıyor → reddedildi. |
| 2026-10-23 | D2 | Fırsat rejimi metrikleri (fırsat açık gün %, fırsat süresi, oyuncu botu getirisi) her deneyde ölçülür |
| 2026-10-23 | D2 | Kıtlıkta ihracat yasağı gibi tepkisel kurumsal kurallar gerekli (kıtlık yayılımı, B5) |
| 2026-10-23 | [D3](../experiments/D3.md) | §6.8 bilgi gemiyle taşınır + limanda söylenti (günlük duyma olasılığı); anlık bilgiye göre fırsat günleri %0,3 → %20-40 |
| 2026-10-23 | D3 | §6.9 beklenti = yaşla genişleyen log-normal dağılım + olağan fiyata (kendi gözlemlerinin medyanı) dönüş; sürü salınımını sönümlüyor |
| 2026-10-23 | D3 | Rakip farkındalığı (yoldaki kargo) ertelendi: asimetrik → aşırı temkin, simetrik → sürü |
| 2026-10-23 | D3 | Tüccar sayısı içsel olmalı (senete bağlı giriş-çıkış) → D3b |
| 2026-10-23 | [D3b](../experiments/D3b.md) | §6.11 tüccar nüfusu içsel: senedin altında kalan çıkar; giriş dışarıdan **sınırlı akış** (orantılı giriş domuz döngüsü yaratıyor); tüccarlar fazla nakdi kâr payı olarak çeker |
| 2026-10-23 | D3b | §7 getiriler sistem düzeyinde, defterden ölçülür (sektör getirisi) |
| 2026-10-23 | [D4](../experiments/D4.md) | §6.1 kent talebi = **LES + CES** (two-stage budgeting): kategoriler arası income effect, tahıl içinde buğday/arpa substitution. Independent ve düz LES reddedildi. |
| 2026-10-23 | D4 | Kent sınıfları gerekli (homojen kentte kıtlık lüks talebini sıfıra indiriyor) |
| 2026-10-23 | [D4b](../experiments/D4b.md) | §6.1 **sınıflı kent talebi** (zengin / orta / yoksul; her sınıf kendi LES + CES'i; parametreler [consumer-profiles](../research/history/consumer-profiles-16c.md)) |
| 2026-10-23 | D4b | §6.2 sürekli üretilen mallarda satış hızı sabit ufuklu (eski hasat mantığı artifact'tı) |
| 2026-10-23 | D4b | §2.3 **kumaş ikiye ayrılmalı:** kaba yünlü (yoksul, orta) ve ince kumaş / ipekli (zengin) |
| 2026-10-23 | [D5a](../experiments/D5a.md) | **Kurumsal toptan pazar (kapan)** doğrulandı: günlük tek fiyatlı takas; dükkâncılar perakendeye çekildi; perakende yerine koyma maliyeti toptan fiyata iki yönlü bağlı. D5 yamaları toptan modda kapalı. |
| 2026-10-23 | [D5a2](../experiments/D5a2.md) | §6.3 **rekabetçi perakende (K-016):** fiyat = yerine koyma maliyeti × (1 + Lerner marjı) × kıtlık çarpanı; logit müşteri payı + atalet; alış = türetilmiş talep (kapan'a kademeli emir); perakende giriş-çıkışı. D5a'nın mekanik iki yönlü çekişi ve tarihsel maliyetin altına satmama kuralı kaldırıldı. Giriş-çıkış 12 aylık işletme kârıyla; dükkâncının geçimi sabit gider (dükkân sayısı pazar büyüklüğüne göre). §7 ölçütlerine "rafta mal yok" günleri eklendi. Aşağıdaki §6.3 kutusu toptan pazarsız (D1-D5) sürümdür. |
| 2026-10-23 | [D5a3](../experiments/D5a3.md) | §6.8 bilgi: işlemsiz kapan oturumunda açık fiyat = en yüksek alış teklifi (K-017). §6.3: rafı boş dükkâncı tâtonnement ile teklifini yükseltir, müşterilerinin ödediği en yüksek fiyatla sınırlı. |
| 2026-10-23 | [D5b](../experiments/D5b.md) | §6.5 tüccar kişiliği (düşünme derinliği Poisson τ=1,5; taklit; aşırı güven; DARA + safety-first; ağ genişliği); §6.8 rakip bilgisi: yükleme söylentisi ve limanda bekleyen kargo, gemiyle taşınır; plan ve rota değiştirmede kalabalık hesabı. |
| 2026-10-26 | [D5b2](../experiments/D5b2.md) | §6.8 G: limandaki alımlar açık, kapan hacmi görünür; B: kendi kargosunun fiyat etkisi + ileriye bakan beklenti (Brock-Hommes karışımı); S: günlük sat/bekle/rota değiştir (optimal stopping); L: stokçu bütün mallarda, envantere göre teklif kaydırma (Ho-Stoll). **Hata düzeltmesi:** `dust_lot = 1`, 1 birimden az kalan kargo fire (Zeno artifact'ı). D5-D5b2.2 sonuçları `dust_lot = 0` ile üretildi. |
| 2026-10-26 | [D5b3](../experiments/D5b3.md) | §6.9 giriş-çıkış: spin-up; liman sermaye havuzu; price current; liman konuşmasıyla genel bilinen fırsat; inanç = sicil + sefer kârı / ufuk; yatırımcı eşik dağılımı; colleganza. **Hata düzeltmesi:** `budget_bids` (dükkân teklifi nakitle sınırlı) + batan dükkân kapanır, son dükkân da. |
| 2026-10-26 | [D5b3b](../experiments/D5b3b.md) | §6.9 colleganza: itibar kapısı ve skora göre sıralı aylık bütçe (`reputation`); giriş alternatifi = colleganza getirisi (devreye girmedi) |
| 2026-10-26 | [D5b3c](../experiments/D5b3c.md) | §6.9 finansman: vadeli borç (kaldıraç ≤ 1, öğrenilmiş kayıp primi, iflas = silinme), deniz ödüncü, batma korkulu karar, denetlenebilir colleganza, yatırımcı öğrenmesi; temettü düzeltmesi |
| 2026-10-26 | [D5b3d](../experiments/D5b3d.md) | §6.9: sefer bazlı alacaklı (`loan_pricing = "voyage"`), girişte ve kalmada batma bedeli (`entry_ruin`), gemi masrafı (`ship_cost_day`), ölçüm düzeltmesi (`record_net_overhead`); metrik: sermaye-yıl ağırlıklı toplam getiri |
| 2026-10-23 | [D5](../experiments/D5.md) | **Eksik yapı: toptan ticaret katmanı** (fondaco / ambar / iskele). Perakende dükkâncılar tüm ticareti taşıyamıyor. Ayrıca: aracı giriş-çıkışı ve kredi, rakip farkındalığı (miktar paylaşımı). Tasarım bekliyor. |
| 2026-10-23 | [D4c](../experiments/D4c.md) | §2.5 **üretim zincirleri:** Leontief reçeteli üretici havuzları (bireysel ajan değil); ortak hammadde; ücretler kent gelirine bağlanabilir. Labrousse çarpanı ihracatlı dünyada (D5) test edilecek. |

Bu doküman, kod yazmadan önce simülasyonun **ne olduğunu** eksiksiz tanımlamaya çalışır. Python deneyleri (Faz 3) bu dokümana göre yazılır. Deneylerde öğrendiklerimiz bu dokümanı günceller.

**Kapsam dışı (bu sürüm):** oyuncu arayüzü, pazarlık, temsilciler, kurumlar (düzey 1 hariç), finans (senet, sigorta, kredi), hane sistemi, kara yolları, tarihsel olay envanteri.

---

# I. GENEL BAKIŞ (Overview)

## 1. Amaç ve desenler

**Amaç:** Oyuncusuz çalışan, canlı ama okunabilir bir ticaret ekosisteminin kurulabileceğini göstermek. Yani fiyatların ne ölü ne kaotik olduğu; fırsatların doğup kapandığı; bilgi gecikmesinin anlamlı fiyat farkları yarattığı bir sistem.

**Hedef desenler** (06 §3'ten bu dilim için seçilenler):

| Kod | Desen | Bu sürümde |
|---|---|---|
| P1 | Hasat şokuna dışbükey fiyat tepkisi (King-Davenant) | ✅ |
| P2 | Uzun sakin dönemler + ani sıçramalar | ✅ |
| P3 | Mevsimsellik | ✅ |
| P4 | Limanlar arası kalıcı ama sınırlı fiyat farkı | ✅ |
| P5 | Aynı limanda dükkâncılar arası küçük fiyat dağınıklığı | ✅ |
| P6 | İkili ilişkilerin ve sadakatin ortaya çıkışı | ✅ |
| P8 | Şoktan toparlanma | ✅ |
| P9 | Fırsat ömrü ne sıfır ne sonsuz | ✅ |
| P10 | Para ve mal muhasebesi tutarlı | ✅ (doğruluk kontrolü) |
| P12 | İflas ve yenilenme | ✅ |

## 2. Varlıklar, durum değişkenleri ve ölçekler

### 2.1 Ölçekler
- **Zaman:** 1 tick = 1 gün. Başlangıç 1 Mart 1560 (çalışma varsayımı, Y11). İlk çalıştırmalar 10 yıl, yani ~3.650 tick.
- **Para:** Tek iç birim, **soldo** (S-008); tamsayı. Arayüzde duka olarak gösterilebilir (1 duka = 124 soldi).
- **Miktar:** Her malın kendi birimi var (tahıl: staio, biber: kantar...). İçeride tamsayı birim.

### 2.2 Dünya (graf)

**Limanlar (S-006 önerisi):**

| Kod | Liman | Karakter (kaba) |
|---|---|---|
| VEN | Venedik | Büyük tüketici, mamul üretici (kumaş, cam), finans ve bilgi merkezi |
| RAG | Ragusa | Aktarma limanı, tarafsız armatörler, Balkan bağlantısı |
| COR | Korfu | Venedik üssü, ara durak, şarap ve yağ |
| IST | İstanbul | Dev tüketici (tahıl), ipek ve Doğu malları pazarı |
| CHI | Sakız | Ceneviz aktarma limanı, sakız, şarap; Ege bağlantısı |
| ALE | İskenderiye | Baharat (biber), pamuk, Mısır tahılı |

**Deniz yolları** (taban seyir süresi, gün; ⚠️ tamamı yer tutucu, tarih araştırmasıyla düzeltilecek):

```
VEN ─8─ RAG ─5─ COR ─9─ CHI ─4─ IST
                 │        │
                 └──14── ALE ─8─┘ (CHI–ALE)
VEN ─12─ COR (doğrudan)
```
Kenar özellikleri:
- `taban_gün`
- `mevsim_çarpanı[ay]`: kışın süre ve risk artar
- `fırtına_riski[ay]`: günlük olasılık
- `korsan_baskısı`: dinamik, 0-1

### 2.3 Mallar (ilk dilim: 8)

| Kod | Mal | Tür | Bozulma | Esneklik (kaba) | Ana üretim | Ana tüketim |
|---|---|---|---|---|---|---|
| GRN | Buğday | Zorunlu | Orta (ayda %1-2) | −0.4 | ALE, (IST çevresi) | IST, VEN, RAG |
| SAL | Tuz | Zorunlu | Yok | −0.2 | VEN (tekel ⚠️), CHI? | Hepsi |
| WIN | Şarap | Yarı lüks | Düşük | −0.8 | COR, CHI | VEN, IST |
| OIL | Zeytinyağı | Yarı zorunlu | Düşük | −0.6 | COR, (RAG çevresi) | VEN, IST |
| CLO | Yünlü kumaş | Mamul | Yok | −1.2 | VEN | IST, ALE, CHI |
| SLK | Ham ipek | Lüks hammadde | Yok | −1.5 | IST | VEN |
| PEP | Biber | Lüks | Yok | −1.5 | ALE | VEN, (IST) |
| COT | Pamuk | Hammadde | Yok | −1.0 | ALE, (CHI) | VEN |

⚠️ Üretim ve tüketim dağılımı makul ama kaba. Kullanıcının tarih okumalarıyla düzeltilecek.

### 2.4 Kitle havuzları (ajan değil)

**Kentsel talep havuzu** `UrbanDemand[liman, mal]`:
- `nüfus`, `kişi_başı_ihtiyaç[mal]`, `mevsim_profili[ay]`
- `referans_fiyat`, `esneklik`
- `karşılanmamış_ihtiyaç` (birikebilir; kıtlık göstergesi)

**Kırsal arz havuzu** `RuralSupply[liman, mal]`:
- `yıllık_kapasite`, `hasat_ayı` (tarım ürünleri) veya `sürekli_üretim` (mamul)
- `verim_şoku` (yıllık rastgele çekiliş)
- `elde_kalan_stok` (hasattan sonra satılmayı bekleyen)
- `asgari_fiyat` (üreticinin bu fiyatın altında satmayı reddettiği seviye)

### 2.5 Ajanlar

Tüm ajanların ortak durumu:
```
id, rol, konum (liman veya yolda)
nakit (soldo, tamsayı)
stok: {mal → miktar}  (konumdaki)
inançlar: {(liman, mal) → Gözlem listesi}        # bilgi modeli
ilişkiler: {ajan_id → puan}                       # ikili ilişki (Y4)
kişilik: {risk_iştahı, sabır, λ_öğrenme, ...}     # Y7, kesin liste sonra
sabit_gider (günlük)                               # baskı: verimsiz ajan batar
```

**Rol 1: Dükkâncı** (yerel, istikrarlı; framework §4)
- Ek durum: `depo_kapasitesi[mal]`, `ortalama_maliyet[mal]`, `marj_bandı`
- Hareket etmez. Kitleye perakende satar; tüccarlardan ve kırsal arzdan alır.

**Rol 2: Tüccar** (gezgin, spekülatif)
- Ek durum: `plan` (hedef liman, mal, miktar), `uzmanlık` (bildiği mallar ve rotalar)
- Limanlar arası mal taşır; navlunla gemide yer kiralar.

**Gemiler (bu sürümde basit):**
- Ajan değil, **kaynak**. Her limanda belirli günlerde kalkan "seferler" var; tüccarlar bunlarda yer kiralar.
- `kapasite`, `navlun_ücreti` (birim × mesafe), `kalkış_tarihi`, `rota`
- Sefer üretimi: Her rota için mevsime bağlı bir sefer sıklığı (ör. VEN-RAG ayda 4 yazın, 1 kışın).
- ⚠️ Armatör ajanları sonraki sürüm. Bu sürümde seferler dışsal.

**Rol listesi açık uçlu** (Y3). Aday roller sonraki sürümler için: armatör, simsar, korsan, kurye.

### 2.6 Bilgi nesneleri

```
Gözlem:     (liman, mal, fiyat, tarih, kaynak_türü)
HaberPaketi: [Gözlem...] + [Olay haberleri...]   # gemiyle taşınır
```
- Kaynak türleri: `kendi_gözü`, `tanıdık_tüccar`, `liman_söylentisi`
- Bilgi modeli: [information-model.md](information-model.md). Bu sürümde basit hali: **en yeni gözlem + yaşa göre genişleyen belirsizlik**.

## 3. Süreç özeti ve zamanlama

**Her gün (tick), sabit sırayla:**
```
1. OLAY KUYRUĞU: bugüne ait olayları işle (zaman damgası + sıra no ile deterministik)
   a. gemi varışları → tüccar ve mal teslimi, haber paketlerinin limana bırakılması
   b. gemi kalkışları
   c. hasat olayları (mevsimsel)
   d. dışsal şoklar (deney senaryosuna göre)
2. KIRSAL ARZ: köylüler dükkâncılara satar (dükkâncının alış fiyatı ≥ asgari fiyat ise)
3. KENTSEL TALEP: kitle dükkâncılardan perakende alır (fiyata göre miktar)
4. DÜKKÂNCILAR ARASI TAKAS: limandaki dükkâncılar arasında çağrılı çift açık artırma
5. HABER YAYILIMI: limana gelen haberler, limandaki ajanlara olasılıklı olarak yayılır
6. TÜCCAR KARARLARI: sadece "karar anı" gelmiş tüccarlar (limanda olan, planı biten,
   yeni haber alan) karar verir: sat / al / bekle / yer kirala / plan yap
7. DÜKKÂNCI FİYAT GÜNCELLEMESİ: stok ve maliyete göre ilanlar
8. MUHASEBE: günlük sabit giderler, bozulma, iflas kontrolü, giriş ve çıkış
9. KAYIT: fiyatlar, hacimler, "neden" kayıtları, metrikler
```

**Aylık:** mevsim çarpanlarının güncellenmesi, yeni ajan girişi değerlendirmesi, metrik özetleri.
**Yıllık:** verim şoklarının çekilmesi (hasattan önce).

---

# II. TASARIM KAVRAMLARI (Design concepts)

| Kavram | Bu modelde |
|---|---|
| **Temel ilkeler** | Arz-talep (rezervasyon fiyatı dağılımı), mekânsal arbitraj, bilgi maliyeti (Stigler), maliyet artı marj perakendesi, depolama kararı (Deaton-Laroque) |
| **Ortaya çıkış** | Limanlar arası fiyat farkları, fırsatlar, ticaret akışları, sadakat ilişkileri, iflas dalgaları. Bunların **hiçbiri doğrudan kodlanmaz.** |
| **Uyum** | Tüccarlar rota ve mal seçimini beklenen kâra göre değiştirir; dükkâncılar fiyatı stoka göre ayarlar |
| **Hedefler** | Tüccar: risk ayarlı beklenen kâr. Dükkâncı: stoku hedef bantta tutmak ve marjı korumak. |
| **Öğrenme** | İkili ilişki puanları pekiştirmeyle güncellenir (Kirman). Fiyat inancı yeni gözlemle güncellenir. Strateji öğrenmesi bu sürümde yok. |
| **Tahmin** | Tüccar varış limanındaki fiyatı inancından tahmin eder; seyir süresi boyunca belirsizliğin büyüyeceğini hesaba katar |
| **Algı** | Ajan sadece bulunduğu limanı doğrudan görür; diğer limanları sadece haber yoluyla bilir. **Global bilgi yok.** |
| **Etkileşim** | Piyasa üzerinden (dolaylı) + ikili ilişkiler (doğrudan) + haber paylaşımı |
| **Rastgelelik** | Hava, sefer süreleri, kayıplar, verim şokları, haber yayılımı, kişilik çekilişi. Hepsi seed'li ve alt sisteme özel PRNG akışlarından ([determinism](determinism.md)). |
| **Kolektifler** | Bu sürümde yok (lonca ve topluluk sonra) |
| **Gözlem** | §11'deki metrikler + "neden" kayıtları |

---

# III. AYRINTILAR (Details)

## 4. Başlatma

1. Seed'den PRNG akışlarını oluştur.
2. Dünyayı yükle (limanlar, yollar, mallar, havuzlar). Veri dosyası: `data/slice_1560.yaml` (ileride).
3. Her limana N_dükkâncı (3-5) dükkâncı yerleştir. Başlangıç stoku ≈ hedef stok × U(0.7, 1.3).
4. M tüccar oluştur (ilk deneylerde 20-60). Konum, sermaye ve kişilik bölge profillerinden çekilir (framework §7).
5. Başlangıç inançları: Her ajan kendi limanını tam bilir; diğer limanlar için "eski ve belirsiz" bir gözleme sahiptir (örneğin 30-90 günlük, referans fiyat civarı).
6. Seferler takvimini ilk 60 gün için üret.
7. **Isınma dönemi:** İlk 1 yıl ölçüme katılmaz.

## 5. Girdi verileri

- Bu sürümde dışsal zaman serisi yok. Hasat şokları ve dışsal olaylar senaryo dosyasından okunur (deney D4 gibi).
- İleride: tarihsel olay envanteri, kalibrasyon verileri.

## 6. Alt modeller

### 6.1 Kentsel talep
```
ihtiyaç_bugün = nüfus × kişi_başı[mal] × mevsim[ay] / 365  +  karşılanmamış_birikim × β_birikim
alım_isteği(P) = ihtiyaç_bugün × (P / referans_fiyat) ^ esneklik
```
- Kitle, dükkâncıları satış fiyatına göre sıralar ve en ucuzdan başlayarak alır. İlişki ve sadakat bu sürümde kitle için yok, sadece ajanlar arası.
- Zorunlu mallarda karşılanmayan ihtiyaç kısmen birikir. Bu, kıtlıkta talebin "kaybolmadığını", ertelendiğini modeller ve King-Davenant dışbükeyliğine katkı yapar.
- ⚠️ Kıtlıkta nüfus etkisi (göç, ölüm) bu sürümde yok.

### 6.2 Kırsal arz
```
hasat (hasat_ayında):  elde_kalan_stok += yıllık_kapasite × verim_şoku     # verim ~ LogNormal(0, σ_verim)
günlük_satış_isteği   = elde_kalan_stok / kalan_gün_tahmini × f(P / asgari_fiyat)
```
- Köylü, fiyat yüksekse daha hızlı, düşükse daha yavaş satar (stok tutar). Bu da basit bir depolama davranışı.
- Mamul mallarda (CLO) sürekli üretim, hammadde girdisi bu sürümde yok ⚠️ (ileride COT, wool → CLO zinciri).

### 6.3 Dükkâncı fiyatlaması (framework §4)
> **Güncel (toptan pazarlı dünya, K-016):** bkz. [wholesale-and-behavior §1b](wholesale-and-behavior.md). Aşağıdaki kural D1-D5 serisinin (toptan pazarsız) sürümüdür; "marjı oynatarak kâr maksimize etmez" varsayımı rekabetçi perakendede geçerli değil.

```
stok_oranı     = stok / hedef_stok
stok_ayarı     = 1 − κ × (stok_oranı − 1)        # sınırlı: [1−κ_max, 1+κ_max]
satış_fiyatı   = ortalama_maliyet × (1 + marj) × stok_ayarı
alış_fiyatı    = referans_satış × (1 − marj) × stok_ayarı
                 # referans_satış: son N günün gerçekleşen satış ortalaması
kapasite_kontrolü: stok ≥ depo_kapasitesi → alım durur
nakit_kontrolü:   nakit yetmezse alım miktarı sınırlanır
```
- `marj` ∈ marj_bandı (ör. %8-15) ve kişiliğe göre sabit kalır. Dükkâncı **marjı oynatarak kâr maksimize etmez.**
- **İlişki etkisi:** Tüccar t ile işlemde marj, `marj × (1 − γ × ilişki[t])` olur. İyi ilişki biraz daha iyi fiyat demek.

### 6.4 Dükkâncılar arası takas (çağrılı çift açık artırma)
- Stoğu hedefin çok üstünde olan dükkâncılar satış, çok altında olanlar alış teklifi verir.
- Teklif fiyatı kendi alış ve satış fiyatı. Eşleşme fiyatı ortalama. Defterler PRNG ile karıştırılıp sıralanır (Doran-Parberry).
- Amacı limandaki dükkâncıları birbirine yakın tutmak (P5'i sınırlamak).

### 6.5 Tüccar kararı (karar anında)

**a) Limandayken satış:** Elindeki malı hangi dükkâncıya satar? En iyi `alış_fiyatı × ilişki_çarpanı` veren dükkâncıya. Ya da satmaz, başka limana taşımayı veya beklemeyi düşünür (§6.7).

**b) Yeni plan:** Her aday (hedef liman h, mal m) için:
```
alış      = bu limandaki en iyi satış fiyatı (dükkâncılar)
miktar    = min(nakit / alış, sefer_kapasite_payı, piyasa_derinliği_tahmini)
yolculuk  = seyir_süresi(h, mevsim)                      # beklenen gün
inanç_h   = bilgi modelinden (h, m) dağılımı, yolculuk süresi kadar ileri taşınmış
satış_tah = inanç_h'nin risk_iştahına göre yüzdeliği     # temkinli: düşük yüzdelik
                                                          # (varışta kendi satışının fiyatı düşüreceğini de hesaba kat: derinlik cezası)
maliyet   = alış × miktar + navlun + gümrük(h) + bozulma(m, yolculuk) + sermaye_maliyeti
kayıp_ris = P(batma) + P(korsan) rota ve mevsime göre
fayda     = (1 − kayıp_ris) × satış_tah × miktar − maliyet  − risk_cezası(kişilik)
```
- En yüksek faydalı seçenek; fayda > 0 ve > `bekleme_değeri` ise uygulanır.
- **Atalet:** Mevcut plana bonus; plan ancak belirgin şekilde daha iyi bir seçenek varsa değişir (utility AI).
- **Uzmanlık:** Tüccar sadece bildiği mallar ve rotalar arasında arar (bu NPC'nin her fırsatı görmesini engeller; Bannerlord önlemi).
- **Gürültü (zorluk düğmesi, framework §5):** inanç ortalamasına küçük, seed'li bir sapma.

**c) Bekleme:** Hiçbir seçenek kârlı değilse tüccar bekler (sabit gider öder). Uzun süre beklemek iflasa götürür.

### 6.6 Seyir
```
gerçek_süre = taban_gün × mevsim_çarpanı × LogNormal(0, σ_süre)
her gün:  P(fırtına kaybı) = fırtına_riski[ay];  P(korsan) = korsan_baskısı × k
kayıp olursa: mallar (tamamen veya kısmen) yok olur → MUHASEBE: mal yutağı
             tüccar hayatta kalırsa en yakın limana düşer
```
- ⚠️ Bu sürümde tüccar ölmez, sadece mal kaybeder. Kaybın büyüklüğü belirlenecek.

### 6.7 Depolama kararı (01 §4)
```
beklet eğer:  E[P_t+k] × (1 − bozulma × k) − P_şimdi > depo_maliyeti × k + faiz × P_şimdi × k
```
Tüccar ve dükkâncı için uygulanır. Dükkâncıda sadece hedef stoğun üstünde kalan miktar için geçerlidir; dükkâncı spekülatif stok tutmaz, yalnızca satmak için acele etmez.

### 6.8 Haber yayılımı
- Gemi limana varınca haber paketini bırakır. Paket, kalkış limanındaki **o anki** dükkâncı fiyatlarından (gözlem) + yolda öğrenilenlerden oluşur.
- Limandaki her ajan, her gün `p_duyma` olasılığıyla paketi öğrenir (Daley-Kendall'ın basitleştirilmiş hali). İlişkisi iyi olanlar daha hızlı duyar.
- Haberi duyan ajanın karar anı tetiklenir.
- Gemideki tüccar, paketin içeriğini **gemiye binerken** bilir (kendi gözü).

### 6.9 İnanç güncellemesi (bilgi modeli, basit hali)
```
inanç(l, m) = en yeni gözlem g
σ(yaş)      = √(σ_kaynak² + v_m × yaş)
ileriye taşıma: yolculuk süresi d kadar ileri → σ(yaş + d)
```
Haberden fiyat çıkarımı ("kötü hasat → fiyat yükselecek") bu sürümde yok ⚠️.

### 6.10 İkili ilişki
```
her başarılı işlem sonrası:  ilişki[a,b] += η × (1 − ilişki[a,b])
her gün:                     ilişki[a,b] *= (1 − δ_unutma)
```
- 0-1 arası. Seyrek tutulur, sadece işlem yapılmış çiftler için.
- Tüccar dükkâncı seçerken: `fiyat × (1 + γ × ilişki)` ile sıralar. Sadakat buradan doğar (P6).

### 6.11 Muhasebe, iflas ve giriş
- **Para muhasebesi:** Toplam para = Σ nakit (ajanlar) + havuz bakiyeleri. Değişim sadece tanımlı musluk ve yutaklardan olabilir. **Her tick bu eşitlik doğrulanır** (P10). Kitle havuzu bir musluk veya yutak gibi davranır: şehir "dışarıdan" para getirir. Bu dengesizlik açıkça izlenir.
- **Mal muhasebesi:** Σ stok + yoldaki mallar; değişim sadece üretim, tüketim, bozulma ve kayıplardan.
- **İflas:** nakit + stok değeri < 0 veya uzun süre nakit < sabit gider eşiği → ajan çıkar, varlıkları tasfiye edilir (dükkâncılara satılır).
- **Giriş:** Aylık; iflasların yerine, **son dönemde kârlı olan rol ve bölgelere** yakın yeni ajanlar girer (Doran-Parberry). Sermaye ve kişilik bölge profilinden çekilir.

---

# IV. GÖZLEM VE DENEYLER

## 7. Metrikler (her çalıştırmada kaydedilir)

| Metrik | Ölçüm | İlgili desen |
|---|---|---|
| Fiyat serileri | Liman × mal × gün (dükkâncıların ortalama satış fiyatı) | P2, P3 |
| Liman içi dağınıklık | Dükkâncı fiyatlarının değişim katsayısı | P5 |
| Limanlar arası fark | Her rota × mal için (P_h − P_k) / taşıma maliyeti | P4 |
| Fırsat ömrü | Fark > eşik olduğu ardışık günler | P9 |
| Ticaret hacmi | Rota × mal × ay | — |
| Kıtlık göstergesi | Karşılanmamış ihtiyaç / ihtiyaç | P1 |
| Sadakat | İşlemlerin "en çok işlem yapılan ortak" ile yapılma oranı | P6 |
| İflas ve giriş | Rol × ay | P12 |
| Para ve mal muhasebesi | Tutarlılık hatası (sıfır olmalı) | P10 |
| Servet dağılımı | Gini (tüccarlar) | — |

## 8. Deneyler (Faz 3)

| Deney | Kurulum | Soru | Geçme ölçütü (kaba) |
|---|---|---|---|
| **D1** | 1 liman, 1 mal (GRN), kitle + 3 dükkâncı, tüccar yok | Fiyat kararlı mı? Mevsimsellik var mı? | Fiyat patlamıyor ve çökmüyor; hasat sonrası düşüş ve ilkbahar yükselişi görülüyor |
| **D2** | 2 liman (ALE üretici, IST tüketici), 1 mal, 10 tüccar, **haber gecikmesi 0** (anlık bilgi) | Fiyat farkı taşıma maliyetine yakınsıyor mu? | Fark ≈ c bandında |
| **D3** | D2 + **gerçekçi haber gecikmesi** | Fark ve oynaklık ne kadar artıyor? Salınım patlıyor mu? | Fark D2'den büyük; salınım var ama sönümleniyor |
| **D4** | D3 + ALE'de hasat %30 düşük | King-Davenant tepkisi? Toparlanma süresi? | IST fiyatı belirgin ve dışbükey artıyor; 1-2 yılda normale dönüyor |
| **D5** | Tam dilim (6 liman, 8 mal, 40-60 tüccar) + açgözlü ve döngü botları | İstismar var mı? Fırsatlar yaşıyor mu? | Botlar ortalama tüccardan çok daha iyi değil; P9 sağlanıyor |

Her deney en az 20 farklı seed ile çalıştırılır, sonuçlar dağılım olarak raporlanır.

## 9. Ayar parametreleri (başlangıç değerleri ⚠️ tamamı tahmin)

| Parametre | Değer | Not |
|---|---|---|
| Dükkâncı marj bandı | %8-15 | |
| κ (stok hassasiyeti) | 0.3 | |
| σ_verim (hasat) | 0.15 | |
| v_m (bilgi eskime) | Tahıl 0.0004/gün, lüks 0.0002/gün | log ölçekte |
| p_duyma (günlük) | 0.3 | |
| η, δ_unutma (ilişki) | 0.1, 0.002 | |
| γ (ilişki fiyat etkisi) | 0.03 | |
| Sabit gider (tüccar) | Sermayenin ~%0.05'i / gün | |
| Atalet bonusu | %15 | |

## 10. Açık sorular (bu spesifikasyona özel)

- **SS-1:** Kitle havuzunun para kaynağı: Şehir parayı nereden buluyor? *D1 sonrası:* Kent geliri açık bir musluk ve bütçe kısıtı şart (D1 B4). İleride vergi ve ücret döngüsü.
- **SS-2:** Gemiler dışsal seferler olarak mı kalsın, yoksa erken bir sürümde armatör ajanı mı gelsin?
- **SS-3:** Tüccar mal kaybında ölmeli mi (ömür ve oyuncu ölümüyle ilişkili)?
- **SS-4:** Dükkâncı sayısı sabit mi, yoksa giriş ve çıkışa tabi mi?
- **SS-5:** Haberden fiyat çıkarımı (olay → inanç kayması) ne zaman eklenecek? *D1 sonrası:* Ertelenemez, ama dükkâncıda değil **stokçu ve spekülatör** ajanlarda yaşamalı (D1 B5). Sonraki deney: D1f.
- **SS-6:** Mamul zinciri (pamuk ve yün → kumaş) ilk dilime girmeli mi?
