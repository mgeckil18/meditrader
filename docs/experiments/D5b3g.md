# D5b3g — Giriş-Çıkış Kuralının Düzeltilmesi (K-029)
> Durum: taslak (Sonuç 1-3 tamam)
> Son güncelleme: 2026-10-30
> İlgili: [D5b3f](D5b3f.md), K-028, K-029, S-020, [11-entry-barriers](../research/simulation/11-entry-barriers.md)

**Kullanıcı notu:** Bu kısımlar gelecek hafta ekonomik literatürle doğrulanacak (K-029 doğrulama listesi). Hepsi deneme.

## Uygulama (`sim/world5.py`; varsayılanlar eski davranışı korur, `check` ile doğrulandı)

| Bayrak | Ne yapar |
|---|---|
| `warm_start` | Başlangıç = snapshot. Ön koşu: seed 1000 + k, 10 yıl, soğuk başlangıç. 8. yıldan sonra her ay başı aday: filo son 5 yılın ortalamasına ±%5 yakın ve donatılan gemi filonun ≤ %2'si. Son aday seçilir. Koşu, seed % 3 numaralı snapshot'tan yeni RNG'yle başlar. Kayıtlar ve sayaçlar sıfırlanır; tüccarlar, pazarlar, sicil ve batma geçmişi kalır. Snapshot yapılandırma hash'ine bağlı (`experiments/out/snapshots/`) |
| `hurdle_rule="common"` | Giriş: ikna olan pay = log-normal(inanç − alternatif − risk primi). Eşiğin altında giriş yok |
| `exit_rule="voyage"` | Her sefer bitince kişisel beklenti eşiğin (senet + prim) altındaysa, açığa ikna olma olasılığıyla çıkmaya karar verir. Limanda boşalınca çıkar. Eski aylık çıkış kapalı |
| `public_track="aggregate"` | Kamu sicili = aylık toplam sermaye getirisi (Σ değer değişimi / Σ ay başı değer; değer = öz sermaye + temettü). Çıkan ve batanlar kalan nakitleriyle sayılır. Son 12 ayın toplamı |
| `shrink_k = 9` | Kişisel beklenti = w × kendi sicili (öz sermaye, son ≤ 12 ay) + (1 − w) × kamu sicili, w = n / (n + 9). n = son 12 aydaki sefer sayısı (~1 yılda w ≈ 0,5) ⚠️ |

**Ölçüm düzeltmesi (bulduk, motorumuzun hatası):**
- `net_worth` borç ve colleganza sermayesini düşmüyordu. Aylık `marks` ve bundan türeyen eski sicil (`trailing_median`) kaldıraçla şişiyordu.
- Etki küçük: tam haritada borç, finansman kararlarının %3-5'i.
- Yeni kurallar `equity()` kullanıyor; eski sicil eski haliyle kaldı (karşılaştırma için).

**Metrikler:** Snapshot'tan başlayan koşuda toplam sermaye getirisi snapshot anındaki değerden ölçülür (`v0`, `t0`). Son-5-yıl pencereleri `t0`'a göre kaydırıldı.

## Kurulumlar (4 seed, 10 yıl, VRS = 3 × 3 ve F = tam harita)

| Kurulum | İçerik |
|---|---|
| `-W` | Yalnızca snapshot (eski kurallar): artifact'ın payı |
| `-WT` | + ortak eşik + sefer sonunda çıkış + bonus yok |
| `-WTA` | + batanlar dahil kamu sicili + credibility; batma bedeli eşikte yok (K-029 m.6) |

## Sonuç 1: W, WT, WTA (4 seed, 10 yıl; `out/d5b3g/`)

Snapshot'ların çoğu kurala uyan andan seçildi (filo 5 yıllık ortalamaya ±%5). Birkaçında "donatılan ≤ %2" koşulu tutmadı; sapması en küçük an alındı (sapma ≤ %4,5).

