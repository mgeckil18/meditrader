# 14 — Giriş-Çıkışı Doğal Mekanizmalara Bağlamak: Öneriler
> Durum: taslak (öneriler; kullanıcı kararı bekleniyor)
> Son güncelleme: 2026-11-02
> İlgili: [D5b3g](../../experiments/D5b3g.md), [11](11-entry-barriers.md), [12](12-entry-decision-timing.md), [durum özeti](../../process/durum-2026-11-02.md), K-029, S-020, framework İ12

**Kullanıcı yönü (2026-11-02):**
- Bant (R) geçici; düzeltmek gerektiğinde düzeltilecek.
- Her şey hem tarihsel hem ekonomik olarak doğru olmalı. Tepeden kodlanmış ayarlar değil, doğal olarak gelişen davranış isteniyor (framework İ12).
- Şimdilik bugünkü yapı kalabilir.

**Kaynak işaretleri:**
- 🔎: bu oturumda arama sonucuyla görüldü (çoğu ikincil özet, birincil metin okunmadı).
- ⚠️: künye bellekten; birincil kaynaktan kontrol edilmedi.
- İşaretsiz: ders kitabı düzeyinde standart sonuç.

## 1. Bugün modelde tepeden ayarlanan neler var?

| Düğme | Değer | Ne yerine geçiyor? |
|---|---|---|
| Eşik = senet + risk primi | %4 + %4 | Yatırımcının alternatifleri ve risk tutumu |
| Band κσ (R) | κ = 1 | Batık maliyet (gemi alınırken pahalı, satılırken ucuz) |
| Teyit 3 × 3 ay (U) | 3, 3 | Yatırım hazırlığının süresi ve kanıt toplama |
| Credibility k | 9 | Kendi sicilinin ne kadar bilgi taşıdığı |
| Giriş dikkati | %2 / ay | Yatırımcının fırsatı fark etme ve sermayeyi bağlama hızı |
| Donatım gecikmesi | 30-60 gün | Gemi bulmak ya da yaptırmak |
| Kamu sicili | toplam getiri, 12 ay | 16. yy yatırımcısının gerçekte bildiği |

İlke İ12 açısından hedef: Bu düğmelerin her biri ya (a) tarihsel ya da ampirik bir değere bağlanmalı, ya (b) modelin kendi verisinden çıkmalı, ya da (c) tamamen kalkıp yerine fiziksel ve kurumsal bir mekanizma gelmeli.

## 2. Öneriler (önerilen sırayla)

### Ö0. Ölçüm ve yöntem: önce neyi ölçtüğümüzü sabitleyelim (ucuz, ilk)

**Ne:**
1. Seed sayısı 4 → 10; her ölçütte seed'ler arası güven aralığı.
2. Getiriyi üç ayrı ölçüyle raporlamak: toplam getiri (K-025), kamu sicili, giren kuşağın getirisi. Aralarındaki farkın kaynağını ölçmek (yerleşik kârı mı, ölçüm penceresi mi).
3. "Hedef %8" yerine **birden çok tarihsel ve ekonomik örüntü** ile doğrulama:
   - İflas ve çıkış oranı
   - Getiri dağılımının çarpıklığı
   - Filo döngüsünün süresi ve genliği
   - Gemi fiyatı oynaklığı (Ö3 gelince)

**Bilimsel dayanak:**
- **Pattern-oriented modeling:** Bir model, tek bir sayıyı tutturmasıyla değil, birden çok bağımsız örüntüyü aynı anda üretmesiyle doğrulanır (Grimm ve ark. 2005, *Science* 310 ⚠️).
- ABM'de stylized facts ile doğrulama (Fagiolo, Moneta & Windrum 2007 ⚠️).
- Tek hedefe ayarlamak "overfitting"in ABM'deki karşılığıdır: model doğru sayıyı yanlış nedenle üretebilir.

**Neden ilk:** Sonraki her öneri bu ölçütlerle değerlendirilecek. Bugünkü 4 seed'de tepe / dip gibi uç değer ölçütleri çok oynak (-k36'da 70-86).

### Ö1. Credibility k'yı modelin kendi verisinden tahmin etmek (ucuz)

**Ne:** k = 9 yerine Bühlmann'ın kendi formülü kullanılır:

  k = (bir tüccarın kendi getirisindeki sefer-sefer gürültü, ortalama) / (tüccarların gerçek ortalama getirileri arasındaki fark)

