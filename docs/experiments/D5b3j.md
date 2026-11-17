# D5b3j — Ö3: Gemi Piyasası (band yerine)
> Durum: taslak (koşular sürüyor)
> Son güncelleme: 2026-11-06
> İlgili: [D5b3i](D5b3i.md), [D5b3h](D5b3h.md), [14-natural-entry-exit §Ö3](../research/simulation/14-natural-entry-exit.md), [shipping-scale-16c](../research/history/shipping-scale-16c.md), [15-macro-abm-methods](../research/simulation/15-macro-abm-methods.md), K-032, K-031, K-030, İ12

## Kullanıcı kararı (2026-11-06, K-032)
- Gemi kaybıyla devam (seçenek a): batan gemi sermaye olarak gider.
- Ö3 öne çekiliyor. Bant sorununun (D5b3i: σ kendi döngüsünden besleniyor) doğal yoldan düzelmesi bekleniyor.
- "Bu işleri doğru olacağını bildiğin şekilde yap." Uygulama seçimleri Claude'un; aşağıda gerekçeleriyle. Hepsi **Claude ekledi, kesin değil** (kural 7d).

## Mekanizma (`ship_market=True`)

### Gemi bir varlık
- Her tüccarın bir gemisi var. Geminin yapım günü tutulur.
- **Yerine koyma değeri R:** yeni bedel (0,5 × sermaye = 120.000 ⚠️), 15 yılda (⚠️) doğrusal olarak söküm değerine (%10 ⚠️) iner.
- **Sicil değeri** = öz sermaye + temettü + R.
  - Batma ve yaşlanma sicile kayıp olarak girer.
  - Gemi piyasası fiyatı sicile girmez. Böylece fiyat şişmesi getiri gibi görünüp kendini beslemez; D5b3i'deki bant sorununun dersi.
- Batan ya da yakalanan gemi gider (`ship_loss` vekili kullanılmaz). Ömrünü dolduran gemi limanda sökülür; söküm parası tüccara geçer.
- Gemisiz tüccar ticaret yapamaz ve gemi masrafı ödemez.

### Değerleme: Tobin's q
Yatırımcının gemiye biçtiği değer:

  W = R + (beklenen getiri − istenen getiri) × (sermaye + R) × a(r, H)

- Beklenen getiri = kamu sicili (girenler) ya da credibility'li kişisel beklenti (kalanlar, gemisini kaybedenler).
- İstenen getiri r = senet + kişisel risk primi (log-normal, eskisi gibi).
- a(r, H): fazla getirinin H = 3 yıl (`invest_horizon`, eski parametre ⚠️) süreceği beklentisiyle bugünkü değer çarpanı. Fazla getirinin kalıcı sayılmaması rekabetçi piyasanın beklentisidir. Ufuk sonsuz olsaydı fiyat küçük getiri farklarına aşırı tepki verirdi.
- Getiri tam istenen düzeydeyse gemi tam yerine koyma değerindedir (q = 1). Literatürde bilinen sonuç: q > 1 iken yatırım yapılır (Tobin 1969; Hayashi 1982 ⚠️).

### Giriş: gemiyi nereden bulacak?
Teyitli giriş süreci (U) aynı kaldı. Ölçüt "fazla getiri > kişisel prim" yerine **en iyi edinme yolunun artığı > 0**. Üç yol var:

| Yol | Bedel | Ne zaman | Gerekçe |
|---|---|---|---|
| İkinci el | Piyasa fiyatı (aylık takas) | Fit-out 30-60 gün | — |
| Tersane | Yeni bedel, ısmarlarken ödenir | Yapım 180 gün ⚠️ + kuyruk. Kapasite yılda filonun %40'ı (son 5 yıl ortalaması) ⚠️ | Sektörün olağan yenileme ihtiyacına göre boyutlanmış tersane |
| Yabancı hazır gemi | Yeni bedel × 1,25 ⚠️ | Fit-out 30-60 gün | Lane 1934: 16. yy'da dışarıdan gemi alınıyordu. **Dayanak zayıf:** Koloni yapımı daha ucuzdu (Gluzman). Prim, hazır gemiyi bulup getirmenin aciliyet maliyeti vekili |

Yabancı gemi neden eklendi: İlk duman testinde tersane tek kaynaktı. Soğuk başlangıçta kuyruk 6 yıla uzadı ve filo dengeye çok yavaş yaklaştı (yılda net ~%17 büyüme). Yabancı gemi, patlamadaki giriş eşiğini de belirliyor: r + prim × R / ((sermaye + R) × a) ≈ r + 3 puan. Bu, bandın üst kenarının doğal karşılığı.

