# 02 — Piyasa Mekanizmaları: Fiyat Nasıl Oluşur?
> Durum: taslak (derin araştırma, 2. tur)
> Son güncelleme: 2026-10-22
> İlgili: [01-temel kurallar](01-economic-fundamentals.md), [00-sentez](00-synthesis.md)

Fiyatın "oluştuğu yer" simülasyonun en kritik tasarım kararlarından biri. Seçenekler, artıları, eksileri ve bizim duruma uygunlukları aşağıda.

---

## 1. Seçenekler haritası

| Mekanizma | Nasıl çalışır | Örnek | Uygunluk |
|---|---|---|---|
| **A. Sabit fiyat** | Tasarımcı belirler | Çoğu RPG | ❌ Ölü ekonomi |
| **B. Formül (stok → fiyat)** | Fiyat = f(stok / hedef stok) | Patrician, Port Royale, Starsector | ⚠️ Basit ama "makine" hissi verir |
| **C. Toplu emir dengesi** | Fiyat = taban × g(talep / arz) | Victoria 3 | ⚠️ Kitle için iyi |
| **D. Çağrılı açık artırma** (call auction) | Tüm teklifler toplanır, turda bir kez eşleştirilir | Doran & Parberry | ✅ Ajanlar için iyi, deterministik |
| **E. Sürekli çift açık artırma** | Teklifler geldikçe eşleşir; emir defteri var | Borsalar, EVE, RuneScape GE | ⚠️ Gerçek zamanlı, karmaşık |
| **F. İkili pazarlık** | İki ajan karşılaşır ve pazarlık eder | Sugarscape, Gintis, Kirman | ✅ RPG hissi, ama yavaş |
| **G. Piyasa yapıcı / tüccar-dükkân** (dealer) | Bir aracı stok tutar, alış ve satış fiyatı ilan eder | Gerçek tarihsel tüccarlar, X4 ticaret istasyonları | ✅✅ Tarihsel olarak en doğru |

## 2. B — Formül tabanlı (stok → fiyat)

Oyun endüstrisinin standart çözümü:
```
fiyat = taban_fiyat × (hedef_stok / mevcut_stok) ^ k
```
- Port Royale 4'te kasabanın "arz çubuğu" var: dolu çubuk = fazla arz ve ucuz, boş çubuk = ihtiyaç ve pahalı. Toplu alım stoku azalttıkça birim fiyatı yükseltir. ([Gamewatcher](https://www.gamewatcher.com/news/port-royale-4-production-and-town-management), [Steam](https://steamcommunity.com/app/1024650/discussions/0/3115908865101467322))
- Starsector'da pazar nüfusu arz ve talebin büyüklüğünü belirler. Toplu alım satış birim fiyatını değiştirir. Oyuncunun sattığı mal talebi 120 gün karşılar, stok her 30 günde yenilenir. Kıtlıkta oyuncu sınırlı miktarı çok yüksek fiyata satabilir. ([Starsector wiki](https://starsector.wiki.gg/wiki/Market))

**Artı:** Basit, hızlı, dengelemesi kolay. Oyuncu mantığı hemen kavrar.
**Eksi:** Kimse "karar" vermiyor; fiyat bir termometre gibi. Ajanlar yok, hikâye yok. Patrician ve Port Royale oyuncularının "10 saat sonra monotonlaşıyor" eleştirisinin bir kaynağı bu.

**Bizim için:** Şehrin kitlesel tüketim talebini temsil etmek için hâlâ kullanışlı. Bir "kentsel talep havuzu" düşünülebilir.

## 3. D — Çağrılı açık artırma (her tick'te bir kez eşleştirme)

Doran & Parberry'nin takas odası (clearing house) bu türden ([ayrıntı](economy-simulation-techniques.md)):
1. Tüm ajanlar o turdaki alış ve satış tekliflerini verir.
2. Defterler karıştırılır (aynı fiyattaki tekliflerde sıra avantajını yok etmek için), sonra fiyata göre sıralanır.
3. En yüksek alış en düşük satışla eşleşir. Fiyat iki teklifin ortalamasıdır. Eşleşme bitene kadar devam eder.
4. Eşleşmeyen teklifler reddedilir; ajanlar fiyat inançlarını günceller.