| | VRS-W | VRS-WT | VRS-WTA | F-W | F-WT | F-WTA |
|---|---|---|---|---|---|---|
| **Toplam getiri** | **7,3%** | 15,8% | 16,7% | 1,2% | 4,5% | **12,9%** |
| Filo (başlangıç → son yıl) | 66 → 79 | 57 → 90 | 60 → 86 | 222 → 236 | 182 → 223 | 135 → 201 |
| **Filo tepe / dip** | 1,9 | **19,3** | **14,3** | 1,5 | 2,5 | **8,9** |
| Filo CV | 0,16 | 0,42 | 0,50 | 0,09 | 0,21 | 0,52 |
| Giriş / çıkış / iflas (yıllık) | 19 / 11 / 5 | 68 / 66 / 2 | 74 / 69 / 2 | 30 / 22 / 7 | 156 / 157 / 1 | 176 / 168 / 1 |
| Kamu sicili (ortalama) | 2,5% | 22,5% | 23,4% | 2,1% | 14,4% | 23,1% |
| Giren kuşağın getirisi (medyan) | −7,0% | −6,6% | −7,8% | −3,7% | −2,5% | −1,6% |

Örnek filo yolu (F-WTA seed 0, yılda bir): 133, 116, 182, 99, 239, 62, 250, 60, 285, 56, 287. Yaklaşık 2 yıllık bir döngü.

**Okuma:**
1. **Snapshot tek başına (W):**
   - Küçük haritada getiri %17,9'dan %7,3'e indi. Önceki D5b3 serisindeki yüksek küçük harita getirisinin büyük kısmı soğuk başlangıç geçişinin ürünüydü. Bulduk; motorumuzun artifact'ı.
   - Tam haritada değişiklik yok (%1,2). Tam haritadaki fazla giriş kalıcı.
2. **Eşik + sefer sonunda çıkış (WT, WTA):**
   - Getiri seviyesi düzeldi, hatta hedefi aştı (tam harita %12,9).
   - Ama dinamik bozuldu: yıllık devir filonun %70-80'i ve filo 2 yıllık şiddetli bir döngüde (tepe/dip 9-19).
3. **Neden:**
   - Giriş de çıkış da artık hızlı. Yeni çıkış kuralında her gemi yılda ~9 kez karar veriyor; eski çıkış yavaştı ve döngüyü sönümlüyordu.
   - Sinyal 12 ay gecikmeli.
   - Literatürde bilinen sonuç: cobweb'de arz tepkisi talep tepkisinden daha esnekse salınım büyür (ıraksak cobweb; Ezekiel 1938 ⚠️). Doğrusal olmayan sınırlar onu bir limit cycle'da tutar. Simülasyon bunu yeniden üretti.
   - Giriş ve çıkışın ikisi de bedelsiz ve anında olunca piyasa "fazla akışkan" hale geliyor.
4. **Giren kuşak hâlâ kötü (−%2 ile −%8):** Yeni girenler kısa yaşıyor; kendi sicilleri gürültülü. Sicilleri senet + primin altına düşen gemi çıkıyor (gürültü kaynaklı devir).

**Çıkarım (Claude, doğrulanmadı):** Eşiğin yeri (kullanıcının önerisi) getiri seviyesini doğru yere taşıyor. Eksik olan sönümleme, yani giriş ve çıkışın bir bedelinin ya da gecikmesinin olması.
- Ekonomik karşılığı: batık maliyet ve Dixit bandı. Gemi alınırken pahalı, satılırken ucuz; bu, giriş ve çıkış eşiklerini birbirinden ayırır.
- Tarihsel karşılığı: gemi piyasası, kereste ve tersane kapasitesi.
- Bu, giriş bariyeri tartışmasının (S-020) doğal adayı.

## Sonuç 2: sönümleme ablation'ları

| Kurulum | Değişiklik (Claude, ablation) |
|---|---|
| `-WTA-band` | Çıkış eşiği = senet (giriş eşiği senet + prim). Batık gemi maliyetinin vekili (Dixit bandı) |
| `-WTA-slow` | Giriş dikkati %2 → %0,5 |
| `-WTA-k36` | Credibility k = 9 → 36 (kendi sicilinin ağırlığı ~4 yılda yarıya ulaşır) |

