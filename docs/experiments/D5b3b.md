# Deney D5b3b: Colleganza + İtibar
> Durum: tamamlandı (2026-10-26)
> Kod: [`sim/world5.py`](../../sim/world5.py) (`reputation`, `colleg_month_frac`, `rep_k`, `rep_lambda`, `rep_window`; `_rep_score`, `_update_pop_roi`, `_process_colleg_requests`, `_settle`), [`experiments/d5b3b_reputation.py`](../../experiments/d5b3b_reputation.py)
> Yeniden üretmek: `python3 experiments/d5b3b_reputation.py 10` (~17 dk); ablasyon: `python3 experiments/d5b3b_reputation.py 10 OCS-gate`
> Çıktı: `experiments/out/d5b3b/table_raw.txt`, `summary.json`, `table_gate.txt`, `summary_OCS-gate.json`
> İlgili: [K-021](../decisions.md), [K-020](../decisions.md), [S-012](../open-questions.md), [D5b3](D5b3.md), [mechanism-registry](../design/mechanism-registry.md)

## Soru

D5b3'te itibarsız colleganza yatırımcıya sözleşme başına −%17 / −%19 kaybettirdi. Sebep adverse selection: nakdi gemisini doldurmaya yetmeyen tüccar çoğunlukla kaybeden tüccardır (Akerlof 1970; Stiglitz & Weiss 1981; literatürde bilinen, D5b3'te yeniden üretildi).

Kullanıcı kararı (K-021):
- Yatırım sermayesi itibara göre verilir.
- Yatırımcılar tüccarları bir skora göre yukarıdan aşağı sıralayıp seçer.
- Kullanıcının ilk skoru: **bir yıllık işlem hacmi × kâr oranı × kârlı işlem oranı**. "Daha doğru bir hesaplama öneriyorsan buyur."
- Hipotez: itibar serbest girişe kendiliğinden friction getirebilir; o zaman ayrıca friction gerekmeyebilir.
- Denge getirisi bununla düzelmezse yeniden konuşulacak; şimdilik onun için bir şey yapılmıyor.

Ölçülecek:
1. İtibar yatırımcı kaybını düzeltiyor mu?
2. Skor gerçekten iyi tüccarı seçiyor mu? (Skor ile sözleşme getirisi arasında Spearman; tüccar getirisinin kalıcılığı)
3. Denge getirisi (D5b3'te hedef %8'in altında, %1-5) değişiyor mu?

## Kullanıcının skoru üzerine eleştiri (deneyden önce)

Skor A = V × p × w (V: bir yıllık hacim, p: kâr / hacim, w: kârlı sefer oranı). Claude'un itirazları:

| Sorun | Neden | Sonuç |
|---|---|---|
| Hacim büyükleri kayırır | V × p = toplam kâr. Zengin, çok sefer yapan tüccar öne geçer | Sermayeye en az ihtiyacı olana sermaye gider. Colleganza talebi zaten nakdi yetmeyenden gelir |
| Çifte sayım | p ve w aynı şeyi iki kez ölçer (kârlılık) | Ağırlıklar keyfî |
| w istismar edilebilir | Çok sayıda küçük kârlı sefer w'yi şişirir; nadir büyük zarar görünmez | Oyuncu için açık bir oyun |
| Cold start | Sicili olmayana skor 0, sermaye yok | Yeni tüccar hiç sermaye alamaz; ilk tüccarlar tekel kurar (kullanıcının K-016 rant kaygısı) |
| Bir yıllık veri gürültülü | 5-10 sefer, getiri varyansı büyük | Şanslı tüccar ödüllendirilir (survivorship bias) |

**Claude önerisi, Skor B (credibility):** Sefer getirisi ortalaması, sefer sayısına göre nüfus medyanına çekilir (Bühlmann 1967; Bayes shrinkage): E = (n × ortalama + k × nüfus medyanı) / (n + k), k = 5 sefer ⚠️. Belirsizlik kadar indirilir: E − λ × σ_nüfus / √(n + k), λ = 1 ⚠️. Sonra yıllıklaştırılır. Böylece:
- Sicilsiz tüccar nüfus ortalamasından başlar (cold start yok, ama indirimli).
- Ölçek değil verim ölçülür.
- Kısa sicil az ağırlık alır.

## Mekanizma (köken etiketleriyle)

