# Gemi Ömrü, Yabancı Gemi, Korsanlığın Zaman Çizelgesi ve Gemi Piyasası Ekonomisi
> Durum: taslak (ikincil kaynaklar ve arama özetleri; motoru yönlendirmek için, son kalibrasyon değil)
> Son güncelleme: 2026-11-09
> İlgili: [shipping-scale-16c](shipping-scale-16c.md), [maritime-risk-16c](maritime-risk-16c.md), [risk-model](../../design/risk-model.md), [D5b3j](../../experiments/D5b3j.md), [15-macro-abm-methods](../simulation/15-macro-abm-methods.md), S-022, K-032

**Amaç (S-022, kullanıcı 2026-11-09):** Gemi kaybı ve yıpranma ölçeği, korsanlığın zaman içinde değişimi ve yabancı gemi seçeneğini modele oturtmadan önce tarihsel ve ekonomik araştırma.

**Kaynak işaretleri:** 🔎 = arama özetinde ya da kitap alıntısında görüldü, birincil metin okunmadı. ⚠️ = doğrulanmadı ya da Claude'un kaba hesabı.

**Erişim notu:** Gluzman 2021'in tam metnine (dokumen.pub kopyası) bu oturumda erişilemedi; TLS hatası verdi, indirme de izin almadı. Aşağıdaki Gluzman alıntıları arama motorunun kitap metninden verdiği parçalar.

## 1. Gemi ömrü (yıpranma)

| Bulgu | Kaynak |
|---|---|
| Venedik yuvarlak gemilerinin (nave) ortalama ömrü **yaklaşık 10 yıl**; barış döneminde **13'e kadar**. Ömrü kısaltan dış etkenler hesaba katılınca ortalama **6 yılın altına** iniyor. | Gluzman 2021, Bölüm 9 🔎 |
| Dönemin gözünde: 8-10 yıl saygın bir ömür; 6-7 yıl kısa ama yaygın; 5 yaşına ulaşamayan gemi ziyan. | Gluzman 2021, Bölüm 9 🔎 |
| İşletmeciler gemilerinin **7 yıldan uzun yaşamayacağını varsaymak zorundaydı**, sonunda daha uzun yüzse bile. | Gluzman 2021, Bölüm 9 🔎 |
| Yuvarlak gemilerin çoğu 10 yaşına varmadan ya hizmetten çekildi ya da kötü bir sonla (batma, yakalanma) yok oldu. | Gluzman 2021, Bölüm 9 🔎 |
| Gluzman ortalama ömrün tek başına az şey söylediğini düşünüyor; ömrü ekonomik açıdan dört sınıfa ayırıyor (yukarıdaki üç aralık ve "ziyan"). | Gluzman 2021 🔎 |
| Ragusa gemileri için tahminler çok farklı: Tadić bazen 26-28 yıl buluyor; Vekarić 16. yy sonunda yapılan Ragusa gemileri için ortalama **8 yıl** öneriyor. | Gluzman 2021, Bölüm 9 (Tadić, Vekarić üzerinden) 🔎 |
| Kadırgalar (ticari) biraz daha uzun: ~13 yıl. | Gluzman 2021 incelemesi (OCR parçası, atıf belirsiz) 🔎 ⚠️ |

**Claude hesabı ⚠️:** Fiziksel ömür T ≈ 10-13 yıl ve yıllık kayıp tehlikesi λ sabitse beklenen ömür (1 − e^(−λT)) / λ olur. Bunun 6 yıla inmesi için **λ ≈ %12-13/yıl** gerekiyor. "7 yıl" varsayımı λ ≈ %10'a karşılık geliyor.
- Yani 1453-1571 Venediği'nde bir gemi yılda **~%10-13 olasılıkla** kayboluyordu.
- Bu oran savaşları içeriyor (1499-1503, 1537-40, 1570-73) ve "dış etkenler" arasında devletin gemiye el koyması da olabilir ⚠️.
- [shipping-scale-16c](shipping-scale-16c.md) yıllık %4-12 demişti; Gluzman'ın verisi bu aralığın **üst ucunu** destekliyor.

