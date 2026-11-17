# 15 — Büyük Ölçekli Ekonomi ABM'leri (EURACE ve benzerleri) ve Yöntemleri
> Durum: taslak (arama özetlerinden; birincil metinlerin çoğu okunmadı)
> Son güncelleme: 2026-11-06
> İlgili: [03-academic-abm](03-academic-abm.md), [05-non-game-applications](05-non-game-applications.md) (EURACE kısa özeti), [06-validation-and-tuning](06-validation-and-tuning.md) (ODD, stylized facts), [13-literature-map](13-literature-map.md), [14-natural-entry-exit](14-natural-entry-exit.md), [D5b3j](../../experiments/D5b3j.md)

**İstek (kullanıcı, 2026-11-06):** EURACE ve benzeri ekonomi ABM'lerini, örneklerini ve yöntemlerini araştırmak.

**Kaynak işaretleri:** 🔎 = arama özetinde görüldü, birincil metin okunmadı.

## 1. Model aileleri

| Model | Kim | Ne modelliyor | Öne çıkan bulgu | Kaynak |
|---|---|---|---|---|
| **EURACE / Eurace@Unibi** | Deissenberg, van der Hoog, Dawid (2008); Cincotti, Raberto, Teglio (Cenova) | AB ekonomisinin tamamı: haneler, firmalar, bankalar, devlet, merkez bankası. Mekânsal yapı (bölgeler). Emek, mal, kredi ve finans piyasaları birlikte. FLAME çerçevesinde paralel çalışır; kod, model tanımından üretilir. | Kredi parası ile reel faaliyetin etkileşiminden içsel konjonktür dalgaları. Konut kredisi içsel para yaratır ve konut balonunu besler; borç servisi/gelir sınırı (DSTI) dengeler. Sıkı bütçe kuralları (İstikrar Paktı) performansı kötüleştirir. Menkul kıymetleştirme finansal istikrarı zayıflatır. | Deissenberg ve ark. 2008 (*Applied Math. and Computation*) 🔎; Teglio, Raberto, Cincotti; Raberto ve ark. 🔎; Holcombe ve ark. 2013 🔎 |
| **K+S (Keynes meets Schumpeter)** | Dosi, Fagiolo, Roventini (2010, 2013 *JEDC*) | Teknoloji arayan sermaye malı firmaları (Schumpeter) + talep tarafı (Keynes) | Büyüme ve dalgalanma aynı modelden. Bir dizi stylized fact'ı aynı anda üretir: yatırım GSYH'den oynak, tüketim daha az oynak, kalın kuyruklu dağılımlar. Politika deneyleri bu doğrulamadan sonra yapılır. | Dosi & Roventini 2025 (Cambridge Element *Agent-Based Macroeconomics*) 🔎; LEM WP 2008-21 🔎 |
| **CATS / Mark-0** | Delli Gatti, Gallegati, Gaffeo ve ark. (2011); Gualdi ve ark. (2015) | Heterojen firmalar ve kredi; Mark-0 sadeleştirilmiş, dış şok yok | Krizler yalnızca içsel kaynaklı. Mark-0'da parametre uzayında **devrilme noktaları (tipping points)**: küçük parametre değişimiyle rejim değişir (tam istihdam ↔ kriz). | Gualdi ve ark., arXiv 1307.5319 🔎; arXiv 2111.08654 🔎 |
| **CC-MABM** | Assenza ve ark. (2015) | Sermaye ve kredi | — | arXiv 2409.18760 🔎 |
| **IIASA / Avusturya modeli** | Poledna ve ark. (2023) | Ülke verisiyle beslenen, tahmin için kalibre edilmiş ABM | Stylized fact üretmekten öteye geçip **zaman serisi tahmini** yapan az sayıdaki modelden. | arXiv 2409.18760 🔎 |
| **Karşılaştırma çerçevesi** | Dawid & Delli Gatti (2018), *Handbook of Computational Economics* 4 | Makro ABM'lerin yapı ve varsayımlarının sistematik karşılaştırması | Çoğu model stylized fact üretiyor; tahmin yapan az. | Bielefeld kaydı 🔎; arXiv 2409.18760 🔎 |

