# Codex: Piyasa ve Fiyat Kavramları
> Son güncelleme: 2026-10-26 · Biçim: [README](README.md)

---

### Supply and demand / rezervasyon fiyatı
- **Oyuncu metni:** Her alıcının ödemeye razı olduğu bir üst sınır, her satıcının razı olduğu bir alt sınır vardır. Bir limana çok mal getirirsen, ilk çuvallar en hevesli alıcılara gider; sonrakiler için fiyatı düşürmen gerekir.
- **Ne zaman çıkar:** Oyuncu bir pazarda büyük miktar sattığında ve birim fiyat düştüğünde.
- **Kaynak:** Smith, V. (1962), çift taraflı açık artırma deneyleri (2002 Nobel).
- **Simülasyonda:** Kent talep havuzları; [01 §1](../research/simulation/01-economic-fundamentals.md).

### Price elasticity ve King-Davenant yasası
- **Oyuncu metni:** Ekmek olmadan yaşanmaz; hasat biraz eksik olsa bile tahıl fiyatı orantısız yükselir. Lüks mallar ise pahalanınca alıcısını kaybeder.
- **Ne zaman çıkar:** Kötü hasat haberi geldiğinde.
- **Kaynak:** Davenant (1699), Gregory King'e atfen; Campbell & Ó Gráda (2011).
- **Tarihsel örnek:** %10 eksik hasat ≈ %30 fiyat artışı; %50 eksik ≈ %450.
- **Simülasyonda:** [D1f](../experiments/D1f.md), [D1g](../experiments/D1g.md).

### Law of one price ve arbitraj bandı
- **Oyuncu metni:** İki limandaki fiyat farkı taşıma, gümrük ve risk maliyetini aşarsa biri malı taşır ve farkı kapatır. Fark bu maliyetlerin altındaysa, kimse taşımaz.
- **Ne zaman çıkar:** Oyuncu iki liman arasında kâr hesabı yaptığında.
- **Kaynak:** Cournot (1838); Samuelson (1952); Takayama & Judge.
- **Simülasyonda:** [D2](../experiments/D2.md): taşıma maliyetinin ~1,06 katı.

### Cobweb (örümcek ağı)
- **Oyuncu metni:** Karar ile sonuç arasında zaman varsa (ekim ile hasat, yükleme ile varış), herkes aynı eski sinyale göre davranır ve fiyat bir yukarı, bir aşağı salınır.
- **Ne zaman çıkar:** Bir pazarda fiyat, toplu varışlardan sonra çöktüğünde.
- **Kaynak:** Kaldor (1934); Ezekiel (1938).
- **Simülasyonda:** [D3](../experiments/D3.md) B3.

### Pork cycle (hog cycle)
- **Oyuncu metni:** Bir iş kârlı görününce herkes ona girer; kapasite fazlalaşır, kâr çöker, herkes çıkar; sonra yine kârlı olur. Herkes çıkarken girmek, cesur tüccarın oyunudur.
- **Ne zaman çıkar:** Bir rotada tüccar sayısı belirgin şekilde artıp azaldığında.
- **Kaynak:** Hanau (1928); Coase & Fowler (1935).
- **Tarihsel örnek:** Tarım ve gemicilik; navlun fiyatlarındaki döngüler.
- **Simülasyonda:** [D3b](../experiments/D3b.md).

### Storage and speculation (depolama ve spekülasyon)
- **Oyuncu metni:** Hasatta ucuz alıp ilkbaharda pahalı satmak, malı saklamanın maliyetini (faiz, bozulma, ambar) aşıyorsa kârlıdır. Stokçular fiyatları yumuşatır, ama kıtlıkta en çok onlar kazanır ve en çok onlardan nefret edilir.
- **Ne zaman çıkar:** Oyuncu ilk kez depoya mal koyduğunda.
- **Kaynak:** Williams & Wright (1991); Deaton & Laroque (1992, 1996).
- **Simülasyonda:** Stokçu rolü, [D1f](../experiments/D1f.md).

