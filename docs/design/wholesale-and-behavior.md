# Toptan Pazar ve Tüccar Davranışı (tasarım)
> Durum: **kararlaştı, uygulanıyor** (kullanıcı onayı 2026-10-23: K-013, K-014, K-016)
> İlgili: [D5](../experiments/D5.md), [codex/behavior](../codex/behavior.md), [codex/institutions](../codex/institutions.md), [information-model](information-model.md)

## 1. Kurumsal toptan pazar (kapan / loggia) — K-013

**Neden:** D5'teki dokuz sorunun çoğu, bütün ticaretin yerel perakende dükkâncılarından geçmesinden doğdu. Tarihsel karşılık: İstanbul kapanları, Venedik Rialto'su, Sicilya caricatori'si. Kuramsal karşılık: aracılık teorisi (Rubinstein & Wolinsky 1987; Spulber 1996) ve piyasa kurumunun önemi (Gode & Sunder 1993).

**Karar kuralı (kullanıcı):** Kurumsal pazar sorunları çözerse öyle kalır. Çözmez ve neden ajan eksikliğiyse, toptancı ajanlar eklenir.

### Mekanizma
Her limanda her mal için **günlük bir toptan takas** (call auction, tek fiyat):

| Satıcılar | Fiyatı |
|---|---|
| Köylü / dışsal arz havuzu | Arz eğrisi: fiyat yükseldikçe daha çok satar |
| Üretici havuzu (atölyeler) | Birim maliyet; stok şiştikçe altına iner |
| Gelen tüccar (kargo) | Kendi rezervasyon fiyatı (sabırla düşer) |
| Stokçu | Satış eşiği |
| Dükkâncı (fazla stok) | Kendi teklifi |

| Alıcılar | Fiyatı |
|---|---|
| Dükkâncı (perakende için yenileme) | Kendi teklifi (PI kuralı) |
| İhracatçı tüccar | Beklenen net satış değerinden türettiği azami fiyat |
| Üretici havuzu (girdi) | Ürün değerinden türeyen azami girdi fiyatı |
| Stokçu | Alış eşiği |

- **Takas:** Toplam talep ve arz eğrilerinin kesiştiği tek fiyat (uniform price). Kesişim fiyatının altında satmak isteyen ve üstünde almak isteyen herkes işlem yapar.
- **Kapan resmi:** İşlem değerinin küçük bir payı (ör. %1), para yutağı.
- **Bilgi:** Günün toptan fiyatı limanda **kamuya açık**. Limanda olan herkes görür; uzaktakiler haberle öğrenir. İşlem olmayan oturumda açık fiyat **en yüksek alış teklifidir** (K-017, [D5a3](../experiments/D5a3.md)): yokluğun da bir fiyat sinyali var.
- **Kapasite:** Takas odasının deposu yok. Malı satıcılar getirir, alıcılar götürür. Kapasite darboğazı yapısal olarak ortadan kalkar.
- **Perakende:** Dükkâncılar kente satmaya devam eder. Stoklarını toptan pazardan yeniler; yerine koyma maliyeti = toptan fiyat. Fiyatlama: §1b.

### Açık uçlar
- Aracı likidite tuzağı: dükkâncılar ve üreticiler için giriş-çıkış (D3b mekanizması) ve basit veresiye. Toptan pazar bunu azaltmalı ama tamamen çözmeyebilir.
- Liman içi bilgi asimetrisi azalır (herkes aynı fiyatı görür); bu kabul edilebilir, çünkü fırsatlar limanlar arası.

### Deney sonucu (D5a)
[D5a](../experiments/D5a.md): Kapan, D5'teki darboğaz ve likidite tuzaklarını el yaması olmadan çözdü (0/5 patlama, 0/18 tuzakta dükkân). Toptancı ajanlara şimdilik gerek yok. Kalan sorun: ticaret yoğunluğu (fark/maliyet 3-5) → D5b.

## 1b. Rekabetçi perakende — K-016

**Neden:** D5a'da perakende fiyatı toptan fiyata mekanik bir kuralla çekiliyordu. Kullanıcının itirazı: Fiyatı toptana yakın tutacak olan **rekabet** olmalı; fiyat yükseltmenin **rekabetçi bir maliyeti** (müşteri kaybı) olmalı.