## 2. Bize yakın alanlar

### 2.1 Gemi piyasası ABM'leri (Ö3 için doğrudan ilgili)

| Çalışma | İçerik | Bulgu | Kaynak |
|---|---|---|---|
| Engelen, Dullaert & Vernimmen (2007) | Yeni gemi ve ikinci el dökme yük piyasası, 1990-2005. İki tür tüccar, iki kural, üç gemi tipi; evrimsel strateji seçimi. | Fiyatları açıklamada strateji seçimi önemli. Kurallarını zamanla değiştiren tüccar kazanıyor. | *Transportation Planning and Technology* 30(4) 🔎 |
| Alizadeh, Thanopoulou & Yip (2017) | Heterogeneous agent model (HAM): spekülatörler (momentum, contrarian) + işletmeciler. İkinci el dökme yük fiyatları. | Momentum yatırımcısı fiyat oynaklığını artırıyor, contrarian azaltıyor. | City Univ. açık erişim 🔎 |
| Beenstock & Vergottis; Tinbergen-Koopmans | Klasik shipping cycle kuramı | Yük talebi sabitken bile teslim gecikmesi salınım üretir. Beklentiler, fiziksel piyasa değişmeden fiyatı oynatır. | handybulk özeti 🔎 |

### 2.2 Tarihsel ve arkeolojik ticaret ABM'leri

[03 §tablo](03-academic-abm.md)'deki Romanowska'ya ek olarak:
- Graham & Weingart: Roma çıkarım ekonomisi (NetLogo). Gözlenen ağın hangi süreçten çıktığını **equifinality** ile sınar: farklı süreçler aynı ağı üretebilir mi? 🔎
- Crabtree: Güney Fransa'da Tunç → Demir Çağı şarap ticareti (tüccar ve Galyalılar) 🔎
- Chliaoutakis & Chalkiadakis: Minos Girit'inde yerleşimler arası ticaret (JASSS); AncientS-ABM 🔎

## 3. Yöntemler

### 3.1 Doğrulama (validation)
- **Stylized facts:** Ortak pratik. Ama Sant'Anna grubunun kendi eleştirisi şu: doğrulama çoğu zaman yüzeysel; kalibrasyon elle ya da geçici yollarla, seçilmiş stylized fact'ları üretmeye yönelik (Fagiolo, Guerini, Lamperti, Moneta & Roventini 2017, "Validation of ABMs in Economics and Finance" 🔎).
- Bizim yöntemimiz (Ö0, pattern-oriented modeling; [D5b3h](../../experiments/D5b3h.md)) bu eleştiriye cevap veren tarafta. Birden çok bağımsız örüntü + seed'ler arası güven aralığı kullanıyoruz.

### 3.2 Kalibrasyon ve tahmin

| Yöntem | Nedir | Kaynak |
|---|---|---|
| **Simulated Minimum Distance (SMD)** | Modelden ve veriden hesaplanan momentlerin farkını en aza indirir. Ergodik modellerde tutarlı (uzun dönem dengede ve uyum sürecinde). | Grazzini & Richiardi 2015, *JEDC* 🔎 |
| **Bayesçi tahmin** | Kernel ile olabilirlik tahmini + MCMC; parametrik olabilirlik yaklaşımları; Approximate Bayesian Computation (ABC). SMD'yi Bayesçi çerçeveye yerleştirebilir. De Grauwe'nin 9 parametreli modelinde denendi. | Grazzini, Richiardi & Tsionas 2017, *JEDC* 77 🔎 |
| **ML surrogate** | Sobol dizisiyle parametre örneklenir, her nokta ABM'de koşulup bir uyum ölçütüyle etiketlenir. Öğrenen bir model (surrogate) etiketi tahmin eder; en umut verici noktalar yeniden ABM'de koşulur (aktif öğrenme). Brock-Hommes ve "Islands" modellerinde hesap süresini büyük ölçüde azalttı. | Lamperti, Roventini & Sani 2018, *JEDC* (arXiv 1703.10639) 🔎 |
| **Karşılaştırma** | Ekonomi ABM'lerinde kalibrasyon yöntemlerinin karşılaştırması | Platt 2020 (arXiv 1902.05938) 🔎 |
| **Parametre uzayı keşfi** | Devrilme noktalarını ve rejimleri haritalamak (Mark-0) | arXiv 2111.08654 🔎 |

