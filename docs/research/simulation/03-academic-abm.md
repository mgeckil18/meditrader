# 03 — Akademik Ajan Tabanlı Ekonomi Modelleri
> Durum: taslak (derin araştırma, 2. tur)
> Son güncelleme: 2026-10-22
> İlgili: [01-temel kurallar](01-economic-fundamentals.md), [02-piyasa mekanizmaları](02-market-mechanisms.md), [05-oyun dışı uygulamalar](05-non-game-applications.md)

Ajan tabanlı hesaplamalı ekonomi (ACE) literatüründen, bizim simülasyona doğrudan fikir veren çalışmalar.

---

## 1. Alanın tanımı: ACE

Leigh Tesfatsion (Iowa State) ACE'yi şöyle tanımlar: ekonomik süreçlerin, etkileşen ajanlardan oluşan dinamik sistemler olarak hesaplamalı incelenmesi. Modelci başlangıç koşullarını kurar, ekonomi ajanlar etkileştikçe ve öğrendikçe kendiliğinden evrilir. Tesfatsion bunu "kültür kabı" (culture-dish) yaklaşımı olarak adlandırır. "Ajan" geniş bir kavramdır: bilişsel yetenekli karar vericilerden pasif dünya özelliklerine kadar her şey olabilir. ([Tesfatsion, Handbook of Computational Economics Vol. 2](https://shop.elsevier.com/books/handbook-of-computational-economics/tesfatsion/978-0-444-51253-6), [Iowa State](https://lib.dr.iastate.edu/econ_las_workingpapers/252))