### İkinci el pazarı: aylık tek fiyatlı takas (kapan ile aynı mantık)
- **Alıcılar:**
  - Teyidi biten yatırımcılar.
  - Gemisini kaybetmiş tüccarlar. Kendi nakdiyle alır; alımdan sonra en az 0,5 × sermaye kalmalı ⚠️.
- **Alıcının teklifi** = W − max(0, tersane artığı, yabancı gemi artığı). Kimse ikinci el gemiye, yeni gemiyi beklemekten ya da dışarıdan almaktan daha kötü bir fiyat ödemez. Bu yüzden ikinci el fiyatı yabancı gemi bedeliyle sınırlı.
- **Satıcılar:** Çıkan ya da batan tüccarın gemisi. Sahibi ana limanın yatırımcı havuzu. En düşük fiyat söküm değeri. Bağlı gemi günde 10 masraf öder ⚠️. Bir yılda satılamazsa sökülür ⚠️.
- **Takas:** Teklifler azalan, satış fiyatları artan sırada eşleşir. Tek fiyat, eşleşen son çiftin arasında. İşlem olmazsa fiyat cetveli en iyi alış teklifini gösterir (D5a3 price discovery kuralı gibi).
- Eşleşmeyen alıcı, artığı pozitifse tersaneye ısmarlar ya da dışarıdan alır. Gemisini kaybetmiş tüccar hiçbir yolu kârlı görmüyorsa çıkar.

### Çıkış: batık maliyet
Sefer sonunda kalma kararında, kalmanın fırsat maliyeti bugün gemiyi satmaktır:

  açık = r − e − (R − satış değeri) / ((sermaye + R) × a)

- **Durgunlukta** gemi R'nin altında satılır. Kalma eşiği düşer ve tüccar zararına satmaktansa bekler. Bu, literatürde bilinen hysteresis (Dixit 1989).
- **Patlamada** gemi R'nin üstünde satılabiliyorsa eşik yükselir: Gemiyi satıp çıkmak cazip hale gelir (asset play).
- Bant (R, `band_kappa`) kaldırıldı.

### Kurulumlar
| Kurulum | Fark |
|---|---|
| `VRS-B-R1-O3`, `F-B-R1-O3` | WTA-UR-B-R1 + gemi piyasası, band yok (κ = 0), U açık |
| `…-O3-noU` | + teyitli giriş kapalı (Ö5 ablation: U gemi piyasasıyla gereksiz mi?) |

- Snapshot'lar gemi piyasasıyla yeniden üretildi (10 yıllık soğuk koşu).
- Karşılaştırma: D5b3i'nin R1 (band açık) ve R1S (gemi kaybı vekili) sonuçları.

### Doğrulama
- Regresyon: Varsayılan yapılandırmada motor eski sürümle birebir aynı (VRS 2 yıl: 24 13 4 14368212).
- Para muhasebesi:
  - Tüccarın ödediği gemi bedeli `shipbuilding`, `ship_purchase` ya da `foreign_ships` olarak defterden çıkar.
  - Söküm `ship_scrap` olarak girer.
  - Havuzlar arası ödemeler defter dışı (havuz zaten defter dışı).

## Duman testi (VRS, soğuk başlangıç, 4 yıl)
- Filo 14 → 55. Soğuk başlangıç patlamasında fiyat endeksi yabancı gemi tavanında (1,25). Tersane kuyruğu ~1,5 yıl.
- Snapshot seçim anlarında kamu sicili:
  - U'lu kurulum: %6,7-7,4 (eşik %8)
  - noU: %7-13,5
  - Bant açıkken %13-15'ti. İlk işaret: kalıcı rant kalkmış olabilir.
- Snapshot'larda donatılan gemi (pending) filonun %2'sinden fazla. Nedeni tersane kuyruğu. Seçim kuralı "ok" demiyor; en küçük sapmalı an seçildi. ⚠️

## Sonuçlar

### VRS (küçük harita), 10 seed × 10 yıl, ortalama ± %95 GA