### 3.3 Belgeleme
- **ODD 2020 güncellemesi** (Grimm ve 19 yazar, JASSS 23(2)): "Purpose and patterns" ilk öğe. Yani model, amaca ve doğrulama örüntülerine göre tanımlanır. Tasarım gerekçesi ve amaca uygunluk bölümleri eklendi ([06 §2](06-validation-and-tuning.md)). 🔎

## 4. Bizim için değerlendirme (Claude)

1. **Ölçek ve yapı:** EURACE ve K+S makro modeller: ülke ekonomisi, para, devlet. Biz bir sektör modeliyiz (deniz ticareti), ama mekanizmalar ortak:
   - Kredi ile gelen içsel döngü (EURACE) ↔ bizim borç ve colleganza
   - Teslim gecikmesiyle gelen döngü (shipping cycle kuramı) ↔ Ö3'teki tersane kuyruğu
   - Beklentilerden gelen fiyat oynaklığı (HAM) ↔ bizim kamu sicili ve gemi fiyatı
   Bunlar çıktığında "literatürde bilinen" diye yazılacak (kural 7b).
2. **Gemi fiyatı (Ö3):** Alizadeh ve ark. HAM'ı, yatırımcı heterojenliğinin (momentum ↔ contrarian) gemi fiyatı oynaklığını belirlediğini gösteriyor. Bizde yatırımcılar şimdilik yalnızca risk primiyle farklı; hepsi aynı kamu sicilini okuyor. Ö4'te (bilgi temelli sicil) beklenti kuralı heterojenliği eklenirse doğal bir sonraki adım.
3. **Kalibrasyon sırası (proje yöntemiyle uyumlu, [experiment-approach]):**
   - Şimdi: yapı ve örüntü (pattern-oriented modeling).
   - Sonda: ML surrogate + Sobol örnekleme (Lamperti ve ark.). Bizim koşularımız pahalı (tam harita 10 yıl ~30 dk), surrogate tam bu durum için.
   - Tarihsel veri az ve dağınık (prim, kayıp, sefer sıklığı). Bu yüzden tam olabilirlik yerine **SMD ya da ABC**: birkaç tarihsel moment (prim dağılımı, yıllık kayıp oranı, yılda sefer) ile.
4. **Ergodiklik uyarısı:** SMD tutarlılığı ergodik model ister. Bizim F'deki çöküş döngüsü (D5b3i) ve snapshot'a bağlılık, modelin bazı ayarlarda ergodik olmayabileceğini gösteriyor. Kalibrasyondan önce bu test edilmeli (farklı başlangıçlardan aynı dağılıma mı yakınsıyor?).
5. **Devrilme noktaları:** Mark-0'da bulunan parametre rejimleri, bizim "bant κ" ve "k" ablasyonlarında gördüğümüz keskin geçişlere (ör. -k36) benziyor. Parametre uzayı haritası, son ayardan önce oyunun hangi bölgede durduğunu gösterir.
6. **Belgeleme:** ODD önerisi (06) hâlâ bekliyor. mechanism-registry kökeni tutuyor ama ODD'nin "purpose and patterns" ve "design rationale" bölümleri eksik. Simülasyon spesifikasyonu yazılırken ODD 2020'ye göre yazılmalı.
7. **Equifinality** (Graham & Weingart): Aynı örüntüyü farklı süreçler üretebilir. Kural 7d ve "Claude ekledi" etiketleri bu riskin bilincinde olmak için var. Önemli bir örüntü için en az iki rakip mekanizma denenmeli (yuva bazlı turnuva yöntemimizle aynı).

## Oyun için çıkarımlar