### Income effect ve substitution effect
- **Oyuncu metni:** Ekmek pahalanınca halkın kumaşa ayıracak parası kalmaz (income effect). Buğday pahalanınca insanlar arpaya döner (substitution effect). Tahıl kıtlığı haberi, kumaş tüccarı için de kötü haberdir.
- **Ne zaman çıkar:** Kıtlık sırasında lüks malların satışı düştüğünde.
- **Kaynak:** Slutsky (1915); Stone (1954) LES; two-stage budgeting (Gorman).
- **Simülasyonda:** [D4](../experiments/D4.md).

### Labrousse etkisi
- **Oyuncu metni:** Kötü hasat, şehrin zanaatkârlarını da işsiz bırakır: halk ekmeğe para yetiştiremeyince kumaş alamaz, dokumacı tezgâhı durur, onun da ekmek parası kalmaz.
- **Ne zaman çıkar:** Kıtlıkta bir kentin zanaat üretimi düştüğünde.
- **Kaynak:** Labrousse, E. (1933, 1944) ⚠️ (18. yy Fransa için).
- **Simülasyonda:** [D4c](../experiments/D4c.md): kapalı tek kentte zayıf, ihracatlı dünyada test edilecek.

### Leontief girdi-çıktı ve ortak hammadde
- **Oyuncu metni:** Zenginin ince kumaşı ile fakirin kaba kumaşı aynı yünden yapılır. Saray modası yünü pahalandırırsa, yoksulun kumaşı da pahalanır.
- **Ne zaman çıkar:** Bir hammaddenin fiyat değişimi birden fazla ürüne yansıdığında.
- **Kaynak:** Leontief (1936, 1941).
- **Simülasyonda:** [D4c](../experiments/D4c.md).

### Barriers to entry ve ekonomik rant
- **Oyuncu metni:** Bir işe girmek zorsa (lonca, imtiyaz, büyük sermaye), içerdekiler fazladan kazanır. Kolaysa kâr herkesin payına bölünür, ta ki senetten biraz fazlası kalana dek.
- **Ne zaman çıkar:** Oyuncu bir loncaya girdiğinde ya da bir imtiyaz elde ettiğinde.
- **Kaynak:** Bain (1956); Stigler (1968).
- **Simülasyonda:** [D3b](../experiments/D3b.md) (yeniden üretim).

### Intermediation (aracılık)
- **Oyuncu metni:** Toptancılar, simsarlar ve kapanlar, alıcıyla satıcının birbirini bulma zahmetini ortadan kaldırır, malı bekletir, kaliteyi tartar. Bunu yaparken bir pay alırlar.
- **Ne zaman çıkar:** Oyuncu ilk kez bir toptan pazarda işlem yaptığında.
- **Kaynak:** Rubinstein & Wolinsky (1987); Biglaiser (1993); Spulber (1996).
- **Simülasyonda:** [D5](../experiments/D5.md) B1: eksikliği; toptan pazar tasarımı.

### Liquidity spiral ve likidite tuzağı
- **Oyuncu metni:** Parası ve malı tükenen bir tüccar mal alamaz, mal alamadığı için satamaz, satamadığı için kazanamaz. Veresiye ya da bir ortak bulamazsa batar.
- **Ne zaman çıkar:** Oyuncunun ya da tanıdığı bir tüccarın nakdi tükendiğinde.
- **Kaynak:** Brunnermeier & Pedersen (2009).
- **Simülasyonda:** [D5](../experiments/D5.md) #8.

### Rockets and feathers
- **Oyuncu metni:** Bazı fiyatlar roket gibi yükselir, tüy gibi iner. Satıcılar maliyet artışını hemen yansıtır, düşüşü yavaş yansıtır.
- **Ne zaman çıkar:** Bir kriz geçtikten sonra fiyatlar uzun süre yüksek kaldığında.
- **Kaynak:** Bacon (1991); Borenstein, Cameron & Gilbert (1997).
- **Simülasyonda:** [D1f](../experiments/D1f.md) (kısmen yanlış teşhis edilmişti). [D5a2](../experiments/D5a2.md) B5: rekabetçi perakendede **kendiliğinden çıkmadı**; literatüre göre nedeni müşterinin arama davranışının fiyatın yönüne göre değişmesi (Tappata 2009; Yang & Ye 2008; Lewis 2011). Modelde müşterinin fiyat duyarlılığı sabit olduğu için asimetri yok.

