# D5b3h — Ölçüm (Ö0), Veriden Credibility (Ö1), Eşik Bileşenleri (Ö2)
> Durum: Ö0 ve Ö1 sonuçlandı; Ö2 risk primi R5'e taşındı
> Son güncelleme: 2026-11-06
> İlgili: [14-natural-entry-exit](../research/simulation/14-natural-entry-exit.md), [D5b3g](D5b3g.md), K-029, S-020, framework İ12

**Kullanıcı onayı (2026-11-02):**
- Ö0, Ö1 ve Ö2 uygulanacak; Ö3 (gemi piyasası) şimdilik yok.
- Literatürdeki modeller koda tam doğrulukla geçirilecek; şüphe varsa kullanıcıyla konuşulacak.

**Taban:** WTA-UR (D5b3g'nin en iyi kurulumu). Bant (R) geçici vekil olarak duruyor.

## Ö0: ölçüm ve yöntem (`experiments/d5b3h_analyze.py`)

- **10 seed;** her ölçüt için seed'ler arası ortalama ± %95 güven aralığı (Student t).
- **Getiri ölçüleri** (hepsi öz sermaye + temettü üzerinden, batanlar ve çıkanlar dahil, snapshot anından sonra):
  - `agg_eq`: toplam sermaye getirisi (K-025; sermaye-yıl ağırlıklı)
  - `agg_incumbent`: snapshot anında var olan tüccarlar
  - `agg_entrant`: snapshot'tan sonra girenler
  - `public_track_mean`: yatırımcının gördüğü kamu sicilinin ortalaması
  - `entrant_ret_median`: giren tüccar getirisinin medyanı (ağırlıksız)
  - `agg_old`: eski tanım (`net_worth`; karşılaştırma için)
- **Örüntü ölçütleri** (pattern-oriented modeling; Grimm ve ark. 2005 ⚠️):
  - Giriş, çıkış ve iflas oranı (gemi-yıl başına)
  - Getiri dağılımının çarpıklığı ve zarar edenlerin payı
  - Filo CV, tepe / dip
  - Döngü süresi: filo serisinin otokorelasyonunda ilk negatif değerden sonraki ilk tepe, ay olarak
- **Tarihsel kontrol değerleri:** henüz yok. Ö2 literatür okumasında aranacak (iflas sıklığı, sigorta primleri).

## Ö1: credibility k veriden (`cred_rule="buhlmann"`)

**Model:** Bühlmann-Straub (1970) ⚠️, eşit ağırlıklı gözlemler, tüccar başına farklı gözlem sayısı.

- Gözlem: X_it = i tüccarının t ayındaki öz sermaye getirisi (son 12 ay, `emarks`).
- X̄_i = tüccarın ortalaması; n_i = ay sayısı (≥ 3); N = Σ n_i; X̄ = Σ n_i X̄_i / N.
- s² (süreç varyansının beklentisi) = Σ_i Σ_t (X_it − X̄_i)² / Σ_i (n_i − 1).
- a (gerçek ortalamaların varyansı) = [Σ_i n_i (X̄_i − X̄)² − (I − 1) s²] / (N − Σ n_i² / N).
- k = s² / a. a ≤ 0 ise k = ∞: tüccarlar arası fark gürültüden ayırt edilemiyor, kendi sicil bilgi taşımıyor.
- Kişisel beklenti = Z · 12 · X̄_i + (1 − Z) · kamu sicili, Z = n_i / (n_i + k).
- Tahmin her ay, yaşayan bütün tüccarlardan (en az 10) yeniden yapılır.

**Çeviride yapılan seçimler ve varsayımlar (Claude, ⚠️):**
1. **Bilgi birimi sefer değil ay.** Eski kuralda n = son 12 aydaki sefer sayısıydı. Bühlmann'da n ile k aynı birimde olmalı; gözlem aylık getiri olduğu için n = ay sayısı.
2. **Koşullu bağımsızlık varsayımı.** Bühlmann, bir tüccarın gözlemlerinin, gerçek ortalaması verildiğinde bağımsız olduğunu varsayar. Aylık öz sermaye getirisi sefer döngüsü yüzünden kısmen bağımlı olabilir (kâr satış ayında gerçekleşir). **Sağlamlık kontrolü:** aynı tahmin çakışmayan çeyreklik getirilerle de yapılıyor (`cred_log`'un 6. alanı, karara girmez).
3. **Kolektif ortalama = kamu sicili.** Bühlmann'ın tamamlayıcısı X̄ (yaşayanların ortalaması). Bizde batanlar dahil kamu sicili kullanılıyor (K-029 m.4). Fark bilinçli: yaşayanların ortalaması survivorship bias taşır.
4. **Kim tahmin ediyor?** Formül, bütün tüccarların verisini kullanıyor. Bu, 16. yy yatırımcısının gerçekte bilebileceğinden fazlası. Ö4'e (bilgi) kadar geçici.
5. **Evler** (çok gemili tüccar) bu kuralın dışında; tam haritada kapalı.

**Duman testi (VRS, kısa snapshot, 3 yıl):**
- 36 aylık tahminin 28'inde a ≤ 0, yani k = ∞. Çeyreklik kontrol de aynı sonucu verdi (28 / 36).
- s² aylık %1,3-8,5 (aylık sd ~%11-29).
- Bu, D5b3b'deki "sıralama formülü beceri ile şansı ayırt etmiyor" (skill vs luck) bulgusuyla tutarlı. Tam koşuda doğrulanacak.

## Ö2: eşik bileşenleri

### Senet getirisi: doğrulandı (birincil kaynağa yakın ikincil kaynak)

Fratianni & Spinelli (OeNB Working Paper 112), Tablo 1 ve dipnot 15:

| Dönem | Cenova (San Giorgio luoghi) | Venedik (Monti) |
|---|---|---|
| 1522-49 ortalama | 3,95% | |
| 1535-48 ortalama | 3,82% | 2,5% (4 gözlem) |
| 1549-76 ortalama | 3,76% | 4,0% (4 gözlem) |
| 1560 | 3,66% | |
| 1574-1603 ortalama | 2,59% | |
| 1604-1739 ortalama | 1,45% | |

- Cenova serisi Cipolla (1952) ve Cuneo verisine dayanıyor; Venedik değerleri Mueller (1997, Tablo 11.3).
- Venedik değerleri, faiz ödemelerinin gecikmesi (paghe) iskonto edilmediği için yukarı yanlı. Yazarlara göre iki kentin getirileri 1535-76'da çok yakın.
- **Düzeltme:** Arama özeti "%4 ortalama 1528-1573"ü Venedik darphanesine (depositi in Zecca) bağlamıştı. Asıl metinde bu, Cenova luoghi getirisi. Darphane mevduatı 1528'de piyasa faizi ödemeye başlıyor, ama oranı metinde yok.
- **Sonuç:** 1560 için senet getirisi %3,7-4,0. Bugünkü `bond_rate = 0,04` kaynakla tutarlı.
- Not: 1573'ten sonra faizler düşüyor. Uzun oyun süresinde senet getirisi zamanla değişen bir dünya değişkeni olabilir. Şimdilik sabit.
- Ek (ikincil, doğrulanmadı): Venedik'te %5'lik devlet borcu özel kredi faizinin hemen altındaydı; 17. yy başında terraferma'da ortalama özel faiz ~%6 (ScienceDirect genel bakış).

### Risk primi: çeviri şüpheleri (kullanıcıyla konuşulacak)

Model (Arrow 1965; Pratt 1964; Markowitz 1952 ⚠️): Göreli riskten kaçınması γ olan yatırımcı, servetinin w payını varyansı σ² olan bir yatırıma koyarsa, istediği ek getiri yaklaşık γ · w · σ²'dir. Merton (1969 ⚠️) portföy kuralının tersidir: w* = (μ − r) / (γ σ²).

Şüphe 1, **hangi σ²?** Sonucu bir büyüklük mertebesinden fazla değiştiriyor:
- (a) Toplam risk: yatırımcı tek gemiye yatırır.
- (b) Yalnızca ortak risk: yatırımcı çok sayıda gemide pay tutar; gemiye özgü risk çeşitlenir (CAPM mantığı; Sharpe 1964 ⚠️).
- (c) Ara: yatırımcı N gemiye pay (carati) dağıtır. Batma kaybı sigortalanabilir (Cenova'da 1564-71 arasından 757 poliçelik bir defter var; primler sefere göre %1-15).

Şüphe 2, **γ dağılımı:** Literatürdeki aralık geniş:
- Laboratuvar deneylerinde küçük bahislerle düşük (Holt & Laury 2002 ⚠️).
- Makro-finansta 1-10 (equity premium puzzle; Mehra & Prescott 1985 ⚠️).
- Tüccarlarımızda bugün U(0,5; 1,5) (Claude seçimi ⚠️).

**Ölçülen σ** (ön ölçüm: VRS-WTA-UR, 3 seed, 10 yıl, `out/d5b3h_probe/`):

| | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| Tek tüccarın yıllık getirisi, sd (en az 1 yıl yaşayan) | 0,60 | 0,48 | 0,58 |
| Aynısı, en az 3 yıl yaşayan | 0,42 | 0,46 | 0,56 |
| Ortak bileşen: toplam getirinin yıllık sd'si (çakışmayan yıllar) | 0,05 | 0,10 | 0,05 |

Uyarılar:
- Tek tüccar sd'si survivorship taşıyor: erken batanlar yaşam filtresiyle dışarıda kalıyor.
- Bu tablo kaba bir büyüklük göstergesi; Ö2 kararından önce aylık panelden düzgün ölçülecek.
- Ağırlıksız ortalamanın toplam getiriden yüksek görünmesi (%19-62'ye karşı %12) bu filtreden geliyor (survivor seçimi). Bütün tüccarlarla ağırlıksız ortalama %−6 ile %20 arası.

**Büyüklük:** γ = 1 için:
- (a) toplam risk, w = 1: prim ≈ 1 × 1 × 0,5² ≈ **%25**
- (a) toplam risk, w = 0,25: ≈ **%6**
- (b) yalnızca ortak risk: ≈ 1 × 1 × 0,05-0,10² ≈ **%0,3-1**

Seçim sonucu bir büyüklük mertebesinden fazla değiştiriyor. Bu yüzden kullanıcıya soruldu.

**Kullanıcı cevabı (2026-11-02, K-030):** (c) seçildi. Risk önce yapılandırılacak (rota ve mevsime bağlı fiziksel risk + ticari risk, sefer başına dinamik ortalama). γ grupları en sonda ayarlanacak. Ö2'nin risk primi kısmı [risk-model](../design/risk-model.md) R1-R5 sırasının sonuna (R5) taşındı.

## Kurulumlar ve koşu

| Kurulum | İçerik |
|---|---|
| `-WTA-UR` | Taban, 10 seed (Ö0 ölçümleriyle yeniden) |
| `-WTA-UR-B` | + Ö1 |

VRS ve F, 10 seed, 10 yıl. `out/d5b3h/`.

## Sonuçlar: Ö0 + Ö1 (2026-11-06)

10 seed, 10 yıl, ortalama ± %95 güven aralığı. Çıktı: `out/d5b3h/summary_F-WTA-UR_F-WTA-UR-B_VRS-WTA-UR_VRS-WTA-UR-B.json`.

| Ölçüt | F-WTA-UR | F + Ö1 | VRS-WTA-UR | VRS + Ö1 |
|---|---|---|---|---|
| Toplam getiri (agg_eq) | 0,185 ± 0,004 | 0,131 ± 0,024 | 0,196 ± 0,018 | 0,156 ± 0,014 |
| Yerleşikler | 0,141 ± 0,011 | 0,118 ± 0,022 | 0,134 ± 0,015 | 0,125 ± 0,029 |
| Girenler (sermaye ağırlıklı) | 0,358 ± 0,036 | 0,313 ± 0,149 | 0,558 ± 0,124 | 0,423 ± 0,200 |
| Giren medyanı (ağırlıksız) | −0,051 ± 0,022 | 0,157 ± 0,131 | 0,055 ± 0,120 | 0,090 ± 0,158 |
| Kamu sicili ortalaması | 0,111 ± 0,003 | 0,097 ± 0,011 | 0,119 ± 0,005 | 0,160 ± 0,047 |
| Zarar edenlerin payı | 0,46 | 0,29 | 0,43 | 0,41 |
| Giriş / gemi-yıl | 0,32 | 0,11 | 0,30 | 0,24 |
| Çıkış / gemi-yıl | 0,35 | 0,12 | 0,27 | 0,15 |
| İflas / gemi-yıl | 0,004 | 0,012 | 0,027 | 0,046 |
| Filo ortalaması | 118 ± 5 | 140 ± 19 | 45 ± 4 | 56 ± 11 |
| Filo CV | 0,32 | 0,22 | 0,42 | 0,39 |
| Tepe / dip | 3,4 ± 0,4 | 3,3 ± 2,1 | 4,6 ± 2,1 | 8,1 ± 5,2 |
| Döngü (ay) | 39 ± 7 | 55 ± 3 | 48 ± 7 | 47 ± 10 |
| k = ∞ payı (aylık / çeyreklik) | | 0,66 / 0,72 | | 0,71 / 0,69 |
| Sonlu k medyanı (ay) | | 100 | | 82 |

**Ö1 bulgusu (modele özgü):** Bühlmann tahmincisi, ayların üçte ikisinde tüccarlar arası gerçek fark bulamıyor (k = ∞). Bulduğunda k ≈ 80-100 ay, yani 12 aylık sicilin ağırlığı Z ≈ 0,1. Çeyreklik kontrol aynı sonucu veriyor. Kendi sicil neredeyse bilgi taşımıyor. Eski sabit kural (k = 9 sefer) kendi sicile yaklaşık %55-60 ağırlık veriyordu.

**Ö1'in etkisi:**
- Getiri hedefe yaklaştı (%18,5-19,6 → %13-16; eşik bandı %12-14).
- Devir azaldı: F'de giriş ve çıkış 3 kat düştü. Kötü sicilli tüccar artık kendi siciline bakıp çıkmıyor; herkes kamu ortalamasına bakıyor.
- Bedeli: iflas 2-3 kat arttı. Kendi sicili kötü olan tüccar, sicili şanstan ayırt edilemediği için kalıyor ve batıyor. Ekonomik olarak tutarlı: bilgi yoksa erken çıkış da yok.
- Döngü uzadı (F 39 → 55 ay). VRS'de tepe / dip kötüleşti ama güven aralığı çok geniş (± 5).

**Ö0 bulguları:**
- Seed'ler arası aralık bazı ölçütlerde çok geniş (giren getirisi, tepe / dip, çarpıklık). Bunlarla karar verilirken 10 seed az; ana ölçütler (toplam getiri, filo, oranlar) yeterince dar.
- **Girenler yerleşiklerden çok daha yüksek kazanıyor** (sermaye ağırlıklı %31-56'ya karşı %12-14), ama giren medyanı düşük. Aday açıklama: getiri öz sermaye üzerinden; gemi kapasitesi sabit olduğu için yerleşiklerin birikmiş fazla sermayesi boşta nakit olarak duruyor. Yani getiri ölçüsü sermaye büyüklüğüyle düşüyor. Doğrulanmadı ⚠️. Ö3 (gemi piyasası) ya da temettü kuralıyla ilgili.
- Kamu sicili (son 12 ay) toplam getiriden 5-9 puan düşük. Pencere ve ağırlık farkı; ayrıca incelenecek.
- Tarihsel kontrol değerleri (iflas sıklığı vb.) henüz yok.

**Karar için:** Ö1 kurulumu (`cred_rule="buhlmann"`) veri temelli olduğu için taban olmaya aday. Kullanıcıya soruldu.
