# Genel Çerçeve (v0)
> Durum: canlı doküman. **Kesin değil**; güven seviyeleriyle tutulan bir yön haritası.
> Son güncelleme: 2026-10-22
> İlgili: [vision](../vision.md), [decisions](../decisions.md), [open-questions](../open-questions.md), `yorumlar.md` (yerel dosya, repoda yok), [00-sentez](../research/simulation/00-synthesis.md)

## Bu doküman ne işe yarar?

Kullanıcı "hiçbir şey kesin değil, ama bir çerçeve çıkaralım" dedi. Bu doküman tam olarak bunu yapıyor: her fikri bir **güven seviyesine** koyuyor. Böylece neyin üzerine inşa edebileceğimizi, neyin hâlâ tartışmalı olduğunu ve neyin sonraya kaldığını bir bakışta görebiliyoruz.

| Seviye | Anlamı | Değişir mi? |
|---|---|---|
| 🟢 **İlke** | Projenin kimliği; bunlar değişirse başka bir oyun yapıyoruz demektir | Çok zor |
| 🔵 **Yön** | Büyük olasılıkla böyle olacak; ayrıntı açık | Gerekçeyle değişebilir |
| 🟡 **Aday** | Olumlu değerlendirildi, test veya tartışma gerekiyor | Kolayca |
| ⚪ **Ertelendi** | Bilinçli olarak sonraya bırakıldı | — |

Bir madde güçlenince [decisions.md](../decisions.md)'ye K-numarasıyla taşınır.

---

## 1. 🟢 İlkeler