### Export base ve çarpan
- **Oyuncu metni:** Bir kentin zenginliği dışarıya sattığı mallardan gelir. Venedik kumaşı Levant'ta satılmazsa, Venedik dokumacısı aç kalır.
- **Ne zaman çıkar:** Bir ihraç pazarındaki kriz, üretici kentin gelirini düşürdüğünde.
- **Kaynak:** North (1955) ⚠️; Keynesyen çarpan.
- **Simülasyonda:** [D4c](../experiments/D4c.md) B3; D5b'de test edilecek.

### Famine propagation ve entitlement
- **Oyuncu metni:** Kıtlık yalnızca yiyeceğin azlığı değildir; kimin ne kadar alabildiğidir. Zengin kıtlıkta da doyar; ucuzlayan malları bile toplar.
- **Ne zaman çıkar:** Kıtlıkta sınıflar arası tüketim farkı açıldığında.
- **Kaynak:** Sen, A. (1981) ⚠️.
- **Simülasyonda:** [D4b](../experiments/D4b.md).

### Bertrand rekabeti ve Diamond paradoksu
- **Oyuncu metni:** Aynı malı satan iki dükkân, müşteri hep ucuz olanı bulursa, birbirinin fiyatını maliyete kadar kırar. Ama müşteri her dükkânı gezmeye üşenirse, kalabalık bir çarşıda bile fiyatlar yüksek kalabilir.
- **Ne zaman çıkar:** Oyuncu aynı limanda iki dükkânın farklı fiyatlarını ilk kez gördüğünde.
- **Kaynak:** Bertrand (1883); Diamond (1971); Varian (1980), *A Model of Sales*.
- **Simülasyonda:** [D5a2](../experiments/D5a2.md) B3: perakende marjının alt sınırı müşterinin fiyat duyarlılığına bağlı.

### Lerner endeksi ve monopolistic competition
- **Oyuncu metni:** Bir satıcının ne kadar kâr payı koyabileceği, müşterisinin onu ne kadar kolay bırakabildiğine bağlıdır. Rakip çoksa ve müşteri kolay geçiyorsa pay küçüktür. Yeni dükkânlar açıldıkça herkesin payı erir, ama müşteriler her gün bütün çarşıyı gezmediği için tamamen yok olmaz.
- **Ne zaman çıkar:** Oyuncu ilk dükkânını açtığında ya da bir dükkâncıyla fiyat pazarlığı yaptığında.
- **Kaynak:** Lerner (1934); Chamberlin (1933); logit oligopol: Anderson, de Palma & Thisse (1992); fazla giriş: Mankiw & Whinston (1986).
- **Simülasyonda:** [D5a2](../experiments/D5a2.md) B1-B3: 3 dükkânda marj %14. Dükkâncının geçimi olunca büyük pazar çok dükkân ve düşük marj (Venedik buğdayı: 31 dükkân, %9,5), küçük pazar az dükkân ve yüksek marj (Korfu yağı: 4 dükkân, %13) taşıyor.

### Switching costs (müşteri ataleti)
- **Oyuncu metni:** Müşteri alıştığı dükkândan kolay kopmaz. Fiyatı artıran dükkâncı müşterisini hemen değil, haftalar içinde kaybeder; bu yüzden kısa vadede fiyat artırmak cazip, uzun vadede pahalıdır.
- **Ne zaman çıkar:** Oyuncunun dükkânından müşteriler rakibe kaymaya başladığında.
- **Kaynak:** Klemperer (1987, 1995).
- **Simülasyonda:** [D5a2](../experiments/D5a2.md): müşteri payı ~30 günde yeni hedefe yaklaşır.

### Derived demand (türetilmiş talep)
- **Oyuncu metni:** Dükkâncı buğdayı kendisi yemek için değil, müşterisine satmak için alır. Toptan pazarda ne kadar ödeyeceği, müşterisinin ne kadar ödeyeceğine bağlıdır.
- **Ne zaman çıkar:** Oyuncu kapanda dükkâncılara mal sattığında.
- **Kaynak:** Marshall (1890), *Principles*; Hicks (1932).
- **Simülasyonda:** [D5a2](../experiments/D5a2.md): dükkânın kapandaki alış emri müşteri talebinden türüyor; kendi maliyetinden türeyen teklif çapasız kaldı (artifact).

