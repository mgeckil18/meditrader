# Mekanizma Kaydı (köken ve durum)
> Durum: canlı doküman
> Son güncelleme: 2026-10-26
> İlgili: [CLAUDE.md 7d](../../CLAUDE.md), [decisions](../decisions.md), [framework](framework.md), [simulation-spec](simulation-spec.md), [process/experiment-log](../process/experiment-log.md)

Bu doküman simülasyondaki her mekanizmanın **nereden geldiğini** tutar. Amaç: ileride her şeyi yeniden inceleyebilmek (kullanıcı isteği, 2026-10-26).

**Köken:**
- **K** = kullanıcının fikri ya da kararı
- **C** = Claude'un önerisi ya da tasarımı
- **L** = literatürden uyarlama (kaynak belirtilir)

Çoğu mekanizma karışıktır, ör. "K fikir + C tasarım". **Fikir** ne yapılacağı, **tasarım** nasıl yapılacağıdır (formül, sınır, katsayı).

**Durum:**
- **Karar:** kullanıcı açıkça onayladı (K-xxx).
- **Claude ekledi, deneyle desteklendi:** deneyde çalıştı, kullanıcı itiraz etmedi. **Kesin değil**, yeniden incelenecek.
- **Deneysel:** henüz yalnızca bir deneyde var.
- **Kaldırıldı:** yerine başka mekanizma geldi.

⚠️ D1-D4c satırları geriye dönük, konuşma kayıtlarından ve süreç günlüğünden derlendi. Köken ayrımı yer yer yaklaşık.