| # | İlke | Kaynak |
|---|---|---|
| İ1 | Tüccar RPG + strateji; tycoon değil | K-001 |
| İ2 | Oyuncu ekonomide sıradan bir ajandır; NPC'ler aynı kurallara tabidir | K-004 |
| İ3 | Önce canlı ekosistem simülasyonu, sonra oyun | K-009 |
| İ4 | Simülasyon deterministik (seed'li) | K-010 |
| İ5 | **Bilgi fiziksel olarak taşınır ve eskir; bu, tasarımın kalbidir** | 00-sentez, yorumlar |
| İ6 | **Okunabilirlik bir tasarım hedefidir; çok oynak ekonomi yorar** | yorumlar (Space Rangers dersi) |
| İ7 | **"Oyuncu bunu nasıl yaşar?" testi:** hissedilmeyen mekanik kaldırılır | yorumlar (Dwarf Fortress dersi) |
| İ8 | Her bireyi modellemeyiz; kitle havuzlarla temsil edilir | yorumlar |
| İ11 | **Gerçek ekonomik fenomenler oyunda görülmeli.** Pork cycle, cobweb, herding, balonlar, famine propagation, survivorship bias gibi dinamikler hata değil, istenen özelliklerdir; oyuncuya fırsat ve risk yaratırlar. Bir dinamik ancak **artifact** ise düzeltilir. Ayırt etme ölçütleri: (1) mikro-davranış gerçekçi mi; (2) büyüklük ve süre tarihsel olarak makul mü; (3) yapay bir sınıra (üst sınır, negatif fiyat, patlama) dayanıyor mu; (4) oyuncu okuyabiliyor ve karşı strateji geliştirebiliyor mu. | Kullanıcı (2026-10-23), [lessons](../process/lessons.md) |
| İ12 | **Davranış doğal olarak gelişmeli, tepeden ayarlanmamalı.** Her mekanizma hem tarihsel hem ekonomik olarak doğru olmalı. Bir parametre ya tarihsel / ampirik bir değere bağlanır, ya modelin kendi verisinden çıkar, ya da yerine fiziksel ve kurumsal bir mekanizma gelir. Geçici vekiller (ör. D5b3g real options bandı) açıkça "geçici" diye işaretlenir | Kullanıcı (2026-11-02), [14](../research/simulation/14-natural-entry-exit.md) |
| İ10 (aday) | **Fırsatlar sürtünmeden gelir, NPC aptallığından değil** (literatür: Grossman & Stiglitz 1980; simülasyonda D2-D3 ile yeniden üretildi). NPC'ler yerel olarak yetkin olmalı; fırsatları bilgi gecikmesi, sermaye ve kapasite kısıtı, risk çeşitliliği canlı tutmalı. D2: anlık bilgi + verimli NPC = fırsat yok (Bannerlord). | [D2](../experiments/D2.md) |
| İ9 (aday) | **Simetri ilkesi:** Bir fiyat kanalı bir yönde hızlı, öteki yönde yavaşsa fiyat zamanla kayar. Asimetriler bilinçli ve tarihsel gerekçeli olmalı. D1 ve D1f'deki dört ayrı hata (mandal, beklenti kovalama, kirlenen hafıza, roket ve tüy) bu ailedendi. | [D1f B7](../experiments/D1f.md) |

## 2. 🔵 Yönler

### Ekonomi çekirdeği
| # | Yön | Not |
|---|---|---|
| Y1 | **Katmanlı yapı:** dünya → kitle havuzları → liman pazarları → ajanlar → kurumlar → olaylar | 00-sentez §3 |
| Y2 | **Mekânsal fiyat farkları kendiliğinden oluşur;** ayrı bir model gerekmez. Arbitraj bandı sadece bir tasarım merceği ve doğrulama testi. | yorumlar, kullanıcı haklı |
| Y3 | **Rol ayrımı:** *Dükkâncı / piyasa yapıcı* (yerel, istikrarlı, perakendeci gibi kâr marjıyla çalışır) ile *tüccar* (gezgin, spekülatif, kâr peşinde) farklı ajan türleridir. **Rol listesi açık uçlu:** simüle ettikçe yeni roller keşfedilip eklenecek. | yorumlar; ayrıntı §4 |
| Y3b | **Dükkâncı fiyatı PI kuralıyla:** integral = stok/müşteri talebi (uzun dönem seviye), oransal = bugünkü kıtlık (anında tepki). Stokçu rolü (temelci, medyan "olağan fiyat", hasat haberi) mevsimsel ve kıtlık arbitrajını yapar. | [D1](../experiments/D1.md), [D1f](../experiments/D1f.md), [D1g](../experiments/D1g.md) |
| Y3c | **"Olağan fiyat" bilgisi aykırı yıllara dayanıklıdır** (yılların medyanı). Hem ajanlar hem bilgi modeli için. | D1g B4 |
| Y4 | **İkili ilişkiler** (ajan↔ajan) tutulur, fiyatı etkiler, pekiştirmeli öğrenmeyle evrilir | Kirman; yorumlar |
| Y5 | **Oyuncu için ikili pazarlık** sınırlı ve önemli durumlarda var | yorumlar |
| Y6 | Depolama ve spekülasyon kararı 01 §4'teki formülle (ek parametreler eklenebilir) | yorumlar |
| Y7 | Ajanlar beklenti türü ve kişilik parametreleri taşır; kesin liste sonra belirlenecek | yorumlar |
| Y8 | Zaman: günlük tick + olay kuyruğu | 00-sentez |

### Oyuncu, zaman ve finans
| # | Yön | Not |
|---|---|---|
| Y10 | **Senetler:** düşük getirili, risksize yakın ama riskli, pek tercih edilmeyen bir alternatif. Asıl caydırıcı **ömür**: zaman oyuncunun en kıt kaynağı. | S-005 |
| Y10b | **Getiri çerçevesi:** senet ≈ %4 = risksize yakın taban; baz ticaret = senet + risk primi (rekabetçi dengede ekstra kâr yok); iyi seçilmiş ticaret bazın üstünde, kötü seçilmiş altında. Oyuncu %50/yıl gibi uç getiriler elde edememeli. Bu denge **senet getirisine bağlı serbest giriş-çıkışla** sağlanır. **D3b'de doğrulandı:** orta hızlı girişte sektör getirisi %6-11; bilgili tüccar %13-17. Giriş hızı (lonca, imtiyaz gibi engeller) rant düzeyini belirler. | S-012, [D3b](../experiments/D3b.md) |
| Y11 | **Çalışma başlangıç yılı: 1560** (kesin değil; tarih okumalarından sonra) | S-001 |
| Y12 | **Deneyler Python ile** | S-010 |

### Fenomenler ve dinamikler (soft kararlar, kullanıcı onayı 2026-10-23)
| # | Yön | Not |
|---|---|---|
| Y13 | **Fenomenlerin büyüklüğü şimdi ayarlanmaz.** Pork cycle, cobweb gibi döngülerin genlik ve periyodu en sonda tarihsel veriyle (ML kalibrasyonu) ayarlanır. Şimdilik yalnızca yapay sınırlara dayanmamalı ve patlamamalılar. | İ11 |
| Y14 | **Fenomenler oyuncu için okunabilir olmalı.** Döngüleri ve herding'i görünür kılan bilgiler (limandaki gemi sayıları, kimin yüklediği, giriş-çıkışlar, haberlerin yaşı) bir tasarım gereksinimi. Karşı döngüsel strateji oyunun parçası. | İ11, Y9 |
| Y15 | **NPC yanılgıları gerçekçidir ve korunur** (survivorship bias ile karar verme, herding). **Bizim ölçümlerimiz ise yanılgısız** (sistem düzeyi, muhasebe defteri). | D3b |
| Y16 | **Yeni bir dinamik görülünce önce sınıflandırılır** (fenomen mi, artifact mı; İ11'in dört ölçütü), sonra müdahale edilir. | [deney stratejisi](../experiments/README.md) |

### Bilgi
| # | Yön | Not |
|---|---|---|
| Y9 | Fiyat bilgisi **olasılık dağılımı** olarak tutulur (yaş, oynaklık ve kaynağa göre genişler) ve eskidikçe olağan fiyata (medyan) döner; oyuncu ve ajanlar aynı veriyi kullanır. **D3'te en iyi aday oldu.** | [information-model](information-model.md), [D3](../experiments/D3.md) |

## 3. 🟡 Adaylar

| # | Aday | Değerlendirme | Ne gerekiyor |
|---|---|---|---|
| A1 | **Dağılımın renk tonlarıyla gösterimi;** zor modda kapalı | Çok güçlü; mekanik, anlatım ve zorluk aynı anda | Gösterim tasarımı; [information-model](information-model.md) |
| A2 | **Farklı tarihli ve kaynaklı bilgilerin birleşmesi** | Doğru yöntem hassasiyet ağırlıklı birleştirme; ilk sürüm basit tutulabilir | [information-model §3](information-model.md) |
| A3 | **Zorluk moduna göre ajan hesaplarına gürültü** | İyi bir düğme. Gürültü **kararlara değil algıya** (inançlara) eklenmeli: NPC saçma davranmasın, "yanlış bilsin". Seed'li olduğu için determinizmi bozmaz. | Gürültü nereye eklenecek? §5 |
| A4 | **Dinamik kurumlar, düzey 1:** politika içi tepkisel kurallar ("fiyat X'i aşarsa ihracatı yasakla") | Ucuz; ilk sürüme girebilir | §6 |
| A6 ✅ D4 | **Mal türüne göre talep davranışı:** zorunlu mallar (esneklik ≈ −0.2 ile −0.4, bir hayatta kalma tabanı var), lüks mallar (esneklik < −1). Spec §2.3'te tabloda var; D1 yalnızca buğdayı test etti. | Kullanıcı (D1 sonrası) | Çok mallı deney |
| A7 ✅ D4 (LES + CES) | **Ortak bütçe:** Bir sınıfın gelirini mallar paylaşır. Ekmek pahalanınca ipek ve kumaş talebi düşer (kıtlık lüksü vurur). | Tarihsel olarak gerçekçi; mallar arası bağ kurar | Çok mallı deney |
| A8 | **Köylünün kendi tüketimi:** Köylü önce kendi ihtiyacını ve tohumluğunu ayırır, kalanı satar. Kötü hasatta **pazara gelen miktar hasattan orantısız düşer.** Bu, King-Davenant dışbükeyliğinin tarihsel açıklamalarından biri. | Kullanıcı ("köylü yemek zorunda") | D1f'e eklenebilir |
| A9 | **Kapalı para devresi:** Köylünün kazandığı para kente geri döner (kumaş, tuz, vergi). Dışarıyla para alışverişi açık tanımlanır: Batı'dan gümüş girişi, Doğu'ya gümüş çıkışı. Kullanıcı: Amerikan gümüşü gibi büyük para arzı değişimleri **tarihsel olay** olarak modellenir (enflasyonun kaynağı para arzı artışı). Şu an kent geliri dışsal bir musluk, köylü geliri dışsal bir yutak. | Kullanıcı (madenî para sorusu) | Para tasarımı ertelendi ama devre kapanışı çok mallı deneylerle gelmeli |
| A5 | **Ajan profillerinin her oyunda yeniden dağıtılması;** bölge karakteri ortalama olarak korunur | Tekrar oynanabilirlik ile gerçekçilik dengesi | §7 |
| A10 | **Beklenti = heuristic switching (HSM) + bilgi temelli temel kural.** Her tüccar birkaç kural kullanır: bilgi temelli temel (hedefte kaç günlük arz var → ima edilen fiyat), çapalama (C4), trend. Kural ağırlıkları tüccarın kendi tahmin başarısıyla güncellenir. Kullanıcı ilkesi: piyasa teknik analize göre çalışmamalı. Literatür: tüccar ticareti negatif geri beslemeli, trend kuralları kaybeder (Hommes 2011). | **K** ilke (beklenti yönetir, TA yönetmemeli); C tasarım; L (Anufriev & Hommes 2012) | S-014; [07-expectation-formation](../research/simulation/07-expectation-formation.md); deney: kural paylarının zamanla ölçülmesi |
| A11 | **Fırsata bağlı giriş + sermaye havuzu + kararlı başlangıç.** Limanların yatırılabilir sermaye havuzu (colleganza/commenda). Giriş akışı = havuz × kamuya açık fırsat (price current'tan görülen fazla getiri). Başlangıç filosu bir ön koşuyla kararlı duruma yakın kurulur. | **K** fikir (genel bilinen fırsat varsa girilir; halk sermayesi; kararlı başlangıç); C tasarım; L (colleganza: Lane 1973, González de Lara 2008 ⚠️) | S-012; giriş dalgası riski (entry cobweb) test edilmeli |
| A12 | **Hibrit tüccar finansmanı.** (a) Likidite için vadeli borç: faiz = senet + kredi primi, kaldıraç sınırı, tam sorumluluk, temerrüt kaydı. (b) Colleganza yalnızca seçkin tüccara ya da gözetimli rotaya. (c) Havuzun senet / borç / colleganza paylaşımı gerçekleşen getiriye göre öğrenilir. | **K** fikir (tersine senet; colleganza seçkinlere; yatırımcı öğrenmesi, liman getirisine bağlı). Kullanıcı notu: emin olmadan önerildi, kesin değil. C tasarım ayrıntıları; L (Townsend 1979; González de Lara 2000; Williamson 2011; Stiglitz & Weiss 1981) | S-015 → **K-022** (kullanıcı onayı; uygulama D5b3c). Sorumluluk kuralı ve kaldıraç sınırı olmadan kötü tüccar borca hevesli olur |
| A13 | **Sefer bazlı alacaklı (Rialto bilgi merkezi).** Faiz, alacaklının sefer sonucu beklentisinden (temerrüt olasılığı) çıkar. Bilgisi: kendisine yapılan başvurular (rota, mal, miktar, gün) + kamuya açık bilgi (price current, limanda görünen yüklemeler, liman konuşması) + kendi borç defteri. Getiri/risk oranı yetersiz seferde faiz yükselir ya da borç verilmez (credit rationing) | **K** fikir (sefere göre faiz; tüccardan fazla bilen kurum; girdiler); C mekanik; L (Diamond 1984; Einav ve ark. 2013; Rialto, Antwerp simsarları) | S-015 → **K-023** (uygulama D5b3d) |
| A14 | **Giriş = meslek seçimi + gemi sabit maliyeti.** Sonlu potansiyel tüccar nüfusu (servet, risk tutumu). Yeni bir geminin beklenen yıllık getirisi (batma riskiyle) senetten iyiyse girilir. Gemi başına sabit maliyet boş kapasiteyi pahalı kılar | C öneri; L (Kihlstrom & Laffont 1979; Bresnahan & Reiss 1991; Mankiw & Whinston 1986) | S-017 → **K-024**: öz sermayede batma riski + gemi masrafı; **sonlu havuz reddedildi** (uygulama D5b3d) |
| A15 | **Rota seçiminde dağılım (K-026).** Sıra: (E1) motor artifact'ları (seviye 0 körlüğü, imitation); (E2) muhabir ağı: ağdaki limanda taze bilgi ve düşük işlem maliyeti, dışında komisyon, ağ deneyimle genişler; (E3) çok gemili ev seferlerini çeşitlendirir; (E4) D5b4 tahmin kuralı çeşitliliği; son çare logit gürültü. Rakipler arası bilgi paylaşımı **reddedildi** | **K** teşhis, limana bağlı tüccar, çok gemili ev, gürültü son çare, ağ paylaşımı reddi; C yumuşak ağ biçimi, ablation, turnuvayı sona alma; L (Arthur 1994; McKelvey & Palfrey 1995; Trivellato; Datini; Roy 1951) | S-018; plan [D5b3e](../experiments/D5b3e.md) |
| A16 | **Ticaret yapısı: liman hiyerarşisi + gemi tipleri.** Liman üç özellik taşır (fiziksel liman, pazar, kurum); büyük/orta/küçük bunların özeti. En az iki gemi tipi (büyük: ton başına ucuz, derin liman ve hacim ister; küçük: her iskeleye girer, az sermaye). Küçük-yerel tüccar kesimi ve fiyat katmanları kendiliğinden oluşmalı | **K** liman çeşitliliği önce, büyük-orta-küçük, küçük-yerel tüccar, sipariş taşıyan büyük gemi, tam harita (K-034, K-035); **C** üç özellik, gemi boyu trade-off'u, marjın engelden gelmesi; **L** (Taaffe-Morrill-Gould 1963; Fujita & Mori 1996; Christaller; Horden & Purcell 2000) | S-023; [trade-structure](trade-structure.md) yol haritası M0-M6 |
| A17 | **Kârlılık ayar değil, doğrulama ölçütü.** Dışsal boyutlar (gemi ömrü, kayıp tehlikesi, liman ve deniz süresi) tarihten alınır; sefer sıklığı, sefer başına getiri ve kârlılık modelde oluşur ve tarihle karşılaştırılır. Kârlılık düzeyini giriş tarafı (faiz, risk tutumu, engeller) belirler | **K** beş boyut; **C** dışsal/içsel ayrımı, girişin rolü (kullanıcı kabul etti); **L** rekabetçi denge | [trade-structure §2](trade-structure.md) |
| A18 | **Oynanışta karar sıklığı gemi seferinden değil gönderiden ve portföyden gelir.** Erken oyun: küçük gemi, kısa rota. Geç oyun: pay (carati), ortaklık, fattore, navlun, sigorta. Geç oyunun yüksek kazancı engellerden doğan ranttan | **K** ilerleme fikri (kısa → uzun, büyük hacim); **C** navlun ayrımı, sedentary merchant, rant kaynağı; **L** (Gras; de Roover ⚠️) | [trade-structure §3](trade-structure.md) |
| A19 | **Bilgi işleme yetenekleri, tek bir yetenek seviyesi yerine.** Tüccar yeni bilgileri ve sınırları (kalkıştaki arz, kıtlık haberi, kalabalık) kendi yeteneğine göre farklı değerlendirir. Yetenek tek bir eksen değil: birkaç bilgi işleme yöntemi için ayrı yetenek kategorileri (ör. arz okuma, haber süzme, kalabalık tahmini, fiyat beklentisi). Her tüccar bazı işlerde daha iyi olur; çeşitlilik buradan gelir | **K** fikir (2026-11-10; "daha derin değerlendirip test edeceğiz, şimdilik not"). Mevcut tek eksenli `level` ve `informed` ile ilişkisi incelenecek; A10 (HSM), A15 (rota dağılımı) ile bağlantılı | S-024 |

## 4. Dükkâncılar: tekel ve açgözlülük sorunu

> **Güncelleme (2026-10-23, K-016):** Toptan pazarlı dünyada perakende artık rekabetçi: dükkâncı marjını müşteri payına göre seçer (Lerner), müşteriler pahalı dükkânı terk eder, giriş-çıkış ve geçim gideri dükkân sayısını belirler. Aşağıdaki "maliyet artı sabit marj, fiyat savaşı yok" önerisi D1-D5 serisinde kullanıldı; D5a2'de rekabetin yokluğunun yüksek perakende-toptan farkı ve kıtlıkta boş raf ürettiği görüldü. Tekel endişesi geçerli kalıyor: kurumsal tekeller açıkça tanımlanır; perakendede rant oluşursa devlet müdahalesi eventi. Bkz. [D5a2](../experiments/D5a2.md).

Kullanıcının endişesi: Piyasa yapıcı açgözlü bir ajan olur ve tekel kurarsa oyunu kırar; rekabet olursa sistem karmaşıklaşır.

**Değerlendirmem: Katılıyorum. Dükkâncılar optimize eden değil, kural izleyen ajanlar olmalı.** Tarihsel olarak da öyleydi:
- Perakende ve yerel ticaret loncalarca düzenleniyordu; "adil fiyat" normları ve geleneksel kâr marjları vardı.
- Venedik'te temel gıdaya resmî fiyat tavanları (calmieri) ve denetim kurumları vardı ⚠️ (doğrulanacak).

**Öneri: maliyet artı marj (cost-plus) dükkâncısı.**
```
satış_fiyatı = ortalama_alış_maliyeti × (1 + marj) × stok_ayarı
alış_fiyatı  = beklenen_satış_fiyatı × (1 − marj) × stok_ayarı
marj         = lonca veya gelenek bandı içinde (ör. %8-15) ve kişiliğe göre küçük oynama
stok_ayarı   = stok fazlaysa biraz düşür, azsa biraz artır (yumuşak)
```
- Dükkâncı **spekülasyon yapmaz**, başka limana mal taşımaz. Bu işi tüccarlar yapar.
- Sermayesi ve depo kapasitesi sınırlıdır; dolunca alımı keser. Bu, "piyasayı boğma" sınırını doğal olarak oluşturur.
- **Tekel önlemi:** Her limanda birden fazla dükkâncı olur. Oyuncu her zaman başka tüccarlara, kitle havuzuna veya kamu açık artırmasına da satabilir.
- **Tekel bir kurumsal durum olarak vardır, kendiliğinden doğmaz:** Venedik tuz tekeli, Sakız'da Ceneviz sakız tekeli gibi. Bunlar açıkça tanımlanır ve oyuncuya görünür.
- **Karmaşıklık kontrolü:** Dükkâncılar arası rekabet sadece "fiyatın bandı aşmaması" düzeyinde. Müşteri, ilişkisi iyi olan veya fiyatı biraz daha iyi olan dükkâncıyı seçer (Kirman). Gerçek bir fiyat savaşı yok.

**Sonuç:** İstikrar dükkâncılardan, oynaklık ve fırsat ise tüccarlardan gelir. Bu ayrım okunabilirliği de artırır: oyuncu "yerel fiyat" ile "fırsat" kavramlarını ayırt edebilir.

## 5. Zorluk gürültüsü nereye?

| Seçenek | Etki | Değerlendirme |
|---|---|---|
| Kararlara gürültü | NPC bazen mantıksız seçim yapar | ❌ İnandırıcılığı bozar |
| **İnançlara/algıya gürültü** | NPC bazen yanlış bilir veya yanlış yorumlar | ✅ Gerçekçi; bilgi sistemiyle uyumlu |
| Bilgi hızına gecikme | NPC haberi geç alır | ✅ Temiz bir düğme |
| NPC sayısı ve sermayesi | Rekabet yoğunluğu | ✅ Klasik |

Not: NPC'lere daha fazla gürültü daha fazla fiyat dağınıklığı demek, yani daha fazla fırsat ve daha kolay oyun. Bu tutarlı bir zorluk ilişkisi.

## 6. Dinamik kurumlar: önerilen yapı (sonra uygulanmak üzere)

**İki düzey ayrılmalı:**
1. **Politika içi tepkisel kurallar (ucuz, ilk sürümde olabilir):** "Şehirde tahıl fiyatı X'i aşarsa ihracatı yasakla, ambardan sat." Kurum davranışı politikanın sınırları içinde zaten dinamik görünür.
2. **Politika değişimi (pahalı, sonra):** Kurumun bağlı ajanlarından gelen baskı bir eşiği aşınca politikanın kendisi değişir.

**Politika değişimi mekanizması (taslak):**
```
baskı = Σ (ajanın etkisi × ajanın memnuniyetsizliği)   # etki: zenginlik, sınıf, makam
eğer baskı > eşik (bir süre boyunca) → politika değişir
```
- **Etki ağırlıklı, çoğunluk değil:** Kullanıcının dediği gibi demokrasi o dönemde pek işlemez. Venedik'te karar patrizilerin, loncada ustalarındır.
- **Histerezis:** Değiştirme eşiği ile geri değiştirme eşiği farklı olmalı; aksi halde politika sürekli gidip gelir.
- **Gecikme:** Değişim bir süre baskı sürdükten sonra olur.
- **Tarihsel olaylar** politikaları doğrudan da değiştirebilir (savaş ilanı, ambargo).
- **Oyuncu etkisi:** Oyuncu etkisini (zenginlik, itibar, rüşvet) kullanarak baskıya katılabilir. Bu bir özellik, ama pahalı ve riskli olmalı; yoksa istismar edilir.

**Şimdilik yapılacak tek şey:** Politikaları kodda sabit değil, **veri olarak** (kurumun parametreleri) tasarlamak. Böylece ileride dinamik hale getirmek kolay olur.

## 7. Ajan profillerinin dağılımı

Kullanıcının dengesi: Sabit dağılım istismar edilir, ama bölge karakteri gerçekçi ve eğlenceli.

**Öneri: bölge profili = dağılım, ajan = o dağılımdan yapılan çekiliş.**
- Ragusa'nın armatörleri **ortalamada** temkinli ve tarafsızlık odaklı; ama her oyunda Ragusa'da cesur bir istisna da çıkabilir.
- Bölge ortalamaları tarihsel karaktere göre ayarlanır, her oyunda biraz kaydırılır.
- Hangi NPC hanelerinin var olduğu, kişilikleri ve sermayeleri her oyunda yeniden çekilir.
- **İstismara karşı:** Oyuncu bölge ortalamasını bilse bile, karşısındaki **bireyi** ancak ilişki kurarak (Y4) öğrenir. Bölge bilgisi faydalıdır ama yeterli değildir.

## 8. ⚪ Ertelenenler

| Konu | Neden | Not |
|---|---|---|
| Para, enflasyon, fiyat devrimi | Kullanıcı: sonranın konusu | **Tek istisna:** Para ve mal muhasebesi (kaynak-yutak) ilk günden kodda olmalı. Bu bir özellik değil, bir doğruluk kontrolü. |
| Topluluk itibarı ve sözleşme uygulaması (Greif) | Kullanıcı: sonranın konusu | İkili ilişkiler (Y4) şimdi; topluluk itibarı sonra |
| Kişilik parametrelerinin kesin listesi | Kullanıcı: sonra kesinleşir | Y7 |
| Akıllı kitle havuzları | Kullanıcı: zamanı gelince | İlk sürümde basit havuz |
| Dinamik politika değişimi (düzey 2) | Kurması zor; kullanıcı onayıyla fikir olarak saklandı | §6: politikalar şimdiden veri olarak tasarlanır. Uygulanırken sıfırdan icat edilmeyecek; kurumsal değişim üzerine akademik modeller taranıp uyarlanacak (araştırma notu: siyasal ekonomi ajan modelleri, kurumsal değişim literatürü) |
| **Müşterinin fiyat düşerkenki arama davranışı** (rockets and feathers) | Kullanıcı (2026-10-23): şimdi modellenmesin, akılda kalsın | Rekabetçi perakendede (K-016) aktarım simetrik çıktı ([D5a2](../experiments/D5a2.md) B5). Literatürdeki neden: fiyat yükselince tüketici daha çok arar, düşerken aramaz; geçmiş fiyatları referans alır (Tappata 2009; Yang & Ye 2008; Lewis 2011). Uygulanacaksa doğru yer: logit β'yı müşterinin fiyat beklentisine/referans fiyatına bağlamak. El ile asimetri eklenmez. S-013. |
| **Araç: kârlı hattın rantına devletin el koyması** (muda / incanto: kapasite sınırı + açık artırma; Stöckly 1995) | Kullanıcı (2026-10-26, K-024): şimdi kurulmayacak; çok kârlı bir rota oyun bug'ı gibi sorun çıkarırsa uygulanır | [09](../research/simulation/09-market-structure-entry.md) |
| **Ayrıcalıklar** (vatandaşlık, lisans) | Kullanıcı (K-024): şimdi değil | 09 |
| **İtibar = disiplin** (Diamond 1989; ucuz kredi kaybedilecek bir varlık) | Kullanıcı (2026-10-26): ilgi çekici, şimdilik rafa; önce sefere göre faiz | S-015 |
| **Dinamik senet getirisi** (S-016) | Kullanıcı (2026-10-26): akılda kalsın, yöntem düşünülmedi | Adaylar: devletin borç ihtiyacı, sermaye bolluğu, kriz primi |
| Batan gemi riski ve gerçek deniz ödüncü (K-022) | Kullanıcı: istenen, ama D5b3c bitince | Sea loan: gemi batarsa borç düşer |
| Dağılım biçimi ve parametre ince ayarı | Kullanıcı: ince ayar sonra | Log-normal önerisi not edildi ([information-model §1](information-model.md)); şimdilik "olasılık dağılımı" kavramı yeterli |
| Gemi alma (yatırım aracı): gemi maliyeti, işletme gideri, amortisman | **K** (K-027) | Kullanıcı önce düşünecek |

## 9. Kaba yol haritası (çerçeve için)

```
Faz 0  Araştırma ✅ (1. ve 2. tur)
Faz 1  Çerçeve ✅ (v0; canlı doküman olarak güncellenmeye devam eder)
Faz 2  Simülasyon spesifikasyonu (ODD formatında, design/simulation-spec.md) ← şu an buradayız (v0 yazıldı)
       - İlk dilim: S-006
Faz 3  Mini deneyler (D1-D5, 00-sentez §8): Python, oyuncusuz
Faz 4  Çekirdek simülasyon + desen testleri (06)
Faz 5  Metin tabanlı oynanış
```