### Fiyatla paylaştırma ve kuyrukla paylaştırma
- **Oyuncu metni:** Kıt bir mal ya fiyatla paylaşılır (pahalılaşır, parası olan alır) ya da kuyrukla (fiyat sabit kalır, ama raflar boşalır, önce gelen alır). Narh ikincisini seçmektir: ekmek ucuzdur, ama fırının önünde kavga çıkar.
- **Ne zaman çıkar:** Kıtlıkta bir limanda raflar boşaldığında ya da narh konduğunda.
- **Kaynak:** Weitzman (1977); Barzel (1974).
- **Simülasyonda:** [D5a2](../experiments/D5a2.md) B4: yapışkan perakende örtük bir narh gibi davranıyor (bazı günler tüketim sıfır); rekabetçi perakende fiyatla paylaştırıyor.

### Tâtonnement ve fiyat keşfi
- **Oyuncu metni:** Bir pazarda mal yoksa fiyat da yok mudur? Hayır: Eli boş dönen müşteriler ve her gün biraz daha yüksek teklif veren dükkâncılar, fiyatın orada olması gerekenden düşük olduğunu söyler. "Venedik'te yağ yok" haberi, en iyi fiyat haberidir.
- **Ne zaman çıkar:** Oyuncu malı tükenmiş bir pazar hakkında haber aldığında.
- **Kaynak:** Walras (1874), tâtonnement; Hayek (1945), "The Use of Knowledge in Society" (fiyat bir bilgi sinyalidir).
- **Simülasyonda:** [D5a3](../experiments/D5a3.md): son işlem fiyatı donunca Venedik yılın üçte birinde yağsız kalıyordu; açık teklif ve tâtonnement ile ithalat ihtiyaca yetişti.

### Market maker ve envanter
- **Oyuncu metni:** Depocu malı ucuzken alır, pahalıyken satar. Deposu dolarsa almak için daha az öder, boşalırsa daha çok. Senin fazla malını hemen alacak biri o; ama karşılığında indirim ister.
- **Ne zaman çıkar:** Oyuncu malını bir depocuya sattığında ya da depocunun teklifi beklenmedik şekilde düştüğünde.
- **Kaynak:** Garman (1976); Amihud & Mendelson (1980); Ho & Stoll (1981); depolama: Williams & Wright (1991).
- **Simülasyonda:** [D5b2](../experiments/D5b2.md), yuva L (K-018). En etkili tek mekanizma: satış bekleyen tüccar kalmadı, Venedik'te malsız gün kalmadı. Literatürde bilinen sonuç (Grossman & Miller 1988); simülasyon yeniden üretti.

### Soudure (hasat öncesi kıtlık)
- **Oyuncu metni:** Hasattan önceki aylarda geçen yılın ambarı boşalır, yeni ürün henüz gelmemiştir. Ekmek bu aylarda pahalanır; kötü bir yılın ardından kıtlığa döner. Bu aylarda buğday getiren tüccar büyük kazanır, ama zamanında getirmek için haberi erken almak gerekir.
- **Ne zaman çıkar:** İlkbahar sonu, buğday fiyatı yükselirken; ya da ithalatçı bir kentte hasat öncesi ambar haberi geldiğinde.
- **Kaynak:** Fransız tarih yazımında *la soudure*; Kaplan (1976), *Bread, Politics and Political Economy*; Persson (1999), *Grain Markets in Europe, 1500-1900*. Doğrulanmadı: sayfa düzeyinde.
- **Simülasyonda:** [D5b2](../experiments/D5b2.md) T3: küçük filo ve bayat bilgiyle hasat öncesi buğday fiyatı Korfu'da 50×'e çıktı. Oyunda bu kadar uç bir kıtlık beklenmiyor; filo büyüklüğü ve giriş kalibrasyonla ayarlanacak (S-012).