## Pazar ve fiyat

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| Kent talep havuzu (esneklik, bütçe) | C tasarım; L (King-Davenant, Stone) | D1 | Claude ekledi, deneyle desteklendi | |
| Mala göre farklı esneklik, zorunlu mal tabanı | K fikir | D1 sonrası, D4 | Karar düzeyinde (A6) | Kullanıcı: "köylü yemek yemek zorunda" |
| Köylünün kendi tüketimi (self_share) | K fikir; C tasarım | D1f | Claude ekledi, deneyle desteklendi | |
| Köylünün hasat sonrası nakit ihtiyacı (front_load) | C | D1g | Claude ekledi, deneyle desteklendi | |
| Dükkâncı cover kuralı (stok / müşteri talebi) | C | D1 | Kaldırıldı (toptan pazarlı dünyada K-016) | D1-D5 serisinde kullanıldı |
| Dükkâncı PI kuralı (integral + oransal) | C; L (kontrol teorisi) | D1g | Kaldırıldı (toptan pazarlı dünyada); oransal kıtlık çarpanı K-016 içinde sürüyor | |
| Yerine koyma maliyeti (RC) | C | D1f | K-016'nın parçası (açık toptan fiyatın 3 günlük ortalaması) | |
| D5a mekanik iki yönlü çekiş | C | D5a | **Kaldırıldı** (kullanıcı itirazı, D5a2) | Teşhissiz eklenmişti |
| Stokçu (temelci; hasat haberi, medyan olağan fiyat, carry) | C; L (Williams & Wright; Deaton & Laroque; King-Davenant) | D1f, D1g | Claude ekledi, deneyle desteklendi | |
| Kurumsal toptan pazar (kapan, tek fiyatlı günlük takas) | C öneri; K karar kuralı ("çözerse kurumsal kalır") | D5a | Karar (K-013) | |
| Kapan resmi %1 | C | D5a | Claude ekledi ⚠️ yer tutucu | |
| Rekabetçi perakende: fiyat kırma ve fiyat yükseltmenin rekabetçi maliyeti olmalı | **K fikir** | D5a2 | Karar (K-016) | |
| Logit müşteri payı + 30 günlük atalet | C tasarım; L (McFadden; Anderson, de Palma & Thisse; Klemperer) | D5a2 | Claude ekledi, deneyle desteklendi | β = 12 ⚠️ |
| Lerner marjı μ = 1/(ε_i − 1) | C; L (Lerner 1934) | D5a2 | Claude ekledi, deneyle desteklendi | |
| Türetilmiş talep: kapan'a kademeli alış emri, gözlenen fiyatın en çok %50 üstü | C; L (derived demand) | D5a2 | Claude ekledi, deneyle desteklendi | %50 tepe Claude'un seçimi ⚠️ |
| Perakende giriş-çıkışı (12 aylık işletme kârı) | C (D3b'nin dükkâna uyarlanması) | D5a2 | Claude ekledi, deneyle desteklendi | |
| Yeni dükkânın ilk satış beklentisi = umduğu pay | C | D5a2 | Claude ekledi, deneyle desteklendi | |
| Dükkâncının geçimi (sabit gider, tüccarla eşit) | C öneri; **K karar** | D5a2 | Karar (K-016) | |
| Örtük anlaşma beklenmiyor; perakende rantı → devlet eventi | **K** | D5a2 | Karar (K-016) | |
| İşlemsiz oturumda açık fiyat = en yüksek alış teklifi | C | D5a3 | Claude ekledi, deneyle desteklendi (K-017) | |
| Rafı boş dükkâncının tâtonnement'ı, ödenen en yüksek fiyatla sınırlı | C; L (Walras) | D5a3 | Claude ekledi, deneyle desteklendi (K-017) | Sınır Claude'un seçimi ⚠️ |
| Müşterinin fiyat yönüne bağlı arama (rockets and feathers) | C öneri | — | **Ertelendi** (K: "akılda kalsın") | framework §8 |

## Talep ve üretim

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| LES + CES talep (two-stage budgeting) | C; L (Stone; Deaton & Muellbauer) | D4 | Claude ekledi, deneyle desteklendi | |
| Kent sınıfları (zengin / orta / yoksul) | **K fikir** (zenginin kumaşı farklı); C tasarım | D4b | Karar düzeyinde | |
| Kumaşın ikiye ayrılması (kaba / ince) | **K** | D4b, D4c | Karar düzeyinde | |
| Üretim zincirleri, ortak hammadde, üretici havuzları | **K fikir**; C tasarım (Leontief reçete) | D4c | Karar düzeyinde | |
| Ücretler ve Labrousse çarpanı | C; L (Labrousse) | D4c | Deneysel (ihracatlı dünyada test edilmedi) | |

## Tüccarlar, bilgi ve beklenti

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| Açgözlü çekirdek karar kuralı | C (D2 yarışması) | D2 | Claude ekledi, deneyle desteklendi | |
| Bilgi gemiyle taşınır + limanda söylenti (p_hear) | **K fikir** (bilgi yavaş yayılmalı); C tasarım | D3 | Karar düzeyinde | |
| C4 beklenti: log-normal dağılım + olağana dönüş | **K** (log-normal); C (olağana dönüş, medyan) | D3 | Claude ekledi, deneyle desteklendi | |
| Senede bağlı serbest giriş-çıkış (senet + risk) | **K** çerçeve; C mekanizma | D3b | Karar düzeyinde (Y10b) | Giriş hızı ⚠️ (D5b B6) |
| Tüccar çeşitliliği (yetenek, risk, servet, bilgi kaynakları) | **K fikir**; C tasarım | D5b | Karar (K-014) | |
| Düzey 0/1/2, Poisson(τ = 1,5) | C; L (Camerer, Ho & Chong) | D5b | Claude ekledi, deneyle desteklendi | |
| Taklit bonusu (%10 × duyulan/derinlik) | C | D5b | Claude ekledi ⚠️ biçim ve büyüklük keyfi | |
| Aşırı güven (log-normal, medyan 0,82) | C; L (Odean) | D5b | Claude ekledi ⚠️ | |
| DARA + safety-first risk formülü | C; L (Arrow-Pratt, Roy) | D5b | Claude ekledi ⚠️ | |
| "X, Y'ye Z yükledi" söylentisi (liman içinde de %30/gün) | **K** (rumor modeli; liman içinde söylenti kalsın) | D5b | Karar (K-014) | |
| Limanda bekleyen kargo görünür, haberle taşınır | C | D5b | Claude ekledi, deneyle desteklendi | |
| Rakip bilgisi rota değiştirmede de kullanılır | C | D5b | Claude ekledi, deneyle desteklendi | |
| Kalabalığın fiyat etkisi D/(D + kalabalık) | C | D5b | Claude ekledi ⚠️ birim esneklik varsayımı | |
| Rota değiştirme: kargo hedefin 30 günlük tüketimine sığmalı | C (D5 yaması) | D5 | El kuralı; S açıkken devre dışı | |
| Kırıntı kargo fire sayılır (`dust_lot = 1` birim) | C (D5b2 teşhisi) | D5b2 | Hata düzeltmesi (Zeno artifact'ı) | Orantılı paylaşım kalan miktarı hiç sıfırlamıyordu; D5-D5b2.2 sonuçları `dust_lot = 0` ile üretildi |
| Satamayan tüccarın asgari fiyatının günde %2 düşmesi | C (D5 yaması) | D5 | El kuralı; S açıkken devre dışı | |

## D5b2 yuvaları (deneysel)

| Mekanizma | Köken | Deney | Durum |
|---|---|---|---|
| **G:** Limandaki alımlar açık (kim, ne, ne kadar); hedef söylenti; kapan hacmi görünür | **K** ("alışverişler explicit") | D5b2 | Karar (K-019); tek başına etkisi küçük, zararı yok |
| **B:** Kendi kargosunun fiyat etkisi | C (D5b2 tartışması) | D5b2 | Claude ekledi, deneyle desteklendi (S'nin fazla gönderimini dengeliyor; GBSL·imp en iyi kurulum) |
| **B:** İleriye bakan beklenti (hasat haberi, mevsim) ve haber/fiyat ağırlığı | **K fikir** (beklenti geleceğe dair projeksiyon); C tasarım; L (Brock & Hommes 1998) | D5b2 | **C tasarımı başarısız** (yarar yok; kendi-etkiyle ısınma kıtlığı). Fikir duruyor, temel yeniden tasarlanacak → S-014 |
| **S:** Günlük sat / bekle / rota değiştir; bekleme maliyeti (fırsat maliyeti) | **K fikir** (fırsat maliyeti yüzünden ucuza satar); C tasarım; L (McCall 1970) | D5b2 | Deneyle desteklendi, koşullu: tek başına fazla gönderim üretiyor; B kendi-etkiyle birlikte dengeli |
| **L:** Stokçu bütün mallarda; envantere göre teklif kaydırma | **K fikir** (depocu; ayrı rol, oyuncuya birlikte sunulur); C tasarım; L (Ho & Stoll 1981) | D5b2 | Deneyle desteklendi (en etkili tek yuva); kaydırma katsayısı 0,3 ⚠️ |

## D5b3 yuvaları (deneysel)

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| Kararlı başlangıç: ön koşu (spin-up) ile başlangıç filosu | **K** (K-020); C tasarım (3 yıllık ön koşu, son 180 günün ortalaması) | D5b3 | Deneysel | |
| Liman başına sermaye havuzu (nüfusa göre bölünmüş; çıkış, iflas artığı, temettü geri döner; senet faizi kadar büyür) | **K** (halk sermayesi, liman başına); C tasarım | D5b3 | Deneysel | Büyüklük `pool_mult = 6` ⚠️ |
| Price current: limanın kamuya açık, gemi haberleriyle güncellenen fiyat tablosu; yeni giren tüccar bununla başlar | C; L (McCusker & Gravesteijn 1991) | D5b3 | Deneysel | |
| "Genel bilinen fırsat" = limandaki tüccarların beklentilerinin medyanı (liman konuşması); tüccar yoksa temsilî düzey 1 | **K** ("genel biliniyorsa"); C tasarım | D5b3.2 | Deneysel | İlk tasarım (yalnızca temsilî tüccar) hayalet farklar gördü |
| Yatırımcı eşik dağılımı: istenen risk primi log-normal (medyan = risk primi) | C | D5b3 | Deneysel | σ = 0,5 ⚠️; aylık ilgi %2 ⚠️ |
| Giriş inancı = sicil + (sefer kârı / sermaye) × gecikme indirimi / ufuk | C; L (optimizer's curse: Smith & Winkler 2006) | D5b3.1 | Deneysel | Ufuk 3 yıl ⚠️ |
| Döngü süresi: konumlanma + 2 × yol + 3 + kargo / talep | C (düzeltme) | D5b3.1 | Deneysel | |
| Donatılan gemiler limanda görünür, kalabalığa sayılır | C | D5b3.1 | Deneysel | Entry cobweb tamponu |
| Çıkış: gerçekleşen getiri < senet **ve** inanç < senet | C (K-020'nin simetrisi) | D5b3 | Deneysel | |
| Colleganza: nakdi yetmeyen tüccara liman yatırımcısı sermaye verir; kârın 3/4'ü yatırımcıya, zarar yatırımcının | **K** ("colleganza da olsun"); C tasarım; L (Lane 1973 ⚠️; González de Lara 2008 ⚠️) | D5b3 | Deneysel | Tek sözleşmede havuzun ≤ %5'i ⚠️ |
| Colleganza kararı: sefer tahmini × w + limanın geçmiş colleganza getirisi × (1−w) | C | D5b3.1 | Deneysel | w = 0,25 ⚠️ |
| Dükkân teklifi nakdiyle sınırlı (`budget_bids`) | C (D5b3.5 teşhisi) | D5b3 | Hata düzeltmesi | Bütçesiz emir kapan'ı donduruyordu; D5a2-D5b3 v1 sonuçları `budget_bids = False` ile |
| Batan dükkân kapanır (son dükkân da); hiç kalmazsa görünen fiyatla yenisi açılır | C | D5b3 | Claude ekledi | Eski çıkış kuralı n > 1 şartıyla son dükkânı koruyordu |

## D5b3b yuvaları (deneysel)

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| Colleganza sermayesi itibara göre: talepler skora göre sıralanır, aylık bütçe (havuzun %10'u ⚠️) yukarıdan aşağı dağıtılır | **K** (K-021: itibar, sıralayıp seçme) | D5b3b | Deneysel → **kapı tutuldu** | Yatırımcı kaybı −%24 → −%4; kazanç sıralamadan değil (gate ablasyonu) |
| Skor A: bir yıllık hacim × kâr oranı × kârlı işlem oranı; beklenen getiri = kâr oranı × 365 / medyan süre | **K** (formül kullanıcının) | D5b3b | Deneysel | Spearman(skor, getiri) ≈ 0; rastgele sıralamadan iyi değil (sinyal yok, kalıcılık 0,06-0,13) |
| Skor B: credibility; sefer getirisi ortalaması k = 5 sefer ağırlığıyla nüfus medyanına çekilir, −1 standart hata, yıllıklaştırılır | C; L (Bühlmann 1967; Bayes shrinkage) | D5b3b | Deneysel | k, λ, pencere ⚠️. user'dan farkı yok; düzey 0 payını azaltıyor (%22'ye karşı %35) ama getiri iyileşmiyor |
| Yeni giriş için yatırımcının alternatifi = max(senet, colleganza'nın sermaye-zaman ağırlıklı yıllık getirisi) | C (kullanıcının "itibar girişe friction getirebilir" hipotezinin mekanizması) | D5b3b | Deneysel; **devreye girmedi** (colleganza getirisi negatif → alternatif = senet) | |
| Sicilsiz tüccara (skor A) sermaye yok | **K** formülünün sonucu | D5b3b | Deneysel | Cold start |
| Ablasyon `reputation="gate"`: skor A kapısı, rastgele sıralama | C | D5b3b.4 | Teşhis aracı | Oyun mekanizması değil |

Açık eksik (Claude tespiti, D5b3b): yatırımcı öğrenmiyor; bütçe sabit, yılda −%40-50 kaybetse de para vermeye devam ediyor. Kullanıcıyla konuşulacak.

## D5b3c yuvaları (deneysel; K-022, kullanıcı notu: kesin değil)

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| Likidite için vadeli borç, liman havuzundan | **K** ("tersine senet") | D5b3c | Deneysel | |
| Kaldıraç sınırı 1 (borç ≤ özsermaye) | **K** | D5b3c | Deneysel | |
| Ödeyemeyen tüccar batar: "battı" işareti, faaliyet yok, denklemden çıkar; bütün nakdi alacaklıya | **K** | D5b3c | Deneysel | |
| Batma korkusu karar ağırlığı ("hassas denge"): U = E[servet] − γ/2 × Var / servet − ruin_weight × γ × P(batma) × özsermaye | **K** fikir; C formül; L (Arrow-Pratt; Roy 1952 safety-first) | D5b3c | Claude ekledi, deneyle desteklendi (ablasyon: korkusuz borç %11 → %17, alacaklı +%2 → −%21) | `ruin_weight = 1` ⚠️. P(batma) normal yaklaşımla; düz borçta + batma olasılığı |
| Borç inancı: kendi tahmini, kendi siciliyle güncellenir (k = 5 sefer) | C; L (Malmendier & Nagel 2016) | D5b3c | Claude ekledi, deneyle desteklendi (düzey 0 %4,6, düzey 1 %18) | Kullanıcının "yeteneği düşük tüccar daha az borçlanmalı" koşulunun mekanizması |
| Faiz = senet + %4 prim ⚠️ + sefer başına öğrenilmiş kayıp primi (son 1 yıl, ≥ 5 borç; önsel: düz borçta %2, deniz ödüncünde rotanın batma olasılığı) | C (alacaklı öğrenmesi) | D5b3c | Claude ekledi; **yetersiz** (alacaklı senedin altında) | İlk sürüm yıllıklaştırılmış primdi (hata, D5b3c.1). Aday: credit rationing |
| Deniz ödüncü (`loan_type = "sea"`): kargo batarsa borç düşer | L (González de Lara 2000); K (batan gemi riski istendi) | D5b3c | Deneysel | Batma motorda zaten vardı (`_p_loss`) |
| Colleganza yalnızca denetlenebilir (tüccarın ana limanı Venedik ⚠️) ve düşük riskli (son 1 yıl ≥ 8 sefer, zararlı payı ≤ %35 ⚠️, ortalama > 0) rota-malda; yatırımcı rotanın siciline bakar | **K** (onay); C öneri; L (González de Lara 2000) | D5b3c | Deneysel | %15 eşiğinde hiç rota yok |
| Yatırımcı öğrenmesi: aylık colleganza bütçesi = %10 × logistic(20 × (son 1 yılın colleganza getirisi − senet)); deneyim yoksa yarı bütçe | **K** fikir (liman getirisine bağlı); C formül | D5b3c | Claude ekledi | β ⚠️ |
| Borç ya da colleganza açıkken temettü yok | C (hata düzeltmesi, D5b3c.1) | D5b3c | Hata düzeltmesi | D5b3/D5b3b'de temettü kuralı yatırımcı parasını çekebiliyordu |

## D5b3d yuvaları (deneysel; K-023, K-024; kullanıcı notu: kesin değil)

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| Ölçüm düzeltmesi: sefer marjı geçim/gemi giderinden arındırılmış (`record_net_overhead`); borç kararında risk = kargo marjı × kargonun sermayedeki payı | C (D5b3c T2 teşhisi); **K** onay ("düzgün olması lazım") | D5b3d | Hata düzeltmesi | Eski deneyler bayrak kapalı, yeniden üretilebilir |
| Sefer bazlı alacaklı: bilgi = başvurular + price current + limanda görünen yüklemeler + borç defteri; tahmin düzey 2 benzeri | **K** fikir (K-023); C mekanik; L (Diamond 1984; Rialto) | D5b3d | Deneysel | |
| Faiz: borç = b × (1 + (senet + %2 ⚠️) × T / 365) / (1 − PD × (1 − RR) − kayıp), RR = 0,5 ⚠️ | C | D5b3d | Claude ekledi | |
| Sıralı fiyatlama: önceki borçların seferleri kalabalık sayılır | C ("sefer başvurularının bilgisi alacaklıda" sorusunun cevabı) | D5b3d | Claude ekledi; piyasa ölçeğinde etkisiz | Congestion pricing; borçlu sefer az olduğu için kalabalığı değiştirmedi |
| Credit rationing: PD > %25 ⚠️ ise borç yok | C; L (Stiglitz & Weiss 1981) | D5b3d | Claude ekledi; **aşırı temkinli** | ~2.400 red, borç seçimi %16 → %5 |
| Alacaklı kalibrasyonu: gerçekleşen / tahmin edilen temerrüt, son 1 yıl, ≥ 10 borç, [0,5; 3] | C | D5b3d | Claude ekledi | |
| Faiz sinyali: düzey ≥ 1 tüccar kendi beklentisini alacaklınınkine %50 ⚠️ yaklaştırır | **K** fikir ("düşük bilgiliye insight"); C formül | D5b3d | Claude ekledi | |
| Giriş ve kalma eşiğine batma bedeli: kamuya açık iflas sıklığı (son 1 yıl / filo) × %90 × ağırlık; kalmada × tüccarın risk tutumu | **K** fikir (öz sermayede batma cezası, K-024); C formül; L (Kihlstrom & Laffont 1979) | D5b3d | Deneyle desteklendi | Filo 81 → 72, toplam getiri %13,6 → %17,2 |
| Gemi masrafı + amortisman: günde 40 ⚠️, boşta da ödenir | **K** (K-024); L (Bresnahan & Reiss 1991 mantığı) | D5b3d | Deneysel | Filo 81 → 71; getiri yükselmedi. Değer tarihsel olarak doğrulanmadı |

## D5b3e yuvaları (deneysel; K-026, K-027; kullanıcı notu: kesin değil)

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| E1 ablation bayrağı `l0_counts_rivals` (seviye 0 da rakip yükleri sayar) | C | D5b3e | Yalnız teşhis | Kalabalığı değiştirmedi |
| Muhabir ağı (`network`): ana liman + 1 muhabir (yakınlığa ağırlıklı); ağdaki limandan haftalık mektup, gecikme = deniz yolu süresi; ağ dışında alış ve satışta %2,5 ⚠️ komisyon; bir limanda 3 satış → muhabir; azami 5 liman | **K** (limana bağlı tüccar, K-026); C yumuşak biçim ve parametreler; L (Trivellato; Datini; Roy 1951) | D5b3e | Deneysel | Komisyon Claude seçti, arşivle düzeltilecek (K-027) |
| Çok gemili tüccar (`houses`): başlangıç filosunun %30'u ⚠️ 2-4 gemili evlerde; ortak kişilik, ağ ve aylık ortak bilgi; günlük ortak kasa (borçsuz üyeler); kendi kargosunu kesin ve tam sayar, kendine taklit yok | **K** (çok gemili tüccar, ortak zarar; K-026, K-027); C biçim; L (Datini) | D5b3e | Deneysel | Gemi alma yok (Ertelendi) |

## D5b3f-g yuvaları (deneysel; K-028, K-029; kullanıcı notu: gelecek hafta literatürle doğrulanacak)

| Mekanizma | Köken | Deney | Durum | Not |
|---|---|---|---|---|
| Teşhis bayrakları `cold_track`, `entry_bonus` | C | D5b3f | Yalnız ablation | |
| Snapshot başlangıcı (`warm_start`): uzun ön koşudan nesnel kuralla seçilen an; yapılandırma hash'ine bağlı; 3 snapshot | **K** (snapshot fikri); C (seçim kuralı, hash, çoklu snapshot) | D5b3g | Deneysel | Motor düzeltmesi (soğuk başlangıç artifact'ı) |
| Ortak eşik (`hurdle_rule="common"`): giriş ve çıkış eşiği = senet + risk primi; log-normal yalnızca hız | **K** (eşik = senet + risk); C (hız biçimi) | D5b3g | Deneysel | ⚠️ %8 düzeltilecek (K-029) |
| Sefer sonunda çıkış (`exit_rule="voyage"`): beklenti < eşik ise açığa ikna olma olasılığıyla çıkar | C | D5b3g | Deneysel | Eski aylık + boş ambar + %10 kuralının yerine |
| Kamu sicili = toplam sermaye getirisi, batanlar ve çıkanlar dahil (`public_track="aggregate"`), son 12 ay, öz sermaye üzerinden | **K** (K-029 m.4); C (aylık hesap, öz sermaye) | D5b3g | Deneysel | |
| Kişisel beklenti: credibility ağırlığı w = n / (n + 9) (`shrink_k`) | K + C (kullanıcı fikri, Claude biçimi; L: Bühlmann ⚠️) | D5b3g | Deneysel | k = 9 Claude seçti ⚠️ |
| Kişisel beklenti, k veriden (`cred_rule="buhlmann"`): Bühlmann-Straub, aylık öz sermaye getirileri, her ay yeniden; tamamlayıcı = kamu sicili | L (Bühlmann & Straub 1970) + C (çeviri seçimleri, D5b3h) | D5b3h | Deneysel; deneyle desteklendi (getiri eşiğe yaklaştı, iflas arttı) | Ayların %66-71'inde k = ∞ |
| `M5.equity()`: öz sermaye = net değer − borç − colleganza sermayesi | C (ölçüm düzeltmesi) | D5b3g | Deneysel | Eski `marks` kaldıraçla şişiyordu (borç kullanımı kararların %3-5'i) |
| Teyitli giriş (`entry_confirm=3`, `entry_confirm_gap=3`): aday tüccar 6 ayda 3 değerlendirme; hepsinde eşiğin üstünde ise girer | **K** (kullanıcı önerisi, 2026-10-30); C (kişisel prim, vazgeçme); L (real options, drift diffusion) | D5b3g | Deneysel; tek başına döngüyü büyüttü, bantla birlikte (U + R) en düşük devir ve pozitif giren kuşak | |
| Real options bandı (`band_kappa`): giriş + κσ, çıkış − κσ | C; L (Dixit 1989) | D5b3g | **Geçici vekil** (kullanıcı, 2026-11-02: gemi piyasası gelene kadar); D5b3g.3'te en etkili sönümleyici, ama getiriyi hedefin üstüne taşıyor | κ = 1 Claude seçti ⚠️ |
| Bacak + bölge tehlikesi (`hazard_model="leg"`): sefer başına doğal + korsan kaybı, bölgesel kış çarpanı | **K** fikir (K-030); L (Ceccarelli 2007, Del Treppo 1972: bölge > mesafe, mevsim bölgesel); C sayılar | D5b3i | Deneysel | Bütün sayılar ⚠️ Claude |
| Korsan baskısı: bölge başına log-AR(1) + sıçrama, ortalama 1 | C; L (prim sıçramaları, Ceccarelli 2007) | D5b3i | Deneysel | ρ, σ, sıçrama ⚠️ |
| Gemi kaybı yenileme bedeli (`ship_loss`) | C (Ö3'e kadar vekil) | D5b3i | Geçici vekil; Ö3 açıkken kullanılmaz | K-032: gemi kaybı (a) seçildi |
| Gemi piyasası (`ship_market`): gemi yaşlanan, batan, alınıp satılan varlık; giriş = gemi edinmek, çıkış = gemiyi satılığa çıkarmak | **K** (Ö3'ü öne çekme, K-032); C (bütün biçim); L (Dixit 1989 batık maliyet; Tobin 1969 q; shipping cycle kuramı) | D5b3j | Deneysel | Band (R) bunun yerine kaldırıldı |
| Değerleme: gemi değeri = R + (beklenen − istenen getiri) × (sermaye + R) × a(r, H); H = `invest_horizon` | C; L (Tobin's q, Hayashi 1982 ⚠️) | D5b3j | Deneysel | Ufuk 3 yıl ⚠️ |
| Çıkış eşiği düzeltmesi: gemi yerine koyma değerinin altında satılıyorsa kalma eşiği düşer, üstündeyse yükselir | C; L (Dixit 1989 hysteresis) | D5b3j | Deneysel | |
| İkinci el: aylık tek fiyatlı çağrılı pazar; alıcı teklifi = gemi değeri − tersane/yabancı seçeneğinin artığı; satıcı en az söküm değeri; işlem yoksa fiyat = en iyi teklif | C (kapan ile aynı mantık) | D5b3j | Deneysel | Yaş farkı yaklaşık (ortalama R) ⚠️ |
| Tersane: yeni bedel 0,5 × sermaye, 180 gün yapım, kapasite yılda filonun %40'ı (son 5 yıl ortalaması), kuyruk | C; L (Gluzman 2021 maliyetler 🔎) | D5b3j | Deneysel | Bütün sayılar ⚠️ |
| Yabancı hazır gemi: yeni bedel × 1,25, beklemesiz | C; L (Lane 1934: 16. yy'da dışarıdan alım) | D5b3j | Deneysel; **tarihsel dayanak zayıf** (kolonilerde yapım daha ucuzdu; prim, aciliyet maliyeti vekili) | ⚠️ |
| Gemi yaşlanması: 15 yıl ömür, doğrusal değer kaybı, %10 söküm; satılamayan gemi 1 yılda sökülür; bağlı gemi günde 10 masraf | C | D5b3j | Deneysel | Ömür Gluzman Bölüm 9'da, okunamadı ⚠️ |
| Gemisini kaybeden tüccar: kendi beklentisiyle yeniden alır (en az 0,5 × sermaye kalıyorsa) ya da çıkar | C | D5b3j | Deneysel | |
| Sicil değeri: öz sermaye + gemi yerine koyma değeri (piyasa fiyatı sicile girmez; batma ve yaşlanma girer) | C | D5b3j | Deneysel | |
| Harita veriden (`core/maps/*.json`): limanlar, bölgeler, bacaklar, arz planı, kumaş havuzları; bacak süresi koordinattan (45 deniz mili/gün, × 1,2 dolanım) | **K** tam harita (K-035); **C** tasarım ve bütün sayılar ⚠️ | M0, M1 | Deneysel; veri geçici vekil (İ12) | [map-v1](map-v1.md) |
| Kalkış arzı (`origin_supply`): bulunduğu limanda seçenek, arz eğrisinden (kırsal arz × 5 gün, depocu, havuz, satıcı tüccarlar, eksi yerel tüketim ve diğer alıcılar; ask × 1-2 fiyat düzeyleri, tek fiyat). Uzak limanda yalnızca yapısal arzı (kırsal ya da havuz) olan mal | **K** kalkıştaki gerçek arz önemli, bilgi yayılmalı (K-036); **C** arz eğrisi tasarımı, 5 gün ufku, fiyat düzeyleri ⚠️ | M1.2 | Deneysel; uzak limanda arz bilgisinin yayılımı yok (K-036 adım 4) | [M1](../experiments/M1.md) |
| Filo alarmı (`fleet_alarm`): NPC sayısı aşarsa koşu durur; `max_merchants` yeni haritada kaldırıldı | **K** sınır kaldırılsın (gemi maliyeti doğal sınırlar); **C** alarm | M1.2 | Kalıcı (güvenlik) | classic6'da 300 kalıyor (Python eşitliği) |
| Süreye bağlı bacak tehlikesi (`hazard_days`): bacak başına değerler referans süreye (60/7 gün) ait; bacak tehlikesi 1-(1-h)^(gün/ref), gerçekleşen süreyle ölçeklenir | **K** düzeltmeyi istedi; **C** biçim ve referans süre ⚠️ | M1.4 | Claude ekledi, deneyle desteklendi | [M1](../experiments/M1.md) |
| Balast riski (`ballast_risk`): boş sefer de batabilir ve ele geçirilebilir (Python mirası: yalnız yüklü) | **K** düzeltmeyi istedi; **C** tespit | M1.4 | Claude ekledi, deneyle desteklendi | Tüccarın kararına gemi kaybı girmiyor (not) |
| Korsan ganimeti (`prize_share` 0,8): ele geçirilen gemi satılığa çıkar, bedel ekonomiden çıkar, bağlama masrafı yok | **K** düzeltmeyi istedi; **C** biçim, 0,8 ⚠️ geçici vekil; **L** ganimetin satışı (Fontenay ⚠️) | M1.4 | Claude ekledi, deneyle desteklendi | Mürettebat esareti ve fidye yok |
| Elleçleme (`handling`): liman kademesine göre yükleme/boşaltma hızı (250/150/100 hacim birimi/gün); satış boşaltılmış kısımdan, kalkış yükleme bitince | **K** limanda zaman (timeline 56), yükleme limana ve iş gücüne bağlı; **C** biçim ve değerler ⚠️ (Gluzman Kıbrıs ~20 gün) | M2.1 | Claude ekledi, deneyde | [M2](../experiments/M2.md) |
| Doldurma kararı (`fill_decision`): marginal value theorem ile kalkış; seçenek skoruna yük toplama süresi (arz akışı = avail / origin_horizon) girer | **C**; **L** Charnov 1976 | M2.1 | Claude ekledi, deneyde | Getiri tahmininde (`ret_of`) toplama süresi yok |
| Gemi riski kararda (`ship_risk`): kayıp olasılığı × gemi piyasa değeri seçenek, yer değiştirme ve yön değiştirme değerine girer | **C** (M1.4 notu) | M2.1 | Claude ekledi, deneyde | |
| Bilgi aktarımı (`info_relay`): gemi bildiği bütün fiyatları (pazar, fiyat, gün) taşır; varışta limanın price current'ına daha taze olanlar işlenir; limandaki tüccar price current'ı her gün okur (herkese açık) | **K** gemiler bildiği her şeyi taşısın, limanda public bilgi; **C** biçim | I1 | Deneysel (kullanıcı yönü, Claude tasarımı) | Gürültü yok (I3) |
| Komşu limanlar arası haber (`courier_every` 7): her bacakta her yönde ortalama 7 günde bir, limanın price current'ı bacak süresinde karşıya ulaşır | **K** doğrudan gemi gelmese de bilgi yayılsın; **C** biçim, 7 gün ⚠️ geçici vekil | I1 | Claude ekledi, deneyde | Tarihsel dayanak araştırılacak (mektup, avvisi hızları) |
| Yön değiştirme teşhis kaydı (`rr_log`) | **C** | I0 | Ölçüm | |
| Gemide yük bozulması (`cargo_spoil`): kalan pay exp(−(t/τ)^k), k = 2, τ mala göre (120-1.000 gün); tüccar alım ve satış/yön değiştirme kararında hesaba katar | **K** gemideki yük bozulmalı, tek seferde bozulmasın, ayar kaba; **C** Weibull biçimi ve τ değerleri ⚠️ | CS | Kullanıcı istedi; değerler kaba vekil | Dükkân/depo bozulması hâlâ mal ayrımsız |
| Yön değiştirme eşiği (`reroute_margin`, varsayılan 0,05) | **C** (sınama için ayar) | T2 | Ölçüm | |
| Gemi maliyet paketi (`port_costs`, S-028): uğrak resmi (gemi başına, varışta), elleçleme ücreti (hacim başına, yüklemede ve boşaltmada), gümrük karaya çıkarken (satışta değil; yeniden yüklenen mal vergiyi kaybeder), gemi zamanının günlük maliyeti kararlarda (mürettebat + geçim + gemi sermayesinin faizi + aşınma) | **K** uğrak maliyetleri, elleçleme maliyeti, geminin opportunity cost'u ve işletme maliyeti; **C** biçim; düzeyler [ship-operating-costs-16c](../research/history/ship-operating-costs-16c.md) üzerinden kaba ⚠️ | PC | Kullanıcı istedi; düzeyler tarihsel aralıktan kaba | Gemi başı maliyet varken navlun vekili kısmen çift sayım |
| `ship_cost_day` 40 → 130 (mürettebat + kumanya yılda gemi fiyatının ~%40'ı; tarihsel aralık %30-60) | **C** (Jones 1998 üzerinden kaba hesap ⚠️) | PL, PC | Tarihsel düzeye çekme | |
| Deniz aşınması (`sea_wear`): yük hacmine bağlı navlun vekili yerine gemi başına onarım maliyeti (deniz günü × gemi fiyatı × 0,25/365); kararlarda da var | **K** çift navlun işine bak; **C** biçim, düzey kaba ⚠️ | PF | Gemi başı maliyet varken vekil çift sayım (Jones 1998: maliyet gemi başına) | |
| Karışık yük (`mixed`, K-040): ambar parti listesi; satılmayan kısım ambara konur (kısmi satış); boşalan yere alım; hedef ambarla birlikte seçilir; satmanın yer açma değeri (`fill_val`); parti başına masraf, kurulum süresi, broken stowage; parti başına kâr kaydı, borç gemi boşalınca | **K** birden fazla mal, çeşit maliyeti, kısmi satışın yer açma avantajı hesaplanmalı, parti başına kayıt; **C** biçim, akış, düzeyler (`lot_fee` 150, `lot_setup_days` 0,5, `stowage_loss` 0,03 ⚠️) | MX | Kullanıcı istedi | Satış hâlâ kapan'da (S1), değerli mal tartı hızı yok (S2) |
| Rota taahhüdü (`commit`): ambara konan parti için gemi o limana gitmeyi taahhüt eder; o limandaki alım ve sonraki ambar kararları bu hedefe göre | **C** (MX teşhisi: partilerin %70'i hedefine gitmiyordu) | MX-v3 | Hata düzeltmesi niteliğinde; tarihsel karşılık sefer için yola çıkma ⚠️ | |
| Aynı maldan partilerin birleşmesi | **C** | MX-v4 | Hata düzeltmesi | |
| Tartı hızı (`weigh_rate`, S2): değerli malda elleçleme hızı birim/gün ile de sınırlı (biber 100, kumaş 400, büyük limanda; kademe oranı `handling` ile) | **K** biber örneği (günde 50 birim); **C** biçim, düzeyler kaba ⚠️ | MW | Kullanıcı istedi; MW: tempo biraz düştü, biber dağıtımı kötüleşti | |
| Satış anlaşması (`sale_contract`, S1): satma kararında depocularla, teklifleri tüccarın kabul fiyatını aşıyorsa, kasa ve yer kadar; para anlaşmada (%1 komisyon), mal boşaltıldıkça teslim; anlaşmalı mal pazarda satılmaz, ambara konmaz | **K** varışta belli fiyattan anlaşma, teslim boşaltmayla günlere yayılır; **C** karşı taraf depocu, biçim | MK | Kullanıcı istedi; MK: getiri arttı, dağıtım kötüleşti; Claude biçimi, kesin değil | Depocu yalnızca bir alıcı türü; yerel tüccar/grossiste ayrı ajan değil |
