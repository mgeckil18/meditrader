# Öğrenilenler Kataloğu
> Son güncelleme: 2026-10-23

## A. Dinamik kalıplar: fenomen mi, artifact mı?

Deneylerde görülen her dinamik iki sınıftan birine girer (bkz. framework İ11):
- **Fenomen:** Gerçek dünyada da görülen, gerçekçi mikro-davranıştan doğan bir dinamik. **Korunur.** Sadece büyüklüğü ve okunabilirliği izlenir.
- **Artifact:** Modelin gerçekçi olmayan bir varsayımından doğan dinamik. **Düzeltilir.**

| Kalıp | Ne olur | Nerede | Sınıf | Gerekçe ve karar |
|---|---|---|---|---|
| **Asymmetric ratchet** | Fiyat bir yönde hızlı, öteki yönde yavaş tepki verir; her şok fiyatı bir basamak kilitler | D1.1 | Artifact | Stok 0'a inebiliyor ama hedefin 1,5 katına çıkamıyordu. Gerçek dükkâncı böyle davranmaz → simetrik (log) tepki |
| **Expectation chasing / bubble** | Beklenti fiyatı izler, fiyat beklentiyi izler | D1.2 | **Fenomen** (sönümlü hali) | Balonlar gerçektir. v1'de patlama yaratan, köylülerin *hızlı ve çapasız* uyarlamasıydı. Sınırlı ve çapalı hali korunabilir. |
| **Liquidity spiral** | Fiyat ↑ → alıcının nakdi yetmez → stok ↓ → fiyat ↑ | D1.4 | Artifact (bu haliyle) | Finansta fire sale olarak gerçek, ama D1'de dükkâncının yanlış sinyale bakmasından doğuyordu → stock/demand sinyali |
| **Contaminated memory / anchoring** | Uç bir dönem "normal" hafızayı bozar | D1f.5 | Fenomen, ama büyüklüğü artifact | Krizden sonra "yeni normal" algısı gerçek; kıtlığın 2 yıl yapay taban olarak sürmesi abartılı → medyan hafıza |
| **Integral lag** | Fiyat kıtlığın birikimini izler, mevsimsel dalga çeyrek dalga gecikir | D1g.2 | Artifact | Gerçek fiyatın seviyesi mevcut kıtlığa bağlıdır → PI kuralı |
| **Rockets and feathers** | Hızlı yukarı, yavaş aşağı fiyat ayarı | D1f.9 | Fenomen (akaryakıtta belgeli); D1f'deki teşhis kısmen yanlıştı | Bilinçli ve gerekçeli olduğu sürece kabul |
| **Herding** | Herkes aynı sinyali aynı anda görüp aynı yöne gider | D3.2, D3.5 | **Fenomen** | Gerçek. D3.2'deki *aşırı* hali (herkes zararına alıyor) artifact'tı. |
| **Cobweb** | Gecikmeli bilgi ve toplu tepki → salınım | D3.5 | **Fenomen** | Klasik ekonomi teoremi; tarım ve ulaşımda belgeli. Korunur, sönümlü olmalı. |
| **Pork cycle (hog cycle)** | Gecikmeli kârlılık sinyaliyle toplu giriş → aşırı kapasite → toplu çıkış | D3b.1 | **Fenomen** | Hanau (1928) ile belgeli; gemicilik ve navlun piyasalarında da görülür. D3b'de orantılı girişin reddedilme nedeni döngünün kendisi değil, mikro-davranışın gerçekçi olmaması ve genliğin yapay üst sınıra (120) dayanmasıydı. Havuz girişi de ılımlı döngüler üretiyor ve bu istenen şey. |
| **Over-caution** | Kural riskten kaçınırken piyasayı aç bırakır | D2.4, D3.1 | Artifact | Gerçekçi olmayan getiri eşiği ve kargo sayımı |
| **Efficient-market opportunity death (Bannerlord)** | Anlık bilgide arbitraj fırsatları anında kapanır | D2.2 | Fenomen, ama oyun için yanlış dünya | Gerçek dünyada anlık bilgi yoktu → sürtünme eklendi (D3) |
| **Famine propagation** | Bir limandaki kıtlık ihracatla diğerine yayılır | D2.5, D3 B6 | **Fenomen** | Gerçek; tarihsel tepkisi ihracat yasaklarıydı (kurum kuralı gerekir) |
| **Labrousse etkisi** (agrarian → industrial crisis) | Tahıl kıtlığı bütçeyi daraltır, lüks ve mamul talebi çöker | D4.2, D4.3 | **Fenomen** | Korunur; homojen kentte büyüklüğü aşırı (lüks talebi sıfır) → kent sınıfları |
| **Sürekli üretimde sahte mevsimsellik** | Hasadı olmayan bir mal, "hasada kalan gün" mantığıyla yıllık salınım üretir | D4b.1-2 | **Artifact** | Sürekli üretimde sabit ufuklu satış hızı |
| **Kıtlıkta sınıflar arası akış** | Yoksul talebi çöker, fiyat düşer, zengin ucuz malı toplar | D4b.4 | **Fenomen** | Korunur; oyuncu için okunabilir olmalı |
| **Aracı kapasite uyumsuzluğu** | Yerel perakendeye göre boyutlu dükkânlar ihracat ve ithalat hacmini taşıyamaz; mal üreticide birikir, ithalatçıda kıtlık olur | D5.1, D5.6, D5.9 | **Artifact** (eksik toptan katman) | Toptan ticaret katmanı tasarımı |
| **Likidite tuzağı** | Nakdi ve malı tükenen aracı mal alamaz, satamaz, toparlanamaz | D5.8 | Fenomen (gerçek) ama kalıcılığı artifact | Aracı giriş-çıkışı, kredi |
| **En kârlı nişe herding** | Çok mallı dünyada tüccarlar aynı değerli nişe koşar, hacimli ama gerekli mallar taşınmaz | D5.5 | Fenomen, büyüklüğü artifact | Rakip farkındalığı (miktar paylaşımı) |
| **Survivorship bias** | Hayatta kalanların getirisi gerçek ortalamadan yüksek görünür | D3b.5 | **Fenomen** (ajanların algısında) ve ölçüm tuzağı (bizim analizimizde) | NPC'lerin bu yanılgıyla karar vermesi gerçekçi; bizim ölçümlerimiz ise defterden yapılmalı |
| **Yapışkan perakende = örtük narh** | Perakende fiyatı yavaş hareket edince kıtlık fiyatla değil boş rafla paylaştırılır | D5a2.6 | **Fenomen** | Weitzman (1977), Barzel (1974); tarihsel karşılığı narh. Korunur; hangi rejimin geçerli olduğunu kurumlar belirler |
| **Çapasız teklif** | Ajanın teklifi kendi geçmiş teklifinden (ya da ondan türeyen maliyetten) türerse, kıtlıkta fiyat kendini kovalar | D5a2.2-3 | **Artifact** | Çapa dışarıdaki bir gözlemden (müşteri talebi) gelmeli → türetilmiş talep |
| **Kendini doğrulayan stok sinyali** | Yüksek fiyat → az satış → az stok hedefi → stok/talep "normal" → fiyat yüksek kalır | D5a2.1 | **Artifact** | Fiyatı indirecek rakip yoktu → rekabetçi perakende |
| **Donmuş fiyat / ölü pazar** | İşlem olmayan pazarın açık fiyatı son işlemde donar; ucuz görünen pazara kimse mal getirmez | D5a3.1 | **Artifact** | Açık teklif + tâtonnement (K-017) |
| **İnce pazar tuzağı** | Az bulunan malın küçük pazarda fiyatı yüksek görünür; tüccarlar yığılır, yıllarca satamaz | D5b.1, D5b.4 | Fenomen (El Farol; derinlik); kalıcılığı artifact (satış kararı fiyata bakıyor, satış hızına değil) | Rakip bilgisi (K-014) + satış kararı yuvası |