| Parça | Kural |
|---|---|
| Maliyet | Yerine koyma maliyeti = açık toptan fiyatın kısa ortalaması (3 gün) |
| Müşteri | Logit seçim: hedef pay ∝ fiyat^−β; pay hedefe ~30 günde yaklaşır (switching cost); mal bulamayan müşteri kopar |
| Marj | Lerner: μ = 1/(ε_i − 1), ε_i = β(1−s_i) + ε_pazar·s_i |
| Alış | Türetilmiş talep: kapan'a kademeli emir; hedef stok = 30 günlük satış × (w/ref)^−ε, gözlenen fiyat aralığının en çok %50 üstüne kadar |
| Giriş-çıkış | Aylık, D3b mekanizması, 12 aylık **işletme kârına** göre: getiri senet + primin üstündeyse yeni dükkân, senedin altındaysa kapanır |
| Geçim | Dükkâncının günlük geçimi sabit gider (tüccarla eşit); dükkân sayısını pazar büyüklüğü belirler |
| Fiyat keşfi (K-017) | Müşterilerini geri çeviren dükkâncı teklifini yükseltir (tâtonnement), müşterilerinin ödediği en yüksek fiyatla sınırlı |

**Sonuç ([D5a2](../experiments/D5a2.md)):** Marj kuramın öngördüğü değerde (3 dükkân %14; geçimli serbest girişte büyük pazarda %9-11 ve 15-31 dükkân, en küçük pazarda %13 ve 4 dükkân; alt sınır 1/(β−1)). Aktarım bir ayda %80-100 ve simetrik. Kıtlık artık boş rafla değil fiyatla paylaştırılıyor. Rockets and feathers çıkmadı: bunun için müşterinin arama yoğunluğu fiyatın yönüne bağlı olmalı (kullanıcı: şimdi değil, akılda tutulacak; framework §8).

**Açık:** β ve dükkân sabit giderleri (S-013); kıtlık zirvelerinin büyüklüğü (arz tarafı, D5b).

## 2. Tüccar çeşitliliği ve rakip bilgisi — K-014

**Neden:** D5'te homojen tüccarlar aynı en kârlı nişe koştu (El Farol problemi). Kullanıcının sezgisi ve literatür (Arthur 1994; Challet & Zhang 1997): tahmin yöntemleri çeşitlenince katılım kendiliğinden kapasite etrafında dengelenir. Uyarı: çeşitliliğin dağılımı yanlışsa çağlayan doğurabilir (Granovetter 1978; Banerjee 1992).

### Tüccar kişiliği (dağılımlardan çekilir)

| Boyut | Model | Kaynak |
|---|---|---|
| **Düşünme derinliği** | Level-0: yalnızca fiyata bakar. Level-1: duyduğu rakip kargoyu derinlikten düşer (kalabalık öngörüsü). Level-2: level-1'lerin kaçınacağını öngörür, kısmen geri ekler. | Nagel (1995); Camerer, Ho & Chong (2004) |
| **Taklit eğilimi** | Duyduğu rakip davranışını "onlar bir şey biliyor" diye çekicilik sinyali olarak da okuyabilir (çağlayan kaynağı; fenomen olarak korunur) | Banerjee (1992); BHW (1992) |
| **Risk tutumu** | Servete bağlı: zengin daha az risk kaçınır; batma eşiğine yakın tüccar safety-first davranır | Arrow-Pratt (DARA); Roy (1952) |
| **Aşırı güven** | Algılanan belirsizlik gerçeğin bir katı (<1 aşırı güven) | Odean (1998); DHS (1998) |
| **Bilgi kaynakları** | Kendi gözü, gemi haberi (söylenti), ileride temsilci mektupları. Her kaynağın gerçek ve algılanan doğruluğu ayrı. | Information-model; Greif; Trivellato (2009) |

