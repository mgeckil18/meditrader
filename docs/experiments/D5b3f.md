# D5b3f — Giriş Teşhisi: Getiri Senedin Altındayken Neden Giriş Sürüyor?
> Durum: taslak (teşhis tamam, kullanıcıyla tartışılacak)
> Son güncelleme: 2026-10-27
> İlgili: [D5b3e](D5b3e.md) tam harita, [11-entry-barriers](../research/simulation/11-entry-barriers.md), S-020, K-028, K-024

**Soru (kullanıcı, 2026-10-27):** Tam haritada gerçekleşen getiri senedin (%4) altında, ama yılda ~29 gemi giriyor ve filo küçülmüyor. Giriş kararı yanlış bir şeye mi bağlı? "Batanın yerine yenisi" mekanizması mı kaldı? Önce sebep saptansın, bariyerler sonra.

**Yöntem:** `experiments/d5b3f_entry_diag.py`. Davranış değiştirmez, yalnızca kayıt tutar. Aynı seed'de giriş ve çıkış sayıları kayıtsız koşuyla birebir aynı (24/13; `check`). VRS (3 × 3) ve F (tam harita), 4 seed, 6 yıl (+3 yıl spinup).

## Giriş kuralı bugün nasıl işliyor (`entry_rule="opportunity"`)

Her ay, her limanda:
1. **İnanç** = sicil + bonus.
   - Sicil: yaşı ≥ 1 yıl olan, hayattaki tüccarların son 12 ay getirisinin medyanı.
   - Bonus: limandaki tüccarların "şu anki en iyi seferi"nin medyanı, donatım süresince sönmüş ve 3 yıla yayılmış.
2. **İkna olan pay:** İnancın alternatifi (senet %4) aşan kısmı, log-normal dağılmış risk primiyle (medyan %4 + batma bedeli) karşılaştırılır.
3. **Beklenen giriş** = dikkat (%2) × limandaki yatırımcı havuzu (sermaye birimi) × ikna olan pay.

"Batanın yerine yenisi" kuralı artık yok. Eski `realized` kuralı kullanılmıyor.

## Sonuç 1 (VRS, F × 4 seed): üç kaynak

| Ölçüt | VRS (9 pazar) | F (45 pazar) |
|---|---|---|
| Giriş / çıkış / iflas (yıllık) | 14,0 / 6,4 / 4,0 | 31,0 / 20,4 / 8,0 |
| **Ana koşunun ilk yılındaki girişler** (sicil yok) | 18-22 | **54-103** |
| İlk yıl giriş inancının medyanı (ham fırsat) | %27-70 | **%87-141** |
| Sicil (ortalama, sicil bilinen aylar) | %8,1 | **%0,2** |
| Sicil, giriş olan aylarda | %16,1 | %6,1 |
| Girişte sefer fırsatı (kârın sermayeye oranı) | %9 | **%30** |
| Sicil < senet iken olan giriş payı | %5 | **%24** |
| Batma bedeli | %6,7 | %3,2 |
| Giren kuşağın gerçekleşen yıllık getirisi (medyan) | %1,6 | **−%3,7** |
| Çıkış adayının sicili (kontrol anında) | −%29 | −%17 |
| "Önümde fırsat var" deyip kalan çıkış adayı | %4 | %1 |

**Kaynak A, bulduk (motorumuzun artifact'ı): soğuk başlangıç patlaması.**
- Spinup yalnızca filo sayısını taşıyor. Ana koşuda bütün gemiler 0. günde yeniden yaratılıyor ve sicilleri yok.
- İlk 12 ay boyunca sicil bilinmediği için inanç ham fırsata düşüyor. F'de bu yıllık %100 civarı.
- Sonuç: tam haritada 6 yıllık girişlerin %30-50'si ilk yılda.
- Aynı patlama spinup'ın kendi ilk yılında da oluyor. Bu yüzden başlangıç filosu (F'de 214) da bu artifact'la şişmiş olabilir (doğrulanıyor, sonuç 2).
- Bu, önceki bütün D5b3 koşularını etkiliyor. Küçük haritada daha hafif.