| Ölçüt | R1 (band) | R1S (band + gemi kaybı vekili) | **O3** (gemi piyasası, band yok) | O3-noU |
|---|---|---|---|---|
| Toplam getiri (öz sermaye + gemi) | %14,0 ± 1,2 | %15,2 ± 1,2 | **%8,9 ± 1,2** | %6,7 ± 0,8 |
| Kamu sicili ortalaması | %13,1 | %10,8 | %8,7 | %11,4 |
| Yerleşik / giren getirisi | %11 / %79 | %11 / %39 | %6 / %12 | %5 / %8 |
| Zarar eden tüccar payı | %24 | %38 | %51 | %55 |
| Giriş / çıkış (gemi-yıl başına) | 0,10 / 0,07 | 0,17 / 0,12 | 0,31 / 0,24 | 0,43 / 0,36 |
| İflas / gemi-yıl | 0,027 | 0,049 | 0,033 | 0,034 |
| Filo ortalaması | 47 | 53 | 70 | 74 |
| Filo CV | 0,26 | 0,33 | **0,20** | 0,23 |
| Filo tepe / dip | 5,7 ± 6,2 | 3,4 ± 0,7 | **2,8 ± 1,3** | 6,9 ± 4,4 |
| Döngü süresi (ay) | 53 | 52 | 45 | 26 |
| Sefer / gemi-yıl | 8,4 | 8,0 | 7,0 | 6,9 |
| Gemi kaybı / gemi-yıl | — | — | 0,145 | 0,144 |

Gemi piyasası (O3):
- **Fiyat endeksi (ikinci el / yerine koyma):**
  - Ortalama 0,52, CV 0,87; en yüksek 1,24 (yabancı gemi tavanı).
  - En düşük 0. Bu bir gösterim kusuru: İşlem olmayan ayda fiyat cetveli, söküm değerinin altındaki en iyi teklifi gösteriyor. Satış değeri hesapta zaten sökümle tabanlanıyor. Düzeltilecek.
- **Fiyat ile kamu sicili arasındaki korelasyon 0,48.** Literatürde bilinen örüntü: ikinci el gemi fiyatı beklenen kazançla birlikte hareket eder (Stopford ⚠️; [15 §2.1](../research/simulation/15-macro-abm-methods.md)). Simülasyon bunu yeniden üretti.
- **Hacim (yılda):** 9 ikinci el işlem, 14,5 tersane siparişi, 1,2 yabancı gemi, 2,7 söküm; ortalama 6 bağlı gemi. Tersane kuyruğu ortalama 282 gün.
- **Gemisini kaybedip yeniden almayan tüccar:** yılda 5,8.
- **Ortalama gemi yaşı 3,1 yıl** (ömür 15 yıl).

### Okuma
1. **Kalıcı rant kalktı.** Toplam getiri %14'ten %8,9'a indi. Bu, eşiğe (senet %4 + prim %4) çok yakın.
   - Literatürde bilinen sonuç: rekabetçi sektörde batık maliyet altında da giriş, getiriyi sermaye maliyetine indirir (Leahy 1993 ⚠️; [14 §Ö3](../research/simulation/14-natural-entry-exit.md) madde 4). Simülasyon bunu yeniden üretti.
   - Bandın getiriyi eşiğin üstünde tutması kuralın ürünüydü; gemi piyasasında üst kenar yabancı gemi primiyle sınırlı (≈ +3 puan).
2. **Filo daha düzenli** (U açıkken): CV 0,26 → 0,20; tepe/dip 5,7 → 2,8.
3. **Giren ile yerleşik arasındaki uçurum kapandı** (%79 / %11 → %12 / %6). Girenler artık gemiye para ödüyor; fırsatı fiyat emiyor.
4. **U hâlâ gerekli (Ö5 ablation).** U kapalıyken filo tepe/dip 6,9, döngü 26 ay (daha hızlı cobweb). Gemi piyasası tek başına U'nun süzmesini yapmıyor. U kalıyor.
5. **Ölçek sorunu baskın hale geldi.**
   - Gemilerin yılda %14,5'i batıyor ya da yakalanıyor. Ortalama gemi 3 yaşında; ömür hiçbir zaman dolmuyor.
   - Giriş ve çıkışın büyük kısmı gemi kaybından geliyor (kaybedip yeniden almayan tüccar, yenileme siparişi).
   - Zarar eden tüccar payı %51. Bunun nedeni gemi kayıpları; tarihsel olarak yüksek ([shipping-scale-16c](../research/history/shipping-scale-16c.md): yıllık kayıp %4-12).
   - Sefer sıklığı düzeltilmeden gemi piyasasının yaş, söküm ve ikinci el örüntüleri anlamlı değil.

**Ölçüm notu:** `agg_old` (eski tanım) gemiyi değerde saymıyor; Ö3'te kullanılmaz. Yerine `agg_eq` (öz sermaye + gemi yerine koyma değeri).

### Tam harita (F), 10 seed × 10 yıl, ortalama ± %95 GA (2026-11-06)