Yani k bir varsayım olmaktan çıkar, verinin bir özelliği olur. Tüccarlar gerçekten farklıysa (beceri, bilgi) kendi sicillerine çok güvenirler. Fark çoğunlukla şanssa kamu siciline güvenirler.

**Bilimsel dayanak:**
- Bühlmann (1967), *ASTIN Bulletin* 4: credibility ağırlığı Z = n / (n + k), k = E[süreç varyansı] / Var[gerçek ortalamalar] ⚠️ (formül standart).
- Bühlmann & Straub (1970) ⚠️: farklı hacimli gözlemlerle genelleme.
- Empirical Bayes: bu oran kitlenin kendi verisinden tahmin edilir.

**Tarihsel karşılık:** Bir yatırımcı, bir tüccarın "şanslı mı, usta mı" olduğunu bu formülle değil sezgiyle ayırır. Ama formül, sezginin doğru olduğu durumu tanımlar: hem rasyonel bir kıyas noktasıdır hem de oyuncuya okunabilir.

**Not:** D5b3b'de sıralama formülünün getiri ayırt etmediği bulunmuştu (skill vs luck). k'nın veriden büyük çıkması (yani kendi sicile az güven) bu bulguyla tutarlı olur. -k36 sonucu da önemli: k büyüyünce herkes aynı kamu siciline bakıyor ve topluca çıkıyor. Doğal k o rejime düşerse, bu bir artifact değil, bilgi yapısının sonucudur. O zaman çözüm Ö4'te (bilgi).

### Ö2. Eşiği yatırımcının gerçek alternatiflerine ve risk tutumuna bağlamak (K-029 doğrulaması; bu hafta)

**Ne:**
1. **Senet getirisi tarihsel kaynaktan alınır.**
   - Venedik devlet borcu (Monte Vecchio / Nuovo / Novissimo) ve Cenova Casa di San Giorgio luoghi getirileri.
   - Cipolla (1952) 16. yy San Giorgio getirilerini izlemiştir. 1435 için luogo başına %4 faiz gösteren bir kaynak var 🔎.
   - Venedik değerleri kaynaktan doğrulanacak; Pezzolo ⚠️.
   - Not: 16. yy sonu - 17. yy başı Cenova'da faizlerin çok düştüğü biliniyor (Homer & Sylla, *A History of Interest Rates* ⚠️). Senet getirisi sabit değil, zamanla değişen bir dünya değişkeni olabilir.