### Colleganza ve commenda (yatırımcı sermayesi)
- **Oyuncu metni:** Venedik'te parası olan herkes tüccar olmak zorunda değildir. Dul bir kadın da, bir loncanın ustası da parasını yola çıkan bir tüccara emanet eder; kârı paylaşırlar. Bir ticaretin kârlı olduğu duyulunca sermaye o yola akar.
- **Ne zaman çıkar:** Oyuncu yatırımcı aradığında ya da kârlı bir rotaya kısa sürede yeni gemiler çıktığında.
- **Kaynak:** Lane (1973), *Venice: A Maritime Republic* ⚠️; González de Lara (2008), "The Secret of Venetian Success", JEH ⚠️.
- **Simülasyonda:** Aday (framework A11, S-012).

### Optimizer's curse (en iyiyi seçmenin laneti)
- **Oyuncu metni:** On fırsat duyarsın, en parlağını seçersin. Ama en parlak görünen genellikle en çok abartılmış olandır. Tecrübeli yatırımcı her parlak haberi biraz indirir, başkalarının gerçekte ne kazandığına bakar.
- **Ne zaman çıkar:** Oyuncu bir rotanın "kesin" kârlı olduğunu duyup büyük yatırım yapmayı düşündüğünde.
- **Kaynak:** Smith & Winkler (2006), "The Optimizer's Curse", *Management Science* 52(3) ⚠️; ilgili: winner's curse (Capen, Clapp & Campbell 1971).
- **Simülasyonda:** [D5b3](../experiments/D5b3.md): kamu fırsat tahmini yıllık %200-900, gerçekleşen −%5; düzeltme: sicil + sefer kârı / ufuk.

### Entry cobweb (giriş dalgası)
- **Oyuncu metni:** Bir rota çok kazandırınca herkes gemi donatır. Gemiler aynı anda varır, mal ucuzlar, kimse kazanamaz; bir kısmı vazgeçer. Az gemi kalınca rota yine kazandırır. Dalga böyle döner.
- **Ne zaman çıkar:** Kârlı bir rotaya kısa sürede çok gemi çıktığında; ya da oyuncu dalganın dibinde girmeyi düşündüğünde.
- **Kaynak:** Cobweb ve domuz döngüsü (Ezekiel 1938); gemi yapım döngüleri: Stopford, *Maritime Economics* ⚠️.
- **Simülasyonda:** [D5b3](../experiments/D5b3.md).

### Adverse selection ve itibar (kime sermaye verilir?)
- **Oyuncu metni:** Parasını emanet edecek tüccar ararken dikkat et: en çok sermaye isteyen, genellikle parasını kaybetmiş olandır. Venedik'te yatırımcılar kime güveneceklerini tüccarın geçmişinden, ailesinden, loncasından bilirdi. İyi bir ün, en değerli sermayedir.
- **Ne zaman çıkar:** Oyuncu colleganza'yla sermaye aradığında (ününe göre kabul ya da ret) ya da yatırımcı olarak tüccar seçtiğinde.
- **Kaynak:** Akerlof (1970), "The Market for Lemons"; Stiglitz & Weiss (1981), kredi tayınlaması; Greif (1993), Maghribi tüccarlarının itibar koalisyonu ⚠️.
- **Simülasyonda:** [D5b3](../experiments/D5b3.md) v1: colleganza yatırımcıları sözleşme başına −%14/−%19 kaybetti. Sermayeyi nakdi yetmeyen, yani çoğunlukla kaybetmiş tüccarlar istiyordu. Literatürde bilinen sonuç (Stiglitz & Weiss 1981); simülasyon yeniden üretti. Aday: yatırımcının tüccarın kendi siciline bakması (itibar).

### Credibility (sicile ne kadar güvenilir?)
- **Oyuncu metni:** İki seferde iki kez kazanan tüccar şanslı da olabilir, usta da. Yirmi seferde on beş kez kazanan ise büyük ihtimalle ustadır. Akıllı yatırımcı az sicili olanı "ortalama bir tüccar" sayar; sicil uzadıkça ona kendi geçmişine göre davranır.
- **Ne zaman çıkar:** Oyuncu ilk yıllarında yatırımcı bulmakta zorlandığında; ya da birkaç şanslı seferden sonra beklediğinden az sermaye aldığında.
- **Kaynak:** Bühlmann (1967), credibility theory (aktüerya); Bayes shrinkage; Efron & Morris (1975) ⚠️.
- **Simülasyonda:** [D5b3b](../experiments/D5b3b.md), skor B.