## B. Tasarım ilkeleri (deneylerden çıkan)

**Not (atıf dürüstlüğü):** "Literatür" sütunu doluysa, ilke ekonomide zaten bilinen bir sonuçtur ve simülasyonumuz onu **yeniden üretmiştir**; bizim keşfimiz değildir. Boşsa, modele ya da oyun tasarımına özgü bir derstir.

| İlke | Kanıt (bizim deney) | Literatür (zaten bilinen) |
|---|---|---|
| Fiyat sinyalinin **anlamı** (neye baktığı) katsayılardan önemlidir | D1.5 | Kısmen: piyasa kurumunun önemi (Gode & Sunder 1993; Smith 1962) |
| Ani tepki için üç parça gerekir: beklenti (haber) → eylem (stoklama) → aktarım (yerine koyma maliyeti) | D1f.3 | Depolama ve zamanlar arası arbitraj (Williams & Wright 1991; Deaton & Laroque 1992); replacement cost pricing |
| Tarihsel davranış eklemek formül ayarlamaktan etkilidir | D1f.7, D1g.5 | — (modelleme dersi) |
| Fiyatın seviyesi mevcut kıtlığa bağlı olmalı (PI) | D1g.3 | Kontrol teorisi (PI/PID); Walras tâtonnement'ın PID genellemesi (Kumar & Shubik 2004); depolama modeli |
| Her fiyat kanalı simetrik olmalı veya asimetrisi bilinçli olmalı (İ9) | D1-D1g | — (modelleme dersi) |
| **Fırsatlar sürtünmeden gelir** (İ10) | D2, D3 | **Grossman & Stiglitz (1980):** bilgi edinmek maliyetliyse piyasa tam verimli olamaz; Stigler (1961) arama maliyeti ve fiyat dağınıklığı |
| Bilginin ölçülebilir bir ekonomik değeri vardır | D3.4 | Stigler (1961); Grossman & Stiglitz (1980) |
| Tek fiyat yasası, taşıma maliyeti bandında | D2.2 | Mekânsal fiyat dengesi (Samuelson 1952; Takayama & Judge) |
| "Olağan fiyat" bilgisi aykırı yıllara dayanıklı olmalı (medyan) | D1g.8, D3.6 | Robust istatistik (genel bilgi); anchoring |
| Kıtlıkta ihracat kaynağı boşaltır → tepkisel kurumsal kurallar gerekli | D2.5, D3 B6 | Tarihsel: Osmanlı ve Sicilya ihracat yasakları; famine propagation literatürü |
| **Giriş engelleri rant yaratır;** serbest girişte getiri senet + risk primine yaklaşır | D3b.5 | **Endüstriyel organizasyonun temel sonucu:** Bain (1956), Stigler (1968); rekabetçi denge ve sıfır ekonomik kâr |
| Rekabet sıradan kârı eritir, bilgi avantajını eritmez | D3b.6 | Grossman & Stiglitz (1980): bilgili ajanın getirisi bilgi maliyetini karşılar |
| Mallar bütçe yoluyla bağlıdır (income effect) | D4.3 | Slutsky ayrışması; LES (Stone 1954); Labrousse |
| Kıtlıkta mal yoksuldan zengine akar | D4b.4 | Gelir dağılımı ve kıtlık (Sen 1981, entitlement yaklaşımı ⚠️) |
| Ortak hammadde fiyat şoklarını ürünler arasında aktarır; girdi payı yüksek ürün daha çok etkilenir | D4c.1, D4c.3 | Leontief girdi-çıktı analizi |
| **Çarpan etkileri sektörün ekonomideki ağırlığına bağlıdır;** yalnızca yerel tüketime üreten bir sektörde gelir çarpanı zayıf kalır | D4c.4 | Keynesyen çarpan / export base teorisi (North 1955 ⚠️); modele özgü sonuç: kapalı tek kent bunu üretemez |
| Perakende marjı piyasa yapısından çıkar: rakip sayısı ve müşterinin fiyat duyarlılığı; giriş marjı alt sınıra indirir ama sıfırlamaz | D5a2.5 | **Lerner (1934); logit oligopol (Anderson, de Palma & Thisse 1992); Chamberlin (1933)**, arama sürtünmesi (Stigler 1961; Diamond 1971) |
| Kıtlık ya fiyatla ya kuyrukla paylaştırılır | D5a2.6 | **Weitzman (1977); Barzel (1974)** |
| Sabit gider, serbest girişte firma sayısını belirler: büyük pazar çok satıcı ve düşük marj, küçük pazar az satıcı ve yüksek marj | D5a2.12 | **Chamberlin (1933); Mankiw & Whinston (1986)** |
| Talep arzı aşınca fiyat yükselmeli; arz hiç yoksa bu süreç ancak alıcıların ödeme gücüyle sınırlanır | D5a3 | **Walras (1874) tâtonnement; Hayek (1945)** |
| Kalabalığı hesaba katan ajanlar El Farol herding'ini tamponlar; düşük düzeyli, taklitçi ve aşırı güvenli ajanlar daha az kazanır | D5b.3 | **Arthur (1994); Challet & Zhang (1997); Camerer, Ho & Chong (2004); Barber & Odean (2000)** |
| Aynı karar kuralına sahip ajanlar, bilgi farklı zamanlarda ulaşırsa farklı kararlar verir; çeşitliliği bilgi dağınıklığı da sağlayabilir | D5b B2 | Kısmen modele özgü (bizim bilgi modelimiz); heterojen inançlar literatürüyle uyumlu |
| Rockets and feathers için maliyet aktarımı yetmez; müşterinin arama davranışı fiyatın yönüne bağlı olmalı | D5a2.7 | Tappata (2009); Yang & Ye (2008); Lewis (2011) (bizde çıkmaması bu literatürle tutarlı) |