### Rakip davranışı bilgisi
- Bir gemi limandan kalkınca **"X, Y'ye Z yükledi"** bilgisi o limanda söylenti olarak yayılır (günlük duyma olasılığı), sonra gemilerle diğer limanlara taşınır.
- Bu bilgi davranışın **sonucundan önce** gelir: varış ve fiyat çöküşü haftalar sonra.
- Nasıl kullanılacağını tüccarın düşünme derinliği ve taklit eğilimi belirler.
- D5'teki "rakip kargoyu anında bil" basitleştirmesinin yerini alır.
- **Limanda bekleyen kargo** limandaki herkesçe görülür ve gemilerle haber olarak taşınır (D5b'de eklendi).
- Rakip bilgisi rota değiştirme kararında da kullanılır.

**Sonuç ([D5b](../experiments/D5b.md)):** Rakip bilgisi olmadan biber nişi bütün tüccarları Korfu'da kilitliyor (5/5 patlama, Venedik açlıkta). Rakip bilgisiyle 0/5. Homojen düzey 1 yeterli: çeşitliliği bilginin dağınıklığı sağlıyor. Kişilik çeşitliliği getiriyi belirliyor: düzey 0 −%5, düzey 1-2 +%37-39; taklit ve aşırı güven kaybettiriyor. Taklit bu güçte çağlayan doğurmadı. Kalan: ince pazar tuzağı (satış kararı) ve yavaş giriş (rant).

## 3. Deney planı

| Deney | Kurulum | Soru |
|---|---|---|
| **D5a** | 3 liman (İskenderiye: buğday ihracatı; Korfu: yağ ihracatı; Venedik: ikisini ithal eder), 2 mal; homojen tüccarlar, D5 yamaları kapalı | Toptan pazar D5'in darboğaz ve likidite sorunlarını, el yaması olmadan çözüyor mu? Karşılaştırma: dükkân-only / D5 yamaları / toptan pazar |
| **D5a2** | D5a + rekabetçi perakende (K-016) | Perakende fiyatı rekabetle toptana iniyor mu? ✅ |
| **D5a3** | D5a2 + malı olmayan pazarda fiyat keşfi (K-017) | Venedik neden yağsız kalıyor? ✅ donmuş fiyat |
| **D5b** | D5a3 + tüccar çeşitliliği + rakip bilgisinin söylentiyle yayılması; biraz daha çok mal (biber gibi değerli bir niş) | Çeşitlilik en kârlı niş herding'ini tamponluyor mu, yoksa çağlayan mı doğuruyor? |
| **D5b2** ✅ | G/B/S/L faktöriyel ([D5b2](../experiments/D5b2.md)) | Tuzağın kalan kısmı Zeno artifact'ıydı; L en etkili; S fazla gönderim üretiyor, B'nin kendi-etkisi dengeliyor; temel beklenti yeniden tasarlanacak (S-014). Önerilen yapı GBSL·imp |
| **D5b3** ✅ | Başlangıç ve giriş (K-020): spin-up ile kararlı başlangıç; liman başına sermaye havuzu; kamuya açık price current'tan fırsat; yatırımcı eşik dağılımıyla giriş; colleganza | ✅ [D5b3](../experiments/D5b3.md): rant eriyor (%33 → %1-5) ama hedefin altına iniyor (fazla giriş, kalibrasyon); spin-up çalışıyor; hafif entry cobweb; colleganza adverse selection'la zarar ediyor → itibar adayı. Bulunan hata: bütçesiz dükkân teklifi |
| **D5b3b** ✅ | Colleganza + itibar (K-021) | İtibar kapısı tutuldu; sıralama bilgi taşımıyor; denge getirisi hedefin altında → konuşulacak. [D5b3b](../experiments/D5b3b.md) |
| **D5b3c** ✅ | Hibrit finansman (K-022) | Karar istenen yönde; borç sürdürülemez (oynaklık); sıradaki: oynaklık teşhisi. [D5b3c](../experiments/D5b3c.md) |
| **D5b3d** ✅ | Sefer bazlı alacaklı + batma bedeli + gemi masrafı (K-023, K-024) | Kalabalık filodan bağımsız → D5b4'e taşındı. [D5b3d](../experiments/D5b3d.md) |
| **D5b4** | Beklenti turnuvası (S-014): tüccar havuzlarında farklı beklenti modelleri ve karışımları (C4/çapalama, bilgi temelli temel, trend, HSM) | Hangisi piyasayı dengede tutuyor, kim kazanıyor, trend kuralı sönüyor mu? |
| **D5c** | Tam dilim (6 liman, 9 mal, üretim ve ihracat) | Hepsi bir arada; ihracatlı Labrousse testi |