**Gode & Sunder (1993), "sıfır zekâlı" tüccarlar:** Tamamen rastgele teklif veren ama **bütçe kısıtına** uyan (zararına satmayan, gücünün yetmediğini almayan) programlar, çift taraflı açık artırmada **%100'e yakın tahsis verimliliği** elde etti. Yorumları şu: verimliliği tüccarların zekâsı değil, **piyasa kurumunun yapısı** sağlıyor. ([Li Calzi & Pellizzari 2008](https://www.unive.it/web/fileadmin/user_upload/dipartimenti/DMAN/pubblicazioni_scientifiche/working_papers/2008/2008wp168.pdf), [arXiv: Econophysics](https://arxiv.org/pdf/0909.1974))

**Ama dikkat, sonuç tartışmalı:**
- Li Calzi & Pellizzari'ye göre sonuç, ajanların tekliflerini sık sık yeniden çekmesi varsayımına bağlı. Bu olmadan sürekli açık artırmada bireysel rasyonellik verimlilik için yeterli değil. ([unive.it](https://www.unive.it/web/fileadmin/user_upload/dipartimenti/DMAN/pubblicazioni_scientifiche/working_papers/2008/2008wp168.pdf))
- Bazı simülasyonlarda fiyatlar makul bir ölçüyle yakınsamıyor. ([Purdue](https://Krannert.purdue.edu/research/working-papers-series/2007/1204.pdf))
- Cliff'in ZIP ajanları sıfır zekâdan biraz daha fazla zekâyla (basit öğrenme) insan verilerine çok daha yakın sonuçlar verdi. "Sıfır yetmez". ([Bristol](https://research-information.bris.ac.uk/en/publications/zero-is-not-enough-on-the-lower-limit-of-agent-intelligence-for-c/))
- Gjerstad-Dickhaut (GD) ve ZIP ajanları insan tüccarlardan sürekli olarak daha iyi performans gösterdi (IBM 2001). GDX daha da güçlü. ([IBM Research](https://research.ibm.com/publications/high-performance-bidding-agents-for-the-continuous-double-auction), [De Luca & Cliff](https://www.scitepress.org/Papers/2011/32939/32939.pdf))

**Bizim için dersler:**
1. **Piyasa kurumu çok önemli.** Ajan zekâsına yatırım yapmadan önce doğru eşleştirme kurumunu kurmak verimliliğin büyük kısmını sağlar.
2. NPC'lerin **çok akıllı olmasına gerek yok;** fazlası Bannerlord'daki gibi oyuncuyu ezer. ZIP düzeyinde basit öğrenen ajanlar yeterli ve hatta ideal.
3. Çağrılı açık artırma (turda bir eşleştirme) bizim **günlük tick** yapısına ve **determinizme** (K-010) tam uyar. Sürekli açık artırma gerçek zamanlı olay sırasına bağlı ve deterministik tutması daha zor.

## 4. F — İkili pazarlık

**Sugarscape (Epstein & Axtell 1996):** İki ajan karşılaşır. Marjinal ikame oranları (MRS) farklıysa takas eder. Fiyat iki MRS'nin geometrik ortalamasıdır. Merkezi bir açık artırmacı olmadan bir fiyat dengesi ortaya çıkabilir. Ama ajanlar ölümlüyse ve tercihleri evriliyorsa fiyat hiç dengelenmez ve piyasa dengeye ulaşmaz. ([Mesa Sugarscape](https://mesa.readthedocs.io/latest/examples/advanced/sugarscape_g1mt.html), [UC Davis](https://www.math.ucdavis.edu/~saito/data/science-news/original%20CD/software/SNData/10520))

**Gintis (2006):** Para ve kamuya açık fiyat yok; her ajanın özel bir takas fiyatı var. Düşük puanlı ajanlar yüksek puanlıları taklit ediyor. Orta vadede yarı-kamusal fiyatlar ortaya çıkıyor, uzun vadede Walras dengesine yaklaşan durağan dağılımlara oturuyor. ([Gintis](https://www.degruyterbrill.com/document/doi/10.2202/1534-5971.1302/pdf?lang=en), [Mandel & Botta](https://halshs.archives-ouvertes.fr/halshs-00634656))

**Bizim için:**
- İkili pazarlık simülasyon çekirdeği için **fazla yavaş ve gürültülü** (binlerce ajan × her gün × her mal).
- Ama **oyuncu deneyimi** için mükemmel: oyuncu bir tüccarla yüz yüze pazarlık eder. RPG katmanı (ikna, itibar, ilişki) buraya oturur.
- **Hibrit öneri:** Ajanlar arası çekirdek ticaret çağrılı açık artırma ve dealer modeliyle yürür. Oyuncunun önemli işlemleri ise isteğe bağlı bir pazarlık katmanından geçer. Bu katmanın sonucu sistemdeki fiyatlardan çok uzaklaşmaz, ama itibar ve beceri fark yaratır.

## 5. G — Piyasa yapıcı / tüccar-dükkân (dealer) modeli: tarihsel olarak en doğru seçenek

16. yüzyılda bir limanda "pazar" büyük ölçüde şuydu: **yerel tüccarlar stok tutar, alış ve satış fiyatı söyler.** Oyuncu "piyasaya" değil, bu tüccarlara satar. Bu tam olarak finans literatüründeki **dealer** modelidir.

**Finans literatürü (piyasa mikroyapısı):**
- **Garman (1976):** Tek bir dealer alış ve satış fiyatını belirler. Asıl problemi stoğun veya nakdin tükenip iflas etmekten kaçınmaktır. Bu kısıt pozitif bir alış-satış farkı (spread) gerektirir. "Piyasa mikroyapısı" terimi de Garman'dan. ([Cornell ders notları](https://sha.cornell.edu/wp-content/uploads/sites/4/2019/04/inventorymodels20081031.pdf))
- **Amihud & Mendelson (1980):** Fiyatlar stoğa göre değişir. Hem alış hem satış fiyatı stok pozisyonunun **azalan fonksiyonudur**: stok fazlaysa ikisini de düşürür (satmak için), azsa ikisini de yükseltir. Spread tercih edilen stok seviyesinde en dardır ve stok bu seviyeden uzaklaştıkça açılır. ([Kearns UPenn](https://www.cis.upenn.edu/~mkearns/finread/marketmaker.pdf), [CFA](https://rpc.cfainstitute.org/research/financial-analysts-journal/1982/asset-price-behavior-in-a-dealership-market))
- **Ho & Stoll (1981):** Dealer'ın taşıdığı **risk** spread'i belirler. Riskli mallarda (fiyatı oynak, bozulabilir) spread geniştir.
- **Avellaneda & Stoikov (2008):** Modern piyasa yapıcı stratejileri bu çerçeve üzerine kuruludur. ([arXiv](https://arxiv.org/pdf/2106.06974v5))

**Basitleştirilmiş dealer formülü (bizim için):**
```
orta_fiyat   = dealer'ın fiyat inancı (ajanın beklentisi; bilgi yaşına göre)
stok_sapması = (mevcut_stok − hedef_stok) / hedef_stok
çarpıklık    = −κ × stok_sapması          # stok fazlaysa fiyatı aşağı çek
yarı_spread  = s0 + s1 × risk(mal) + s2 × |stok_sapması|

alış_fiyatı  = orta_fiyat × (1 + çarpıklık − yarı_spread)   # dealer bu fiyattan alır
satış_fiyatı = orta_fiyat × (1 + çarpıklık + yarı_spread)   # dealer bu fiyattan satar
```

**Neden bu model bizim için ideal:**
1. **Tarihsel olarak gerçekçi:** Oyuncu "Rialto'daki baharat tüccarı Bembo"ya biber satar, soyut bir "Venedik piyasası"na değil.
2. **RPG ile doğal uyum:** Dealer bir NPC; itibarı, ilişkisi, kişiliği ve bilgisi var. Spread oyuncuyla ilişkisine göre daralabilir (müşterileşme, Geertz).
3. **K-004 ile uyumlu:** Dealer da bir ajan; sermayesi, stoğu ve batma riski var. Oyuncu da ileride dükkân açınca dealer olur.
4. **Fiyat farkı ve dağınıklık doğal olarak oluşur:** Aynı limanda 3 tüccarın fiyatı farklıdır. Kirman'ın Marsilya'sı gibi.
5. **Dealerlar birbirinden ve toplu talepten beslenir:** Dealer kentsel talebe perakende satar, toptancıdan ve gelen gemilerden alır.
6. **Hesaplama açısından ucuz:** Her işlem bir formül değerlendirmesi.
7. **Doğal bir piyasa derinliği verir:** Oyuncu çok mal satarsa dealer'ın stoğu şişer, alış fiyatı düşer, sermayesi biter. "Piyasayı boğmak" böylece fiziksel bir anlam kazanır.

**Dealer'lar arası denge:** Bir limandaki dealer'lar birbirleriyle de ticaret yapar (toptancılar arası). Bu iç takas, dealer'lar arasında çağrılı bir açık artırma olabilir (bkz. D). Böylece aynı limandaki fiyatlar birbirinden çok uzaklaşmaz, ama tamamen de eşitlenmez.

## 6. Toplu talep katmanı: kent ve köy

Ajanların hepsini tek tek modellemek imkânsız: Venedik ~170.000 kişi, İstanbul çok daha büyük. Kitlesel tüketim ve üretim **havuzlar** olarak modellenir:

```
Kentsel talep havuzu (şehir × mal):
  temel_talep         = nüfus × kişi_başı_ihtiyaç(mal, sınıf_dağılımı, mevsim)
  fiyat_hassasiyeti   = esneklik(mal)
  günlük_alım(P)      = temel_talep × (P / referans_fiyat) ^ esneklik
  → dealer'lardan bu miktar perakende olarak satın alınır

Kırsal arz havuzu (bölge × mal):
  hasat / üretim      = kapasite × verim(hava, savaş, veba)
  günlük_satış(P)     = arz eğrisi; köylüler fiyat yükseldikçe daha çok satar (ama hasat sınırlı)
  → dealer'lara veya yerel pazarlara satılır
```

Victoria 3'ün "yerel tüketim alım emri üretir, yerel üretim satım emri üretir" mantığı buna yakın. Bu havuzların **cevap verdiği fiyat** dealer'ların fiyatıdır. Böylece kitle ile ajanlar arasında bir köprü kurulur.

## 7. Bilgiye dayalı fiyat inancı: bizim için özel bir mekanizma

Hiçbir mevcut modelde tam olarak bizim ihtiyacımız yok: **farklı yaşta bilgiler** taşıyan ajanlar.

**Öneri: inanç = bilinen fiyat + bilgi yaşına göre genişleyen belirsizlik.**
```
Ajanın X limanındaki M malı için bildiği:  (fiyat_gözlemi, gözlem_tarihi, kaynak_güvenilirliği)

inanç_ortası    = fiyat_gözlemi  (ya da yaşla birlikte uzun dönem ortalamaya doğru kayan bir değer)
inanç_genişliği = taban_belirsizlik + oynaklık(M) × √(bugün − gözlem_tarihi) / kaynak_güvenilirliği
```
- Taze haber → dar inanç → güvenli karar.
- 60 günlük haber → geniş inanç → riskli karar. Temkinli ajan gitmez, cesur ajan gider.
- Haber gelince inanç daralır ve kayar. Bu, Doran-Parberry'nin "inanç aralığı" fikrinin bilgi yaşıyla birleşmiş hali.
- **√zaman** ifadesi rastgele yürüyüşün belirsizliğinin büyüme hızından geliyor: oynak mallarda bilgi daha hızlı eskir.

## 8. Mekanizma seçimi: öneri

| Katman | Mekanizma | Neden |
|---|---|---|
| Kitlesel tüketim ve üretim | Toplu havuz (§6) | Ölçek, tarihsel tutarlılık |
| Liman içi ticaret | **Dealer modeli** (§5) + dealer'lar arası günlük çağrılı açık artırma (§3) | Tarihsellik, RPG, determinizm |
| Ajan beklentileri | Bilgi yaşına dayalı inanç (§7) | Bilgi gecikmesi tasarımın kalbi |
| Oyuncunun önemli işlemleri | İsteğe bağlı pazarlık katmanı (§4) | RPG hissi |
| Finansal araçlar (senet, sigorta) | Ayrı pazarlar: senetler için dealer veya açık artırma, sigortacılar dealer gibi fiyat verir | Ayrı tasarım dokümanı gerekir |

Ayrıntılı mimari önerisi: [00-sentez](00-synthesis.md).
