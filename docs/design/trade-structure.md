# Ticaretin Yapısı: Taşıma Boyutları, Liman Hiyerarşisi, Gemi Tipleri
> Durum: taslak (yön kararlaştı: K-034, K-035; ayrıntılar açık: S-023)
> Son güncelleme: 2026-11-10
> İlgili: [port-hierarchy-16c](../research/history/port-hierarchy-16c.md), [ship-life-piracy-16c](../research/history/ship-life-piracy-16c.md), [shipping-scale-16c](../research/history/shipping-scale-16c.md), [risk-model](risk-model.md), [rust-core](rust-core.md), K-032, K-033, K-034, K-035, S-022, S-023

Bu doküman, 2026-11-09/10 konuşmalarında gemi piyasasından (S-022) ticaretin yapısına uzanan tartışmayı ve çıkan yol haritasını toplar. Kural 7d gereği her fikrin kökeni işaretli: **K** = kullanıcı, **C** = Claude, **L** = literatür.

## 1. Çıkış noktası: S-022 araştırması

[ship-life-piracy-16c](../research/history/ship-life-piracy-16c.md) dört bulgu verdi:
- Gemi ömrü ~10 yıl (Gluzman); motordaki 15 yıl uzun.
- Yıllık gemi kaybı ~%10-13 (savaşlar dahil).
- Yabancı gemi ucuzdu; engel yasaydı.
- Korsanlık 1580-1620 arasında patladı.

Claude önerisi G1-G4 idi: ömür, ucuz ve geç yabancı gemi, korsanlık zaman çizelgesi, limanda zaman. Kullanıcı bunları uygulamadan önce daha geniş bir çerçeve açtı.

## 2. Kârlılığın boyutları (konuşma 1)

**K:** Gemi ömrü, sefer sıklığı, ticaretin maliyeti (süre ve fırsat maliyeti), sefer başına getiri ve gemi kaybı kârlılığı doğrudan etkiler. Hepsi tarihe göre ayarlanırsa kârlılık da tarihe yakın çıkmalı.

**C değerlendirmesi (kullanıcı kabul etti):**
1. **Beşi aynı türden değil.**
   - Dışsal (teknolojik, fiziksel): gemi ömrü, kayıp tehlikesi, limanda süre, deniz süresi. Tarihten alınır.
   - İçsel (modelde oluşan): sefer sıklığı (kısmen), sefer başına getiri, kârlılık. Bunlar **doğrulama ölçütü**, ayar düğmesi değil.
2. **Kârlılığın düzeyini giriş belirler.** Serbest girişte getiri sermaye maliyeti + risk primine iner. D5b3j'de yıllık %28 kayıpla bile getiri eşiğe indi; risk navluna ve fiyat farkına geçti. Literatürde bilinen sonuç (rekabetçi denge; [14](../research/simulation/14-natural-entry-exit.md)).
   - Beş boyutun belirlediği şeyler: fiyat farklarının ve navlunun büyüklüğü, filo büyüklüğü, devir hızı, oynaklık, kazananın kim olduğu.
   - Kârlılığın tarihe yakın olması için giriş tarafı da tarihsel olmalı: faiz, risk tutumu, giriş engelleri (sermaye, bağlantı, muda ihaleleri, soyluluk).
3. **Listede olmayan etmenler:** mürettebat ücreti ve işletme masrafı, gümrük ve liman vergileri, gemi bedeli/yük değeri oranı, pazar derinliği, haber gecikmesi.

## 3. Oynanış: tek gemi ve yılda 3-4 sefer (konuşma 1)

**K:** Oyuncu tek gemiyle yılda 3-4 sefere sınırlanırsa uzun süre karar vermediği bir oyun olur. Fikir: başta kısa seferler ve küçük ticaret, sonra uzun ve kârlı rotalarda büyük hacim. Bunun tarihsel ve ekonomik olarak doğru olması gerekir.

**C değerlendirmesi:**
1. **"Yılda 2-4 sefer" büyük gemilerin uzun rotaları içindir.** Akdeniz trafiğinin büyük kısmı küçük gemilerle kıyı taşımacılığıydı (Braudel; Horden & Purcell). Küçük gemi kısa rotada çok daha sık sefer yapar ⚠️. Bizdeki sorun sefer sıklığının yüksekliği değil, bütün gemilerin aynı olması.
2. **Tüccar ile gemi sahibi çoğu zaman ayrıydı.** Mal başkasının gemisine navlunla yüklenirdi. Karar sıklığı geminin sefer sayısına değil, gönderi sayısına bağlı olur.
3. **Kariyer:** genç tüccar yolcu ortak (commenda tractator) ya da fattore; olgun tüccar Venedik'te oturur, carati, fattori, mektuplar (sedentary merchant; Gras, de Roover ⚠️). Erken oyun denizde, geç oyun portföy yönetiminde.
4. **İtiraz:** Uzun rota kendiliğinden daha kârlı olamaz; herkes girer, fark kapanır. Geç oyunun daha kârlı olmasının kaynağı engellerden doğan rant olmalı: büyük sermaye eşiği, itibar, kredi, konsolos, haber ağı, muda'lar. Oyuncu uzun rotayı keşfedince değil, girme hakkını kazanınca daha çok kazanır.