## 2. Gemi bedeli ve ikinci el değer

| Bulgu | Kaynak |
|---|---|
| 1530'ların ortasında 700 botte'lik bir nave Venedik'te ~6.000 duka, kolonilerde ~5.000 duka (**~%17 ucuz**). | Gluzman 2021 🔎 ([shipping-scale-16c §3](shipping-scale-16c.md)) |
| 1506'da el konan 500 botte'lik yaşlı *Malipiera* için 2.300 duka ödendi. Yeni bir gemi, ölçekle, ~4.300 duka ederdi ⚠️; yani yeni bedelin yaklaşık **yarısı** (yaşı bilinmiyor). | Gluzman 2021 🔎; oran Claude hesabı ⚠️ |
| Gemi satışında vergi ~%2,2. | Gluzman 2021 🔎 |

## 3. Yabancı gemi

| Bulgu | Kaynak |
|---|---|
| 16. yy ortasında küçük ticaret gemileri bile dışarıdan alınıyordu; bu, Venedik yasasına açıkça aykırıydı. | Lane 1934, yayıncı özeti 🔎 |
| Hollanda gemileri Baltık kerestesiyle daha ucuza yapılabiliyordu. | Lane 1934, yayıncı özeti 🔎 |
| Önce Venedik yapımı gemilere tanınan ayrıcalıklar dışarıdan gemi alan Venediklilere, sonra yabancı yapımı gemilere genişletildi. Tüccarlar bundan şikâyetçiydi. | İkincil, güvenilirliği düşük kaynak; Lane'in tezine uygun 🔎 ⚠️ |
| 1606'da Venedik ticaret gemilerinin bir kısmı yabancı kökenliydi; Arsenale savaş kadırgası yapımına yoğunlaşmıştı. | DergiPark makalesi 🔎 |
| Venedik büyük gemiler için yapım sübvansiyonu (sovvenzione) verirdi. | Lane 1934 ⚠️ (Claude'un bilgisi; bu oturumda doğrulanmadı) |
| Yapım süresi: 16. yy yuvarlak gemisi için doğrudan sayı bulunamadı. Kaynaklar yalnızca "aylar" diyor; bir gemiyi uzatma işi için ~4 ay (Leiden 1594). | Genel kaynaklar 🔎 ⚠️ |
| Yabancı gemiyi bulma ve getirme süresi: bulunamadı. | — |

**Çıkarım:** Tarihte yabancı gemi pahalı değil, **ucuz**ydu (koloni ~%17, kuzey de ucuz). Engeli fiyat değil, yasa ve ayrıcalıktı (Venedik yapımı gemiye tanınan haklar). Kullanıcının "ucuz ama geç" önerisi kaynaklarla uyumlu. Bugünkü motordaki "%25 pahalı ama hemen" seçeneğinin dayanağı yok.

## 4. Korsanlığın zaman çizelgesi

| Dönem | Bulgu | Kaynak |
|---|---|---|
| 1453-1571, barış yılları | Levant'a gidişte sigorta primi ~%1-1,5, dönüşte %2-2,5 (15. yy sonu). Prim doğal tehlikeyi, korsanı ve sigortacının payını birlikte içerir. | Gluzman 2021 incelemesi 🔎 |
| 1499-1503, 1537-40, 1570-73 | Venedik-Osmanlı savaşları. Gemi kaybı ve el koyma bu yıllarda yoğun ⚠️. | Genel bilgi ⚠️ |
| 1540-1640 | Uskoklar (Senj üssü) Adriyatik'te aktif. | Tenenti 1967 inceleme özeti 🔎 |
| 1571-1581 | İnebahtı ve Kıbrıs (1571), Halkulvadi (1574), Osmanlı-İspanya ateşkesi (1581'de onaylandı). Sonraki on yıllarda doğu Akdeniz'de korsan şiddetinde patlama. | storiamediterranea makalesi 🔎 |
| 1580-1584 sonrası | Korsanlar ateşkeslere uymadı; onlara göre korsanlık savaş değildi. Braudel 1580'lerin "dönüşü"nü (Atlantik'in öne çıkması) vurgular. | OpenEdition (cvz/1134) 🔎 |
| **1580-1680** | Fontenay: "korsan yüzyılı"; **1580-1620 patlaması**. Braudel'den: "Tüccar yoksa korsan da yok." Yani korsanlık, ticaretin sürdüğünün de işareti. | Fontenay, Revista Áreas (um.es) 🔎 |
| 1580-1615 | Katolik korsanlar (Malta, San Stefano), İngiliz ve Hollandalı tüccar-korsanlar Osmanlı Akdenizi'ne doluşuyor. Osmanlı deniz savunması zayıfladı. Tenenti 1961/1967: kuzey korsanlığı Venedik ticaretini vurdu; 17. yy başında ağır bir gemi yapımı krizi. | storiamediterranea 🔎; Tenenti, UC Press tanıtımı 🔎 |
| 1592-1609 | Venedik noter kayıtlarında yılda ~37 batma ya da yakalanma. | Tenenti 1959 ([maritime-risk-16c §3](maritime-risk-16c.md)) |
| Tartışma | "1580'den sonra çöküş" anlatısı tartışmalı: de Groot gibi tarihçiler Osmanlı tehdidinin 17. yy'da da güçlü kaldığını savunuyor. | arama özeti 🔎 |
| Malta korsanlığı | Korsanlık 1605'te Tribunale degli Armamenti ile kurumsallaştı; Malta korsanlığının doruğu ise 1660-75. | Malta Üniversitesi kaynakları 🔎 |

**Bulunamayanlar:** Venedik 1590-1610 prim serisi (Tenenti 1985, *Studi Veneziani*); yıl bazında yakalanan gemi sayısı.

**Çıkarım:**
- Kullanıcının "başta az, 1580'den sonra hızla artar" senaryosu tarih yazımının ana çizgisiyle uyumlu (Fontenay, Braudel, Tenenti).
- İki düzeltme:
  - (a) 1560'larda korsanlık sıfır değil; Uskok, Berberi ve Malta korsanları var, savaş yıllarında kayıp yüksek.
  - (b) Barış dönemi primi (%1-2,5 / sefer) yalnızca korsandan değil, doğal tehlikeden de geliyor. **Korsana düşen pay sefer başına ~%0,5 civarındaysa, kullanıcının "%0,5" önerisi barış dönemi tarihiyle uyumlu**; toplam tehlike (doğal + korsan) ise %1-1,5.

## 5. Ekonomi literatürü: gemi piyasası, time-to-build

| Sonuç | Kaynak |
|---|---|
| **Time-to-build:** Yatırım ile kapasitenin gelişi arasındaki gecikme dalgalanma üretir. | Kydland & Prescott 1982 ⚠️ |
| **Kuru dökme yük piyasası:** Yapım süresi patlamalarda uzar (tersane kuyruğu). Time-to-build kaldırılırsa navlunlar düşer, yatırım hem artar hem çok daha oynak olur. İkinci el satış fiyatları firmanın değer fonksiyonunu doğrudan gösterir. | Kalouptsidi 2014, *AER* 104(2) 🔎 |
| **Yeni gemi fiyatı maliyetle, ikinci el fiyatı piyasayla belirlenir.** İkinci el fiyatına en çok navlun ve yeni gemi fiyatı etki eder. | Tsolakis 2005 (tez); Tsolakis, Cridland & Haralambides 2003 🔎 |
| İkinci el fiyatı yeni gemi fiyatından daha oynak. Asset value modeli: gemi fiyatı beklenen kazançların bugünkü değeri; freight, ikinci el, yeni gemi ve söküm piyasaları rational expectations altında birlikte çözülür. | Beenstock & Vergottis 1989 🔎 |
| Hemen teslim alınan ikinci el gemi için alıcılar **zaman primi** öder; patlamada ikinci el fiyatı yeni gemi fiyatına yaklaşır, aşabilir. | sektör yazıları 🔎; Stopford, *Maritime Economics* ⚠️ |
| İkinci el fiyatları yeni gemi fiyatının ima ettiği düzeye uzun dönemde döner. | 2000-2024 kuru dökme yük çalışması 🔎 |

**Bizim motorla ilişkisi:**
- D5b3j'deki Tobin's q değerlemesi Beenstock-Vergottis'in asset value mantığıyla aynı aileden.
- Fiyat ile kamu sicili arasında 0,48-0,82 korelasyon: literatürde bilinen "ikinci el fiyatı kazançla birlikte hareket eder" örüntüsü (Tsolakis) yeniden üretildi.
- **Kalouptsidi'nin sonucu doğrudan ilgili:** Bugünkü "hemen teslim yabancı gemi" seçeneği time-to-build'i fiilen kaldıran bir kapı. Kapı kapanır ve yabancı gemi geç gelirse literatüre göre:
  - yatırım dalgalanması azalır,
  - patlamada fiyatlar (navlun ve ikinci el) yükselir,
  - ikinci el fiyatı yeni gemi bedelini aşabilir.

## Oyun için çıkarımlar

1. **Gemi ömrü 15 yıl değil, ~10-12 yıl** (Gluzman: ortalama 10, barışta en çok 13). Fiziksel ömrü kaynaktan almak tepeden ayar değil; motordaki 15 Claude seçimiydi ⚠️.
2. **Yıllık kayıp hedefi %10-13 civarı** (1453-1571 Venedik, savaşlar dahil). Bu, [shipping-scale-16c](shipping-scale-16c.md)'deki %4-12 aralığının üst ucu. Sonuçları:
   - VRS'deki yıllık %14,5 kayıp tarihten çok uzak değil.
   - Tam haritadaki %28 iki katı.
   - Hedef örüntü: kayıpla birlikte ortalama gemi yaşı ~5-6 yıl. Bugün 3,1 yıl, çünkü sefer çok sık.
3. **Sefer sıklığı hâlâ ana sorun:** Tarihte sefer başına ~%3-4 kayıp × yılda 3 sefer ≈ yıllık %10. Bizde sefer başına %2 × 7-14 sefer. Yıllık oran VRS'de doğru çıkıyor, ama sefer başına risk tarihin altında, sefer sayısı üstünde. Tüccarın her seferi tartması yanlış ölçekte.
4. **Korsanlık zaman çizelgesi:** Barış dönemi tabanı düşük (korsan payı ~%0,5 / sefer; doğal tehlikeyle toplam %1-1,5). Savaş yılları sıçrama. **1580-1620 arasında yapısal artış.** Korsan baskısı sürecinin (AR(1)) uzun dönem ortalaması yıla bağlanır; artış bir tarihsel olay olarak gelir (ateşkes, kuzeylilerin gelişi). Bu tarihle uyumlu; "korsanlık başta sıfır" demek ise tarihin altında kalır, oyun tasarımı sapması olarak işaretlenmeli.
5. **Yabancı gemi: ucuz ve geç.**
   - Fiyatta koloni farkı %17; kuzey gemisi de ucuz. Gecikme için kaynak yok; "+6 ay" (kullanıcı) oyun tasarımı varsayımı ⚠️.
   - Literatüre göre bu değişiklik ikinci el fiyat tavanını kaldırır: patlamada ikinci el fiyatı yeni bedelin üstüne çıkabilir (zaman primi). Yatırım dalgalanması da azalır (Kalouptsidi).
   - **İstismar riski:** Yabancı gemi hem ucuz hem sınırsızsa, Venedik tersanesi ancak aciliyet anında seçilir. Oyuncu da patlama dışında hep ucuz yoldan büyür. Bu tarihle uyumlu (Venedik gemi yapımı gerçekten çöktü). Ama yabancı kaynağın kapasitesi ve gecikmesi de talebe bağlı olmalı (Kalouptsidi: kuyruk patlamada uzar).
   - Tarihsel karşılığı olan bir denge ⚠️: Venedik yapımı gemiye tanınan yasal ayrıcalıklar (sübvansiyon, yük ayrıcalığı).
6. **Gemi değeri yaşla hızlı düşer** (Malipiera: yaşlı gemi yeni bedelin ~yarısı). Fiziksel ömür 10-12 yılsa doğrusal amortisman bu örnekle uyumlu.
7. **Bakım (careening, yıllık onarım) maliyeti için kaynak bulunamadı.** Motorda sıfır (`ship_cost_day=0`). Araştırma açığı.

## Kaynaklar
- Gluzman, R. (2021). *Venetian Shipping from the Days of Glory to Decline, 1453–1571.* Brill. Bölüm 9: https://brill.com/display/book/9789004398177/BP000019.xml ; Ek C: https://brill.com/view/book/9789004398177/back-3.xml ; metin kopyası (erişilemedi): https://dokumen.pub/venetian-shipping-from-the-days-of-glory-to-decline-1453-1571-9004398163-9789004398160-9789004398177.html ; inceleme: https://www.researchgate.net/publication/353391191
- Lane, F. C. (1934). *Venetian Ships and Shipbuilders of the Renaissance.* JHU Press. https://www.press.jhu.edu/books/title/2977/venetian-ships-and-shipbuilders-renaissance ; özet: https://test.blackwells.co.uk/bookshop/product/Venetian-Ships-and-Shipbuilders-of-the-Renaissance-by-Frederic-Chapin-Lane/9781614274995
- Tenenti, A. (1967). *Piracy and the Decline of Venice 1580–1615.* UC Press. https://www.ucpress.edu/books/piracy-and-the-decline-of-venice-1580-1615/paper
- Fontenay, M., Revista Áreas (Murcia). https://revistas.um.es/areas/article/download/145601/130251/548571
- "The Sound and the Fury" (Mediterranea). https://storiamediterranea.it/wp-content/uploads/mediterranea/p2357/The%20Sound%20and%20the%20Fury.pdf
- *L'esclavage en Méditerranée et dans l'Atlantique nord (1571-1700).* https://books.openedition.org/cvz/1134
- Venedik deniz ticareti ve Arsenale (1606). https://dergipark.org.tr/en/download/article-file/4269003
- Malta korsanlığı. https://www.um.edu.mt/library/oar/bitstream/123456789/22300/1/2004%20%28b%29.The%20Order%20of%20St%20John%20and%20corsairing%20in%20the%20Meditterranean%20in%20the%2016th%20and%20the%2017th%20Centuries.pdf
- Kalouptsidi, M. (2014). Time to Build and Fluctuations in Bulk Shipping. *AER* 104(2): 564-608. https://ideas.repec.org/a/aea/aecrev/v104y2014i2p564-608.html
- Beenstock, M., Vergottis, A. (1989). An econometric model of the world shipping market. *Applied Economics* 21(3). Tez: https://openaccess.city.ac.uk/id/eprint/7940/1/An_econometric_model_of_the_world_shipping_markets.pdf
- Tsolakis, S. (2005). Econometric analysis of bulk shipping markets (tez). https://repub.eur.nl/pub/6717/Phd_Stavros_Tsolakis_9June05.pdf
- Kydland, F., Prescott, E. (1982). Time to Build and Aggregate Fluctuations. *Econometrica* 50(6) ⚠️
- İkinci el / yeni gemi oranları: https://www.seatrade-maritime.com/tankers/secondhand-to-newbuild-price-ratios-signal-shipowners-sentiment ; https://pyxida.aueb.gr/server/api/core/bitstreams/b45b53e3-c701-45d4-8530-e63593f26404/content
