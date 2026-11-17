# 01 — Temel Ekonomik Kurallar ve Simülasyonu
> Durum: taslak (derin araştırma, 2. tur)
> Son güncelleme: 2026-10-22
> İlgili: [00-sentez](00-synthesis.md), [02-piyasa mekanizmaları](02-market-mechanisms.md)

Bu doküman simülasyonun dayanacağı temel ekonomik ilişkileri, her birinin **nasıl simüle edileceğini** ve **oyunda ne işe yarayacağını** anlatır. Matematik minimumda tutuldu; formüller sadece kodlanacak kadar.

---

## 1. Arz ve talep eğrisi aslında bir insan listesidir

Kullanıcının sorusu: "Her fiyattan belli sayıda alıcı ve satıcı var."

Doğru, ve simülasyonda talep eğrisini tam olarak böyle kurarız. Her alıcının bir **rezervasyon fiyatı** vardır: bu fiyatın üstünde almaz. Her satıcının da bir **maliyeti** veya rezervasyon fiyatı vardır: bu fiyatın altında satmaz.

```
Alıcılar (rezervasyon fiyatı):   A=90  B=80  C=70  D=60  E=50
Satıcılar (maliyet):             V=40  W=55  X=65  Y=75  Z=85

Fiyat 60 olsa:  isteyen alıcılar A,B,C,D (4 kişi)  · satmak isteyen V,W (2 kişi)  → talep fazlası
Fiyat 70 olsa:  A,B,C (3)                           · V,W,X (3)                    → denge
Fiyat 80 olsa:  A,B (2)                             · V,W,X,Y (4)                  → arz fazlası
```

- **Talep eğrisi** = rezervasyon fiyatlarını büyükten küçüğe dizip "bu fiyatta kaç kişi alır" diye saymak.
- **Arz eğrisi** = maliyetleri küçükten büyüğe dizip "bu fiyatta kaç kişi satar" diye saymak.
- **Denge** = iki sayımın eşitlendiği fiyat.

Vernon Smith 1962'deki deneylerinde öğrencilere gizli rezervasyon fiyatları ("induced values") dağıttı. Kimse dengeyi bilmediği halde, çift taraflı açık artırmada fiyatlar birkaç turda teorik dengeye çok yaklaştı; bu 3 alıcı ve 3 satıcıyla bile oldu. ([Nobel 2002 özeti](https://www.nobelprize.org/prizes/economic-sciences/2002/popular-information/), [Econlib](https://www.econlib.org/library/Enc/bios/SmithV.html)) Smith bu çalışmayla 2002 Nobel'ini aldı.

**Simülasyon karşılığı:**
- *Ajan modelinde:* Her ajan kendi rezervasyon fiyatını taşır. Eğri hiçbir yerde tanımlanmaz, kendiliğinden ortaya çıkar.
- *Toplu modelde:* Bir şehrin 100.000 kişilik talebini tek tek ajan yapmak yerine rezervasyon fiyatlarının **dağılımını** tutarız. Örneğin "tahıl için rezervasyon fiyatları ortalaması μ, yayılımı σ olan bir dağılım". Bu dağılımın kümülatifi talep eğrisidir. Böylece "fiyat P iken kaç birim alınır" sorusu tek bir formülle cevaplanır.

**Oyundaki anlamı:** Oyuncu bir limana 500 çuval tahıl getirdiğinde fiyat düşer. Neden? İlk 100 çuval en çok ödemeye razı alıcılara gider, sonrakiler daha az razı olanlara. Bu, "piyasayı boğmak" mekaniğinin doğal açıklamasıdır. Elite Dangerous'ta talebin %25'inden fazlası satılınca fiyatın düşmesi aynı olgunun kaba bir versiyonu.

## 2. Esneklik: fiyat değişince miktar ne kadar değişir?

**Fiyat esnekliği** = miktardaki % değişim / fiyattaki % değişim.