## 4. Bir taşıma işinin boyutları (konuşma 2)

**K:** Bir taşıma işinin üç boyutu var:
1. **Kargo miktarı:** Gemi kapasitesiyle sınırlı. Kapasitenin maliyeti olduğu için genellikle sonuna kadar kullanılır.
2. **Süre:** Rotaya, mevsime ve gemi tipine bağlı. Başarı olasılığı ve risk de buradan bulunabilir.
3. **Malın cinsi.**

Taşıma dışındaki işler:
- satın alma (fiyat, cins, büyüklük),
- satış (fiyat, durum, cins, büyüklük),
- yükleme ve boşaltma (gemiye, mevsime, limana yani iş gücü piyasasına, kargoya bağlı),
- risk yönetimi (sigorta, refakat; sonra).

Bunlar ticaretin çeşitliliğini oluşturmalı; bizde çoğu eksik.

**C değerlendirmesi:**

| Boyut | Motorda bugün |
|---|---|
| Kapasite | Tek tip gemi (2000 birim), tek mal; yük = min(ambar, nakit, derinlik) |
| Süre | Rota ve mevsim (kış × 1,5); gemi tipi yok; limanda zaman yok |
| Mal | 9 mal (hacim, hasat, üretim zinciri) |
| Risk | Bacak, bölge, mevsim, korsan baskısı (R1) |
| Alım, satım | Kapan ve dükkânlar |
| Yükleme | Yok (aynı gün) |
| Sigorta, refakat | Yok |

Üç düzeltme:
1. **Kapasite her zaman bağlayıcı değil.** Dökme yükte ambar dolar; biberde sermaye bağlar. Tarihte boşluk karışık yük ve başkasının malıyla doldurulurdu. Gemiyi doldurmak zaman alırdı; limanda zamanın büyük kısmı buydu.
2. **Risk yalnızca süreden bulunmaz.** Değerli yük korsanı çeker, bozulan mal yolda değer kaybeder, aynı rotanın riski yıldan yıla değişir.
3. **Süre = yük bulma + yükleme + rüzgâr bekleme + deniz + karantina/gümrük + boşaltma ve alıcı bulma.** Bizde yalnızca deniz var. Sefer sıklığının tarihin 3-5 katı çıkmasının nedeni bu.

**İlke (C, kullanıcı kabul etti):** Çeşitlilik, her seçeneğin farklı bir trade-off kurmasından gelir; seçenek sayısından değil. Her boyut ayrı bir adım olarak eklenir ve ölçülür.

## 5. Başlangıç: liman hiyerarşisi (konuşma 3, K-034)

**C önerisi:** gemi tipleri + limanda zaman.

**K kararı:** Önce **liman çeşitliliği**:
- Büyük gemilerin yanaşıp yüklenebildiği, nüfusu deniz taşımacılığıyla geçinen büyük liman kentleri (bizde var olanlar).
- En az bir küçük liman katmanı; tercihen büyük, orta, küçük.
- Böylece kısa rotalarda büyük kargoları küçük parçalara bölerek para kazanan küçük-yerel tüccar kesimi oluşur. Büyük gemi seferlerinden mal sipariş etmek de mümkün olur.
- Yakın yerler arasında fiyat farkı daralır; çevre limanların talep ve üretimi eklenince uzak rotalarda marj yükselir.
- Liman çeşitliliğinde hareket eden gemi tipleri de olmalı. Büyük gemi yalnızca kendi sermayesiyle (ya da borçla) ticaret yapan tüccarı değil, çevre limanlara mal gönderen tüccarın ya da depocunun siparişini de taşır.
- Amaç: tarihsel gerçekleri ve yapıları uygulayarak gerçek dinamiklerin simülasyonda kendiliğinden ortaya çıkması için zemin.

**C değerlendirmesi (kabul):**
- Liman hiyerarşisi kök. Gemi tipi anlamını limandan alır: büyük gemi her limana girebiliyorsa küçük gemiye gerek kalmaz.
- **Düzeltme:** Serbest girişte uzak rotanın marjı kalıcı yükselmez. Yükselen şeyler:
  - hacim,
  - büyük limandaki fiyatın derinliği ve temsil gücü,
  - fiyat katmanları (iskele, bölge merkezi, antrepo).
  
  Kalıcı marjın kaynağı engellerdir (büyük gemi sermayesi, bağlantı, staple yasası).