### Skill vs luck (şans mı ustalık mı?)
- **Oyuncu metni:** Denizde bir sefer, ustayı da acemiyi de aynı fırtınaya sokar. Bir tüccarın iki yıllık defteri çoğu zaman ustalığından çok talihini gösterir. Bu yüzden Venedik yatırımcısı yalnızca deftere değil, tüccarın kimden haber aldığına, kimlerle mektuplaştığına, hangi limanları tanıdığına da bakardı.
- **Ne zaman çıkar:** Oyuncu birkaç şanslı seferden sonra kendini usta sandığında; ya da yatırımcı olarak "geçen yıl en çok kazanan"a para verip kaybettiğinde.
- **Kaynak:** Carhart (1997), fon getirilerinin kalıcılığı; Fama & French (2010), "Luck versus Skill in the Cross-Section of Mutual Fund Returns" ⚠️.
- **Simülasyonda:** [D5b3b](../experiments/D5b3b.md). Tüccar getirisinin kalıcılığı 0,06-0,13. Skorla seçmek, rastgele seçmekten iyi değil. Beceri farkı var (düzey 2 +%12, düzey 0 −%4/−%12), ama sefer gürültüsü altında kalıyor. Literatürde bilinen sonuç; simülasyon yeniden üretti.

### Sıfır-kâr dengesi ve kâr paylaşımlı sözleşme
- **Oyuncu metni:** Herkesin bildiği bir rotada kâr, sermayenin faizinden pek fazla değildir. Kârın dörtte üçünü alıp zararın tamamını taşıyan colleganza ortağı, böyle bir rotada er geç kaybeder. Colleganza büyük kâr vadeden uzak seferlerin sözleşmesidir; sıradan bir buğday seferi için deniz ödüncü ya da ortaklık daha uygundur.
- **Ne zaman çıkar:** Oyuncu yatırımcı olarak kalabalık bir rotaya colleganza verdiğinde.
- **Kaynak:** Serbest giriş → sıfır ekonomik kâr (standart mikroekonomi); colleganza'nın Levant ticaretindeki yeri: Lane (1973) ⚠️; deniz ödüncü: Hoover (1926) ⚠️.
- **Simülasyonda:** [D5b3b](../experiments/D5b3b.md). İtibarla bile yatırımcı sözleşme başına yaklaşık −%4 kaybediyor; denge sefer getirisi sıfıra yakın.

### Credit rationing (neden faizi artırmak yetmez?)
- **Oyuncu metni:** Borç verdiğin tüccarlar batmaya başladığında faizi artırmak akla ilk gelen çaredir. Ama yüksek faize razı olanlar, en çok umut edenler ve en az kaybedecek olanlardır. Akıllı sarraf faizi değil, verdiği parayı kısar; kimi tanımıyorsa ona hiç vermez.
- **Ne zaman çıkar:** Oyuncu sermayedar olarak borç verdiğinde ve temerrütler arttığında; ya da borç almak istediğinde "bu kadar veremem" cevabı aldığında.
- **Kaynak:** Stiglitz & Weiss (1981), "Credit Rationing in Markets with Imperfect Information", *AER* 71(3).
- **Simülasyonda:** [D5b3c](../experiments/D5b3c.md). Alacaklı kayıp primini öğrenip faizi artırdı, ama senedin altında kazanmaya devam etti. Adverse selection'la açıklanabilir ⚠️ (doğrulanmadı).

