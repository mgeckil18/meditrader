# Deney D5b3c: Hibrit Tüccar Finansmanı (Borç + Denetlenebilir Colleganza)
> Durum: tamamlandı (2026-10-26)
> Kod: [`sim/world5.py`](../../sim/world5.py) (`debt`, `loan_type`, `loan_lev`, `loan_premium`, `ruin_weight`, `colleg_mode`, `colleg_ports`, `colleg_max_loss`, `colleg_beta`; `_update_finance`, `_loan_terms`, `_own_view`, `_finance`, `_repay`), [`experiments/d5b3c_finance.py`](../../experiments/d5b3c_finance.py)
> Yeniden üretmek: `python3 experiments/d5b3c_finance.py 10` (~18 dk)
> Çıktı: `experiments/out/d5b3c/table_raw.txt`, `summary.json`; duman: `smoke.txt`, `smoke2.txt`
> İlgili: [K-022](../decisions.md), [S-015](../open-questions.md), framework A12, [08-trade-finance-contracts](../research/simulation/08-trade-finance-contracts.md), [D5b3b](D5b3b.md), [mechanism-registry](../design/mechanism-registry.md)

## Soru

Kullanıcı kararı (K-022). Kullanıcı notu: tasarım kesin değil, deneyle sınanıyor.
- Likidite sıkıntısı çeken tüccar vadeli borç alır: faiz = senet + risk primi, kaldıraç ≤ 1.
- Borcunu ödeyemeyen batar ve silinir. Batma korkusu kararda ağırlık taşır ("hassas denge").
- Risk iştahı ve yeteneği düşük tüccar daha az borçlanmalı.
- Colleganza yalnızca çok düşük riskli, denetlenebilir rota-malda; yatırımcı öğrenir.
- Kullanıcı hipotezi: batma endişesi bir giriş friction'ı olarak işleyebilir.

Ölçülecek:
1. Borç likiditeyi çözüyor mu? Alacaklı kazanıyor mu?
2. Kim borçlanıyor (düzey, risk tutumu)?
3. Batma korkusunun etkisi ne (ablasyon)?
4. Colleganza düşük riskli rotada yatırımcıya kazandırıyor mu?
5. Denge getirisi ve giriş değişiyor mu?

## Mekanizma (köken etiketleriyle)

Ayrıntı ve köken: [mechanism-registry § D5b3c](../design/mechanism-registry.md).

- **Tetik:** Nakdi gemisini doldurmaya yetmeyen tüccar (D5b3'teki colleganza tetiği) üç seçenekten birini seçer: kendi nakdiyle git / borç al (özsermayenin %25, 50, 75 ya da 100'ü) / colleganza. **K**
- **Karar (C; L: Arrow-Pratt, Roy 1952):** U = E[servet] − γ/2 × Var(servet) / özsermaye − ruin_weight × γ × P(batma) × özsermaye. γ = tüccarın risk tutumu (DARA dahil).
  - P(batma) = P(sefer getirisi < borç / toplam sermaye − 1), normal yaklaşımla. Düz borçta buna batma olasılığı eklenir.
- **İnanç (C; L: Malmendier & Nagel 2016):** Tüccarın kendi sefer tahmini, kendi siciliyle güncellenir (k = 5 sefer). σ kendi sicilinden, sicil yoksa nüfustan; aşırı güven σ'yı daraltır.
- **Alacaklı (C):** Faiz = senet (%4) + prim (%4 ⚠️) yıllık + sefer başına öğrenilmiş kayıp primi (son 1 yılın temerrüt ve batma kaybı / anapara). Borç sefer sonunda ödenir.
- **İflas (K):** Ödeyemeyen tüccarın bütün nakdi alacaklıya gider; "battı" işaretlenir, aynı gün hiçbir şey yapamaz, ertesi gün silinir.
- **Deniz ödüncü (L: González de Lara 2000; K):** Kargo batarsa borç düşer, alacaklı deniz riskini taşır. Batma motorda zaten vardı (`_p_loss`, sefer başına ~%1-3).
- **Colleganza (K onay; C):**
  - Tüccarın ana limanı Venedik olmalı (sözleşme orada kayıtlı, denetlenebilir ⚠️).
  - Rota-mal son 1 yılda ≥ 8 sefer, zararlı payı ≤ %35 ⚠️, ortalama > 0.
  - Yatırımcı rotanın siciline bakar. Bütçe: aylık %10 × logistic(20 × (colleganza getirisi − senet)) (yatırımcı öğrenmesi).