## Sonuç 3: U, R, U + R (kullanıcı onayı 2026-10-30)

| Kurulum | Değişiklik | Köken |
|---|---|---|
| `-WTA-U` | Teyitli giriş: eşiği aşan fırsata ikna olan yatırımcı aday olur (kişisel prim log-normal, medyan risk primi). 3 ay arayla toplam 3 değerlendirme yapar. Hepsinde fazla getiri kendi priminin üstündeyse sermaye bağlanır, gemi donatılır (+30-60 gün). Bir değerlendirmede ikna olmazsa vazgeçer. Adaylar birbirini görmez | **K** (kullanıcı önerisi); C (kişisel prim, vazgeçme) |
| `-WTA-R` | Real options bandı: giriş eşiği + κσ, çıkış eşiği − κσ; σ = kamu sicilinin son 24 aylık sd; κ = 1 ⚠️ | C; L (Dixit 1989; Dixit & Pindyck 1994) |
| `-WTA-UR` | İkisi birlikte | K + C |

Not: `pub_log` artık snapshot'tan sonra da korunuyor (σ için durum). Eski kurulumların davranışı değişmedi (`check`).
Bakınız [12-entry-decision-timing](../research/simulation/12-entry-decision-timing.md).

## Sonuç 2 + 3: tablo (4 seed, 10 yıl; `out/d5b3g/summary_*.json`)

**Tam harita (F):**

| | WTA | -band | -slow | -k36 | **-U** | **-R** | **-UR** |
|---|---|---|---|---|---|---|---|
| Toplam getiri | 12,9% | 12,2% | 25,2% | 11,5% | 24,3% | 16,0% | 18,5% |
| Filo tepe / dip | 8,9 | 6,7 | 3,4 | 86 | 11,1 | **3,2** | **3,4** |
| Filo CV | 0,52 | 0,48 | **0,24** | 0,62 | 0,66 | 0,32 | 0,32 |
| Giriş / çıkış (yıllık) | 176 / 168 | 143 / 144 | 70 / 64 | 167 / 153 | 142 / 134 | 56 / 56 | **34 / 38** |
| Filo (son yıl ort.) | 201 | 206 | 133 | 243 | 198 | 149 | 114 |
| Giren kuşak (medyan) | −1,6% | −3,9% | +18,2% | −3,9% | −2,4% | +3,8% | +9,0% |

**Küçük harita (VRS):**

| | WTA | -band | -slow | -k36 | **-U** | **-R** | **-UR** |
|---|---|---|---|---|---|---|---|
| Toplam getiri | 16,7% | 13,5% | 26,3% | 18,2% | 21,5% | 15,6% | 19,4% |
| Filo tepe / dip | 14,3 | 11,6 | 4,7 | 70 | 24,0 | 5,9 | **3,8** |
| Filo CV | 0,50 | 0,44 | **0,32** | 0,62 | 0,70 | 0,40 | 0,38 |
| Giriş / çıkış (yıllık) | 74 / 69 | 59 / 53 | 33 / 27 | 81 / 77 | 72 / 58 | 27 / 23 | **13 / 12** |
| Giren kuşak (medyan) | −7,8% | −9,7% | +5,7% | −9,4% | −9,2% | −7,0% | +1,1% |

Örnek filo yolları (yılda bir, seed 0):
- F-WTA-U: 119, 162, 48, 278, 34, 230, 48, 163, 175, 61, 243. 2 yıllık döngü duruyor, hatta genliği büyüdü.
- F-WTA-R: 132, 158, 121, 137, 100, 155, 104, 234, 116, 110, 92. Düzenli döngü kayboldu; düzensiz dalgalanma ve ara sıra sıçrama kaldı.
- F-WTA-UR: 144, 107, 103, 111, 97, 81, 137, 140, 90, 81, 64.