2. **Alternatif yatırımlar eklenir.** Gerçek fırsat maliyeti yalnızca senet değildi:
   - Toprak (16. yy Venedik soylularının terraferma'ya yönelişi ⚠️)
   - Deniz ödüncü ve colleganza (zaten modelde)
   - Kira ve ofis
3. **Risk primi sabit %4 değil, yatırımcının risk tutumundan ve gerçek getiri oynaklığından doğar.**
   - Arrow-Pratt: küçük riskler için risk primi ≈ ½ · A · σ². A = mutlak riskten kaçınma, σ² = getiri varyansı (Arrow 1965; Pratt 1964, *Econometrica* 32; standart sonuç).
   - Yatırımcılar arasında A heterojen dağılır. Dağılım ampirik risk tutumu çalışmalarına bağlanır: göreli riskten kaçınma (CRRA) çoğu çalışmada kabaca 1-4 aralığında ⚠️ (ör. Holt & Laury 2002, *AER* 92 ⚠️).
   - Sonuç: Savaş, korsanlık ya da kıtlık getiri oynaklığını artırınca prim kendiliğinden yükselir ve giriş yavaşlar. Bunun için ayrı bir kural gerekmez.
4. **Doğrulama için tarihsel kontrol değerleri:**
   - Deniz sigortası primleri: 16. yy Akdeniz'de sefere göre değişen yüzdeler; Cenova / Floransa / Venedik sigorta kayıtları ⚠️.
   - Deniz ödüncü faizleri ⚠️.
   - Bunlar eşiği ayarlamak için değil, modelin ürettiği primin makul olup olmadığını kontrol etmek için kullanılır.

**Bilimsel dayanak:**
- Normal profit = fırsat maliyeti + risk primi (standart).
- Fırsat maliyeti yatırımcının en iyi alternatifidir; tek bir sabit değil.

### Ö3. Gemi piyasası: bandın doğal yerine geçmesi (ana yapı; önce tasarım tartışması)

**Ne:** Gemi, alınıp satılan dayanıklı bir varlık olur.
- **Giriş = gemi edinmek:**
  - (a) Çıkan tüccardan ikinci el almak, ya da
  - (b) Tersanede yaptırmak. Yaptırmak zaman alır (aylar), tersane kapasitesi sınırlıdır ve kereste maliyetine bağlıdır.
  - (c) İleride: kiralamak (noleggio).
- **Çıkış = gemiyi satmak.** Alıcı yoksa ya da fiyat çok düşükse:
  - Gemiyi bağlamak (laid-up; masrafı düşük, gelirsiz bekleyiş), ya da
  - Sökmek (kereste değeri).
- **İkinci el fiyatı piyasada oluşur.** Alıcıların teklifi, geminin beklenen kazancının bugünkü değeridir. Kötü dönemde çok gemi satılığa çıkar, fiyat düşer. İyi dönemde az satılık gemi vardır, fiyat yükselir, yeni yapım devreye girer.
- **Yaşlanma:** Gemi yıprandıkça değeri ve verimi düşer; doğal bir çıkış kanalı oluşur ⚠️ (geminin ömrü kaynaktan belirlenmeli).

**Neden bu, bandın doğal yerine geçer:**
1. **Hysteresis kendiliğinden doğar.** Batık maliyet ve belirsizlik altında optimal giriş eşiği tam maliyetin üstünde, çıkış eşiği altındadır (Dixit 1989, *JPE* 97(3) ⚠️; Dixit & Pindyck 1994, bölüm 7-8 ⚠️).
   - Gemi piyasasında batık maliyet, yeni gemi fiyatı ile ikinci el ya da söküm değeri arasındaki farktır. κ gerekmez; band genişliği bu fiyat farkından çıkar.
   - Shipping'de real options modeliyle giriş-çıkış eşikleri türetilmiştir (Balliauw, Antwerp working paper 2015; Ruiz-Aliseda & Wu 2012 modeli) 🔎.
2. **Fiyat, döngüye karşı çalışır.**
   - Shipping ekonomisinde ikinci el gemi fiyatı navlunla güçlü biçimde birlikte hareket eder; gemi bir gelir varlığıdır ve fiyatı beklenen kazancı yansıtır 🔎 (ampirik çalışmalar; Stopford, *Maritime Economics* ⚠️).
   - İkinci el piyasası, sahiplerin yeni yapım ve sökümden daha hızlı büyüyüp küçülmesini sağlar 🔎.
   - Sonuç: Patlamada pahalı gemi alan yatırımcının getirisi düşük olur. Bu da giriş kararına kendiliğinden yansır (yatırımcı beklenen kazancı gemi fiyatına böler). Döküntüde ucuz gemi, sabırlı yatırımcıya fırsattır. Bu tarihsel olarak da makul bir oyun dinamiği: "dipte gemi al".
3. **Yeni yapım gecikmesi döngüyü güçlendirebilir.** Bu bir risk ve bir gerçek: Shipping'de sipariş ile teslim arasındaki gecikmenin döngüyü büyüttüğü biliniyor 🔎 (time-to-build; Kydland & Prescott 1982 ⚠️). Ama ikinci el piyasası, kısa dönemde giriş fiyatını yükseltip girişi süzer; gecikmeli yapım ancak fiyat yeterince yükselince başlar. Bu iki etkiyi deney gösterecek. Döngünün kalması İ11'e göre hata değil, sınıflandırılır.
4. **Uzun dönem getirisi rant yaratmaz.** A türü bariyer (herkese eşit batık maliyet) dengede getiriyi sermaye maliyetinin üstüne kalıcı olarak çıkarmaz ([11 §1](11-entry-barriers.md)). Rekabetçi dengede batık maliyet altında da miyop davranış optimaldir ve fiyat giriş tetiğinde tavanlanır (Leahy 1993, *QJE* 108(4) ⚠️).
   - Bugünkü "sistem bandın üst kenarında, getiri %16-18" sorunu buradan bakınca kuralın ürünü: band genişliği sabit, ama giriş bedeli yok. Kalıcı rantın gerekçesi yok.
   - Gemi piyasasında üst kenardaki kâr, gemi fiyatına yansır (rant gemi sahibine, yani varlığa gider; yeni girenin sermaye getirisine değil).

**Tarihsel dayanak:**
- Lane, *Venetian Ships and Shipbuilders of the Renaissance* (1934) 🔎: gemi maliyetleri, navlun ve kereste üstüne bölümler var.
  - 15. yy sonu bunalımında özel yapım büyük gemi sayısı azaldı; 400 ton üstü bir geminin sermayesi tek bir yapımcı için fazlaydı.
  - 16. yy ortasında, Venedik yasası açıkça yasaklasa da küçük gemiler bile dışarıdan satın alınıyordu.
- **Kereste kıtlığı:** 16. yy ortasında özel yapım gemilerde kullanılan meşenin çoğu Venedik toprakları dışından alınıyordu; koruma çabaları başarısızdı 🔎 (Lane; Appuhn, *A Forest on the Sea* 2009 ⚠️). Bu, tersane maliyetini zamanla değişen bir dünya değişkeni yapar. Üretim zinciriyle (D4c) bağlanabilir.
- **Gemi payları (carati):** Bir geminin maliyeti 24 eşit paya bölünebiliyordu; bu, tek kişinin yetemediği sermayeyi toplamanın ve riski bölmenin yoluydu 🔎 (kadırga işletmesi örneği üzerinden). Bu, ileride sermaye havuzunun gerçekçi bir biçimi olabilir.

**Ne kalkar:** Band (R) kalkar; ablation ile doğrulanır (gemi piyasası + band yok). Donatım gecikmesi tersane ve ikinci el arzından doğar. Giriş dikkati muhtemelen fiyatla birlikte gereksizleşir; ablation ile bakılır.

**Riskler ve açık tasarım soruları (kullanıcıyla):**
- Kapsam büyük: yeni bir varlık piyasası, fiyat oluşumu ve yaşlanma.
- İkinci el fiyatı nasıl oluşur? Kapan benzeri bir çağrılı pazar mı, ikili pazarlık mı?
- Gemi tipi çeşitliliği (kadırga, nave, küçük gemiler) şimdi mi, sonra mı?
- Oyuncu açısından okunabilirlik: gemi fiyatı listesi oyuncuya doğal bir "piyasa termometresi" olur (İ6, İ7 açısından artı).

### Ö4. Bilgi: kamu sicilini 16. yy yatırımcısının gerçekten görebildiğiyle değiştirmek (sonra)

**Ne:** 16. yy'da "bütün tüccarların toplam sermaye getirisi" diye bir kamu istatistiği yoktu. Yatırımcı şunlara bakardı:
- Kendi ağındaki tüccarların sonuçları (mektuplar, muhabirler)
- Limana dönen ya da batan gemiler
- Fiyat listeleri (price current)
- Söylenti

Modelde bunların çoğu zaten var: söylenti (K-014), muhabir ağı (E2) ve bilginin taşınması (İ5). Kamu sicili bunlarla yer değiştirir: her yatırımcının sicil tahmini, gördüğü örnekten çıkar.

**Bilimsel dayanak:**
- Social learning ve information cascade (Banerjee 1992, *QJE* 107 ⚠️; Bikhchandani, Hirshleifer & Welch 1992, *JPE* 100 ⚠️).
- Örneklem farklı olunca yatırımcılar farklı inançlara ulaşır. Bu, -k36'da görülen "herkes aynı sinyale bakıp topluca çıkıyor" sorununu doğal yoldan kırar (inanç heterojenliği).
- Tarih: tüccar mektupları ve price current'lar (McCusker & Gravesteijn 1991 ⚠️); Datini arşivi; Trivellato ⚠️.

**Neden sonra:** Ö3 ile etkileşir. Gemi fiyatı da bir bilgi kaynağıdır ve limanda görülebilir. Ayrıca bilginin kendisi projenin kalbi (İ5); dikkatli tasarlanmalı.

### Ö5. Teyitli girişi (U) yeniden değerlendirmek (Ö3'ten sonra)

U, gemi piyasası gelince gereksizleşebilir: Gemi yaptırmanın süresi ve ikinci el fiyatının yükselmesi, U'nun yaptığı süzmeyi doğal yoldan yapar. Ö3'ten sonra U kapalı / açık ablation'ı yapılır.

U kalırsa, 3 × 3 ay sabit değil, kanıt toplama sınırından türetilmeli. Kanıt toplamanın bir maliyeti (zaman, kaçan fırsat) varken optimal durma kuralı: Wald (1947) SPRT ⚠️; drift diffusion, Ratcliff (1978) ⚠️.

## 3. Önerilen sıra ve gerekçesi

| Sıra | Öneri | Maliyet | Neyi değiştirir |
|---|---|---|---|
| 1 | Ö0 ölçüm ve yöntem | Düşük (koşu süresi uzun) | Sonraki her kararın güvenilirliği |
| 2 | Ö1 credibility k veriden | Düşük | Bir keyfi parametre kalkar |
| 3 | Ö2 eşik bileşenleri (literatür doğrulaması) | Orta (okuma) | Seviyenin tarihsel ve ekonomik dayanağı; kullanıcının bu haftaki doğrulama notu |
| 4 | Ö3 gemi piyasası | Yüksek (tasarım + kod) | Band ve büyük olasılıkla U kalkar; hysteresis ve maliyet doğal hale gelir |
| 5 | Ö4 bilgi | Yüksek | Kamu sicili kalkar; inanç heterojenliği |
| 6 | Ö5 U'nun yeniden değerlendirilmesi | Düşük | Ö3'ten sonra |

**Bu sırayla gitmenin mantığı:** Önce ölçüm (yoksa neyin düzeldiğini bilemeyiz). Sonra ucuz ve yalnızca keyfiliği kaldıran adımlar. Sonra yapısal değişiklik. Yapısal değişiklik her seferinde bir tane: Ö3 ile Ö4'ü birlikte yaparsak hangisinin ne yaptığını ayıramayız.

## Oyun için çıkarımlar

1. Gemi piyasası hem en önemli doğal sönümleyici hem de oyun için zengin bir mekanik. Oyuncu "dipte ucuz gemi al, tepede sat" ya da "patlamada gemi yaptırmanın tuzağı" gibi gerçek shipping stratejilerini yaşar.
2. Risk primi oynaklığa bağlı olunca savaş ve korsanlık haberleri, kural eklemeden yatırımı yavaşlatır. Oyuncu bunu okuyabilir: "korsan haberi → yatırımcı çekiliyor → az gemi → yüksek navlun".
3. Bilgi temelli sicil (Ö4), İ5'i (bilgi taşınır ve eskir) giriş kararına da yayar. Uzak limandaki patlamayı geç duyan yatırımcı geç girer; bu da coğrafyaya bağlı döngüler üretir.
4. Her öneri bir tepeden ayarı kaldırıyor (İ12). Kalan düğmeler (A dağılımı, tersane kapasitesi, gemi ömrü) tarihsel ya da ampirik kaynaklara bağlanabilecek türden.

## Kaynaklar (bu oturumda görülen)
- [Bulk Shipping Markets in Maritime Economics (handybulk)](https://www.handybulk.com/bulk-shipping-markets-in-maritime-economics-freight-rates-ship-prices-fleet-size-and-market-interaction/)
- [Balliauw, University of Antwerp RPS-2015-013](https://medialibrary.uantwerpen.be/oldcontent/container1244/files/TEW%20-%20Onderzoek/Working%20Papers/RPS/2015/RPS-2015-013.pdf)
- [Bank of Saint George (Wikipedia)](https://en.wikipedia.org/wiki/Bank_of_Saint_George)
- [Cipolla 1952 özeti (openedition)](https://books.openedition.org/igpde/3982?dir=next)
- [San Giorgio, 1435 %4 (memoriedigitaliliguri)](https://memoriedigitaliliguri.it/Docs/Biblioteca_Digitale/SB/396b22c37e8bbc6c44c30828fc127900/Estratti/f72d5b0211a938ffd0a20ec54e436848.pdf)
- [Lane, Venetian Ships and Shipbuilders, yayıncı özeti](https://test.blackwells.co.uk/bookshop/product/Venetian-Ships-and-Shipbuilders-of-the-Renaissance-by-Frederic-Chapin-Lane/9781614274995)
- [Kereste, 16. yy (um.edu.mt)](https://www.um.edu.mt/__data/assets/pdf_file/0008/96074/ozverenyildirim2006.pdf)
- [Carati (weaponsandwarfare)](https://weaponsandwarfare.com/?p=22590)