## C. Yöntem dersleri

| Ders | Nereden |
|---|---|
| Toplu metrikler **neyin** yanlış olduğunu söyler, **nedenini** söylemez → gün gün iz kaydı ve ablasyon şart | D1g.1, D1g.7 |
| Hipotezler sık yanlış çıkar; ölçmeden düzeltme yapma | D1g.1, D1g.7, D3.1 |
| Başarıyı nakitle değil net servetle ölç | D1f.4 |
| **Hayatta kalanlar yanılgısı:** getiriyi sistem düzeyinde, muhasebe defterinden ölç; listeden çıkan ajanların akışları kaybolmasın | D3b.4, D3b.5 |
| İşlemsiz ilan fiyatı yanıltıcıdır; gerçekleşen işlem fiyatını da izle | D1.9 |
| Bu aşamada ince ayar yapma; yapıyı bul, ayar en sonda (ML) | D1g.11, deney stratejisi |
| Her deneyde tek yuva değiştir; diğerlerini sabit tut | D3 (rakip farkındalığı ayrıldı) |
| Yeni kod eski deneylerin sonuçlarını değiştirmemeli; her seferinde kontrol et | D1f, D1g, D2 |
| **Konfigürasyon nesneleri kopyalanır, değiştirilmez.** Determinizm testi bu hatayı yakalamaz (aynı sıra, aynı yanlış sonuç); beklenen bir sonucun tekrar üretilmesi yakalar. | D4b.3 |
| **Birden çok el müdahalesi gerekiyorsa eksik bir kurum ara.** D5'teki dört yama, tek bir eksik kurumun (toptan pazar) belirtileriydi; kurum eklenince hepsi gereksizleşti. | D5a |
| **Bir el kuralı bir fenomenin sonucunu taklit ediyorsa, o fenomeni üreten mekanizmayı ara.** D5a'daki iki yönlü çekiş rekabetin sonucunu taklit ediyordu; asimetrik fenomenleri (rockets and feathers) silebilir, gerekçesizdi. | D5a2 (kullanıcı itirazı) |
| **Bir ajanın teklifi kendi geçmişine göreliyse çapası yoktur.** Çapa dış bir gözlemden gelmeli (müşteri talebi, açık fiyat). | D5a2.2-3 |
| **Getiriyi işletme kârından ölç.** Özsermaye değişimi stok değer artışını kâr sayar; fiyat şişerken zarar eden işletme kârlı görünür ve giriş durmaz. | D5a2.10 |
| **Yokluğu ayrıca ölç.** Fiyat ölçütleri yalnızca işlem olan günlerden hesaplanırsa malın olmadığı günler görünmez (D5a'da Venedik yağı günlerin üçte birinde yoktu, rapor bunu göstermedi). | D5a2.13 |
| **İşlem yokken son işlem fiyatı bilgi değildir.** Mal tükendiği için işlem olmuyorsa son işlem büyük ihtimalle bir bolluk gününden kalmadır; bu sinyal ölü pazarı ölü tutar. Yokluğun da bir fiyat sinyali olmalı (açık teklif, tâtonnement). | D5a3 |
| **Aynı kararın bütün kapılarına aynı bilgiyi ver.** Rakip bilgisi plan kararına eklenip rota değiştirme kararına eklenmeyince, sürü arka kapıdan geri geldi. | D5b.2 |
| **Toplu medyanlar seed'lerdeki çöküşü gizler.** D5b'nin ilk özetinde medyanlar iyi görünüyordu; seed seed son durum 3/5'te kilitlenme gösterdi. Her deneyde seed bazında son durum da incelenir. | D5b.1 |
| **Entegrasyon da yuva yuva yapılmalı.** Çok sayıda yeni şeyi aynı anda eklemek sorunları birbirine karıştırır; düzeltmeler birbirinin yan etkisini doğurur (köstebek oyunu). Ardışık 3 düzeltme sorunu sadece kaydırıyorsa durup ortak kökü ara. | D5 |
| Sınıflandırma ablasyonu (Y16) yanlış bir "fenomen" yorumunu önledi: düzeltmeden önce sınıflandır | D4b.1 |
| Yeni mal türleri (sürekli üretim, ara mal, ithal) motorun mevsimsel varsayımlarını yeniden sorgulatmalı | D4b.2 |
| **Orantılı paylaşım + "sıfır olunca bitir" koşulu = Zeno tuzağı.** Kalan miktarla orantılı dağıtım miktarı hiçbir zaman tam sıfırlamaz. Her durum makinesinin çıkış koşulu sürekli niceliklerde bir alt eşikle (lot) yazılmalı. Bir "kilitlenme" fenomeni yorumlanmadan önce kilitli ajanların gerçek durumuna (miktar, fiyat, teklif) bakılmalı: D5b'deki "ince pazar tuzağı"nın bir kısmı kırıntıydı. | D5b2.4 |
| **Patlamanın gördüğün yerde olmayan kökleri olabilir.** D5b2'de perakende patlamasının kökü kırıntıya takılan tüccarlar → düşen getiri medyanı → duran giriş → buğday kıtlığı zinciriydi. Önce zinciri geriye doğru izle. | D5b2.3 |
| **Metrik penceresi tutarlı olmalı.** Bütün metrikler son 5 yıla bakarken patlama ölçütü bütün seriye bakıyordu; ısınma artifact'ı, mekanizma etkisi gibi göründü. Isınma ayrıca raporlanmalı. | D5b2.9 |
| **5 seed etkileşim için az.** B×S "etkisi" 5 seed'de belirgin göründü; 10 seed ve parçalara ayırma, etkinin B'nin iki parçasının birlikte çalışmasından geldiğini gösterdi. Etkileşim iddiası için ≥10 seed ve ablasyon. | D5b2.12 |
| **Her teklif bütçeyle sınırlı olmalı.** Ödeyemeyeceği emri veren ajan takas fiyatını kurar ama takası yapmaz; pazar donar ve donmuş fiyat başka ajanların "olağan"ını bozar (kendini besleyen döngü). Bütçe kısıtı her karar modülünde açık yazılır. | D5b3.5 |
| **"Son ajan çıkamaz" kuralları tuzak yaratır.** Tek dükkân batınca çıkamadığı için pazar yıllarca kilitlendi. Çıkış kuralı, yerine girişin de tanımlı olduğu bir olay olmalı. | D5b3.5 |
| **Teşhis aracı da yanlı olabilir.** D5b3'te "tüccarlar iyimser" sanıldı; sefer bazında ölçünce iyimser olanın Claude'un temsilî kamu tüccarı olduğu çıktı. Bir yanlılık iddiasını önce ex-ante / ex-post kıyasla ölç. | D5b3.2 |
| **Seçim mekanizması test edilirken rastgele seçim kontrolü koy.** D5b3b'de itibar skoru kaybı beşte bire indirdi. Ama rastgele sıralama da aynısını yaptı: kazanç skordan değil, kapıdan ve ex-ante tahminin terk edilmesinden geliyordu. Ablasyon olmadan kullanıcının skoru "çalışıyor" diye kaydedilecekti. | D5b3b.4 |
| **Sinyal yoksa sıralama formülü tartışması boştur.** Önce hedeflenen özelliğin (beceri) gözlenen veride kalıcı olup olmadığını ölç (kalıcılık testi); sonra formül seç. | D5b3b.3 |
| **"Sonra ekleriz" demeden önce motora bak.** Kullanıcıya batan gemi riskinin eklenmesi gerektiğini söyledim; motorda zaten vardı (`_p_loss`). Bir özelliğin yokluğunu iddia etmeden önce kodda ara. | D5b3c |
| **Ardışık başarısız mekanizmalar ortak bir köke işaret edebilir.** İtibar (D5b3b), colleganza (D5b3, D5b3b) ve borç (D5b3c) aynı nedenle zorlandı: sefer getirisinin oynaklığı. Üçüncü mekanizmayı eklemeden önce ortak girdiyi (getiri dağılımı) ölçmek daha ucuzdu. | D5b3c |
| **Yeni bir öğrenen bileşenin "unutma" yolu olmalı.** Yatırımcı öğrenmesi bütçeyi 0'a indirince yeni veri gelmedi ve görüş sonsuza kadar bayat kaldı (absorbing state). Deneyim penceresi ve nötre dönüş gerekli. | D5b3c.2 |
| **Oran metriklerinin paydası küçülünce gürültü patlar.** Birim kargo başına getiri, ambar %9 doluyken geçim giderini birim başına şişirdi; derin zararların ~%40'ı bu yüzden. Bir metrik karar girdisi olarak kullanılmadan önce paydası (kargo mu, sermaye mi) sorgulanmalı. | D5b3c.4 |
| **Çarpık dağılımda medyan, "sermaye ne kazanıyor" sorusunun cevabı değildir.** Ömür boyu getiri medyanı (her kişi bir oy, kısa ömür yıllığa çevrilince patlıyor) ~%0 gösterirken, sermaye-yıl ağırlıklı toplam getiri %12,8'di. D5b3'ten beri "denge hedefin altında" diye yanlış yorumlandı. Bir hedef (S-012'deki %8) hangi ölçütle kıyaslanacaksa o ölçüt baştan tanımlanmalı. | D5b3d.2 |
| **Python 3.14'te multiprocessing varsayılanı `forkserver`.** İşçiler modülü yeniden yükler; `__main__`'de değiştirilen global değişkenler işçilere geçmez. Değişen her şey argümanla geçirilmeli. | D5b3d.2 |
| **Bir sorunun nedenini müdahaleyle sına.** "Tüccar fazla, pazar az" teşhisi filoyu %11 küçülten iki müdahaleyle sınandı: kalabalık değişmedi. Neden sayı değil koordinasyondu. Korelasyondan (boş ambar + çok gemi) çıkan nedensellik yanlış olabilir. | D5b3d.3 |

- **Ortak kasa, kişi başı ölçütleri bozar** (D5b3e.3): Birden çok ajanın sermayesi birleşince, ajan bazlı getiri, iflas ve çıkış kuralları anlamını yitirir. Yeni bir sahiplik yapısı eklerken bu kuralların hepsi yeni birime (ev) göre gözden geçirilmeli.

- **Açıklamadaki sayıyı da ölç** (D5b3g.3, 2026-11-02): Sonuçları yorumlarken "σ ~%10-15, giriş eşiği ~%20" diye ölçmeden bir sayı yazıldı. Ölçünce σ %4-6 çıktı ve yorum değişti: bant çok geniş değil, sistem bandın üst kenarında duruyor. Bir mekanizma açıklamasında geçen her sayı, kayıtlardan ölçülmeden yazılmaz; ölçülmediyse "tahmin, ölçülmedi" diye işaretlenir.

- **Ablation sonucu dünyanın büyüklüğüne bağlı olabilir** (D5b3j.1, 2026-11-06): U'yu kapatmak küçük haritada döngüyü hızlandırıp büyüttü (tepe/dip 2,8 → 6,9), tam haritada hiç etkilemedi (2,1 → 2,1). Bir mekanizmanın "gerekli" ya da "gereksiz" olduğu tek haritadan söylenmez; iki ölçekte de sınanır.

- **Derleyici matematik çağrılarını "eşdeğer" ifadelere çevirebilir** (P2, 2026-11-09): Rust/LLVM, glibc `pow(x, -1.0)` çağrısını `1.0 / x` yaptı. glibc `pow` her zaman doğru yuvarlanmadığı için sonuç 1 ulp farklı çıktı ve iki motor 107. günde ayrıştı. Bit düzeyinde eşdeğerlik gerekiyorsa matematik kütüphanesi çağrıları derleyiciden gizlenmeli (`black_box`). Bedeli, sabit argümanlı çağrıların gerçekten hesaplanması; sabitler önceden hesaplanır.

- **Alan başına özet, küçük farkı yerinde yakalar** (P2): 1 ulp'lik talep farkı nakitte (tamsayıya yuvarlanıyor) ve stokta (yutuluyor) görünmedi, yalnızca `op_profit`'te çıktı. Tek bir toplam özet olsaydı fark ancak günler sonra, kaynağından uzakta görünürdü. Durum alan alan (ve tüccar/pazar başına) özetlenince ilk ayrışan alan doğrudan kaynağı gösterdi.

- **Önce doğruluk, sonra hız; her hızlandırmadan sonra yeniden doğrula** (P4): Python profilinden beklenen darboğaz (`rivals`) Rust'ta ilk sırada değildi; ilk sırada söylenti kümeleri vardı. Darboğaz dile göre değişir, her dilde yeniden ölçülür. Her hızlandırma (veri yapısı, önbellek, tablo) gün iziyle yeniden sınandı; hiçbiri sonucu değiştirmedi.

- **"Benzersiz" sanılan kimliği doğrula** (P7, 2026-11-09): Port, dükkânı kimlik dizgisiyle izleyerek Python'un nesne kimliğini taklit etti. Kimlik bir sayaçtan üretiliyordu ve sayaç snapshot'ta sıfırlanıyordu: aynı pazarda iki `sk99e` oldu ve 40 koşudan biri 9. yılda ayrıştı. Kısa eşdeğerlik testleri (400 gün, 3 yıl) bunu yakalamadı; uzun ve çok seed'li bir uçtan uca karşılaştırma yakaladı. Port sırasında yapılan her "X benzersizdir / X boş olmaz" varsayımı, ya kodda doğrulanmalı (assert) ya da nesne kimliği gibi daha güvenli bir şeyle değiştirilmeli.

- **Paralel koşu sayısını makineye göre ölç** (P8): Dizüstü işlemcide (6 performans + 10 verimlilik çekirdeği, güç sınırlı) 4'ten fazla eşzamanlı koşu toplam verimi artırmadı, düşürdü (8 paralelde her koşu 5 kat yavaş). "Çekirdek sayısı kadar süreç" varsayımı yerine 1/2/4/8 ile kısa bir ölçüm yapılmalı.

- **Ölçeği büyütmek gizli artifact'ları açığa çıkarır** (M1, 2026-11-10): 6 limanda düzgün çalışan seçenek hesabı, 20 limanda "kalkış limanında arzı olmayan mal" seçeneklerine kilitlendi. Küçük ağda dağıtım kısaydı, tüketim pazarlarında fiyat patlamadığı için hata görünmüyordu. Ders: yeni bir ölçekte ilk koşuların sonuçları ölçüm sayılmaz; önce ajan durumları (ne yapıyorlar, nerede, yüklü mü) ve fiyat dağılımları kontrol edilir. Ortalama tablolar (getiri %32) yanıltıcıdır; snapshot'taki tek tek ajan durumları neyin bozuk olduğunu gösterir.

- **Davranışı değiştirmek için maliyetin nerede işlediğine bak** (PC, 2026-11-12): Gemi günlük maliyetini üç katına çıkarmak gemilerin limanda ya da denizde ne yaptığını değiştirmedi, yalnızca filoyu küçülttü. Gün başına aynı işleyen bir maliyet seçenekler arasındaki sıralamayı değiştirmez; yalnızca giriş-çıkış eşiğini değiştirir. Bir davranışı (yön değiştirme, kısa liman kalışı) hedefleyen mekanizma, o davranışın marjında işlemeli: olay başına maliyet ya da süre. Önceden "bu maliyet şu davranışı azaltır" demeden önce maliyetin karar denkleminde hangi terimi değiştirdiği yazılmalı.

- **Yeni bir yapıda ilk koşu ölçüm değil; önce tek tek ajan durumuna bak** (MX, 2026-11-12): Karışık yükün ilk iki sürümü tablolarda yalnızca "fiyatlar patladı" diye göründü. Koşu sonu durum dökümü (`MEDI_STATE`) iki gerçek hatayı gösterdi: istek fiyatına yanlışlıkla eklenen değer, kurulum süresinin mal sanılıp gümrüklenmesi. Ayrıca bir yapısal sorunu (dolaşan yolcu partiler) ortaya koydu. Toplu ölçütler hatanın yerini göstermez; ambar, nakit ve parti yaşı dağılımı gösterir (M1 dersinin tekrarı).

- **Yalnızca tüccara değil, karşı taraftaki ajanların kasasına da bak** (MK, 2026-11-12): Sözleşmenin karşı tarafını (depocu) incelerken, PF'den beri depocuların 2/5'inin iflas halinde olduğu görüldü. Hiçbir tablo bunu göstermiyordu; fiyat sorunları (ihracatçı tabanı, kıtlık sıçramaları) yıllardır tüccar ve taşıma tarafında aranıyordu. Her yeni yapıda tüm ajan türlerinin kasa ve stok dağılımı kontrol edilir.

- **Özet grafikler ve metinler rakamı raporun ölçüm aracından almalı** (GitHub vitrini, 2026-11-17): M2 grafiği için kayıp oranını yeniden hesaplarken filoyu bütün koşunun ortalaması ve kalkışları ısınma dahil aldım; rapor (`an_loss.py`) son 120 günün filosunu ve `ships_lost`u kullanıyor. Sonuç %37 yerine %41 çıktı. Ayrıca D5b raporunun başındaki düzeltme notu ana metindeki "5/5 patlama"yı 4/5 yapmıştı; özetin ana metinden değil düzeltme notundan beslenmesi gerekti. Kural: vitrin/özet rakamı ya raporun aracını çağırır ya da aynı tanımı kodda belgeler; raporların düzeltme notları ana metinden önce okunur.