**Okuma:**
1. **U tek başına döngüyü çözmedi, kötüleştirdi** (tepe / dip F 8,9 → 11,1; VRS 14 → 24). Kuramsal beklentiyle ([12](../research/simulation/12-entry-decision-timing.md) §2 risk 1-2) uyumlu. Literatürde bilinen sonuç: cobweb'de gecikmeyi uzatmak salınımı sönümlemez (Ezekiel 1938 ⚠️). Simülasyon bunu yeniden üretti. Üstüne, birbirini görmeyen adaylar uzun yüksek dönemden sonra birlikte testi geçiyor (yığılma). Çıkış tarafı da hâlâ hızlı.
2. **R (bant) en etkili tek değişiklik.** Devir ~3 kat düştü, düzenli 2 yıllık döngü kayboldu (tepe / dip 3,2). Literatürde bilinen sonuç: batık maliyet + belirsizlikte giriş-çıkış arasında hareketsizlik bandı (Dixit 1989); simülasyon, bandın devri ve salınımı azalttığını yeniden üretti.
3. **U + R:** Devir en düşük (F 34 / yıl, VRS 13 / yıl); küçük haritada salınım en düşük. Giren kuşağın getirisi ilk kez belirgin pozitif (F +%9, VRS +%1). Teyit, bant varken işe yarıyor: gürültülü girişleri süzüyor ve bant yığılmayı sınırlıyor.
4. **-slow** CV'de en iyi ama getiriyi %25'e taşıyor (rant). Literatürde bilinen sonuç: giriş yavaşsa rant (Bain 1956; D3b'de de yeniden üretilmişti).
5. **-band (yalnızca çıkış eşiği senet)** zayıf; **-k36** kötü (kendi sicile az güvenen tüccar kamu siciline uyup topluca çıkıyor; tepe / dip 70-86).
6. **Yeni sorun: seviye.** Sönümleyen her kurulumda getiri hedefin (senet + prim ≈ %8) çok üstünde (R %16, UR %18,5). Bandın beklenen sonucu: ortalama getiri giriş eşiği ile çıkış eşiği arasında, Marshall eşiğinin üstünde (Dixit & Pindyck 1994). Ama bizdeki fark büyük. Nedenler (Claude, doğrulanmadı):
   - ~~σ ~%10-15, giriş eşiği ~%20~~ (2026-10-30'da ölçmeden yazılmıştı; 2026-11-02'de `pub_log`'dan ölçüldü, yanlış). Ölçülen σ (24 aylık sd, medyan): F-WTA %17,5 → F-R %4,9, F-UR %4,1; VRS-R %6,1, VRS-UR %3,9. Yani giriş eşiği ≈ %8 + %4-6 ≈ %12-14.
   - Kamu sicilinin medyanı R / UR'de %12-14. Sistem bandın **üst kenarında** duruyor: giriş eşiği tavanı tutuyor, çıkış eşiği (%2-4) neredeyse hiç çalışmıyor. Getirinin seviyesi bandın üst kenarından geliyor.
   - Toplam getiri (%16-18,5) kamu sicilinden (%12-14) daha yüksek. Aday açıklama (doğrulanmadı): toplam getiri `v0`'dan bütün koşu için ölçülüyor ve yerleşiklerin kârını da içeriyor; giren kuşağın getirisi daha düşük (F-UR +%9).

**Çıkarım (Claude, doğrulanmadı):**
- Kullanıcının U önerisi tek başına değil, bantla birlikte anlamlı: U + R hem devri hem salınımı hem de giren kuşağın kaybını en iyi düzelten kurulum.
- Sıradaki ayar, bandın genişliği ve yeri. κ'yı küçültmek (0,5) ya da σ'yı döngüden bağımsız bir kaynaktan almak (ör. sefer kârının kesitsel dağılımı). Ayrıca iki toplam getiri ölçüsünün farkı açıklanmalı. İleride bant, gemi piyasasındaki alım-satım farkından (batık maliyet, S-020) kendiliğinden doğmalı.
- Seviye sorusu K-029 doğrulamasına (haftaya) bağlanıyor.