## Kurulumlar

Hepsi D5b3 OS yapısında (spin-up + fırsata bağlı giriş + liman havuzu), 10 seed, metrikler son 5 yıl.

| Kurulum | Fark |
|---|---|
| OS | Finansman yok (taban) |
| D | Borç (düz: kargo batsa da ödenir) |
| D-sea | Deniz ödüncü |
| D-korkusuz | D, `ruin_weight = 0` (ablasyon) |
| DC | D + denetlenebilir colleganza + yatırımcı öğrenmesi |

## Koşu geçmişi (başarısızlar dahil)

| # | Ne | Sonuç |
|---|---|---|
| 1 | Duman, seed 0, çıktı klasörü yoktu | Koşu başlamadı (D5b3b'deki hatanın aynısı) |
| 2 | Duman, seed 0 | Davranış yönü doğru. Üç sorun: (a) colleganza'ya uygun hiçbir rota yok; (b) kayıp primi yıllıklaştırılmıştı, deniz ödüncü alacaklısı yılda −%109; (c) 🐞 temettü kuralı yatırımcı ve alacaklı parasını çekebiliyordu. Düzeltmeler: experiment-log D5b3c.1 |
| 3 | Duman 2 (D-sea, DC) | Yatırımcı öğrenmesi bütçeyi 0'a indirdi ve hiç geri dönmedi (bayat getiri). Düzeltme: görüş her ay son 1 yıldan; deneyim yoksa nötr |
| 4 | Asıl koşu, 5 × 10 seed | Aşağıda |

**Teşhis (duman 2'den önce): sefer getirisinin oynaklığı.** Seed 0, 6 yıl, son 2 yıl:

| Rota-mal | Sefer | Zararlı | Ortalama | sd | %10'luk dilim |
|---|---|---|---|---|---|
| ALE→VEN buğday | 190 | %34 | +%51 | %89 | −%47 |
| ALE→VEN biber | 109 | %28 | +%51 | %64 | −%23 |
| COR→VEN yağ | 117 | %56 | −%1 | %54 | −%68 |
| VEN→COR buğday | 35 | %63 | −%10 | %44 | −%52 |

- Venedik çıkışlı bütün rotalar ithalat yönünde ve zararlı.
- En güvenli rotada bile seferlerin %28'i zararlı.
- %15 eşiğiyle "çok düşük riskli rota" bu piyasada yok.

Not: Sefer getirisi = satış geliri / birim maliyet − 1. Küçük partilerde geçim gideri birim başına büyüdüğü için uç değerler şişebilir; sd'nin bir kısmı ölçüm gürültüsü olabilir ⚠️.

## Sonuçlar (10 seed medyanı, son 5 yıl)

### Tüccar kararı: kim borçlanıyor?

Oranlar, nakdin bağladığı plan kararları içinde borç seçilme oranıdır.

| Kurulum | Borç seçimi | Düzey 0 / 1 / 2 | Risk tutumu düşük / yüksek (alt / üst üçte bir) | Sicilsiz / ≥ 5 sefer | Borç / özsermaye (düzey 0 / 1 / 2) |
|---|---|---|---|---|---|
| D | %11 | **%4,6** / %18 / %13 | **%17 / %5,7** | %11 / %10 | 0,56 / 0,62 / 0,55 |
| D-sea | %12 | %4,8 / %21 / %14 | %17 / %6,7 | %15 / %12 | 0,47 / 0,64 / 0,53 |
| D-korkusuz | **%17** | %9,8 / %25 / %21 | %27 / %9,3 | %16 / %18 | 0,41 / 0,57 / 0,49 |
| DC | %9,8 (+ colleganza %3,5) | %5,0 / %16 / %11 | %16 / %3,9 | %3,8 / %11 | 0,57 / 0,62 / 0,66 |

### Alacaklı ve iflas

| Kurulum | Borç (5 yıl) | Temerrüt / borç | Kargo battı / borç | Alacaklının yıllık getirisi (seed aralığı) | Borçtan iflas (10 yıl) | Diğer iflas |
|---|---|---|---|---|---|---|
| D | 56 | **%10,3** | %2,9 | **+%1,8** (−%53 … +%59) | 10 | 38 |
| D-sea | 51 | %6,0 | %3,2 | −%2,4 (−%93 … +%58) | 8,5 | 43 |
| D-korkusuz | 88 | %10,8 | %3,2 | **−%20,7** (−%99 … +%23) | 11 | 37 |
| DC | 56 | %8,4 | %1,7 | +%0,1 (−%25 … +%18) | 8,5 | 43 |

### Piyasa ve giriş

| Kurulum | Getiri medyanı | Düzey 0 / 1 / 2 | Filo (başlangıç → son 5 yıl) | Giriş | Çıkış | Kıtlık | Glut / yıl |
|---|---|---|---|---|---|---|---|
| OS | %0,4 | −8 / −3 / +6 | 65 → 82 | 155 | 87 | 2/10 | 35,8 |
| D | −%0,5 | −10 / −2 / +5 | 59 → 80 | 173 | 92 | 1/10 | 35,4 |
| D-sea | −%0,5 | −16 / −3 / +6 | 65 → 82 | 162 | 89 | 0/10 | 34,6 |
| D-korkusuz | −%0,5 | −19 / −1 / +6 | 60 → 81 | 160 | 89 | 1/10 | 34,7 |
| DC | −%1,1 | −25 / −3 / +4 | 66 → 78 | 159 | 93 | 1/10 | 35,8 |

### Colleganza (DC)

- Uygun rota sayısı: 3 (seed medyanı).
- Son 5 yılda yalnızca 19,5 sözleşme var. Yatırımcı sözleşme başına **−%10,8** kaybediyor; sözleşmelerin %50'si zararlı.
- Yatırımcı öğrenmesi bütçeyi kısıyor. Yıl sonu bütçe payı %5, yani nötr: son yılda yeterli deneyim yok.

OS sonuçları D5b3b'deki OS ile birebir aynı (determinizm kontrolü ✅).

## Bulgular

**1. Karar mekanizması istenen yönde çalışıyor (Claude mekanizması, deneyle desteklendi).**
- Risk tutumu düşük tüccar, yüksek olandan üç kat sık borçlanıyor (%17'ye karşı %5,7).
- Düzey 0 tüccar, düzey 1'in dörtte biri kadar borçlanıyor (%4,6'ya karşı %18). Kendi kötü sicili inancını aşağı çekiyor (learning from experience).
- Batma korkusu kapatılınca borç %11'den %17'ye çıkıyor. Alacaklının getirisi +%1,8'den −%21'e düşüyor.
- Kullanıcının "risk iştahı ve yeteneği düşük tüccar daha az borçlanmalı" koşulu sağlanıyor.

**2. Ama borç sürdürülebilir değil: alacaklı senedi (%4) kazanamıyor.** Borçların %10'u temerrüde düşüyor. Alacaklı kayıp primini öğrenip faizi yükseltiyor (yıllığa çevrilmiş faiz %35-85). Ama getirisi senedin altında kalıyor ve seed'den seede −%53 ile +%59 arasında savruluyor. Olası iki açıklama ⚠️ doğrulanmadı:
- **(a) Adverse selection:** Faiz yükselince yalnızca en iyimser tüccarlar borçlanmaya devam eder (Stiglitz & Weiss 1981). Literatürün önerdiği çözüm fiyatı yükseltmek değil, kredi miktarını kısmak (credit rationing).
- **(b) Öğrenme gecikmesi ve küçük örnek:** Limanda yılda ~10 borç var; kayıp primi gürültülü.

**3. Asıl sorun sefer getirisinin oynaklığı (Claude teşhisi).**
- Sefer getirisinin sd'si %40-90. Seferlerin yaklaşık %10'u %50'den fazla kaybediyor (kaldıraç 1'de temerrüt eşiği).
- Aynı oynaklık D5b3b'de itibarın beceriyi ayırt edememesini ve colleganza'nın kaybettirmesini de açıklıyor.
- Hiçbir finansman sözleşmesi, ortalaması sıfıra yakın ve kuyruğu bu kadar kalın bir getiriyi alacaklıya kârlı hâle getiremez.
- Bu oynaklık tarihsel olarak makul mü? Doğrulanmadı. Glut sıklığı (yılda 35) ve kalabalık varışlar başlıca aday. Ölçüm gürültüsü de payı olabilir (yukarıdaki not).

**4. Kullanıcının friction hipotezi bu modelde desteklenmedi.** Giriş azalmadı, D'de arttı (155 → 173). Çünkü modelde yeni tüccar girişi borçla değil yatırımcı özsermayesiyle finanse ediliyor; batma korkusu yalnızca mevcut tüccarın borçlanmasını etkiliyor. Korkunun girişe yansıması için girişin kendisinin borçla finanse edilmesi gerekir. Bu bir tasarım sorusu.

**5. Deniz ödüncü düz borçtan ne iyi ne kötü.** Temerrüt azalıyor (%10 → %6), çünkü kargosu batan tüccar artık batmıyor. Alacaklının getirisi ise biraz daha kötü. Batan kargolar borçlu seferlerde %3 civarında, yani motorun ortalamasına yakın. Bu turda "deniz riskini alacaklı taşıyınca borçlu daha riskli rotaya kayar" (moral hazard) etkisi görülmedi.

**6. Denetlenebilir colleganza nadiren kullanılıyor ve yine kaybettiriyor.** Uygun rota az, çünkü düşük riskli rota yok (bulgu 3). Yatırımcı öğrenmesi kaybı sınırlıyor: bütçe kısılıyor ve toplam kayıp küçük kalıyor. Öğrenme mekanizması işliyor.

**7. Denge getirisi değişmedi (≈ %0, hedef %8).** Finansman yapısı, serbest girişin sıfır-kâr dengesine dokunmuyor. Kullanıcı talimatı gereği bu konu "sonra konuşulacak".

## Tasarıma etkileri ve açık sorular

- **K-022 sonucu:**
  - Karar mekanizması (hassas denge) tutuldu.
  - Borç teknik olarak çalışıyor, ama alacaklı için sürdürülemez.
  - Colleganza ölçütü, düşük riskli rota olmadığı için boşa düşüyor.
- **Önerilen sıradaki adım (kullanıcıyla konuşulacak):** Önce sefer oynaklığının teşhisi.
  - Zararlı seferler neden bu kadar sık ve derin? Glut, kalabalık varış, rota değiştirme, küçük partide geçim gideri.
  - Bu ölçüm hatasıysa düzeltilir. Gerçek dinamikse kalibrasyon sorusudur ve marj ve friction tartışmasına bağlanır.
  - Bunun ardından credit rationing (alacaklı borç miktarını sicile ve rotaya göre kısar) sınanabilir.
- **Girişin finansmanı:** Batma endişesinin friction olması isteniyorsa, yeni tüccar kendi sermayesinin bir kısmını borçla kurmalı. Bu, kullanıcının hipotezini sınanabilir kılar.
- **Batan gemi:** Zaten motorda vardı. Bunu önceki mesajda "eklenmesi gerekiyor" diye yanlış söyledim (lessons).

## Teşhis T2: sefer getirisi neden bu kadar oynak? (2026-10-26)

Script: [`experiments/d5b3c_volatility.py`](../../experiments/d5b3c_volatility.py), 6 seed, OS, son 5 yıl, 13.987 sefer; çıktı `out/d5b3c/volatility.json`.

| Grup | Sefer | Zararlı | Derin zarar (< −%50) | Geçim gideri hariç derin zarar | Rota değişti | Kalabalık (hedefin talep günü) | Varış fiyatı / kalkış fiyatı | Ambar doluluğu (medyan) | Kullanılan sermaye (medyan / ort.) |
|---|---|---|---|---|---|---|---|---|---|
| Bütün | 13.987 | %46 | **%14,1** | **%8,7** | %17 | 32 | 0,94 | **%8,8** | **%12 / %26** |
| Derin zarar | 1.968 | — | — | %62 | %35 | 56 | **0,67** | %6,8 | %6 / %25 |
| Kâr | 7.544 | — | — | — | %11 | 23 | 0,99 | %7,4 | %10 / %23 |
| Kalabalık düşük (alt üçte bir) | 4.663 | **%23** | %5,6 | %3,4 | %6 | 13 | 1,01 | | |
| Kalabalık yüksek (üst üçte bir) | 4.663 | **%65** | **%24** | %13 | %33 | 82 | **0,68** | | |
| Düzey 0 / 2 | | %55 / %42 | %15 / %13 | | %26 / %14 | | | | |

Diğer ölçümler:
- Sermaye ağırlıklı sefer getirisi +%14. Kâr eden seferlerin ortalaması +%72.
- Gemi başına yılda 5,75 sefer.
- Getiri ile korelasyon: kalabalık −0,18, rota değiştirme −0,09, doluluk +0,03.

**Bulgular (Claude teşhisi; literatür bağları ⚠️):**

1. **Oynaklığın ~%40'ı ölçüm.** Sefer getirisi birim kargo maliyetine göre ölçülüyor ve geçim gideri içinde. Ambar doluluğu medyanı %9 olduğu için geçim gideri birim başına şişiyor. Geçim gideri hariç tutulunca sd 1,31'den 0,80'e, derin zarar %14'ten %9'a iniyor.
   - Bu metrik sicilde, credibility'de ve borç kararındaki σ'da kullanılıyor.
   - Doğrusu, sermayeye göre getiri.
   - Motorumuza özgü bir ölçüm sorunu.

2. **Gerçek oynaklığın kaynağı varıştaki kalabalık (koordinasyon başarısızlığı).** Bir seferle aynı hedef-mala ±3 hafta içinde kalkan kargo, medyanda hedefin 32 günlük talebi. Bu, tüccarların hedef aldığı 30 günlük derinliğin üstünde.
   - Kalabalığın üst üçte birinde zararlı sefer %65, derin zarar %24; varış fiyatı kalkıştakinin %68'i.
   - Alt üçte birde zararlı sefer %23.
   - Literatürde bilinen: entry cobweb ve market entry oyunlarında koordinasyon (Camerer & Lovallo 1999 ⚠️). Simülasyon sefer düzeyinde yeniden üretti.

3. **Beceri farkı kuyrukta küçük.** Derin zarar düzey 0'da %15, düzey 2'de %13. Kalabalık herkesi vuruyor. Bu, D5b3b'deki "sicil beceriyi göstermiyor" bulgusunun mekanizması.

4. **Sıfır-kâr dengesi ince marjla değil, boş sermayeyle geliyor.**
   - Sefer marjları yüksek: sermaye ağırlıklı +%14, kâr eden seferlerde +%72.
   - Ama sefer başına kullanılan sermaye medyanda %12 ve ambar %9 dolu. Engel, pazar derinliği: çok fazla gemi küçük partiler taşıyor.
   - Literatürde bilinen fazla giriş sonucu: rant kopyalanan kapasiteyle eriyor (Mankiw & Whinston 1986 ⚠️). Simülasyon yeniden üretti.
   - Bu, finansmanın neden etkisiz kaldığını da açıklıyor: tüccarların çoğunu bağlayan nakit değil derinlik. Kararların yalnızca ~%11'inde nakit bağlıyor.

5. **Açık uyumsuzluk ⚠️.** Ortalamalarla kaba hesap yılda ~%16 brüt getiri veriyor (sefer başına %14 × sermayenin %26'sı × 5,75 sefer − geçim). Oysa ömür boyu getiri medyanı ~%0.
   - Olası nedenler: ortalama ile medyan farkı (kazanç az sayıda tüccarda toplanıyor); kısa ömürlü girişler; batan kargoların sefer kaydına girmemesi.
   - Ayrıştırılmadı.

## Düzeltme (2026-10-26, D5b3d T1)

T2'nin 4. bulgusu ("sıfır-kâr dengesi boş sermayeyle geliyor, getiri ≈ %0") ve 7. bulgusu ("denge getirisi değişmedi ≈ %0") **ömür boyu getiri medyanına** dayanıyordu. Bu ölçüt yanıltıcı:
- Sermaye-yıl ağırlıklı toplam getiri (batanlar dahil) OS'te %12,8, D''de %12,4.
- Medyanı, kısa ömürlü başarısız girişler aşağı çekiyor: tüccarların %52'si zararlı, en iyi %10 kârın %58'ini alıyor.
- Boş kapasite (ambar %9 dolu) ve kalabalık bulguları geçerli. Ama "kârlılık sıfır" değil; kâr çok çarpık dağılıyor.
- T2'deki "açıklanamayan fark" (5. bulgu) böylece açıklandı: brüt tahmin (%16) ile toplam getiri (%12-13) tutarlı.

Ayrıntı: [D5b3d](D5b3d.md) T1.