| Parça | Ne yapar | Köken |
|---|---|---|
| Talep sırası | Nakdi gemisini doldurmaya yetmeyen tüccar günün talebine yazılır; yatırımcılar talepleri skora göre büyükten küçüğe dolaşır | **K** |
| Aylık bütçe | Limanın colleganza bütçesi ayda havuzun %10'u ⚠️; tek sözleşme havuzun en çok %5'i ⚠️ | C |
| İkna | Yatırımcı skorun ima ettiği yıllık getiri − senet farkına göre, giriş kuralındaki aynı log-normal eşik dağılımıyla ikna olur | C (D5b3'ten) |
| Kapı | Skor ≤ 0 → sermaye yok | **K** (Skor A'nın sonucu) |
| Skor A | V × p × w; beklenen yıllık getiri = p × 365 / medyan sefer süresi | **K** |
| Skor B | Credibility, yukarıda | C; L (Bühlmann 1967) |
| Giriş için alternatif | Yeni tüccara sermaye vermenin fırsat maliyeti = max(senet, colleganza'nın son 1 yıllık sermaye-zaman ağırlıklı getirisi) | C (kullanıcının friction hipotezinin mekanizması) |
| Kâr paylaşımı | D5b3'teki gibi: kârın 3/4'ü yatırımcıya, zarar oransal olarak yatırımcının sermayesinden | **K** fikir; L (Lane 1973 ⚠️) |

Not: İtibarsız sürümde (D5b3) yatırımcı **tüccarın kendi ex-ante sefer tahminine** bakıyordu (limanın colleganza geçmişiyle karıştırılmış). İtibarlı sürümlerde bu tahmin hiç kullanılmıyor; yalnızca gerçekleşmiş sicil kullanılıyor. Bu fark sonuçları açıklamada önemli (aşağıda).

## Kurulumlar

Hepsi D5b3 OCS yapısında (spin-up + fırsata bağlı giriş + liman havuzu), 10 seed, metrikler son 5 yıl.

| Kurulum | Colleganza | Sermaye dağıtımı |
|---|---|---|
| OS | Yok | — |
| OCS-itibarsız | Var | D5b3: tüccarın sefer tahmini + liman colleganza geçmişi |
| OCS-user | Var | Skor A (kullanıcı) |
| OCS-cred | Var | Skor B (credibility) |
| OCS-gate (ablasyon) | Var | Skor A'nın kapısı (kârlı sicil şart), ama sıralama rastgele |

## Koşu geçmişi (başarısızlar dahil)

| # | Ne | Sonuç |
|---|---|---|
| 1 | Duman, seed 0 | cred'de filo 13'e çöktü. Giriş alternatifi, sözleşme getirisinin kendi süresiyle yıllıklaştırılmış EMA'sıydı; kısa sözleşmelerde %541'e çıktı ve kimse yeni tüccara para vermedi. Düzeltme: son 1 yılın sermaye-zaman ağırlıklı oranı |
| 2 | Asıl koşu ilk deneme | Çıktı klasörü yönlendirme açılırken yoktu, koşu başlamadı; klasör oluşturulup yeniden çalıştırıldı |
| 3 | Asıl koşu, 4 kurulum × 10 seed | Aşağıda |
| 4 | Ablasyon OCS-gate | Aşağıda |

## Sonuçlar (10 seed medyanı, son 5 yıl)

### Yatırımcı tarafı

| Kurulum | Sözleşme | Sözleşme başına getiri (sermaye ağırlıklı) | Yıllık | Zararlı sözleşme | Düzey 0 / 1 / 2 payı | Spearman (skor, getiri) |
|---|---|---|---|---|---|---|
| OCS-itibarsız | 106 | **−%23,9** | −%227 | %79 | 36 / 14 / 48 | — |
| OCS-user | 178 | **−%3,9** | −%45 | %58 | 34 / 13 / 55 | −0,03 |
| OCS-cred | 84 | **−%4,3** | −%51 | %56 | 22 / 17 / 65 | −0,06 |
| OCS-gate | 155 | **−%3,6** | −%41 | %57 | 35 / 14 / 51 | +0,03 |

Seed bazında sözleşme getirisi:
- itibarsız: −%13 ile −%40 arası, 10 seed'in hepsi negatif
- user: −%0,7 ile −%7,8 arası, hepsi negatif
- cred: −%17 ile +%7 arası, 1 seed pozitif
- gate: −%16 ile +%3 arası, 3 seed pozitif

"Yıllık" sütunu sözleşmeler kısa olduğu (yaklaşık 1 ay) için büyük görünüyor. Yatırımcının senede bir kez yatırdığını değil, parasının sürekli dönüp kaybettiğini gösteriyor.

### Piyasa ve giriş tarafı

| Kurulum | Getiri medyanı | Düzey 0 / 1 / 2 getirisi | Filo (başlangıç → son 5 yıl) | Giriş | Çıkış | İflas | Sicil ort. | Kıtlık | Glut / yıl | Tüccar getirisi kalıcılığı (n) |
|---|---|---|---|---|---|---|---|---|---|---|
| OS | %0,4 | −8 / −3 / +6 | 65 → 82 | 155 | 87 | 40 | %3,0 | 2/10 | 35,8 | 0,09 (97) |
| OCS-itibarsız | %1,0 | −17 / −1 / +8 | 62 → 77 | 149 | 93 | 40 | %3,4 | 1/10 | 35,0 | 0,09 (94) |
| OCS-user | **%6,5** | −12 / +1 / +12 | 42 → 69 | 120 | 69 | 28 | %3,5 | 1/10 | 34,3 | 0,06 (88) |
| OCS-cred | **%4,5** | −5 / +1 / +12 | 42 → 72 | 135 | 68 | 33 | %5,3 | 0/10 | 36,5 | 0,06 (95) |
| OCS-gate | **%5,7** | −4 / +1 / +12 | 48 → 69 | 122 | 70 | 29 | %5,8 | 1/10 | 34,7 | 0,13 (91) |

Kalıcılık: aynı tüccarın kaydındaki ilk yarı ve ikinci yarı seferlerinin ortalama getirisi arasındaki rank korelasyonu (Spearman; en az 8 sefer). Kayıt `rep_window` = 730 gün ile budandığı için fiilen son 2 yılı kapsıyor.

## Bulgular

**1. İtibar yatırımcı kaybını beşte bire indiriyor, ama sıfırlamıyor.** Sözleşme başına −%24'ten −%4'e iniyor. Zararlı sözleşme oranı %79'dan %57'ye düşüyor.

**2. Kazancın kaynağı sıralama değil.** Rastgele sıralama (gate) kullanıcının skoru kadar iyi: −%3,6'ya −%3,9. Skor ile sözleşme getirisi arasında Spearman, üç kurulumda da sıfır civarında (−0,06 … +0,03). Kazanç iki şeyden geliyor:
- **(a) Tüccarın kendi ex-ante tahmini artık kullanılmıyor.** İtibarsız sürümde yatırımcı, tüccarın sefer tahminine güveniyordu. Tahmini en iyimser olan tüccar en çok sermaye istiyor ve alıyordu: optimizer's curse ile adverse selection'ın birleşimi (Smith & Winkler 2006; Stiglitz & Weiss 1981). Gerçekleşmiş sicile bakmak bu kanalı kapatıyor.
- **(b) Kapı.** Son bir yılda kârlı sicil şartı, sicilsiz ve kaybeden tüccarı dışarıda bırakıyor.

Hangisinin ne kadar katkı verdiği ayrıştırılmadı. Bunun için "kapısız ama sicile dayalı" bir kurulum gerekir.

**3. Modelde kalıcı "beceri" sicilden okunamıyor.** Tüccar getirisinin kalıcılığı 0,06-0,13. Sicil, sonraki seferi neredeyse hiç tahmin etmiyor. Oysa beceri farkı var: düzey 2 yılda +%12, düzey 0 −%4 / −%12 kazanıyor. Ama bu fark sefer gürültüsünün altında kalıyor. Yaklaşık 8 seferlik bir sicilde şans, beceriyi bastırıyor. Sermaye alanların hâlâ üçte biri düzey 0. Bu, literatürde bilinen "skill vs luck" sorunu: fon yöneticisi getirisinin kalıcılığı çok zayıf (Carhart 1997; Fama & French 2010 ⚠️). Simülasyon bunu yeniden üretti.
- Kullanıcının skorundaki V × p × w ile credibility arasındaki fark bu yüzden görünmüyor: sıralanacak bir sinyal yok.
- cred düzey 0 payını azaltıyor (%22'ye karşı %35), ama yatırımcı getirisi iyileşmiyor.

**4. Yatırımcının kalan kaybı yapısal: sıfır-kâr dengesi + asimetrik sözleşme.** Colleganza'da yatırımcı kârın 3/4'ünü alıyor, ama zararın tamamını taşıyor. Ortalama sefer getirisi ρ sıfıra yakınsa yatırımcının beklenen getirisi ≈ −¼ × E[ρ⁺], yani negatif. Serbest giriş, sefer marjını tam bu sıfır-kâr noktasına itiyor (literatürde bilinen; D3b ve D5b3'te yeniden üretildi). Sonuç: denge getirisi düşük kaldıkça hiçbir skor colleganza'yı kârlı yapamaz.
- Tarihsel karşılığı: colleganza yüksek marjlı Levant ticaretinde gelişti (Lane 1973 ⚠️). Düşük marjlı ticarette ise başka sözleşmeler (faizli deniz ödüncü, ortaklık) baskındı. ⚠️ doğrulanmadı.

**5. Yatırımcı öğrenmiyor (model eksiği, Claude tespiti).** Yatırımcı yılda −%40-50 kaybediyor, ama her ay bütçe ayırmaya devam ediyor. Çünkü bütçe sabit (havuzun %10'u) ve ikna kararı yalnızca tüccarın skoruna bakıyor. Gerçek yatırımcı, limanın colleganza geçmişi kötüyse çekilirdi. Bu yapılmadı, kullanıcıyla konuşulacak.

**6. Denge getirisi kısmen yükseldi: %1'den %4,5-6,5'e, ama hedef %8'in altında.** Daha az giriş (149 → 120-135) ve daha az iflas (40 → 28-33) var. Kanal teşhis edilmedi. Giriş alternatifi (colleganza getirisi) negatif olduğu için max(senet, ·) = senet; yani tasarlanan friction mekanizması devreye girmedi. Olası kanallar ⚠️ doğrulanmadı:
- Kaybedilen colleganza sermayesi havuzu küçültüyor.
- Colleganza mevcut tüccarın kapasitesini doldurarak fırsatı yeni girenden önce alıyor.

Medyanlar 10 seed üzerinden; seed dağılımı bu tabloda yok, fark gürültü sınırına yakın olabilir.

## Tasarıma etkileri ve açık sorular

- **K-021 sonucu:** İtibar kapısı tutuldu (yatırımcı kaybını beşte bire indirdi). Skorun biçimi (A ya da B) bu modelde fark etmiyor. Oyun için okunabilirlik ve istismar açısından seçilmeli (eleştiri tablosu). Sinyal yokken sıralamayı sınamak anlamsız.
- **Beceri sinyali:** Oyunda itibarın anlamlı olması için ya beceri farkları sefer gürültüsüne göre büyük olmalı, ya da sicil daha uzun ve daha zengin olmalı (aracılar, mektuplar, lonca kaydı). Bu bir tasarım sorusu, bkz. S-012 notu.
- **Kullanıcıyla konuşulacak (kullanıcı talimatı: "denge getirisi düzelmezse yine konuşalım"):**
  1. Denge getirisi hedefe ulaşmadı → serbest girişe friction.
  2. Yatırımcı öğrenmesi: bütçe, limanın gerçekleşen colleganza getirisine bağlansın mı?
  3. Sözleşme biçimi: düşük marjlı rotalarda colleganza yerine faizli deniz ödüncü ya da compagnia.
- Taban yapı önerisi değişmedi: D5b4 beklenti turnuvası OS üzerinde (colleganza hesabı karıştırmasın).

## Sonradan bulunan hata (2026-10-26, D5b3c.1)

🐞 Temettü kuralı (nakit > 1,2 × başlangıç sermayesi), colleganza sözleşmesi açık olan tüccarda yatırımcının parasını da temettü olarak çekebiliyordu. Bu, D5b3 ve D5b3b'deki colleganza getirilerini aşağı çekmiş olabilir. Düzeltme D5b3c'de yapıldı: sözleşme ya da borç açıkken temettü yok. D5b3b yeniden koşulmadı; bulgular niteliksel olarak (kapı > sıralama, sinyal yok) etkilenmemeli ⚠️, ama sayılar düzeltilmiş motorda farklı çıkabilir.