### Fazla giriş ve boş kapasite (excess entry)
- **Oyuncu metni:** Kârlı bir rota dillere düşünce limana her ay yeni gemiler gelir. Kâr marjı aslında hâlâ iyidir, ama herkes ambarının onda birini doldurabilir. Pazarın derinliği bellidir, gemi sayısı değil. Kâr, kullanılmayan ambarlarda ve limanda boş bekleyen sermayede erir.
- **Ne zaman çıkar:** Oyuncu iyi bir marja rağmen yıllık kazancının düşük olduğunu fark ettiğinde; ya da yeni gemi almayı düşündüğünde.
- **Kaynak:** Mankiw & Whinston (1986), "Free Entry and Social Inefficiency", *RAND J.* ⚠️; Camerer & Lovallo (1999), "Overconfidence and Excess Entry", *AER* ⚠️.
- **Simülasyonda:** [D5b3c](../experiments/D5b3c.md) T2. Sermaye ağırlıklı sefer getirisi +%14, ama ambarın medyanı %9 dolu ve yıllık getiri ≈ %0. Literatürde bilinen; simülasyon yeniden üretti.

### İtibar bir disiplindir (Diamond)
- **Oyuncu metni:** Sarrafın sana ucuz borç vermesi, geçmişte ne kadar kazandığından çok bugüne kadar hiç batmamış olmandandır. Bu ün kaybedilmeye değmeyecek kadar değerlidir; onu taşıyan tüccar gözü kara bir sefere daha zor çıkar. Ünü olmayan genç tüccar ise önce pahalıya borçlanır.
- **Ne zaman çıkar:** Oyuncu ilk borcunu aldığında (yüksek faiz); ya da riskli bir seferle temiz sicilini kaybetmek üzereyken.
- **Kaynak:** Diamond (1989), "Reputation Acquisition in Debt Markets", *JPE* 97(4).
- **Simülasyonda:** Henüz yok. Tartışılıyor: S-015.

### Çarpık kazanç: tipik tüccar ile ticaretin kendisi
- **Oyuncu metni:** Rialto'da herkes ticaretin çok kazandırdığını söyler, ve haklıdır: ticarete konan her yüz duka yılda on iki-on üç duka getirir. Ama tüccarların yarısı batar ya da kaybederek çekilir. Kazancın yarısından fazlasını en iyi onda biri toplar. "Ticaret kârlı mı?" ile "ben kazanır mıyım?" ayrı sorulardır.
- **Ne zaman çıkar:** Oyuncu tüccar olmaya karar verirken; ya da limandaki başarılı tüccarlara bakıp kendi beklentisini kurarken (survivorship bias).
- **Kaynak:** Moskowitz & Vissing-Jørgensen (2002), private equity premium puzzle ⚠️; Hamilton (2000) ⚠️.
- **Simülasyonda:** [D5b3d](../experiments/D5b3d.md) T1. Toplam sermaye getirisi %12,8, ömür boyu getiri medyanı −%1,4, tüccarların %52'si zararlı.

### Gemi fiyatı: dipte ucuz, tepede pahalı (Tobin's q, batık maliyet)
- **Oyuncu metni:** Bir geminin değeri tersanedeki bedeli değil, onunla kazanılacak paradır. Ticaret iyiyken satılık gemi bulunmaz: tersanenin önünde sıra vardır, aceleci olan dışarıdan pahalı gemi alır. Ticaret kötüyken limanda bağlı gemiler çürür, kereste fiyatına alıcı aranır. Bu yüzden kötü günde çok az kişi gemisini satar: zararına satmaktansa bekler. Sabırlı yatırımcı ise dipte ucuz gemi toplar.
- **Ne zaman çıkar:** Oyuncu ilk gemisini alırken; bir patlama ya da durgunluk sırasında limandaki gemi ilanlarına bakarken.
- **Kaynak:** Tobin (1969) ⚠️; Dixit (1989), *JPE* 97(3) ⚠️; Stopford, *Maritime Economics* ⚠️; Lane (1934); Gluzman (2021).
- **Simülasyonda:** [D5b3j](../experiments/D5b3j.md) (Ö3).