- **Koşul:** Liman ve gemi çeşitliliği birlikte gelmeli. Küçük liman büyük gemi için ya kapalı ya da pahalı (mavna, yavaş yükleme) olmalı; yoksa hiyerarşi oluşmaz. Limanda zaman (G4) buraya kendiliğinden girer.
- **Riskler:**
  - Küçük iskeleye tam pazar modeli ağır; hafif pazar gerekir.
  - Küçük limanların fiyatı uzaktan görünmemeli: yerel tüccarın nişi yerel bilgiden gelir.
  - Sipariş ve navlun ikinci adım.

## 6. Ölçek ve kapsam (konuşma 4, K-035)

**K:**
1. Harita küçük değil: **Cenova'nın doğusundaki Akdeniz'in geniş bir kopyası**. Büyük şehirler ve limanları, küçük şehirler ve küçük limanları, kasabalar ve iskeleleri.
2. **Önce tam harita (büyük ve orta limanlar); küçük yerel limanlar sonra peyderpey.**
3. Küçük limanlar için büyük şehirlerden daha ufak bir ekonomi yapısı.
4. **Karadeniz dahil edilecek** (plan).
5. Karasal sınırlar: kervan yolları ve oradaki hazır arz ve talep olarak. Şimdinin işi değil.
6. Her limanın nüfusu, üretimi ve fiziksel özellikleri gerekli. Bunları liste olarak veren bir kaynak yok, arşiv araştırması ister. **Şimdilik kaba değerler.**

**C notu:** Kaba değerler İ12 kapsamında geçici vekil olarak işaretlenir. Her değerin yanında kaynağı ya da "Claude tahmini ⚠️" yazar; sonra doğrulanabilsin diye veri dosyasında tutulur.

## 7. Liman modeli (C önerisi; S-023'te konuşulacak)

[port-hierarchy-16c §2](../research/history/port-hierarchy-16c.md) bulgusu: liman türü tek boyut değil. Her limanın üç özelliği olur:

| Özellik | İçerik | Bugün |
|---|---|---|
| **Fiziksel liman** | En büyük gemi boyu (yanaşma ya da mavna), yükleme hızı (ton/gün), mavna maliyeti | Yok |
| **Pazar** | Nüfus ve sınıflar, art bölge üretimi, tüketim; büyük ve orta limanda tam pazar (kapan, dükkân, depocu), küçükte hafif pazar | Var (6 limanda tam pazar) |
| **Kurum** | Gümrük, staple (Venedik Körfezi), karantina, ayrıcalık | Tek gümrük oranı (%3) |

"Büyük, orta, küçük" bu üç özelliğin özeti. İskenderiye (büyük pazar, zayıf liman) ve Split (küçük şehir, 1592'den sonra transit merkezi) ancak böyle temsil edilir.

## 8. Yol haritası (C önerisi, sıra K-034/K-035'e göre)

| Adım | İçerik | Ölçüt |
|---|---|---|
| **M0** | Haritayı veriden okuyan motor (Rust): limanlar, bacaklar, bölgeler, arz planı bir veri dosyasında. Varsayılan dosya bugünkü 6 limanı birebir üretir (K-033: Python'la eşit) | `run_rs.py compare` EŞİT |
| **M1** | Tam harita v1: Cenova'nın doğusu, büyük ve orta limanlar (~20-25), kaba veri; mevcut 9 mal; tek gemi tipi | Soğuk başlangıç kararlı mı; fiyat katmanları; filo, rota dağılımı; hız |
| **M2** | Gemi tipleri (en az 2) + limanın fiziksel özellikleri (yanaşma, yükleme hızı) + limanda zaman | Sefer sıklığı dağılımı; gemi tipine göre rota ayrışması |
| **M3** | Küçük limanlar, bölge bölge (önce Adriyatik ve İyon); hafif pazar modeli | Küçük-yerel tüccar kesimi kendiliğinden oluşuyor mu; yakın fiyat farkları |
| **M4** | Navlun ve sipariş: başkasının gemisine yük, depocunun siparişi | Büyük gemi doluluk oranı; gönderi sayısı |
| **M5** | Karadeniz; kervan sınırları (dış arz ve talep) | — |
| **M6** | Kurumlar: staple, karantina, tratta, tarihsel olaylar (Sakız 1566, Kıbrıs 1571, Split 1592, Livorno 1593) | — |

S-022'nin G1-G3'ü (gemi ömrü, yabancı gemi, korsanlık zaman çizelgesi) M2 ile birlikte ele alınır: gemi tipine göre ömür ve bedel.

## 9. Açık konular

S-023'te: liman sınıfı mı üç özellik mi; küçük pazar modeli; gemi tipi sayısı; harita sınırı; veri vekilleri. Mal çeşitliliği (ipek, tuz, kuru üzüm, kereste, şeker, pamuk) M1'de yok; mevcut 9 mal korunur. Yeni mallar ayrı bir adım (C önerisi ⚠️).