| Ölçüt | R1 (band) | **O3** | O3-noU |
|---|---|---|---|
| Toplam getiri (öz sermaye + gemi) | %13,0 ± 1,4 | **%9,0 ± 1,6** | %8,0 ± 1,0 |
| Kamu sicili ortalaması | %30,8 ± 23,3 | %6,9 | %6,2 |
| Yerleşik / giren getirisi | %22 / %19 | %8 / %10 | %9 / %8 |
| Zarar eden tüccar payı | %34 | %48 | %50 |
| Giriş / çıkış (gemi-yıl başına) | 0,24 / 0,20 | 0,31 / 0,30 | 0,38 / 0,36 |
| İflas / gemi-yıl | 0,022 | 0,008 | 0,008 |
| Filo ortalaması | 152 | 142 | 150 |
| Filo CV | 0,39 | **0,20** | 0,18 |
| Filo tepe / dip | 72 ± 88 | **2,1 ± 0,2** | 2,1 ± 0,4 |
| Döngü süresi (ay) | 48 | 49 | 56 |
| Sefer / gemi-yıl | 14,9 | 14,4 | 13,9 |
| Gemi kaybı / gemi-yıl | — | **0,28** | 0,27 |

**Seed bazında filo (en düşük–en yüksek):** R1'de çöken üç seed (1, 4, 7) R1'de 1–299, 3–299, 1–299 idi. O3'te 96–219, 81–162, 79–186. On seed'in hepsinde filo 79'un altına inmiyor. **Çöküş kalktı.** Bandın σ'sı kendi döngüsünden besleniyordu (D5b3i.2); band kalkınca o geri besleme de kalktı.

Gemi piyasası (O3, F):
- Fiyat endeksi ortalaması 0,60, CV 0,82, en yüksek 1,31 (yabancı gemi tavanı). Fiyat ile kamu sicili korelasyonu **0,82** (VRS'de 0,48).
- Yılda 14 ikinci el işlem, 25 tersane siparişi, 8 yabancı gemi, 2 söküm.
- **Tersane kuyruğu ortalama 386 gün.** Tersane kapasitesi (son 5 yıl filosunun %40'ı/yıl) gemi kaybının (%28/yıl) yarattığı yenileme talebine yetmiyor. Sorunun kaynağı gemi kaybının fazlalığı; tersane parametresi değil.
- Gemisini kaybedip yeniden almayan tüccar: yılda 26.

### Okuma (F)
1. **Asıl soru: bant çöküşü düzeldi mi? Evet.** Tepe/dip 72 → 2,1, CV 0,39 → 0,20; seed'ler arası fark kalmadı. Kullanıcının beklentisi tuttu: bant sorunu gemi piyasasıyla kendiliğinden çözüldü.
2. **Rant kalktı** (%13 → %9, eşik %8); VRS ile aynı sonuç. Kamu sicilinin %31 ± 23 gibi patlayan değerleri, çöken seed'lerdeki az sayıda hayatta kalanın getirisiydi (survivorship bias); O3'te sicil %6-7'de sabit.
3. **İflas 3 kat azaldı** (0,022 → 0,008). Gemi artık satılabilir bir varlık: kötü giden tüccar gemisini satıp çıkabiliyor.
4. **U ablation'ı haritaya göre farklı.** Tam haritada U kapalı da filo düzenli (tepe/dip 2,1). VRS'de U kapalıyken tepe/dip 6,9 idi. U'nun sönümleme etkisi küçük dünyada görülüyor, büyük dünyada görülmüyor. Yorum (⚠️ sınanmadı): büyük dünyada çok sayıda rota birbirinden bağımsız dalgalanıyor; toplam filo bunların ortalaması olduğundan kendiliğinden düzgün. **U'yu kaldırmak için yeterli değil; VRS'de gerekli.**
5. **Ölçek sorunu tam haritada iki kat ağır:** yılda 14,4 sefer, gemilerin yılda %28'i kayıp. Tarihsel aralık %4-12 ([shipping-scale-16c](../research/history/shipping-scale-16c.md)). Tersane kuyruğu, zarar eden payı, kısa gemi ömrü bu tek nedenden geliyor.

**Düzeltme (koşulardan sonra):** İşlem olmayan ayda fiyat cetveli artık sökümle tabanlı. Satış değeri zaten sökümle tabanlı olduğundan sonuçlar değişmiyor; yalnızca kayıttaki fiyat. Yukarıdaki tablolarda `ship_px_min` = 0 bu kusurun izi.

### Sonuç
Ö3, bandın iki sorununu birlikte çözdü: kalıcı rant (getiri eşiğe indi) ve tam haritadaki çöküş. Sıradaki darboğaz motorun zaman ölçeği: limanda geçen zaman olmadan sefer sıklığı tarihin 3-5 katı, gemi kaybı da öyle.