**Farmer & Foley (Nature, 2009), "The economy needs agent-based modelling":** Ekonometrik modeller işler aynı kaldıkça birkaç çeyrek ilerisini iyi tahmin eder ama büyük değişikliklerde çöker. DSGE modelleri mükemmel bir dünya varsayar ve krizleri doğası gereği dışlar. Ajan tabanlı modeller ise kurallarla etkileşen karar vericileri ve kurumları simüle eder. ([Nature](https://link.springer.com/article/10.1038/460685a), [Zenodo](https://zenodo.org/records/897777))
→ **Bizim için:** Oyunumuz tam olarak "büyük değişiklikler"le ilgili: savaşlar, kıtlıklar, iflaslar. Ajan tabanlı yaklaşım bu yüzden doğru seçim.

## 2. Santa Fe Yapay Borsası (Arthur, Holland, LeBaron, Palmer, Tayler; 1990'lar)

- **Yapı:** Sabit hisse arzı, program tüccarlar, arz ve talebe göre fiyat belirleyen bir "uzman" (specialist), değişken faizli tahvil alternatifi ve rastgele temettü akışı. ([LeBaron 2002](https://trevcan.duckdns.org/files/trevor/papers/emintham-Papers/LeBaron-%20Building%20the%20Santa%20Fe%20Artificial%20Stock%20Market.pdf), [Telepolis](https://telepolis.de/features/The-Simply-Complex-3445813.html?seite=2))
- **Ajanlar:** Her ajan bir dizi tahmin kuralı taşır ("eğer fiyat 5 günlük ortalamanın üstündeyse ve... o zaman tahminim..."). Kurallar genetik algoritmayla evrilir.
- **Bulgu (literatürden genel bilgi ⚠️ ayrıntı doğrulanacak):** Ajanlar yavaş öğrendiğinde piyasa rasyonel dengeye yakınsar. Hızlı öğrendiğinde teknik analiz kuralları ortaya çıkar, balonlar ve çöküşler, oynaklık kümelenmesi gibi gerçek piyasa özellikleri görülür. Ehrentreich'in düzeltilmiş versiyonu bazı sonuçları sorguluyor. ([Ehrentreich](https://ideas.repec.org/p/wpa/wuwpco/0209001.html), [JEBO 2006](https://ideas.repec.org/a/eee/jeborg/v61y2006i4p599-616.html))

**Bizim için:**
- **"Öğrenme hızı" oynaklığın ana ayar düğmesi.** Bu, Brock-Hommes'un β'sıyla aynı ders.
- **Tahvil alternatifi:** Santa Fe'de ajanlar hisse ile risksiz tahvil arasında seçim yapıyor. Bu bizim S-005 (senetler) sorusunun ta kendisi. Senet getirisi ticaretin "fırsat maliyeti"ni belirler: senet getirisi yükselirse ticaret azalır.

## 3. Brock & Hommes: uyarlamalı inanç sistemleri

Ayrıntı: [01 §7](01-economic-fundamentals.md). Özet:
- Sonlu sayıda tahmin stratejisi var (temelci, trend takipçisi...). Ajanlar her stratejinin geçmiş kârlılığına göre lojit kuralıyla strateji seçer.
- Seçim yoğunluğu (β) yükseldikçe sistem kararlıdan kaosa geçer.
- Temelci stratejinin bir **maliyeti** var (bilgi toplamak pahalı). Bu yüzden trend takipçiliği hayatta kalabiliyor.

**Bizim için en değerli fikir: bilginin bir maliyeti olması.** 16. yüzyılda temelci olmak, yani malın gerçek arz-talep durumunu bilmek, **temsilci ağı ve mektup ağı** demekti. Bunlar pahalıydı. Zengin tüccar temelci olmayı karşılayabilir, küçük tüccar ise söylentiyle (trend) hareket eder. Bu, oyuncunun büyümesinin "daha iyi bilgiye erişim" olarak hissedilmesini sağlar.

## 4. Kirman & Vriend: Marsilya balık pazarı

([Kirman & Vriend 2001, JEDC](https://nvriend.econ.qmul.ac.uk/abs/abs.jedc2.html), [Cornell PDF](https://lblume.economics.cornell.edu/econ6100/KirmanVriend.pdf), [Weisbuch vd. 2000](https://ideas.repec.org/a/ecj/econjl/v110y2000i463p411-36.html))

**Gerçek dünya gözlemi:** Marsilya toptan balık pazarında aynı alıcı ve satıcılar her gün aynı yerde buluşuyor. Buna rağmen:
- **Kalıcı fiyat dağınıklığı** var: aynı balık farklı fiyatlara satılıyor.
- **Yüksek sadakat** var: alıcıların çoğu hep aynı satıcıdan alıyor.

**Model:**
- Satıcılar miktar, fiyat ve sadık müşteriye nasıl davranacaklarını seçer.
- Alıcılar hangi satıcıya gideceklerini ve hangi fiyatları kabul edeceklerini seçer.
- Öğrenme **pekiştirmeli** (reinforcement): iyi sonuç veren davranışın seçilme olasılığı artar.

**Bulgular:**
- Sadakat **birlikte evrimle** ortaya çıkar: alıcılar sadık olmayı öğrenir, satıcılar sadık müşteriye daha yüksek fayda sunmayı öğrenir, çünkü sadık müşteriler daha fazla gelir getirir.
- Weisbuch vd.: Alıcılar kendi deneyimlerinden öğrenirse keskin bir ayrışma olur. Bir kısmı belirli satıcılara sadık kalmayı öğrenir, bir kısmı sürekli "pazar gezer".
- 100 tekrarlı replikasyon (Kopányi & Possajennikov): niteliksel bulgular sağlam. Sabah fiyatları yakınsıyor, dağınıklık ve sadakat ortaya çıkıyor. ([UCLouvain](https://uclouvain.be/en/node/52321))
- Ağ analizi (Vignes & Etienne): Rakipleriyle en çok müşteriyi paylaşan, yani en merkezi satıcılar en yüksek fiyatı alıyor. ([HAL](https://hal.inrae.fr/hal-05494188v1))

**Bizim için:** Bu model, bölgesel itibarın (K-003) ve dealer ilişkilerinin (02 §5) **akademik temeli.**
- Oyuncu bir limanda bir dealer'a sadık kaldıkça daha iyi fiyat ve öncelik alır.
- "Pazar gezen" bir oyuncu her seferinde en iyi anlık fiyatı arar ama ilişki kuramaz.
- Bu iki strateji arasındaki gerilim **oyuncu için anlamlı bir seçim.**

## 5. Doran & Parberry ve BazaarBot

İlk turda ayrıntılı incelendi: [economy-simulation-techniques.md §2](economy-simulation-techniques.md). Özetle:
- Meslek (üretim kuralları), fiyat inancı aralığı, çağrılı çift açık artırma.
- İflas eden ajan en kârlı mesleğe dönüşür.
- 5 yıllık günlük simülasyonda kararlı.
- **Kapalı olmayan ekonomiler iyi sonuç vermez.**

## 6. Sugarscape (Epstein & Axtell, 1996)

*Growing Artificial Societies* kitabındaki model. ([Mesa örneği](https://mesa.readthedocs.io/latest/examples/advanced/sugarscape_g1mt.html), [Intro to ABM](https://pressbooks.pub/intro2abm/?p=81))
- Izgara üzerinde iki kaynak (şeker, baharat) ve hareket eden, metabolizması olan ajanlar.
- Karşılaşan ajanlar marjinal ikame oranları farklıysa takas eder (bkz. 02 §4).
- Sonsuz ömürlü ajanlarla fiyat dengelenir. **Ölümlü ve tercihleri evrilen** ajanlarla fiyat hiç dengelenmez.
- Kültür, hastalık, savaş ve miras gibi kuralların eklenmesiyle zengin toplumsal davranış ortaya çıkar.

**Bizim için:**
- **Ölümlü ajanlar + nesil değişimi (S-002) piyasayı canlı tutar.** Dengeye hiç ulaşmamak bizim için bir özellik.
- Sugarscape'teki **miras** kuralı servetin nesiller boyunca yoğunlaşmasını gösterir. Bu, hane sistemi (S-002) için ilginç.
- **Servet eşitsizliği** de doğal olarak ortaya çıkar. Bunu izlemek gerekir (bkz. 06).

## 7. Gintis: merkezsiz fiyat sistemi

Ayrıntı: [02 §4](02-market-mechanisms.md). Ders: **Taklit** (başarılı komşuyu kopyalamak) basit ama etkili bir öğrenme mekanizması. Fiyatlar merkezi bir açık artırmacı olmadan da yakınsar.
→ **Bizim için:** NPC'ler başarılı tüccarların rotalarını ve mallarını taklit edebilir. Oyuncu başarılı bir rota bulursa, haber yayıldıkça rakipler de gelir ve fırsat kapanır. Bu "rakiplerin seni takip etmesi" deneyimi oyuncu için çok güçlü bir his olur. Bu da K-004'ün doğal sonucu.

## 8. Tedarik zinciri yarışması (TAC-SCM) ve tüccar ajanlar

Doran & Parberry'nin taradığı literatür ([econ.pdf](https://ianparberry.com/pubs/econ.pdf)):
- **TAC-SCM** (2003'ten beri her yıl): Ajanlar mal alıp satıyor ve ürün üretiyor; fiyat değişimlerini tahmin edip kârlı çalışmaya çalışıyor.
- **Botticelli** ajanı siparişleri doldurma olasılığını tahmin edip, beklenen işlem hacmi kapasitesine eşit olana kadar teklif fiyatlarını ayarlıyor.
- **Ketter:** Piyasa rejimlerini (aşırı arz gibi) işlem sonuçlarından çıkarıyor (Gauss karışım modelleri).
- **Roth & Erev:** Pekiştirmeli öğrenme ile fiyat öğrenimi. Doran & Parberry durum uzayının çok büyük olacağı endişesiyle bunu kullanmamış.

**Bizim için:** Akıllı NPC'ler için literatür zengin, ama **NPC'leri fazla akıllı yapmak oyuncuyu ezer** (Bannerlord). Hedef "en iyi tüccar" değil, **"inandırıcı ve çeşitli tüccarlar"**. Basit kurallar artı kişilik parametreleri büyük ihtimalle yeterli.

## 9. Bilgi yayılımı modelleri

**Daley-Kendall söylenti modeli (1964-65):** Nüfus üçe ayrılır: **bilmeyenler** (ignorant), **yayanlar** (spreader), **susturanlar** (stifler).
- Yayan + bilmeyen karşılaşırsa → bilmeyen yayan olur.
- Yayan + yayan veya yayan + susturan karşılaşırsa → yayan(lar) susturan olur ("herkes zaten biliyor").
- **Sonuç:** Başlangıçta yayanların oranı neredeyse %100 olsa bile, bilmeyenlerin bir kısmı söylentiyi **asla duymaz.**
([arXiv 1607.05771](https://arxiv.org/pdf/1607.05771), [ASU MTBI](https://mcmsc.asu.edu/sites/default/files/2024-09/MTBI%202003%20Spread%20of%20Rumors%20Report.pdf))

Varyantlar: heterojen temas hızları, duyduğu anda susturan olma olasılığı (Maki-Thompson).

**Bizim için: bu, haber sisteminin çekirdeği olabilir.**
- Haberler fiziksel olarak **gemilerle, kervanlarla ve kuryelerle** taşınır. Gemi limana varınca haberler limana "yayılır".
- Limanda haber, tüccarlar arasında Daley-Kendall benzeri bir süreçle yayılır: bazı tüccarlar hemen duyar, bazıları geç, bazıları hiç.
- **Haberin değeri zamanla azalır.** Herkes bildiğinde ticari değeri sıfırdır. Bu "susturan" dinamiğinin ticari karşılığı.
- **Gizli tutmak bir strateji:** Oyuncu bir haberi ilk duyan olursa onu satabilir, kullanabilir ya da saklayabilir. Sardella'nın Venedik'teki "haber ve spekülasyon" çalışması tam olarak bunu belgeliyor.
- **Yanlış haber ve söylentiler** de taşınabilir. Kaynak güvenilirliği (bkz. 02 §7) burada devreye girer.

**MERCURY modeli** (aşağıda §10) ticari bilginin bir tüccar ağında aktarıldığını modelliyor. Bu, mekânsal bir bilgi ağının arkeolojik verilerle test edilmiş bir örneği.

## 10. Tarihsel ekonomi ajan modelleri

| Model | Konu | Bulgu ve ders |
|---|---|---|
| **MERCURY** (Brughmans & Poblome 2016, JASSS) | Roma Doğu Akdeniz'inde sofra seramiği ticareti (MÖ 200 - MS 300) | Tüccarlar ağ bağlantılarından edindikleri arz-talep bilgisiyle fiyat tahmin ediyor. Alıcı ya yerel tüketiciye satıyor ya da daha kârlı olacağını düşünürse bir sonraki tura saklıyor. **Bulgu:** Düşük piyasa entegrasyonu, gözlenen geniş ve dengeli dağılımları olası kılmıyor. Kod NetLogo'da açık. ([JASSS](https://www.jasss.org/19/1/3.html), [CoMSES](https://comses.net/codebases/4347)) |
| **Hansa ticaret ağı** (Ewert & Sunder 2011, 2018) | Hansa ağ ticaretinin oluşumu ve çözülmesi | Ciddi veri kısıtlarına rağmen basit bir ajan modeli kurmuşlar ve ajan modellerinin tarih araştırmasındaki potansiyelini ve sınırlarını tartışmışlar. NetLogo. ([CoMSES](https://catalog.comses.net/publications/234066), [SSOAR](https://www.ssoar.info/ssoar/handle/document/56433)) |
| **Doğu Hindistan Şirketi vs. Yeni Culfa Ermeni tüccarları** (Sedigh 2020, Otago doktora tezi) | 17-18. yüzyıllar; kurumlar ve asil-vekil problemi | Şirket hiyerarşisi ile aile ve ağ temelli ticaretin karşılaştırması. ([Otago](https://ourarchive.otago.ac.nz/handle/10523/10223)) |
| **Romanowska** | Roma ekonomisi, uzun mesafe ticaret, tüccar alım stratejileri | ([SDU eScience](https://escience.sdu.dk/index.php/2023/09/19/utilizing-agent-based-models-in-archaeological-data-%E2%80%AF/)) |

**Bizim için:**
- **MERCURY bize en yakın model:** Akdeniz, tüccarlar, bilgi ağı, saklama kararı. Kodu açık ve incelenebilir. **2. tur görevi olarak kodu okumayı öneriyorum.**
- **Ermeni tüccarlar (Yeni Culfa):** Aile ağıyla çalışan tüccarlar ile şirket karşılaştırması bizim **hane mi, şirket mi** (S-002) sorumuzun tarihsel karşılığı.
- **Asil-vekil (principal-agent) problemi** temsilci sistemimizin (K-008) kuramsal adı. Greif'in Mağribi tüccarlarıyla birlikte okunmalı.
- Tarihçilerin ajan modelleri **soru sormak** için kullanılıyor ("şu kurum olmasaydı ne olurdu?"), tahmin için değil. Bizim de tarihsel doğruluk iddiamız bu düzeyde olmalı: **makul mekanizmalar**, birebir rakamlar değil.

## 11. Ekonofizik ve stilize gerçekler

- **Cont (2001):** Varlık getirilerinin 11 "stilize gerçeği" var: kalın kuyruklar (aşırı basıklık), oynaklık kümelenmesi, getirilerde otokorelasyon olmaması vb. ([Cont](https://ideas.repec.org/a/taf/quantf/v1y2001i2p223-236.html), [arXiv 2023 yeniden inceleme](https://arxiv.org/pdf/2311.07738)) 2024'teki bir çalışma Dow 30 verisinde bunlardan 8'ini doğruladı.
- Ajan tabanlı modellerin "gerçekçi" sayılması için genelde bu gerçekleri yeniden üretmesi beklenir. ([Econophysics review](https://arxiv.org/pdf/0909.1974))

**Bizim için:** Finansal stilize gerçekler doğrudan geçerli değil, çünkü bizim mallarımız hisse değil, emtia. Ama emtia fiyatlarının kendi stilize gerçekleri var: **uzun sakin dönemler ve ani sıçramalar** (Deaton-Laroque), **mevsimsellik**, **kıtlıkta dışbükey fiyat artışı** (King-Davenant). Bunlar doğrulama hedefimiz olur (bkz. [06](06-validation-and-tuning.md)).