### Time-to-build: geminin gelmesi zaman alır
- **Oyuncu metni:** Tersaneye gemi ısmarlayan, ticaretin bugünkü değil, gemi suya indiğinde olacak hâline bahse girer. Herkes aynı anda ısmarlarsa tersanenin önünde sıra uzar; gemiler geldiğinde patlama çoktan sönmüş olabilir. Hazır gemi bu yüzden değerlidir: iyi günde ikinci el gemi yeni bedelinden pahalıya satılabilir. Ucuz yabancı gemi ise ancak beklemeyi göze alana ucuzdur.
- **Ne zaman çıkar:** Oyuncu gemi ısmarlarken; tersane kuyruğu uzadığında; yabancı gemi ile hazır gemi arasında seçim yaparken.
- **Kaynak:** Kydland & Prescott (1982) ⚠️; Kalouptsidi (2014), *AER* 104(2); Tsolakis (2005).
- **Simülasyonda:** Tersane kuyruğu [D5b3j](../experiments/D5b3j.md)'de var. Ucuz ve geç yabancı gemi önerisi: S-022 ([ship-life-piracy-16c](../research/history/ship-life-piracy-16c.md)).

### Korsan yüzyılı: tüccar yoksa korsan da yok
- **Oyuncu metni:** Büyük donanmalar İnebahtı'dan sonra limanlarına çekildi; savaşın yerini korsan aldı. Ateşkesler imzalandı ama korsan ateşkes tanımaz: ona göre bu savaş değil, geçim. Kuzeyden gelen gemiler de hem tüccar hem korsan. Denizde korsanın çoğalması ticaretin ölmediğini de gösterir: avlanacak gemi olmasa korsan da olmaz.
- **Ne zaman çıkar:** 1580'ler sonrası; sigorta primleri yükseldiğinde; oyuncunun gemisi ilk kez yakalandığında.
- **Kaynak:** Braudel, *La Méditerranée* II ⚠️; Fontenay ("korsan yüzyılı" 1580-1680); Tenenti (1967).
- **Simülasyonda:** Henüz yok; S-022 (yıla bağlı korsan baskısı).

### Büyük liman, küçük iskele: neden her mal Venedik'ten geçer?
- **Oyuncu metni:** Büyük nave ton başına ucuza taşır ama doldurması zordur. Derin bir limana, kalabalık bir pazara ihtiyaç duyar. Küçük marciliana her iskeleye girer ama ton başına pahalıdır. Bu yüzden mal küçük iskelelerden teknelerle toplanır, büyük limanda büyük gemilere yüklenir, uzak limanda yine tekneyle dağıtılır. Bir kez kurulan merkez kolay değişmez: tüccar oradadır, çünkü herkes oradadır.
- **Ne zaman çıkar:** Oyuncu küçük bir iskeleden ilk yükünü aldığında; büyük bir gemi alırken; Split scala'sı ya da Livorno serbest limanı gibi bir olay merkezleri yerinden oynattığında.
- **Kaynak:** Taaffe, Morrill & Gould (1963); Fujita & Mori (1996), *JDE*; Horden & Purcell (2000); van Lottum (2014).
- **Simülasyonda:** Henüz yok; [trade-structure](../design/trade-structure.md) M1-M3.

### Sabit maliyet ve günlük karar: masraf neyi değiştirir?
- **Oyuncu metni:** Tayfanın ücreti ve kumanyası, gemi limanda da yatsa denizde de gitse her gün ödenir. Bu yüzden hangi yükü alacağına ya da hangi limana gideceğine karar verirken bu masraf işe yaramaz: her seçenekte aynıdır. Ama gemi tutup tutmamaya karar verirken her şeydir. Masraflar arttığında tüccarlar seferlerini değiştirmez; zayıf olanlar gemisini bağlar ve denizdeki gemi azalır. Limana uğramanın, malı karaya çıkarmanın bedeli ise başkadır: her uğrakta ödenir, bu yüzden uğrak kararını değiştirir.
- **Ne zaman çıkar:** Oyuncu ilk kez tayfa ücretini ödediğinde; masraflar arttığında piyasadan çekilen gemiler görüldüğünde.
- **Kaynak:** Standart firma teorisi (kısa dönemde sabit maliyetin üretim kararına etkisizliği, uzun dönemde giriş-çıkış) ⚠️; Jones (1998), Bristol gemiciliği.
- **Simülasyonda:** [M2](../experiments/M2.md) PC/PL: maliyet üç katına çıkınca filo %24 küçüldü, gemi başına davranış değişmedi.