1. Makro ABM'lerin gösterdiği içsel döngüler (kredi, konut, teslim gecikmesi) oyuncu için okunabilir "piyasa hikâyeleri"dir. Oyunda tepeden olay olarak değil, mekanizmadan doğmalılar.
2. Gemi fiyatı oynaklığı yatırımcı tiplerine bağlı (momentum ↔ contrarian). Oyunda tüccar kişilikleri ve "dipte alan" contrarian yatırımcılar, piyasayı oyuncunun sezebileceği biçimde sönümler ya da büyütür.
3. Son kalibrasyon makine öğrenmesiyle yapılabilir; ama hedefler tarihsel örüntüler olmalı ki oyun hem tarihsel hem dengeli kalsın.
4. Devrilme noktaları oyun tasarımı için hem risk hem fırsat: Zorluk ayarı ya da savaş/korsan olayları, sistemi istenmeyen bir rejime itebilir. Bunun haritası çıkarılmalı.

## Kaynaklar
- Deissenberg, van der Hoog, Dawid (2008). EURACE: A massively parallel ABM of the European economy. https://halshs.archives-ouvertes.fr/halshs-00339756 ; https://catalog.comses.net/publications/1653
- van der Hoog, Deissenberg, Dawid (2008). Production and Finance in EURACE. https://core.ac.uk/download/47889202.pdf
- Holcombe ve ark. (2013), FLAME ve EURACE. https://tuprints.ulb.tu-darmstadt.de/27388/1/holcombe%20complex%20systems%202013.pdf
- Eurace bankacılık ve kredi düzenlemesi, *J. Evol. Econ.* 29 (2019). https://ideas.repec.org/a/spr/joevec/v29y2019i1d10.1007_s00191-018-0568-2.html
- Eurace mali politika ("Budgetary rigour with stimulus in lean times"). https://core.ac.uk/download/154911402.pdf
- Eurace konut ve ipotek. https://core.ac.uk/download/459189144.pdf ; https://www.siecon.org/sites/default/files/media_wysiwyg/raberto.pdf
- Dosi, Fagiolo, Roventini (2010), K+S. https://www.lem.sssup.it/WPLem/files/2008-21.pdf
- Fagiolo, Guerini, Lamperti, Moneta, Roventini (2017), Validation of ABMs. https://www.lem.sssup.it/WPLem/files/2017-23.pdf
- Dosi & Roventini (2025), *Agent-Based Macroeconomics*. https://core-cms.cambridgecore.org/core/services/aop-cambridge-core/content/view/B7016A5CEE59694A420AF51A1347F00E/9781009598743AR.pdf/agentbased_macroeconomics.pdf
- Lamperti, Roventini, Sani (2018), ML surrogate. https://ar5iv.arxiv.org/html/1703.10639
- Platt (2020), calibration methods comparison. https://arxiv.org/pdf/1902.05938
- Grazzini & Richiardi (2015), SMD. https://catalog.comses.net/publications/4852
- Grazzini, Richiardi, Tsionas (2017), Bayesian estimation of ABMs. https://eprints.lancs.ac.uk/id/eprint/84557
- Gualdi ve ark. (2015), Tipping points (Mark-0). https://arxiv.org/pdf/1307.5319
- Mark-0 parametre uzayı. https://arxiv.org/pdf/2111.08654
- Makro ABM tahmin karşılaştırması (Poledna/IIASA dahil). https://arxiv.org/pdf/2409.18760
- Dawid & Delli Gatti (2018), Handbook bölümü. https://pub.uni-bielefeld.de/record/2917066
- Engelen, Dullaert, Vernimmen (2007), dry bulk ABM. https://ideas.repec.org/a/taf/transp/v30y2007i4p377-389.html
- Alizadeh, Thanopoulou, Yip (2017), ship price HAM. https://openaccess.city.ac.uk/id/eprint/18475/
- Shipping cycle kuramı özeti. https://www.handybulk.com/theory-of-shipping-cycles-fleet-supply-delivery-lags-market-expectations-ship-prices-and-business-cycles/
- Graham & Weingart; Crabtree; Chliaoutakis & Chalkiadakis (arkeolojik ticaret ABM'leri). https://core.ac.uk/download/147823014.pdf ; https://mdpi.com/2073-445X/5/1/5 ; https://escience.sdu.dk/index.php/2023/09/19/utilizing-agent-based-models-in-archaeological-data-%E2%80%AF/
- Grimm ve ark. (2020), ODD second update. https://www.jasss.org/23/2/7.html
