# Açık Sorular
> Durum: canlı doküman
> Son güncelleme: 2026-10-22
> İlgili: [decisions](decisions.md)

Format: **S-xxx — Soru** · bağlam · seçenekler · durum.

---

**S-001 — Başlangıç yılı ve seçilebilirlik**
Öneri: 1560 civarı, Kıbrıs Savaşı (1570) ve İnebahtı (1571) öncesi. Tek bir sabit tarih mi olacak, birkaç başlangıç tarihi mi? Bağlam: tarihsel veri hazırlama yükü tarih sayısıyla katlanır.
Durum: **çalışma varsayımı 1560 (2026-10-22).** Kullanıcı tarih okumalarından sonra birlikte kesinleştirilecek.

**S-002 — Oyuncunun ölümü ve devamlılık**
Seçenekler: (a) ölüm = oyun sonu, (b) hane/varis ile devam, (c) tüzel kişilik (şirket/ortaklık) ile devam, (d) b+c. Kullanıcı b/c'den hoşlandı. Mimariyi etkiler: "oyuncu = bir kişi" mi, "oyuncu = bir hane/firma" mı?
Durum: açık, eğilim b+c.

**S-003 — Oyuncunun tarih bilgisi istismarı**
Oyuncu Kıbrıs'ın 1570'te düşeceğini veya İspanya'nın 1575'te iflas edeceğini bilirse bu en değerli ticari bilgi olur. Öneri: büyük olaylar sabit ama etki büyüklüğü ve süresi değişken; küçük olaylar olasılıksal ve bulanık zamanlı; bilgi gecikmesi etkiyi doğal olarak törpüler.
Durum: açık.

**S-004 — Simülasyon tick çözünürlüğü**
Günlük tick mi? Bazı sistemler (üretim, hasat) haftalık/aylık, bazıları (seyir, haber) günlük çalışabilir.
Durum: açık, araştırma bekliyor.

**S-005 — Borç senetlerinin istismarı**
"Risksiz senet" ölü zamanı risksiz faizle doldurmayı optimal strateji yapar. Öneri: düşük ama sıfır olmayan risk (İspanyol iflasları 1557/1560/1575/1596), ticaretten belirgin düşük getiri, likidite kısıtı. Kullanıcı bu konuya ayrıca değinecek.
Araştırma bulgusu: Venedik Monte senetleri ikincil piyasada işlem görüyordu ve 1509-1529 krizinde nominal değerin %3-10'una kadar düştü. Tarihsel çözüm: senetler **piyasada fiyatlanan** varlıklar olur, savaş ve krizlerle değer kaybeder. Bkz. [history overview §6](research/history/mediterranean-16c-overview.md).
Durum: **yön belirlendi (2026-10-22).** Kullanıcı: senetler risksiz faize yakın ama yine de riskli, pek tercih edilmeyen bir alternatif olarak sunulur. Asıl doğal sınır **oyuncunun ömrü**: parayı senede bağlayıp bekleyen oyuncunun hayatı biter. Zaman, oyuncunun en kıt kaynağı. Bkz. [framework](design/framework.md) Y10.
Kalan not: Hane/varis sistemi (S-002) gelirse, senet nesiller boyunca birikebilir. O zaman istismar yeniden değerlendirilmeli.

**S-006 — İlk simülasyon dilimi**
Öneri: Venedik–Ragusa–Korfu–İstanbul–Sakız–İskenderiye, 8-10 mal, ~10 yıl. Simülasyonun ilk testleri için.
Durum: açık.

**S-007 — Köle ticareti nasıl ele alınacak?**
Tarihsel gerçeklik: korsan akınları, esir ticareti ve fidye ekonomisi. Seçenekler: (a) oyuncunun alıp satamadığı ama dünyada var olan bir arka plan gerçekliği; fidye ve esir kurtarma ise oyuncu mekaniği, (b) tamamen dışarıda bırakmak, (c) oyuncu mekaniği. Öneri: (a). Atmosferi ve riski korur, oyuncuyu bu ticarete sokmaz.
Durum: açık.

**S-008 — Para birimleri ne kadar ayrıntılı?**
Duka (hesap), zecchino (altın), lira/soldi, akçe, real, Ceneviz scudo... Kurlar ve gümüş değer kaybı zengin bir katman ama anlaşılırlığı zorlar. Öneri: simülasyonda tek bir iç birim (ör. soldo, tamsayı), arayüzde yerel birimler; kur mekaniği geç oyun finansçılığına ayrılır.
Durum: açık.

**S-010 — Simülasyon prototipi için teknoloji**
Öneri: Araştırma ve deney aşamasında Python (hızlı deneme, kolay analiz ve grafik). Nihai oyun motoru kararı simülasyon oturduktan sonra ayrıca verilir; Python prototipi o motor için bir "özellik belgesi" olur. Bkz. [05 §6](research/simulation/05-non-game-applications.md).
Durum: **deneyler için Python kabul edildi (2026-10-22).** Nihai motor sorusu açık.

**S-011 — Ekonomi mimarisi önerisinin kabulü**
[00-sentez](research/simulation/00-synthesis.md) şunları öneriyor: kitle havuzları + dealer modeli + bilgi yaşına dayalı inançlar + günlük tick ve olay kuyruğu. Hangileri karara dönüşecek?
Durum: kısmen cevaplandı (yorumlar.md). Çoğu "yön" seviyesinde kabul edildi; dealer modeli "maliyet artı marj dükkâncısı" olarak revize edildi. Bkz. [framework](design/framework.md).

**S-012 — Hedef fırsat rejimi (oyun tasarımı kararı)**
Yetenekli bir oyuncu yılda ne kadar kazanabilmeli? Fırsatlar günlerin ne kadarında açık olmalı? NPC tüccarlar ne kazanmalı? D2 bunun simülasyonun kural seçimiyle doğrudan belirlendiğini gösterdi. Kaba öneri: fırsat açık günler %10-30, yetenekli oyuncu %15-30/yıl, NPC medyanı %5-15/yıl, senet %3-5/yıl. Bu aynı zamanda sonraki ML kalibrasyonunun hedef fonksiyonunun bir parçası.
Durum: **yön belirlendi (2026-10-23), sayısal ayar ertelendi.** Kullanıcının çerçevesi:
- Devlet senedi ≈ %4/yıl (risksize yakın getiri).
- "Baz ticaret" = senet + o ticaretin riski. Rekabetçi dengede **ekstra kâr yok**.
- Bazı ticaretler bazın üstünde, bazıları altında. Doğru ticareti seçen kazanır, ama rakipsiz kalmak mümkün olmaz; rekabet marjları eritir.
- Oyuncu yılda %50 gibi getiriler elde edememeli. Sistem büyüdükçe (daha çok tüccar, şehir, mekanizma) dengelenme hızlanacağı için bu kendiliğinden törpülenecek.