| Mal türü | Esneklik | Anlamı | Bizim mallar |
|---|---|---|---|
| Zorunlu | Düşük (\|e\| < 1) | Fiyat ne olursa olsun alınır; kıtlıkta fiyat patlar | Tahıl, tuz, odun |
| Lüks | Yüksek (\|e\| > 1) | Pahalanınca alıcı vazgeçer ya da bekler | İpek, baharat, kadife, şeker |
| İkame edilebilir | Yüksek | Pahalanınca başka mala geçilir | Zeytinyağı ↔ tereyağı, yün ↔ keten |

**Tarihsel kural: King-Davenant yasası (1699).** Tahıl hasadındaki küçük bir eksiklik fiyatı orantısız şekilde artırır. Davenant'ın (Gregory King'e atfettiği) tablosu: ([HET](https://www.hetwebsite.net/het/essays/theorem/kingdavenant.htm), [Campbell & Ó Gráda 2011](https://ideas.repec.org/a/cup/jechis/v71y2011i04p859-886_00.html))

| Hasat eksiği | Fiyat artışı (normalin üstünde) |
|---|---|
| %10 | %30 |
| %20 | %80 |
| %30 | %160 |
| %40 | %280 |
| %50 | %450 |

Bu tablo, tahıl talep esnekliğinin yaklaşık **-0.4** olduğu bulgusuyla uyumlu (Saksonya tahıl piyasaları üzerine bir çalışma). Ayrıca doğrusal değil, **dışbükey**: kıtlık derinleştikçe fiyat çok daha hızlı artar.

**Simülasyon karşılığı:**
- Her mal için bir esneklik parametresi (veya rezervasyon dağılımının şekli) tanımlanır.
- Tahıl için King-Davenant tablosu doğrudan bir **kalibrasyon hedefi** olur: Simülasyonda hasadı %30 düşürdüğümüzde fiyat ~2.6 katına çıkıyor mu?

**Oyundaki anlamı:** Kıtlık olan bir şehre tahıl yetiştirmek oyunun en büyük kâr fırsatlarından biri olur. Bu tarihsel olarak da öyleydi; Osmanlı ve Sicilya ihracat yasakları tam da bu yüzden vardı. Lüks mallarda ise fırsatlar daha istikrarlı ama daha sığdır.

## 3. Mekânsal fiyat dengesi: tek fiyat yasası ve arbitraj bandı

**Tek fiyat yasası:** Rekabetçi bir piyasada aynı mal her yerde aynı fiyata satılmalı, aradaki fark taşıma maliyeti kadar olmalı.

**Mekânsal denge (Cournot 1838 → Enke 1951 → Samuelson 1952 → Takayama & Judge):** Ticaret varsa, ithal edilen yerdeki fiyat = ihraç eden yerdeki fiyat + taşıma maliyeti. Fark taşıma maliyetinden küçükse ticaret olmaz. ([Nagurney ders notları](https://supernet.isenberg.umass.edu/courses/OIM413-Fall2018/OIM413lecture12.pdf), [Dünya Bankası](https://documents1.worldbank.org/curated/pt/623561493321126110/pdf/DWC8402000A0sp0sh0equilibrium0model.pdf))

Buradan **arbitraj bandı** kavramı çıkar:

```
            ← ticaret yok (bant içi) →
P_B ────────┬──────────────────────────┬────────
            P_A − c                    P_A + c
   (B'den A'ya taşımak kârlı)    (A'dan B'ye taşımak kârlı)

c = toplam işlem maliyeti: navlun + sigorta + gümrük + risk primi + sermayenin bağlı kalma maliyeti + bilgi maliyeti
```

İki liman arasındaki fiyat farkı ±c bandının içindeyse kimse taşımaz ve fark kalıcıdır. Fark bandı aşınca tüccarlar devreye girer ve farkı banda geri iter.

**Bizim için kritik nokta:** Bannerlord'un sorunu **c'nin çok küçük olması**. Kervanlar ucuz, güvenli ve her şeyi biliyor, bu yüzden bant daralıyor ve fırsat kalmıyor. Bizim tasarımımızda c'yi büyük ve **değişken** tutan unsurlar zaten var:

| c bileşeni | Bizdeki kaynak |
|---|---|
| Navlun | Gemi kirası, mevsim |
| Risk primi | Korsan, fırtına, savaş (değişken) |
| Sigorta | Risk bilgisine göre prim |
| Gümrük ve vergi | Bayrağa ve imtiyaza göre (Ragusa %2) |
| Sermaye maliyeti | 40-90 gün yolda bağlı kalan para |
| **Bilgi maliyeti** | Varış fiyatını bilmiyorsun; beklenen fiyat ile gerçek fiyat farkı |

c herkes için aynı değildir: Ragusalı tüccarın gümrüğü düşük, Venedikli patrizinin sigortası ucuz, Yahudi tüccarın Selanik'te ağı var. Yani **aynı fiyat farkı birine kârlı, ötekine zararlıdır.** Bu, heterojen ajanların ve bölgesel itibarın (K-003) ekonomik temeli.

**Tarihsel veri:** Avrupa tahıl piyasaları entegrasyonu kademeli ve adım adım ilerledi; coğrafya siyasi sınırlardan daha belirleyiciydi; gerçek bir Avrupa piyasası ancak 19. yüzyılda oluştu. Osmanlı içindeki buğday piyasası entegrasyonu uzun vadeli bir eğilim göstermeden kısa ve orta vadeli dalgalanmalarla seyretti; Osmanlı fiyatları çoğu Avrupa şehrinin altında kaldı. ([Chilosi vd. 2013](https://researchonline.lse.ac.uk/id/eprint/46891), [ERF 2025](https://erf.org.eg/app/uploads/2025/12/1766898326_559_2764832_1805.pdf))
→ 16. yüzyıl Akdeniz'inde limanlar arası büyük ve kalıcı fiyat farkları tarihsel olarak gerçekçi.

## 4. Depolama ve spekülasyon

**Rekabetçi depolama modeli (Williams & Wright 1991; Deaton & Laroque 1992, 1996):**
- Tüccarlar, bugünkü fiyat ile beklenen gelecek fiyat arasındaki fark depolama maliyetini (depo + bozulma + faiz) aşıyorsa mal stoklar.
- Stok **negatif olamaz**. Bu basit kısıt modeli doğrusal olmaktan çıkarır.
- **Sonuç:** Fiyatlar uzun süre düşük ve sakin seyreder, stok bitince **ani sıçramalar** yapar. Bu, gerçek emtia fiyatlarının karakteristik deseni.
- Stok varken fiyat şokları yumuşar (stoklar tampon görevi görür); stok bitince ("stockout") şok doğrudan fiyata yansır.
- Kısa vadeli dalgalanmaların ana kaynağı büyük ama düşük olasılıklı arz şoklarıdır (kötü hava gibi).
([Deaton & Laroque PDF](https://www.princeton.edu/~deaton/downloads/Competitive_Storage_and_Commodity_Price_Dynamics.pdf), [Cafiero vd.](https://hal.archives-ouvertes.fr/hal-00631675), [IMF WP 2011/064](https://www.imf.org/en/publications/wp/issues/2016/12/31/reviving-the-competitive-storage-model-a-holistic-approach-to-food-commodity-prices-24720/index.md))

**Simülasyon karşılığı:**
```
eğer  E[P_gelecek] × (1 − bozulma_oranı) − P_bugün  >  depolama_maliyeti + faiz × P_bugün
   → stokla (al ve beklet)
aksi halde
   → sat
```
Her mal için bozulma oranı ve depolama maliyeti farklıdır: tahıl çürür ve fare yer, tuz bozulmaz, ipek değerli ve küçüktür.

**Oyundaki anlamı:**
- Oyuncunun kendi deposu veya dükkânı olduğunda **zaman arbitrajı** açılır: hasatta ucuz al, ilkbaharda pahalı sat.
- Tarihsel olarak tahıl istifçiliği (incettatori) şehir devletlerince ağır cezalandırılırdı. Bu bir risk ve itibar mekaniği olabilir.
- Şehir devletlerinin resmî tahıl ambarları (Venedik'in Provveditori alle Biave kurumu ⚠️ doğrulanacak) NPC "dengeleyici" olarak modellenebilir: kıtlıkta stok satar, bollukta alır.

## 5. Gecikmeler ve salınımlar: örümcek ağı (cobweb) modeli

**Model:** Üreticiler bugünkü kararlarını (ekim, sefer) **geçmiş fiyata** göre verir, ürün ise gecikmeli gelir.
- Geçen yıl tahıl pahalıydı → herkes çok eker → bu yıl bolluk, fiyat düşer → gelecek yıl az ekilir → fiyat yükselir...
- **Kararlılık koşulu:** Arz esnekliği talep esnekliğinden (mutlak değer) küçükse salınım söner. Büyükse **patlar**, eşitse sonsuz salınır. ([Economics Help](https://economicshelp.org/?p=136238), [MDPI 2024](https://www.mdpi.com/2227-7390/12/20/3220))
- Gerçekte patlayan salınım nadirdir, çünkü üreticiler öğrenir ve geçmişin tek bir değerine değil ortalamasına bakar.

**Bizim oyunda bu çok önemli,** çünkü yapısal olarak gecikmeli bir dünyamız var:
- Haber 40 gün gecikmeli geliyor.
- Gemi 30-90 gün yolda.
- İskenderiye'de biberin pahalı olduğunu duyan 10 tüccar aynı anda yola çıkıyor ve hepsi aynı anda varıyor. Sonuç: varışta fiyat çöker.

Bu bir hata değil, **oyunun özüdür.** "Herkes aynı haberi duydu, ben de gitmeli miyim?" sorusu stratejinin kalbi. Ama simülasyonun **patlayan salınıma** girmemesi şart.

**Önlemler:**
- Ajanlar tek bir son fiyata değil, **ağırlıklı ortalama** fiyata bakar.
- Ajanlar diğerlerinin de aynı haberi duyduğunu tahmin edebilir (daha akıllı NPC'ler, bkz. 03 §5).
- Ajanların karar zamanları farklı olur; hepsi aynı anda karar vermez.
- Hasat gibi doğal gecikmeler yıllık; ticaret gecikmeleri haftalık ölçekte.

**Sterman'ın Bira Oyunu (1989):** Tedarik zincirinde gecikmeler varken insanlar sipariş verirken yoldaki malları hesaba katmayı unutur, aşırı sipariş verir, sonra stok taşar. Siparişler zincirde yukarı çıktıkça artan genlikle salınır: **kamçı etkisi** (bullwhip). Forrester bunu 1961'de "talep büyütmesi" olarak gözlemlemişti. İnsanlar bu sistemleri kontrol etmeyi öğrenemez, çünkü geri beslemeyi yanlış algılarlar. ([Sterman 1989](https://ideas.repec.org/a/eee/proeco/v236y2021ics0925527321000967.html), [CMU](https://www.cmu.edu/dietrich/sds/ddmlab/papers/MartinGonzalezLebiere2004.pdf))
→ **Oyun için:** Oyuncunun "yoldaki mallar" ve "yoldaki haberler" hakkında bir görünümü olmalı (sevkiyat defteri). Bu tarihsel olarak tüccar defterlerinin işiydi. Arayüzün en önemli parçalarından biri bu olabilir.

## 6. Bilgi, arama ve fiyat dağınıklığı

**Stigler (1961), "The Economics of Information":** "Fiyat dağınıklığı piyasadaki cehaletin bir göstergesi, hatta ölçüsüdür." ([Healthcare Economist](https://www.healthcare-economist.com/?p=881), [Baye, Morgan & Scholten](https://faculty.haas.berkeley.edu/rjmorgan/Information%20Search%20and%20Price%20Dispersion.pdf))

Stigler'in tahminleri:
- Fiyat dağınıklığı arttıkça aramanın getirisi artar.
- Büyük miktar alanlar daha çok arar.
- Tek seferlik alıcılar (turistler) tekrarlayan alıcılardan daha yüksek ortalama fiyat öder.
- Aramanın marjinal getirisi azalır: 5. fiyat teklifi ilk 2'si kadar değerli değildir.
- **Simsarlar (brokers)** dağınıklığı azaltır ama yok etmez, çünkü onlar da kâr etmek zorundadır.

**Geertz (1978), "The Bazaar Economy":** Fas'taki Sefrou pazarında bilgi "yetersiz, kıt, kötü dağılmış, verimsiz iletilen ve çok değerli". Pazar kaotik bir kalabalık değil; rekabet ve karşılıklı bağımlılık içindeki katılımcılar arasında karmaşık bağlar var. Arama verimliliği iki temel yönteme dayanır: ([Geertz PDF](https://www.gwern.net/doc/economics/mechanism-design/1978-geertz.pdf), [HSE](https://ecsoc.hse.ru/article/view/2252))
- **Müşterileşme (clientelization):** Belirli satıcılarla tekrarlanan ilişki kurmak. Bilgi ve güven sağlar.
- **Yoğun ve çok boyutlu pazarlık:** Sadece fiyat değil, miktar, kalite ve vade üzerinden de.

**Kirman'ın Marsilya balık pazarı:** Aynı alıcı ve satıcılar her gün aynı salonda buluştuğu halde **kalıcı fiyat dağınıklığı** ve **yüksek müşteri sadakati** var. Ajan tabanlı model, sadakatin karşılıklı öğrenmeyle ortaya çıktığını gösteriyor: alıcılar sadık olmayı öğrenir, satıcılar sadık müşteriye daha iyi hizmet vermeyi öğrenir. ([Kirman & Vriend 2001](https://nvriend.econ.qmul.ac.uk/abs/abs.jedc2.html), [Weisbuch, Kirman & Herreiner 2000](https://ideas.repec.org/a/ecj/econjl/v110y2000i463p411-36.html)) Ayrıntı: [03 §4](03-academic-abm.md).

**Bizim için bunların anlamı:**
1. Fiyat dağınıklığı bizim oyunda bir **hata değil, hedef metrik**. Ne kadar olacağını bilgi yayılım hızı belirler.
2. **Müşterileşme = bölgesel itibar (K-003).** Bir limanda tekrar tekrar işlem yaptığın tüccarlar sana daha iyi fiyat ve daha taze bilgi verir. Bu, ekonomik literatürde gerçek ve belgelenmiş bir mekanizma.
3. **Simsarlar (sensali)** Venedik'te resmî bir meslekti ⚠️. NPC simsarlar bilgi satan ve aracılık yapan ajanlar olabilir.
4. **"Turist" etkisi:** Yeni geldiğin bir limanda daha kötü fiyat alırsın. Bu, yeni başlayan oyuncunun neden küçük kalması gerektiğini doğal yoldan açıklar.

## 7. Beklentiler: ajanlar geleceği nasıl tahmin eder?

| Beklenti türü | Formül (kaba) | Davranış |
|---|---|---|
| Naif | E[P_t+1] = P_t | Son fiyat devam eder. Örümcek ağı salınımına yol açar. |
| Uyarlamalı | E[P_t+1] = E[P_t] + λ(P_t − E[P_t]) | Yavaş öğrenir, salınımı söndürür. λ "unutma hızı". |
| Trend takipçisi (chartist) | E[P_t+1] = P_t + g(P_t − P_t−1) | Yükselen daha da yükselir. Balonlar ve çöküşler üretir. |
| Temelci (fundamentalist) | E[P_t+1] = P* (temel değer) | Fiyatı "olması gereken"e çeker. Dengeleyici. |
| Rasyonel | Modeli tam bilir | Gerçekçi değil; ajanlar dünyanın tam modelini bilmez. |

**Brock & Hommes uyarlamalı inanç sistemi (1997-98):** Ajanlar temelci ve trend takipçisi gibi stratejiler arasında, son dönemdeki kârlılıklarına göre **lojit kuralıyla** geçiş yapar. Geçiş hızı (β, "seçim yoğunluğu") arttıkça sistem kararlıdan döngülere ve kaosa geçer. Trend takipçileri piyasadan elenmek zorunda değildir. ([Brock & Hommes özetleri](https://ideas.repec.org/p/man/cgbcrp/104.html), [He & Li](https://www.uts.edu.au/sites/default/files/qfr-archive-03/QFR-rp291.pdf))

```
pay_i = exp(β × kârlılık_i) / Σ_j exp(β × kârlılık_j)
```

**Bizim için:** NPC tüccar tiplerine bu beklenti türlerini **kişilik** olarak vermek mümkün:
- *Temkinli yaşlı Venedikli* → temelci, uyarlamalı (düşük λ)
- *Hırslı genç spekülatör* → trend takipçisi
- *Ceneviz bankacısı* → temelci, iyi bilgili

β parametresi bize oynaklık için **tek bir ayar düğmesi** verir: düşük β sakin bir piyasa, yüksek β çalkantılı bir piyasa demek.

## 8. Fiyat ayarlama dinamikleri: ne kadar hızlı?

**Walras tâtonnement'ı ("el yordamı"):** Hayali bir açık artırmacı, fazla talep olan malın fiyatını yükseltir, fazla arz olanınkini düşürür. Samuelson'un formu: ([MIT](https://economics.mit.edu/sites/default/files/inline-files/taton_NBER_new_2.pdf))
```
P_t+1 = P_t + α × FazlaTalep(P_t)
```
- **Scarf (1960) uyarısı:** Mallar birbirinin ikamesi değilse bu süreç dengeye hiç yakınsamayabilir ve fiyatlar dengenin etrafında sonsuza kadar döner. Laboratuvar deneyleri de bu dönüşü gösterdi (Anderson vd. 2004).
- Ayrık zamanda **α çok büyük seçilirse** fiyat iki değer arasında zıplar (2 noktalı limit döngüsü). Sönümleme miktarı kararlılığı belirler ([Kemp-Benedict](https://arxiv.org/pdf/1108.0188)). Fiyat değişimine **alt ve üst sınır** koymak dinamiği kararlı hale getirebilir ([Naimzada & Sordi](https://usiena-air.unisi.it/bitstream/11365/993644/1/2016_NS_WP.pdf)).

**Oyunlardaki pratik çözümler:**
- RuneScape Grand Exchange: Fiyat günde en fazla %5 değişebilir. ([RS Wiki](https://runescape.wiki/w/User:PointyBot))
- Victoria 2 v1.3: Fiyatlar taban fiyatın %20'si ile %500'ü arasında kalır. ([Gamepressure](https://www.gamepressure.com/download/victoria-ii-v13-patch/zf7f20))
- Victoria 3: Fiyat taban etrafında bir bant içinde kalır.

**Bizim için:**
- Toplu modeldeki fiyat güncellemelerinde α küçük tutulmalı. Gerekirse günlük değişime bir üst sınır konmalı.
- Ama mutlak taban ve tavan fiyatlar **tarihsel gerçekliğe aykırı**: kıtlıkta tahıl 5 katına çıkabiliyordu (King-Davenant). Bu yüzden sert sınırlar yerine **yumuşak sınırlar** (sigmoid) daha uygun.

## 9. Para, enflasyon ve fiyat devrimi

- 16. yüzyıl Avrupası'nda **fiyat devrimi** yaşandı: Amerikan gümüşü ve nüfus artışıyla fiyatlar yüzyıl boyunca kabaca birkaç kat arttı ⚠️ (rakamlar doğrulanacak; Braudel'de var).
- Gümüş, Doğu ile ticaret açığı yüzünden **Doğu'ya akıyordu**.
- Venedik'te gümüşün değer kaybıyla altın duka (zecchino), sabit hesap dukasından değerli hale geldi (bkz. [tarih genel çerçeve §6](../history/mediterranean-16c-overview.md)).

**Simülasyon karşılığı:**
- Toplam para arzı izlenen bir değişken olur. Musluklar (yeni gümüş) ve yutaklar (Doğu'ya akış, vergiler, kayıplar) açıkça modellenir.
- Uzun bir oyunda (1560-1600) yavaş ama kalıcı bir enflasyon **tarihsel olarak doğru**. Ultima Online'daki gibi hatalı bir enflasyon ise "kontrolsüz" olandır. Bizim hedefimiz enflasyonun **tasarlanmış ve tarihsel** olması.
- Ultima Online dersini unutmamalıyız: NPC'ler yoktan para basmamalı. ([Simpson 1999](https://gwern.net/doc/economics/1999-04-07-simpson-theingameconomicsofultimaonline.html))

## 10. Güven, itibar ve sözleşmelerin uygulanması

**Greif'in Mağribi tüccarları (11. yüzyıl Akdeniz):** Uzak limanlardaki temsilcilerin hile yapmasını önleyen şey mahkemeler değil, **çok taraflı ceza** idi. Bir tüccarı dolandıran temsilci "hilekâr" damgası yer ve koalisyondaki **hiçbir** tüccar onu bir daha işe almazdı. Bunun için tüccarlar arasında temsilcilerin geçmiş davranışları hakkında ayrıntılı bilgi akışı gerekiyordu. Dürüst temsilcilere ödenen ek ücret, sistemi kendi kendini uygulayan hale getiriyordu. Cenevizliler ise daha çok hukuki yaptırım ve ikili itibara dayanıyordu. ([Greif 2012](https://web.stanford.edu/~avner/Greif_Papers/2012_Greif_long_ssrn_Maghribi.pdf), [MPRA](https://mpra.ub.uni-muenchen.de/1889/1/MPRA_paper_1889.pdf))

Bu yorum tartışmalı: Edwards & Ogilvie ilişkilerin hukuka dayandığını savunuyor ([CESifo](https://www.cesifo.org/DocDL/cesifo1_wp2254.pdf)). Bernstein'ın ağ temelli okuması ise Greif'in ana içgörüsünü destekliyor: itibara dayalı topluluk yaptırımı ticarette merkezi bir rol oynadı ([Bernstein](https://ostromworkshop.indiana.edu/pdf/piep2018/bernstein-abs.pdf)).

**Bizim için çok değerli:**
1. **Temsilci (fattore) sistemi (K-008):** Temsilcinin dürüstlüğünü sağlayan şey ücret primi + itibar kaybı tehdidi + bilgi ağı. Oyuncu temsilcisine iyi ödemezse temsilci çalma eğiliminde olur. Temsilcinin itibarı ise tüm ağda görünür.
2. **İtibar topluluk bazlıdır.** Venedikli tüccar ağında, Yahudi ağında, Rum ağında itibarın ayrı ayrıdır. Bir ağda dolandırıcılık yaparsan o ağın tamamı öğrenir, ama haber de gecikmeli yayılır!
3. **İki model:** "Mağribi" tipi (koalisyon ve dedikodu) ile "Ceneviz" tipi (mahkeme ve noter). Topluluklar farklı kurumlara sahip olabilir.
4. Sigorta dolandırıcılığı (K-012) bu mekanizmayla çözülür: sigortacılar bilgi paylaşır.

---

## Bu dokümandan simülasyona aktarılacaklar (özet)

| Kavram | Simülasyondaki yeri | Ayar parametresi |
|---|---|---|
| Rezervasyon fiyatı dağılımı | Toplu talep ve arz | μ, σ (mal, şehir ve mevsime göre) |
| Esneklik | Dağılımın şekli | Tahıl ≈ -0.4; King-Davenant kalibrasyonu |
| Arbitraj bandı | Ajanların sefer kararı | c bileşenleri, ajana özgü |
| Depolama | Ajan ve şehir stok kararları | Bozulma oranı, depo maliyeti, faiz |
| Gecikme / örümcek ağı | Haber ve seyir süresi | Ajanların ortalama penceresi, karar zamanlarının dağılımı |
| Bilgi ve arama | Fiyat inancı, haber yaşı | Haber yayılım hızı |
| Müşterileşme | İkili ilişki puanı | Sadakat öğrenme hızı |
| Beklenti türleri | Ajan kişiliği | λ, g, β |
| Fiyat ayarlama | Toplu modelde fiyat güncellemesi | α, yumuşak sınırlar |
| Para arzı | Musluk-yutak muhasebesi | Gümüş girişi, Doğu'ya akış |
| İtibar ve yaptırım | Topluluk bazlı itibar, dedikodu | Bilgi paylaşım hızı, ceza şiddeti |