**Kaynak B: bonus büyük haritada daha büyük (optimizer's curse adayı).**
- Girişteki sefer fırsatı F'de %30, VRS'de %9. En iyisi daha çok seçenekten seçiliyor (6 kalkış limanı × 45 pazar).
- Sicil senedin altındayken olan girişlerin %24'ünü bonus taşıyor.
- Karşı-olgusal ayrıştırma (`d5b3f_counterfactual.py`; aynı aylar, filo geri beslemesi yok, sicil bilinen aylar):

| F, sicil bilinen aylar | Yıllık beklenen giriş |
|---|---|
| Gerçek kural | 19,8 |
| Bonus yok | 5,7 |
| Sicil 12 ay ortalaması + bonus | 13,8 |
| Sicil 12 ay ortalaması, bonus yok | 1,6 |

VRS'de aynı sıra 12,2 → 8,8 → 11,5 → 8,1. Yani bonus büyük haritada girişin ~%70'ini, küçük haritada ~%30'unu taşıyor.

**Kaynak C: giriş hızlı ve tek yönlü, çıkış yavaş.**
- Giriş, sicilin ve bonusun yukarı dalgalanmalarına anında tepki veriyor. Aşağı dalgalanma girişi sıfırlıyor ama gemi çıkarmıyor.
- Çıkış yavaş: limanda boş ambarla beklerken, sicil < senet ise ayda %10 olasılıkla. Çıkış adayları kontrol anında −%17 ile −%29 sicilde. Yani gemiler derin zarara kadar kalıyor.
- Literatürde bilinen sonuç: gürültülü sinyale dışbükey tepki (convex response), ortalama sinyal eşiğin altındayken bile pozitif giriş akışı üretir (Jensen eşitsizliği). Simülasyon bunu yeniden üretti.
- Bu yüzden denge "beklenen getiri = senet + prim" noktasında değil, "dalgalanma girişleri = yavaş çıkış" noktasında kuruluyor.

**Giren kuşak sistematik iyimser.** Her iki haritada girişteki inanç medyanı ~%24, gerçekleşen ise %1,6 ve −%3,7. Bu literatürdeki aşırı güven ve fazla giriş bulgusuyla uyumlu (Camerer & Lovallo 1999 ⚠️). Ama bizdeki kaynağı mekanik: A + B + giriş zamanlamasının yüksek sinyale denk gelmesi (regression to the mean).

## Sonuç 2: düzeltme varyantları (4 seed, 6 yıl)

| Kurulum | Değişiklik (köken: Claude) |
|---|---|
| `-cold` | Sicil yokken inanç = senet + risk primi (artifact düzeltmesi denemesi) |
| `-cold-nobonus` | + girişte bonus yok; inanç = yalnızca kamuya açık sicil (kalma kararı değişmedi; ablation) |

| | VRS | VRS-cold | VRS-cold-nobonus | F | F-cold | F-cold-nobonus |
|---|---|---|---|---|---|---|
| Toplam getiri | 17,9% | 19,4% | 24,0% | −1,5% | −1,0% | **1,8%** |
| Başlangıç filosu (spinup) | 57 | 56 | 53 | 222 | 212 | 194 |
| Filo, 1. yıl sonu | 72 | 68 | 64 | 299 | 295 | 249 |
| Filo, son yıl | 72 | 66 | 61 | 237 | 220 | 209 |
| İlk yıl giriş | 20 | 15 | 13 | 83 | 92 | 64 |
| Giriş / yıl | 14,0 | 12,5 | 10,6 | 31,0 | 29,2 | 24,3 |
| Sicil ortalaması | 8,1% | 7,3% | 7,6% | 0,2% | 1,4% | 3,6% |
| Giren kuşağın getirisi (medyan) | 1,6% | −0,6% | 5,4% | −3,7% | −2,5% | −1,8% |

**Filo yolu (6 ayda bir, seed ortalaması):**

| Kurulum | Filo | Giriş (6 aylık) |
|---|---|---|
| F | 222, 264, **299**, 281, 261, 240, 222, 214, 212, 229, 236, 236, 238 | 55, 28, 0, 0, 0, 2, 5, 20, 24, 22, 13, 17 |
| F-cold-nobonus | 194, 223, **249**, 235, 218, 204, 194, 190, 201, 231, 220, 208, 206 | 37, 27, 0, 0, 0, 3, 6, 27, 33, 3, 2, 9 |
| VRS | 56, 63, 72, 70, 67, 62, 56, 60, 64, 74, 70, 70, 75 | 9, 11, 5, 2, 2, 5, 9, 10, 10, 5, 8, 10 |

## Teşhis: sorunun kaynakları

Kullanıcının gözlemi ("getiri senedin altında, ama filo küçülmüyor") baştaki ve sondaki filoya bakınca doğru görünüyor (214 → 228). Ama filo yolu başka bir şey gösteriyor: **filo bir döngüde.** Önce %35 şişiyor (222 → 299), 3 yılda yavaşça eriyor (→ 212), sonra yeni bir giriş dalgası geliyor.

1. **Giriş dalgalı ve gecikmeli: cobweb / pork cycle.** Literatürde bilinen sonuç (Ezekiel 1938 ⚠️; bkz. D3b). Simülasyon bunu yeniden üretti.
   - Sicil son 12 ayın getirisi, yani geriden gelen bir sinyal. Yatırımcı bir yıl önce kazanılmış getiriye bakıp giriyor. Gemi donatılıp gelince getiri çoktan düşmüş oluyor.
   - Sınırsız havuzda giriş hızı yüksek: tam haritada 6 ayda 55 gemiye kadar (filonun %25'i).
2. **Kuralın tek durma noktası senet (%4), senet + risk primi değil.** İkna olan pay log-normal; inanç senedi az bile aşsa riskten az kaçınan yatırımcılar girer. Risk primi yalnızca girişin hızını belirliyor, nerede durduğunu değil. Bu yüzden `-cold` (sicil yokken inanç = senet + prim) ilk yılın patlamasını önlemedi. O inanç bile yatırımcıların yarısını ikna ediyor (batma geçmişi de 0. günde boş).
3. **Çıkış yavaş ve tek yönlü.**
   - Çıkış yalnızca aylık kontrolde gemi limanda boş ambarla bekliyorsa, ayda %10 olasılıkla oluyor. Bu nadir bir an.
   - Gemiler −%17 ile −%29 sicile kadar kalıyor.
   - Döngünün yukarı kolu hızlı, aşağı kolu yavaş. Bu yüzden ortalama filo denge filosunun üstünde ve ortalama getiri senedin altında.
4. **Sicil, yeni girenin kazanacağından yüksek.**
   - Yalnızca hayatta kalanların medyanı (survivorship bias).
   - Girişler sicilin yüksek olduğu anlara denk geliyor (regression to the mean).
   - Bonus kapalıyken bile tam haritada sicil %3,6, giren kuşak −%1,8.
5. **Bonus büyük haritada şişiyor (optimizer's curse).** Kapatınca tam haritada getiri −1,5% → +1,8%, son filo 237 → 209. Küçük haritada etkisi daha az.
6. **Bulduk (motorumuzun artifact'ı): soğuk başlangıç.**
   - Spinup yalnızca filo sayısını taşıyor; sicil, batma geçmişi ve tüccar durumu taşınmıyor.
   - Ana koşu ve spinup'ın kendisi aynı patlamayla başlıyor. 6 yıllık bir koşunun büyük kısmı bu ilk dalganın sönmesiyle geçiyor.
   - Önceki D5b3 sonuçlarının hepsi bundan etkilenmiş olabilir. Etki tam haritada büyük, küçük haritada küçük.

**"Batanın yerine yenisi" kuralı kalmadı.** Giriş tamamen yukarıdaki inanca bağlı.

## Sonraki adımlar için adaylar (kullanıcıyla tartışılacak)

| Aday | Neyi düzeltir | Tür |
|---|---|---|
| Spinup durumunu taşımak (sicil, batma geçmişi, tüccarlar) ya da ilk yılları ölçmemek | 6 (artifact) | Motor düzeltmesi |
| Çıkış kararını her sefer sonunda vermek (yalnızca aylık boş-ambar anında değil) | 3 | Kural düzeltmesi |
| İleriye bakan giriş: donatılan gemileri sicilden düşmek (yatırımcı tersanede ne yapıldığını görür) | 1, 4 | Beklenti (D5b4 alanı) |
| Gemi arzının fiyatı: talep artınca gemi pahalılaşır, donatım uzar; çıkışta gemi düşük fiyata satılır | 1, 2 | Bariyer (sermaye dışı; gemi piyasası, K-027 Ertelendi ile bağlantılı) |
| Bonus yerine kamuya açık sicil | 5 | Beklenti |

## Kullanıcı önerileri ve Claude değerlendirmesi (2026-10-27, tartışma açık)

Kullanıcı önerileri. Kullanıcı bunları "emin olmadan" öneriyor; kesin değil.
1. **Soğuk başlangıç:** Bir seed'le koşu yapılsın; orada iyi bir an kaydedilsin ve başlangıç durumu o olsun.
2. **Giriş ve çıkış eşiği senet + risk primi olsun.** Sabit %8 konmasın; ekonomik ve tarihsel olarak doğru olmaz.
3. **Kamuya açık sicil**, batanlar ve çıkanlar dahil toplam sermaye getirisi olsun (K-025 ölçütü). Kişisel siciller bu ortalamayla karşılaştırılarak değerlendirilsin.

Claude değerlendirmesi:

**1. Başlangıç anı (snapshot).** Katılıyorum. ABM'de standart yöntem: burn-in + checkpoint. Dört koşulla:
- (a) "İyi an" nesnel bir kuralla seçilmeli, yoksa cherry-picking olur. Öneri: ≥ 8 yıl sonra, filonun son 5 yıllık ortalamasına ±%5 yakın olduğu ve donatılan gemi dalgasının olmadığı son an.
- (b) Snapshot yapılandırmaya bağlı. Kural değişince eski snapshot yeni modelin dengesi olmaz. Yapılandırma hash'iyle önbelleğe alınmalı ve kural değişince yeniden üretilmeli.
- (c) Tek snapshot bütün seed'leri aynı başlangıca bağlar. Birkaç snapshot (ör. 4 ayrı ön koşu seed'i) daha iyi; ana koşunun RNG'si yeni seed'le yeniden tohumlanır.
- (d) Döngü 4-5 yıl. Ölçüm penceresi birkaç döngüyü kapsamalı; filo oynaklığı (CV, tepe/dip) yeni bir ölçüt olmalı.

**2. Eşik = senet + risk primi.** Katılıyorum, ama bir tutarlılık sorunu var:
- Bugün risk primi yatırımcılar arasında log-normal dağılıyor. Havuz sınırsızken (K-028) giriş, primi en düşük yatırımcının eşiğinde durur, yani fiilen senette.
- "Senet + prim"in gerçekten durma noktası olması için iki yol var:
  - (i) **Eşik herkes için ortak**, heterojenlik yalnızca hızda (fazla getiri arttıkça daha çok kişi ikna olur). Claude önerisi: şimdilik bu.
  - (ii) Heterojenlik sınırlı bir aralıkta kalsın. O zaman denge, aralığın alt ucuna (ör. senet + 0,5 × prim) iner.
- Çıkış eşiği de aynı. Batık maliyet olmadığı sürece ekonomik olarak giriş ve çıkış eşiği aynı olmalı. İleride gemi piyasası gelirse ve gemi zararına satılırsa, eşikler kendiliğinden ayrılır (Dixit hysteresis).
- Çıkışın **zamanı** da düzeltilmeli. Çıkış her seferin sonunda (mal satılınca) kararlaştırılsın. Bugünkü "aylık kontrol + boş ambar + %10 olasılık" kalkar. Tarihte de karar yeni sefere donatmadan önce verilir.

**3. Batanlar dahil kamuya açık sicil.**
- Katılıyorum. Survivorship bias'ı kaldırır. Banca rotta kamuya açık olduğu için tarihsel olarak da makul bir yaklaşım.
- **Çakışma: K-024'teki batma bedeli.** Bugünkü batma bedeli (iflas sıklığı × %90) beklenen kaybın kendisi. Sicil batanları içerince bu kayıp ortalamada zaten var; eşiğe ayrıca eklemek çifte sayım olur.
  - Öneri: batma bedeli beklenen kayıp olarak kalksın.
  - Batmaya karşı risk tutumu, risk priminin içinde ya da onun üstünde (risk tutumuyla ölçeklenen ek prim) kalsın.
  - K-024 kullanıcı kararı; değişiklik kullanıcı onayı ister.
- **Kişisel sicil × ortalama (Claude yorumu, kullanıcı teyidi gerekli):** Tüccarın kendi beklentisi = w × kendi sicili + (1 − w) × kamu ortalaması, w = n / (n + k) (n: sefer sayısı). Literatürde bilinen yöntem: credibility / empirical Bayes shrinkage (Bühlmann ⚠️).
  - Tek kötü sefer tüccarı çıkarmaz.
  - Sürekli kötü giden tüccar ise ortalamaya saklanamaz.
  - Çıkış: bu beklenti < senet + prim.
- Sicil hâlâ geriden gelen bir sinyal (son 12 ay). Bu yüzden cobweb'in bir kısmı kalacak. Tersanede donatılan gemilerin beklentiden düşülmesi (ileriye bakan giriş) ayrı bir aday; önce kullanıcının setinin etkisi ölçülsün.

**4. Ek öneriler.**
- Girişteki "şu anki en iyi fırsat" bonusu kalksın. Optimizer's curse büyük haritada şişiriyor. Kamuya açık sicil daha dürüst bir sinyal. Rota seçiminde fırsatlar kullanılmaya devam eder.
- Giriş hızı (dikkat %2 × sınırsız havuz), doğru eşikte bile eşik aşılınca dalga üretir. Sonraki aday frenler: gemi piyasası fiyatı ya da tersanedeki gemileri görmek.