Claude'un üç notu: (1) Marjların tamamen erimesi Bannerlord sorunudur (D2). Yetenekli oyuncunun kalıcı avantajı kıt girdilerden gelmeli: bilgi ağı, ilişkiler, sermaye, risk toleransı. (2) Bazı fırsatlar dengelemez, kendini besler (sermaye ve itibar birikimi, sürü davranışı, köşeleme). Yüksek getiri tek tek ticaretlerden değil, geç oyunda biriken avantajlardan gelir; ölçek büyüdükçe dengeleyici mekanizmalar gerekir. (3) Getiri riskle birlikte ölçülmeli (dağılım, iflas olasılığı), ortalama tek başına yanıltıcı.
Yapısal öneri: **senet getirisine bağlı serbest giriş-çıkış.** Ticaret senet + risk priminin üstünde kazandırıyorsa yeni tüccar girer, altındaysa tüccarlar çıkar (parasını senede koyar). Kullanıcının "baz ticaret" dengesini üreten mekanizma bu; ayrı bir deneyde test edilecek.

*Not (2026-10-23, [D5b](experiments/D5b.md) B6):* Rakip bilgisi olan dünyada medyan tüccar yılda %30-35 kazanıyor; giriş akışı ayda ~0,7 tüccar (başlangıç filosunun %5'i). Yavaş giriş = rant (D3b). Kalibrasyonda giriş akışı ticaretin büyüklüğüne göre tanımlanmalı.

*Not (2026-10-26, [D5b2](experiments/D5b2.md) teşhisi):* Giriş sinyali içerideki tüccarların **gerçekleşmiş** medyan getirisi (D3b). İçerisi tıkanınca (D5b2'de kırıntıya takılan tüccarlar) medyan düşüyor ve giriş duruyor. Bu sırada ALE-VEN buğday farkı 28×'e çıktı ama giren olmadı. Tarihte giriş görülen fırsatlara da tepki verir (liman söylentisi: "Venedik'te buğday altın fiyatına"). Aday: giriş sinyaline görünen fiyat farkını eklemek. ⚠️ Claude önerisi, henüz test edilmedi. Önce kırıntı düzeltmesinden sonra sorunun kalıp kalmadığına bakılacak.

*Kullanıcı yönü (2026-10-26):*
1. Önce başlangıç durumu kararlı duruma yakın başlatılsın.
2. Giriş hızı toplam halk sermayesine ve fırsata bağlı olsun. "Kimse toplam taşıma kapasitesi az diye tüccar olmaz, fırsat varsa girer. Kârlı bir ticaret varsa ve bu genel biliniyorsa tüccar girişi olmalı."

*Not (2026-10-26, [D5b3b](experiments/D5b3b.md)):* İtibarlı colleganza ile denge getirisi %1'den %4,5-6,5'e çıktı (giriş 149 → 120-135), ama hedef %8'in altında. Tasarlanan friction kanalı (girişin alternatifi = colleganza getirisi) devreye girmedi, çünkü colleganza getirisi negatif. Ayrıca sicil tüccar becerisini ayırt etmiyor (kalıcılık 0,06-0,13). Oyunda itibarın anlamlı olması için ya beceri farkı sefer gürültüsüne göre büyük olmalı, ya da sicil daha zengin olmalı (mektup ağı, lonca, aile). Kullanıcı talimatıyla friction konusu yeniden konuşulacak.

Modelleme yolu açık. **Öneri (Claude, framework A11):**
- **Sermaye havuzu:** Her limanın yatırılabilir sermayesi K_p var (patriciate, esnaf birikimi). Senetlerde durur, tasarrufla büyür; çıkan tüccarın parası ve temettüler oraya döner. Bugünkü "senetten para gelir" musluğunun yerine geçer; para korunumu da netleşir. Tarihsel karşılığı colleganza / commenda: yerinde oturan yatırımcı (stans) sermayeyi, yola çıkan tüccara (tractator) verir.
- **Kamuya açık fırsat:** Her limanın bir price current'ı var, yani o limana gelen haberlerle oluşan fiyat tablosu (bayat). Aday yatırımcı bu tabloyla temsilî bir düzey 1 hesabı yapar; bilinen rakip kargo ve yeni girenler de kalabalığa dahil. Sonuç beklenen fazla getiri x = beklenen getiri − (senet + risk primi).
- **Giriş akışı:** aylık beklenen giriş ∝ (K_p / gemi + sermaye maliyeti) × F(x). F, yatırımcıların eşik dağılımı: her yatırımcının risk primi farklı, x büyüdükçe daha çok yatırımcı ikna olur. Böylece "genel biliniyor + kârlı" → giriş.
- **Gecikme:** gemi bulma ve donatma 1-2 ay (tarihsel: kiralık gemi ya da muda'ya katılım).
- **Çıkış simetrik:** gerçekleşmiş değil beklenen getiriye bakar (bugünkü kural gerçekleşmiş getiri; yine de öğrenme sinyali olarak tutulabilir).
- **Başlangıç:** ön koşu (spin-up). Dünya kısa bir süre hızlı girişle koşulur, kararlı filo büyüklüğü ve sermaye dağılımı ölçülür, asıl koşu o filoyla başlar. Ayrıca ilk yıl metriklerden ayrılır (`explode_last` gibi).

⚠️ **Risk (eleştirel not):** Herkes aynı kamu tablosunu görürse giriş dalgası olur: hep birlikte girerler, glut olur, hep birlikte çıkarlar. Bu entry cobweb'dir; gemi yapım döngüleri literatürde bilinir (Stopford, *Maritime Economics* ⚠️). Tamponlar: gecikme, yeni girenlerin kalabalığa sayılması (düzey 1), yatırımcı eşiklerinin dağılımı. Bu dalga bir dereceye kadar gerçek ve istenen bir fenomen olabilir; test edilip sınıflandırılmalı (Y16).

Açık sorular kullanıcıya: havuz liman başına mı, tek mi? Giriş yalnızca yeni tüccar mı, yoksa mevcut tüccara sermaye (colleganza) de mi?
*Cevap (kullanıcı, 2026-10-26):* liman başına havuz; colleganza da olsun (K-020). Uygulama D5b3.

*D5b3 sonucu (2026-10-26):* Fırsata bağlı giriş rantı eritiyor: medyan getiri %33'ten %1-5'e, filo 40'tan 80'e. Denge hedefin (senet + risk %8) altında; fazla giriş. Sebepler: marjinal yatırımcı, sefer kârı terimi, yapışkan çıkış. Düzey kalibrasyon sorusu: eşik dağılımı, ilgi oranı, çıkış. Colleganza adverse selection yüzünden zarar ediyor; aday: itibar. Ayrıntı [D5b3](experiments/D5b3.md).

**S-009 — Oyuncunun toplumsal statüsü**
Venedik'te patrizi, cittadini originari ve popolani sınıfları farklı ticari haklara sahipti (ör. Levant ticareti ve bazı imtiyazlar). Oyuncu hangi sınıftan başlar? Yabancı (Ragusalı, Yahudi, Rum, Floransalı) bir tüccar olarak başlamak mümkün mü? Bu, başlangıç konumu seçimini (K-005) zenginleştirir.
Durum: açık, araştırma gerekli.

**S-013 — Perakende sürtünmesi ve dükkân sayısı: müşteri ne kadar bilgili, dükkân ne kadar sabit gider öder?**
D5a2'de perakende marjı iki şeyle belirleniyor: (1) β, müşterinin fiyat duyarlılığı (arama sürtünmesi): marjın alt sınırı 1/(β−1); (2) dükkânların sabit giderleri: serbest girişin nerede duracağını, dolayısıyla dükkân başına kârı belirler. Modelde sabit gider neredeyse sıfır olduğu için giriş üst sınıra dayanıyor. Ayrıca modeldeki "dükkân", kentteki yüzlerce fırıncı ve bakkalın temsilcisi.
Kullanıcının ilkesi: perakendede rant olmamalı; oluşursa devlet müdahalesi eventi.
Sorular: β kente göre mi değişmeli (büyük kentte müşteri daha bilgili mi)? β müşterinin fiyat beklentisine bağlanırsa rockets and feathers çıkar mı (kullanıcı: şimdi değil, akılda kalsın; framework §8)?
Durum: **kısmen cevaplandı (2026-10-23):** Dükkâncının geçimi sabit gider olarak eklendi (kullanıcı kararı, tüccarla eşit). Dükkân sayısı artık pazar büyüklüğüne göre kendiliğinden belirleniyor (D5a2 REL). β'nın değeri ve kente göre değişip değişmeyeceği açık; sayısal ayar Y13 gereği ertelenir.


**S-014 — İleriye bakan beklentinin "temel"i ne olmalı?** (D5b2'den, 2026-10-26)
Kullanıcı ilkesi: piyasayı yöneten beklentidir, fiyat geçmişi değil. D5b2'deki uygulama (Claude tasarımı) temeli şöyle kurdu: olağan fiyat = tüccarın son 20 gözleminin medyanı × hasat haberi × mevsim. Sonuç: ölçülebilir yarar yok; kendi-etkiyle birlikte ısınma kıtlığını artırıyor (15/50'ye karşı 1/50).
Sebep: temel arz durumunu görmüyor. Kıtlıkta "olağan" bayat medyana çapalanıyor, tüccar yüksek fiyata inanmıyor.
Aday: temel = görünen arz-talep dengesi (hedefteki stokçu ve dükkân stoğu, yoldaki ve limanda bekleyen kargo, günlük tüketim → kaç günlük stok var) ve buradan ima edilen fiyat (King-Davenant / esneklik). Tarihsel karşılığı tüccar mektuplarındaki "orada X gemi bekliyor, ambarlar dolu/boş" bilgisi. ⚠️ Claude önerisi, test edilmedi.
Durum: **açık.** Şimdilik B'nin yalnızca kendi-etki parçası kullanılabilir (GBSL·imp).

*Araştırma (2026-10-26, [07-expectation-formation](research/simulation/07-expectation-formation.md)):*
- Deneysel olarak en iyi doğrulanmış beklenti modeli **heuristic switching** (Anufriev & Hommes 2012; Hommes 2011): birkaç basit kural, geçmiş başarıya göre seçilir.
- Kullanıcının sorusu ("TA'ya göre mi çalışır? çalışmamalı"): belirleyici olan **geri besleme yönü**. Mal piyasalarında (negatif geri besleme) fiyat dengeye yakınsıyor, trend kuralları sönüyor; spekülatif piyasalarda (pozitif) balon çıkıyor (Heemeijer ve ark. 2009; Bao ve ark. 2012).
- Tüccar ticareti negatif geri beslemeli. Pozitif kanallar: stokçu / istifçi, dükkân envanteri, köylünün satışı ertelemesi.

**Öneri (Claude, A10):**
- Temel kural = bilgi temelli arz durumu. Hedefteki bilinen stok, yoldaki ve limanda bekleyen kargo, hasat haberinden "kaç günlük arz" çıkarılır; talep esnekliğiyle ima edilen fiyata çevrilir.
- Buna çapalama (C4) ve trend kuralları eşlik eder. Ağırlıklar kişi düzeyinde tahmin başarısıyla güncellenir.
- Doğrulama: trend kuralının payı tüccar piyasasında sönmeli; sönmüyorsa motorda pozitif geri besleme sızıntısı var.

*Kullanıcı yönü (2026-10-26):* Farklı tüccar havuzlarında farklı beklenti modelleri (ve kombinasyonları) uygulanıp simüle edilsin, sonuçlar karşılaştırılsın. Bu bir model turnuvası (experiment-approach: her yuva için akademik modeller yarışır). Plan: D5b4, D5b3'ten sonra.

**S-015 — Tüccar finansmanı: borç, colleganza ve yatırımcı öğrenmesi nasıl birleşmeli?** (D5b3b'den, 2026-10-26)
Durum: **tartışılıyor; simülasyon yok.** Araştırma: [08-trade-finance-contracts](research/simulation/08-trade-finance-contracts.md).

*Kullanıcı önerisi (2026-10-26). Kullanıcı notu: "bu tarz tasarımları emin olmadan öneriyorum veya onaylıyorum", yani hiçbiri kesin değil:*
1. **"Tersine senet":** Likidite sıkıntısı çeken tüccar, senet getirisi + risk primi faizle vadeli borç alır. Böylece havuzdaki para boşta (senette) kalmaz ve sistem gerçeğe benzer.
2. **Colleganza** yalnızca çok yüksek kredibiliteli tüccara, hacmini artırmak için verilir.
3. Riski ve yeteneği düşük tüccar borç almaya daha az motive olur (yeni davranış, uygulanacak).
4. **Yatırımcı öğrenmesi** olmalı; colleganza'nın liman getirisine bağlanması mantıklı görünüyor.
5. Giriş friction'ı ve kâr marjı artırımı **sonra** konuşulacak.

*Claude değerlendirmesi (2026-10-26, tartışma için; köken C/L):*
- (1) Teori ve tarihle uyumlu: costly state verification altında optimal sözleşme borçtur (Townsend 1979). Venedik'te sea loan, commenda'dan önce ve ticaretin sınırlarında baskındı (González de Lara 2000; Williamson 2011). Yatırımcının sıfır-kâr kaybını çözer: alacaklı yalnızca temerrütte kaybeder. Kaldıraç sınırı varsa temerrüt nadirdir.
- (3) Kendiliğinden olmaz, sorumluluk kuralına bağlı. Sınırlı sorumlulukta ve aşırı güvende kötü tüccar borca daha hevesli olur (Stiglitz & Weiss 1981; Malmendier ve ark. 2011 ⚠️). Gerekenler:
  - Tam sorumluluk (borç tüccarın bütün servetinden ödenir, temerrüt limanlar arası duyulur).
  - Kaldıraç sınırı (teminat; Bester 1985 ⚠️).
  - Borç kararında tüccarın **kendi** sicili (learning from experience) ve risk tutumu (mevcut `risk_aversion`, DARA).

  D5b3.2 uyarısı: düzey 0 tüccar iyimser (beklenen %31, gerçekleşen −%17). Kendi sicili olmadan en hevesli borçlu o olur.
- (2) D5b3b'ye göre sicil beceriyi ayırt etmiyor (kalıcılık 0,06-0,13). "Çok yüksek kredibilite" pratikte "şanslı" demek. Alternatif ölçüt: doğrulanabilirlik. Colleganza gözetimli rotalarda ve limanlarda (Venedik konvoyu), borç her yerde (González de Lara).
- (4) Öğrenme, havuzun senet / borç / colleganza arasındaki paylaşımı olarak kurulabilir: gerçekleşen getiriye göre logit paylar (A10'daki HSM'nin sermaye karşılığı). Riski: credit cycle (Kiyotaki & Moore 1997 ⚠️; Minsky). Bu bir istismar değil oyun fenomeni olabilir, ama sınanmalı.
- İstismar riski (oyuncu): küçük güvenli seferlerle sicil şişirip büyük borçla kumar (asset substitution; Jensen & Meckling 1976 ⚠️). Önlemler:
  - Kaldıraç özsermayeye bağlı.
  - Sicil hacimle ağırlıklı. Kullanıcının skorundaki hacim terimi bu açıdan haklı.
  - Temerrüt kaydı.

*Karar (2026-10-26):* K-022'ye bağlandı. Açık kalanlar: batan gemi riski (sea loan için), karmaşık araçlar (supplier credit, cambio). Uygulama D5b3c.

**S-016 — Senet getirisi dinamik olmalı mı, nasıl?** (kullanıcı, 2026-10-26)
Şimdi sabit (≈%4). Kullanıcı: dinamik olmalı, ama yöntem düşünülmedi; akılda kalsın. Aklımdaki adaylar (Claude, tartışma için):
- (a) Devletin borç ihtiyacı: savaş ve olağanüstü vergide getiri yükselir (Venedik Monte'leri ⚠️).
- (b) Sermaye bolluğu: havuz büyüdükçe getiri düşer (arz-talep).
- (c) Kriz sonrası güven primi.

Durum: **açık, ertelendi.**

*Kullanıcı önerisi 2 (2026-10-26, kesin değil):*
- Devlet senet faiziyle borçlanır, tüccar borçlanamaz. Tüccar başına kredi skoru ve ona göre faiz konursa, alacaklı mahsuptan sonra senede yakın kazanır.
- Pahalı borç tüccarın davranışını değiştirir. Belki hacim düşer, ticaret kârlılaşır; fiyat etkisi ne olur?
- Belki tüccar getirileri biraz artırılır ya da başka ayrıcalıklar konur.
- İtibar sorununu da çözebilir.

Araştırma: [08 §5](research/simulation/08-trade-finance-contracts.md). Teşhis: [D5b3c T2](experiments/D5b3c.md).

*Claude değerlendirmesi (tartışma için):*
- Kredi skoru, temerrüt olasılığı gözlenebilir değişkenlerden tahmin edilebildiği ölçüde çalışır (Einav ve ark. 2013).
- Teşhise göre temerrütü belirleyen beceri değil seferin koşulu: varıştaki kalabalık, kaldıraç, parti büyüklüğü. Bu yüzden skor **sefer + tüccar** düzeyinde olmalı: rota, mevsim, limanda görülen rakip yüklemeleri, kaldıraç ve tüccarın temerrüt geçmişi. Tarihte de deniz ödüncü ve sigorta primi rotaya ve mevsime göre belirlenirdi.
- İtibar, beceri sinyali olarak değil disiplin olarak çalışabilir (Diamond 1989): ucuz kredi kaybedilecek bir varlık olursa tüccar daha güvenli seçer. Bunun için batma bedeline "gelecekteki kredi fiyatı" eklenmeli.
- Hacim ve fiyat etkisi bu modelde küçük kalır, çünkü tüccarların çoğunu bağlayan nakit değil pazar derinliği (ambar %9 dolu). Kârlılığın asıl engeli fazla giriş ve boş kapasite (Mankiw & Whinston 1986 ⚠️). Kullanıcının ertelediği giriş ve marj konusu bu teşhisle merkeze geliyor.

*Kullanıcı yönü 3 (2026-10-26; tasarım kesin değil, uygulama yok, tartışılıyor):*
1. **Sefere göre faiz:** Alacaklı faizi kendi sefer sonucu beklentisine göre verir. Alacaklı, ticaret loncası gibi tüccardan fazlasını bilen bir kurum olabilir (gemilerdeki yük, rotalar, yer yer fiyatlar). Riskli seferler ve getiri/risk oranı düşük seferler daha yüksek faiz alır. Bu, o seferlere sermayeyi kısar ve borç batmasını belli ölçüde önler. Bilgi işleme yöntemi ve parametreleri hassas denge ister.
2. **Faizin girdileri:** limanda görülen rakip yüklemeleri, kaldıraç, rota ve mevsim, temerrüt geçmişi.
3. **İtibar + disiplin (Diamond):** ilgi çekici, şimdilik rafa (framework Ertelendi).
4. **Pahalı borç** yalnızca "yanlış" sefere pahalı olursa ticaretin kârlılığı genel olarak artar. Faiz, bilgisi ya da becerisi düşük tüccara da bir insight olur; bu doğal.
5. **Ölçüm hatası** (birim kargo başına getiri) düzeltilmeli; üstüne kurulan hesaplar hatayı büyütür.
6. **Brüt-ömür boyu getiri farkı** tekrarlanırsa incelenecek.
7. **Asıl sorun ayrı:** tüccar fazla, pazar az. Rekabeti azaltıp getiriyi artırmak olmamalı. Kalabalık azaltılmalı. Tarihsel mekanizma ne? Neden herkes borç alıp ticaret yapmıyor? Batma cezası ölüm olsa caydırır mı?
8. **Bilgi sorunu:** Alacaklının tüccardan çok akıllı olması istenmiyor, ama başvuran bütün seferlerin bilgisi alacaklıda olacak. Bunun için bir mekanik gerekiyor.
9. **İki ana mesele:** borç ve perfect competition. Tarihsel ve ekonomik olarak doğru mekanizmalarla çözülmeli.

Araştırma: [09-market-structure-entry](research/simulation/09-market-structure-entry.md), [08 §5](research/simulation/08-trade-finance-contracts.md).

**S-017 — Perfect competition: getiri neden %0'a iniyor ve doğru giriş mekanizması ne?** (D5b3c T2'den, 2026-10-26)
Durum: **tartışılıyor.**
- Teşhis: sefer marjları iyi (+%14), ama ambar %9 dolu; fazla giriş. Hedef S-012'deki ~%8 (senet + risk).
- Ekonomi: serbest girişte pazar büyüklüğü ve tarife getiriyi değil filo büyüklüğünü belirler. Getiri, giriş-çıkış kuralının durduğu yerde durur.
- Claude önerisi (tartışma için; ayrıntı 09):
  - (a) Giriş = sonlu potansiyel tüccar nüfusunun meslek seçimi (Kihlstrom & Laffont). Kişinin kendi serveti risk altında, batma riski hesaba katılır.
  - (b) Gemi başına sabit maliyet: boş kapasitenin bedeli (Bresnahan & Reiss).
  - (c) Yeni tüccarın sinyali, gelecek bir geminin yıllık sermaye getirisi olmalı; mevcut tüccarların sefer marjı değil (business stealing; Mankiw & Whinston).
  - (d) Ayrıcalıklı hatlar (muda, incanto) sonraki katman.

*Not (2026-10-26, D5b3d T1; S-012 ve S-017 için):*
- "Denge getirisi %0-5" yargısı ömür boyu getiri medyanına dayanıyordu ve yanıltıcıydı. Sermaye-yıl ağırlıklı toplam getiri ~%12-13 (batanlar dahil); hedef %8'in üstünde.
- Dağılım çok çarpık: tüccarların yarısı kaybediyor; hayatta kalanlar ~%26, kısa ömürlü girişler büyük zararda; en iyi %10 kârın ~%58'ini alıyor.
- S-012'deki %8 hedefinin hangi ölçütle kıyaslanacağı kullanıcıyla netleşmeli:
  - (a) toplam sermaye getirisi
  - (b) tipik (medyan) tüccarın getirisi
  - (c) yeni girenin beklenen getirisi

**S-018 — Herkes aynı en kârlı işi seçemez: rota seçiminde dağılım mekanizması** (kullanıcı, 2026-10-26)
Durum: **yön kararlaştı (K-026); plan [D5b3e](experiments/D5b3e.md), uygulama bekliyor.** Araştırma: [10-route-choice-coordination](research/simulation/10-route-choice-coordination.md).

*Kullanıcı teşhisi ve önerileri (kesin değil):*
- Tüccarlar en kârlı işi seçiyor; hepsi aynı işe yığılıyor ("A Beautiful Mind"daki bar sahnesi). Dağılım gerekiyor.
- Öneriler:
  1. Tüccar ağı yönlendirmesi (kullanıcı: "game theoretic olarak etkisi olmamalı")
  2. Hesaplara noise
  3. Tüccarların bir kısmı limana bağlı, yalnızca bazı rotalarda ticaret yapabilir
- Mekanizma tarihsel ve ekonomik olarak doğru olmalı.

*Claude değerlendirmesi (tartışma için):*
- Teşhise katılıyorum. Saf argmax congestion oyununda denge değildir (karma denge; Arthur 1994). D5b3d: kalabalık filodan bağımsız.
- (2) → logit seçim (QRE / random utility; McKelvey & Palfrey 1995). Kesinlik bilgi düzeyine bağlı.
- (3) → ağ ve uzmanlaşma, yumuşak maliyetle: bilinen limanlarda taze bilgi ve düşük işlem maliyeti, dışında komisyon ve bayat bilgi; ağ deneyimle genişler (Trivellato; Datini; Roy modeli). Sert yasak yerine.
- (1) → bilgi paylaşımı olarak etkisi sınırlı ama sıfır değil (correlated equilibrium). Asıl etkili biçimi şubeli ticaret evi (Datini): ev kendi gemilerini aynı rotaya yığmaz. Yeni varlık gerekir; sonraya.
- Ek: tahmin kuralı çeşitliliği (D5b4; El Farol), gemi türü çeşitliliği (kabotaj).
- **D5b3e sonucu:** E1, E2, E3 3 limanlı dünyada kalabalığı değiştirmedi. Aday neden dar dünya; tam haritada test gerekiyor.
- Motor kontrolü (`_rivals`): seviye 0 rakipleri saymıyor; imitation bonus kalabalığa çekiyor; yalnızca yola çıkmış yükler görülüyor. Önce bunların ablation'ı.

**S-019 — Simülasyon motoru hangi dilde ve mimaride olmalı?** (kullanıcı, 2026-10-26)
Durum: **açık; kullanıcı söylemeden migration yok.** Araştırma: [tech/01](research/tech/01-simulation-engine-options.md).
- Kullanıcı: Python bu motoru taşıyamaz. Harita büyüyecek, tick saat seviyesine inecek.
- Claude eğilimi:
  - Dilden bağımsız olarak olay güdümlü kararlar, multi-rate tick ve dizi tabanlı veri düzeni.
  - Uzun vade için hibrit: çekirdek Rust, deneyler Python (PyO3). Alternatifler C# (Godot/Unity arayüzü olacaksa) ve Julia.
- **2026-11-09 (kullanıcı):** İlk iş hızlandırma; araştırma genişletildi: [tech/02](research/tech/02-performance-plan.md). Tam harita profili: tek baskın yapı (`_rivals` %40, karar başına iş liman² × mal × yük). Claude önerisi: A (Python'da algoritma, davranış birebir) → B (taşınabilir RNG, gün sonu hash) → C (Rust çekirdek, önce spike). Kullanıcı kararı bekleniyor.

**S-020 — Büyük haritada fazla giriş: hangi giriş bariyeri?** (kullanıcı, 2026-10-27)
- D5b3e.5: 45 pazarda getiri ~%0, filo 3 kat.
- Seçenekler ve türleri: [11-entry-barriers](research/simulation/11-entry-barriers.md).
- Claude eğilimi (Claude önerisi, kesin değil):
  - Önce teşhis: giriş anındaki beklenti ile gerçekleşen getiri karşılaştırılsın.
  - Sonra sonlu, heterojen aday tüccar + statüye göre maliyet farkı.
  - Eşit batık maliyet yalnızca ablation olarak denensin.
- Kullanıcı (K-028): sonlu aday havuzu yok; diğer bariyerler uygulanmalı (kesin değil).
- Kullanıcı sorusu: varışta fiyat düşer, gemi başka limana gider ya da ucuza depocuya satar; bu fırsat maliyeti yığılmayı engellemeli. Bir mekanizma mı eksik?
- Claude cevabı:
  - Mekanizma var (fiyat etkisi, reroute, kapan). Büyük haritadaki rota dağılımını o sağlıyor.
  - Ama rotalar arası getiriyi eşitler, toplam filoyu sınırlamaz. Toplamı giriş-çıkış kararı belirler.
  - Aday neden: optimizer's curse seçenek sayısıyla büyür (doğrulanmadı).
- **Teşhis (D5b3f):** Filo döngüde (cobweb). Kaynaklar:
  - Soğuk başlangıç artifact'ı.
  - Gecikmeli sicil.
  - Kuralın durma noktası senet (prim yalnızca hızı belirliyor).
  - Yavaş çıkış.
  - Survivorship.
  - Büyük haritada bonus (optimizer's curse adayı; ölçülen ve doğrulanan kısım: büyük haritada daha büyük).
- **K-029:** giriş-çıkış kuralı düzeltiliyor (snapshot, ortak eşik, sefer sonunda çıkış, batanlar dahil sicil, credibility). Bariyerler bunun sonucuna göre seçilecek.
- D5b3g: seviye düzeldi, filo döngüde (ıraksak cobweb). Kullanıcı önerisi (2026-10-30): 3 × 3 ay teyitli giriş. Claude alternatifi: real options bandı ([12](research/simulation/12-entry-decision-timing.md)).
- D5b3g sonucu: U tek başına döngüyü büyüttü; R ve U + R sönümledi (tepe / dip ~3, devir 3-5 kat az). Getiri hedefin üstünde (%16-18,5): giriş eşiği σ ile %12-14 (σ ölçüldü: %4-6); sistem bandın üst kenarında duruyor.
- Kullanıcı (2026-11-02): bant geçici; her şey tarihsel ve ekonomik olarak doğru olmalı, tepeden ayar değil doğal gelişme (İ12). Şimdilik bugünkü yapı kalabilir.
- Claude önerileri: [14](research/simulation/14-natural-entry-exit.md). Sıra: Ö0 ölçüm → Ö1 credibility k veriden → Ö2 eşik bileşenleri (K-029 doğrulaması) → Ö3 gemi piyasası (bandın doğal yerine geçer) → Ö4 bilgi temelli sicil → Ö5 U'nun yeniden değerlendirilmesi.
- Durum: açık; kullanıcı kararı bekleniyor.

## S-021 — Risk modelinin ayrıntıları (K-030)
> Açıldı: 2026-11-02 · İlgili: [risk-model](design/risk-model.md), [maritime-risk-16c](research/history/maritime-risk-16c.md)

- ~~Gemi kaybı: bugün yalnız yük kayboluyor. Gemi sermaye olarak batmalı mı?~~ Cevaplandı: K-032 (gemi gider; Ö3 öne çekildi).
- Sefer sıklığı: modelde yılda 8-15 sefer, tarihte 2-4 ([shipping-scale-16c](research/history/shipping-scale-16c.md)). Limanda geçen zaman (yükleme, alıcı arama) eksik. Ayrı bir motor adımı olarak önerildi.
- Bölgelerin tehlike seviyeleri: 16. yy kaynağı eksik (Tenenti 1967, Greene 2010, Lane 1973).
- Yatırımcının servet payı (w) ve gemi sayısı (N): tarihsel kaynak aranacak.
- Sigortacı kim: tüccarlar arası mutual grup (Cenova 1564-72) mi, ayrı havuz mu?
- Durum: açık.

## S-022 — Gemi kaybı ölçeği, korsanlığın zaman çizelgesi, yabancı gemi
> Açıldı: 2026-11-09 · İlgili: [D5b3j](experiments/D5b3j.md), [shipping-scale-16c](research/history/shipping-scale-16c.md), [risk-model](design/risk-model.md), S-021, K-030, K-032
> Durum: **açık. Kullanıcı: modele oturtmadan önce akademik (ekonomik model) ve tarihsel araştırma, sonra karar.** Sıra: önce motor hızlandırma (S-019).

**Kullanıcı yönü (2026-11-09):**
1. Gemi kaybı ölçeği (depreciation) düzeltilmeli. Tarihe yakın olunmalı, ama 50-100 yıllık bir oyun için oynanış senaryoları da kurulmalı.
2. **Korsanlık başta çok az, ~1580'den sonra hızla artar.** Orta oyuna dinamik getiren bir tarihsel olay olarak etkinleşir. Başta "varla yok arası", ör. sefer başına %0,5.
3. **Yabancı gemi:** Ucuzsa (tarihte öyle) teslim süresi uzun olmalı (ör. +6 ay). Tüccar da oyuncu da bunu vade maliyetiyle kendisi tartar.

**Claude ilk değerlendirmesi (araştırma öncesi, ⚠️):**
- **Hesap:** Sefer başına %0,5, yılda 15 seferde 1 − 0,995¹⁵ = **%7,2** (bileşik; doğrusal %7,5). Yılda 3-4 seferde %1,5-2.

  | Sefer başına | 3 sefer/yıl | 4 | 7 (VRS) | 14,4 (F) |
  |---|---|---|---|---|
  | %0,5 | %1,5 | %2,0 | %3,4 | %7,0 |
  | %1 | %3,0 | %3,9 | %6,8 | %13,5 |
  | %2 (bugün) | %5,9 | %7,8 | %13,2 | %25,2 |

- **Yılda %7 nasıl bir risk?** Tarihsel aralığın (%4-12) içinde; tek başına fazla değil. Kayıptan beklenen gemi ömrü ~14 yıl, yıpranma ömrüyle (15 yıl) aynı mertebe. 50-100 yıllık oyunda bir tüccar birkaç gemi kaybı yaşar. Ama:
  - **Sefer başına %0,5'i sefer sıklığını telafi etmek için seçmek tepeden ayar olur (İ12).** Kaynaklara göre sefer başına kayıp %2-4, sefer sayısı yılda 2-4. Bizdeki fazlalık sefer sayısında. Sefer başına oranı düşürürsek yıllık kayıp doğru çıkar, ama sefer başına sigorta primi (R4) tarihin çok altında kalır, ve limanda zaman düzeltildiğinde kayıp bir daha düşer (yılda %1,5-2).
  - **Doğal kayıp (fırtına, karaya oturma) korsanlıktan ayrı.** Bugün kayıpların ~%58'i korsan. Korsanlık sıfırlansa bile doğal kayıp sefer başına ~%0,8; F'de bu tek başına yılda %11. Yani "başta az korsanlık" yıllık kaybı ancak sefer sıklığı düzelince istenen düzeye indirir.
  - Öneri sırası: (1) limanda zaman ile sefer sıklığı → yılda 2-4; (2) sefer başına tehlike tarihsel düzeyde; (3) korsan baskısı yıla bağlı bir süreç (aşağıda).
  - Dengede kayıp oranı getiriyi bozmuyor: risk navlun ve fiyat farkına geçiyor (D5b3j'de yıllık %28 kayıpla bile getiri ≈ eşik). Kayıp oranının asıl etkisi devir hızı, iflas, gemi yaşı ve oyuncunun hissettiği varyans.
- **Korsanlık zaman çizelgesinin tarihsel dayanağı (araştırılacak):**
  - Braudel'in bilinen tezi: 1571-80 sonrası büyük donanma savaşları biter (İnebahtı 1571, Osmanlı-İspanya ateşkesleri 1578-81), savaşın yerini korsanlık alır. 1580-1620 korsanlığın doruğu; Tenenti'nin 1592-1609 verisi bu dönemden. Kuzeyli gemilerin (İngiliz, Hollanda) gelişi 1570'ler-1590'lar.
  - Ama 1560 öncesi de boş değil: Barbaros (1510'lar-1546), Turgut Reis (1550'ler), Uskoklar (1530'lar sonrası), Malta şövalyeleri. Bu dönemde baskın daha çok devlet savaşına (1537-40, 1570-73) bağlı.
  - Çalışma başlangıç yılı 1560 (Y11). O zaman kullanıcının senaryosu tarihle uyumlu: başta görece düşük, savaş yıllarında sıçrama, 1580'den sonra yapısal artış. "Varla yok arası" ise tarihin biraz altında; oyun tasarımı sapması olarak işaretlenmeli.
  - Model biçimi: bugünkü korsan baskısı süreci (AR(1), bölge bazlı) uzun dönem ortalaması yıla bağlı bir trendle. Trend, tarihsel olay (ateşkes, kuzeyli gemilerin gelişi) olarak etkinleşir.
- **Yabancı gemi:**
  - Kullanıcının önerisine katılıyorum. Motor bunu zaten taşıyor: tersane siparişinde olduğu gibi peşin bedel + gecikmeli teslim, tüccar bekleme süresini iskontoyla hesaba katıyor.
  - Bugünkü "%25 pahalı, hemen" seçeneği ikinci el fiyatına **tavan** görevi görüyor (D5b3j: en yüksek 1,25-1,31). Ucuz ve gecikmeli yabancı gemi olunca bu tavan kalkar. Patlama dönemlerinde ikinci el gemi yeni gemiden pahalı olabilir. Bu shipping ekonomisinde bilinen bir örüntü (Stopford ⚠️); doğal sonuç olarak kabul edilebilir.
  - Araştırılacak:
    - Venedik'in dışarıdan aldığı gemilerin kaynağı (Ragusa, Dalmaçya, Girit; sonra kuzey)
    - Fiyat farkı (kolonilerde ~%15-20 ucuz, Gluzman 🔎)
    - Getirme süresi ve riski
    - "Venedik yapımı" şartının kalkışı
- **Araştırma planı (karar öncesi):**
  - Tarih:
    - Tenenti 1959/1967
    - Greene 2010, *Catholic Pirates and Greek Merchants*
    - Braudel II (korsanlık bölümü)
    - Fontenay
    - Gluzman 2021 Bölüm 9 (gemi ömrü)
  - Ekonomi:
    - Risk primi ve navlun ilişkisi (Stopford; North 1968)
    - Shipping cycle'da yeni ve ikinci el fiyat ilişkisi
    - "Time-to-build" (Kydland-Prescott 1982)

**Araştırma sonucu (2026-11-09, [ship-life-piracy-16c](research/history/ship-life-piracy-16c.md)):**
- **Gemi ömrü ~10 yıl, barışta en çok 13** (Gluzman Bölüm 9). Dış etkenlerle ortalama ömür 6 yılın altında; işletmeci ≤ 7 yıl varsayıyordu. Motordaki 15 yıl (Claude ⚠️) uzun.
- **Yıllık kayıp ~%10-13** (Claude hesabı, Gluzman'dan; 1453-1571 Venedik, savaşlar dahil). Bu, önceki %4-12 aralığının üst ucu. Sonuçları:
  - VRS'deki %14,5 tarihten çok uzak değil.
  - F'deki %28 iki katı.
  - Sorun yine sefer sıklığı: tarihte sefer başına ~%3-4 × yılda 3 sefer.
- **Barış dönemi primi** Levant'a gidişte %1-1,5, dönüşte %2-2,5 (15. yy sonu). Korsana düşen pay ~%0,5 ise kullanıcının "%0,5" önerisi barış tabanıyla uyumlu; doğal tehlike ayrıca var.
- **Korsanlık zaman çizelgesi:** 1580-1620 patlaması (Fontenay: "korsan yüzyılı" 1580-1680); Tenenti: kuzey korsanları 1580-1615. Kullanıcının senaryosu tarihle uyumlu. 1560'larda korsan sıfır değil (Uskok, Berberi, Malta), savaş yılları (1570-73) sıçrama.
- **Yabancı gemi ucuzdu** (koloni −%17; Hollanda gemisi Baltık kerestesiyle ucuz). Engel fiyat değil, yasaydı: Venedik yapımı gemiye ayrıcalık tanınıyordu, dışarıdan alım yasaya aykırıydı ama yapılıyordu (Lane). Getirme süresi için kaynak yok; "+6 ay" oyun varsayımı.
- **Ekonomi:**
  - Kalouptsidi 2014: time-to-build kalkarsa yatırım çok daha oynak olur. Bugünkü "hemen yabancı gemi" time-to-build'i fiilen kaldırıyor.
  - İkinci el fiyatı piyasayla, yeni gemi fiyatı maliyetle belirlenir (Tsolakis). Patlamada ikinci el fiyatı yeni gemi bedelini aşabilir (zaman primi).

**Seçenekler (Claude, kullanıcı kararı bekleniyor):**
1. **G1 Gemi ömrü:** 15 → 12 yıl (kaynakta 10-13; doğrusal amortisman, söküm %10).
2. **G2 Yabancı gemi:** bedel × 0,83, teslim tersane süresi + 180 gün; Venedik tersane kuyruğundan bağımsız.
   - İstismar önlemi: yabancı kaynağın da kendi kuyruğu olsun (kapasite sınırlı, patlamada uzar). Kalouptsidi'nin bulgusu ve oyuncunun sınırsız ucuz büyümesine karşı.
   - Venedik yapımı ayrıcalıkları ileride.
3. **G3 Korsanlık zaman çizelgesi:** Korsan baskısının uzun dönem ortalaması yıla bağlı:
   - 1560-1579 düşük taban (korsan payı ~%0,5 / sefer);
   - 1570-73 savaş sıçraması (tarihsel olay);
   - 1580-1620 artış, doruk ~3-4 kat ⚠️ (sayı yok; Tenenti 1959 verisiyle sonra).
   - Doğal tehlike ayrı ve sabit.
4. **G4 Limanda zaman** (timeline 56'da kullanıcı kararı): sefer sıklığını yılda 2-4'e indiren mekanizma. Bu olmadan G1-G3'ün yıllık kayıp ve yaş örüntüleri yanlış ölçekte kalır.
- **Önerilen sıra:** G1 + G2 küçük ve bağımsız (gemi piyasası); hemen yapılabilir, VRS/F ile ölçülür. Sonra G4 (büyük motor değişikliği). G3, G4'ten sonra; G3'ün ölçeği sefer sıklığına bağlı.

## S-023 — Liman hiyerarşisinin tasarımı (K-034)
> Açıldı: 2026-11-10 · İlgili: [port-hierarchy-16c](research/history/port-hierarchy-16c.md), K-034, S-022
> Durum: **açık; araştırma ilk taraması bitti, kullanıcıyla konuşulacak.**

Konuşulacaklar:
1. Liman tek bir sınıf mı (büyük, orta, küçük), yoksa üç özellik mi (fiziksel liman, pazar, kurum)? Claude: üç özellik; sınıf bunların özeti.
2. Harita ölçeği: tarihsel tabloda 40-60 liman var. Hepsi mi, yoksa önce merkezler ve ortalar, sonra küçük iskeleler mi?
3. Küçük limanlar için hafif pazar modeli.
4. Gemi tipleri: kaç tip (en az 2: nave ve marciliana/caramusal)?
5. Haritanın sınırı: Karadeniz, Kahire, Halep, Atlantik dış arz/talep olarak.
6. Veri açıkları: liman özellikleri, yükleme hızı, hacimler, nüfuslar. Geçici vekiller (İ12).

## S-024 — Tüccar yetenekleri: bilgi işleme yöntemlerine göre ayrı kategoriler
> Açıldı: 2026-11-10 · İlgili: framework A19, A10, A15, [M1](experiments/M1.md)
> Durum: **not alındı; sonra derinlemesine değerlendirilip test edilecek** (kullanıcı).

**Kullanıcı:** Tüccarlar yeni bilgileri ve sınırları (kalkıştaki gerçek arz, kıtlık haberi) yetenek seviyelerine göre farklı değerlendirmeli. Tüccarları tek bir yetenek ekseninde sınıflamak yerine, birkaç bilgi işleme yöntemi için ayrı yetenek kategorilerine ayırmak: her tüccar bazı işleri daha iyi yapar, çeşitlilik artar.

**Claude ilk not:** Bugünkü motorda yetenek tek eksenli: `level` (bilgi düzeyi), `informed`, kişilik parametreleri (`imitation`, `overconf`, `risk_aversion`). Ayrık yetenekler bu parametrelerin bir kısmını yeniden düzenleyebilir. Literatür: heterojen beklenti ve kural seçimi (Brock & Hommes 1997; HSM, A10); uzmanlaşma ve karşılaştırmalı üstünlük ⚠️.

## S-025 — Talep modeli: "her fiyattan kaç alıcı" (K-037)
> Açılış: 2026-11-10. Kaynak: kullanıcı (vazgeçme fiyatı olmalı, tüketiciler agent değil ama talep "gerçek" yapılanmalı); ara çözüm önerisi Claude.

Sorun: LES lüks talebi unit-elastic; choke price (talebin bittiği fiyat) yok. Küçük limanlarda biber ve ince kumaş 10-34 × referans (M1.2).

**Ara çözüm (onaylandı; kod hazır 2026-11-10, bayrak `wtp`, ayrıntı [M2 §D](experiments/M2.md)):** her gelir sınıfına lognormal reservation price dağılımı (medyan sınıf geliriyle orantılı). Talep = Σ sınıf nüfusu × (1 − F(p)). Fiyat yükseldikçe önce yoksul, sonra orta sınıf çekilir. Claude ekledi; deneyle desteklenecek.

**İleride yapılacak (not, kullanıcı: "mutlaka not düşelim"):** literatür derlemesi ve modele ekleme: discrete choice / logit + outside option (Berry 1994; BLP 1995), Stone-Geary/LES eşik, QUAIDS (Banks-Blundell-Lewbel 1997), mallar arası ikame (baharatlar arası). Depocu davranışıyla etkileşim (talep bitince stok elde kalır) birlikte incelenecek.

## S-026 — Toplu ve seyrek varış (lumpy arrivals) (K-037)
> Açılış: 2026-11-10.

Küçük limanlarda büyük parti seyrek gelir, iki varış arasında stok tükenip fiyat fırlar. Kullanıcı: M3 (küçük limanlar, yerel kabotaj) uygulandıktan sonra yeniden değerlendirilecek. Aday katmanlar (Claude): vazgeçme fiyatı (S-025) derinliği gerçekçi yapar; depocu sermayesi liman ekonomisinden türetilir (elle limit değil); M3 kabotajı merkezden küçük partilerle dağıtım.

## S-027 — Üretici havuzlarına sermaye girişi (yoksulluk tuzağı)
> Açılış: 2026-11-12. Kaynak: kullanıcı ("kârlıysa sermaye girmeli, o sermayeyle yün alınıp üretim yapılmalı"); teşhis Claude ([M2](experiments/M2.md)).

Venedik ince kumaş atölyesi nakitsiz kaldığında girdi alamıyor, üretemiyor, nakit kazanamıyor. Fiyat referansın 21 katı olduğu halde dışarıdan sermaye ya da kredi girmiyor. Seçenekler (Claude, karar bekliyor): (a) tüccar havuzundaki gibi yatırımcı girişi (kâr fırsatına bağlı, Tobin's q); (b) atölyeye kredi (borç verenin aynı mekanizması); (c) putting-out: tüccar girdiyi kendisi alıp atölyeye işletir (tarihsel Venedik/Floransa yün sanayii, ⚠️ araştırılacak).

**Genişleme (2026-11-12):** aynı tuzak depocularda da var. PF'de bile 186 depocudan 77'sinin kasası ~0; depocuya sermaye girişi/çıkışı yok (dükkânlarda var). İhracatçı taban fiyatı ve S1 sözleşmesinin zayıf karşı tarafıyla bağlantılı. Öneri (Claude): depocu, atölye, havuz için tek bir sermaye giriş-çıkış modeli. Ayrıntı: [M2 "Depocular iflas halinde"](experiments/M2.md).

## S-028 — Gemi maliyet yapısı ve sefer kısıtları
> Açıldı: 2026-11-12 · İlgili: M2.md "Gemi maliyetleri", S-026, S-027

Modelde uğrak maliyeti, girişte vergi, gemi zamanının fırsat maliyeti, gemi başına (yükten bağımsız) işletme maliyeti, denizde aşınma, sigorta ve sefer bazlı sözleşme kısıtı yok. İşletme maliyeti tarihsel düzeyin muhtemelen ~5 katı altında ⚠️. Ölçüm: yön değiştirmelerin çoğu gerçek büyük fiyat farklarına rasyonel tepki (gerçekleşen kazanç medyanı +%130). Maliyetler gerçekçilik için gerekli ama tek başına yön değiştirmeyi çözmez. Karar: hangi kalemler, hangi sırayla, hangi tarihsel düzeyde (araştırma gerekir).

**Durum (2026-11-12):** Araştırma ([ship-operating-costs-16c](research/history/ship-operating-costs-16c.md)) ve paket (PC) yapıldı. Sonuç: maliyetler filoyu küçültüyor, gemi davranışını (denizde gün, yön değiştirme) değiştirmiyor. Açık: PC temel olsun mu; sefer sözleşmesi (öncelik değil); navlun vekilinin çift sayımı; limandaki zaman (sürtünme).

