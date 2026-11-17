# Codex: Davranışsal Ekonomi ve Bilgi
> Son güncelleme: 2026-10-23 · Biçim: [README](README.md)

---

### Grossman-Stiglitz paradoksu (bilginin değeri)
- **Oyuncu metni:** Herkes her şeyi bilseydi kimse kâr edemezdi. Kâr, başkalarından önce ve daha doğru bilenindir. Haber almak masraflıdır, ama bilmemek daha masraflıdır.
- **Ne zaman çıkar:** Oyuncu ilk kez bir haber için para ödediğinde ya da bir temsilci tuttuğunda.
- **Kaynak:** Grossman & Stiglitz (1980); Stigler (1961).
- **Simülasyonda:** [D3](../experiments/D3.md): bilgili tüccar yılda 11-23 puan fazla kazanıyor.

### Search costs ve fiyat dağınıklığı
- **Oyuncu metni:** Aynı mal aynı şehirde farklı fiyatlara satılır, çünkü her dükkânı gezmek zaman alır. Şehre yabancı olan daha pahalıya alır.
- **Ne zaman çıkar:** Oyuncu yeni bir limana ilk kez geldiğinde.
- **Kaynak:** Stigler (1961).

### Bazaar economy ve clientelization
- **Oyuncu metni:** Pazarda bilgi kıt ve değerlidir. Tüccarlar bunu, aynı kişilerle tekrar tekrar iş yaparak (müşterileşme) ve uzun pazarlıklarla aşar.
- **Ne zaman çıkar:** Oyuncu bir dükkâncıyla ilişki kurduğunda.
- **Kaynak:** Geertz (1978).

### Loyalty (sadakat)
- **Oyuncu metni:** Aynı balıkçıdan alan, iyi günde de kötü günde de öncelik görür.
- **Ne zaman çıkar:** Oyuncunun bir dükkâncıyla ilişkisi belirgin şekilde güçlendiğinde.
- **Kaynak:** Kirman & Vriend (2001), Marsilya balık pazarı.

### Reputation ve koalisyonlar
- **Oyuncu metni:** Uzak limandaki temsilcini dürüst tutan şey mahkeme değil, onu dolandırırsa topluluktaki hiçbir tüccarın onu bir daha işe almayacak olmasıdır.
- **Ne zaman çıkar:** Oyuncu ilk temsilcisini tuttuğunda.
- **Kaynak:** Greif (1989, 1993), Mağribi tüccarları; tartışma: Edwards & Ogilvie (2012).
- **Tarihsel örnek:** 11. yy Mağribi tüccarları; Trivellato (2009), Sefarad ağları.

### Information cascade
- **Oyuncu metni:** Önündeki üç tüccar biber yükledi diye sen de yüklersen, kendi bildiğini değil onların ne bildiğini sandığını izliyorsun demektir. Bazen hepsi aynı yanlışın peşindedir.
- **Ne zaman çıkar:** Birden çok tüccar aynı mal ve rotaya yöneldiğinde.
- **Kaynak:** Banerjee (1992); Bikhchandani, Hirshleifer & Welch (1992).

### Herding
- **Oyuncu metni:** Tüccarlar sürü gibi aynı yöne koşar. Sürüyle gitmek güvenli hissettirir, ama varış limanında herkes aynı malı satmaya çalışır.
- **Ne zaman çıkar:** Toplu varışlar bir pazarı çökerttiğinde.
- **Kaynak:** Scharfstein & Stein (1990); Kirman (1993), karınca modeli.
- **Simülasyonda:** [D3](../experiments/D3.md), [D5](../experiments/D5.md) #5.

### El Farol / minority game
- **Oyuncu metni:** Herkes küçük bir pazara gitmek ister. Herkes "nasılsa kalabalık olur" derse kimse gitmez; herkes "kimse gitmez" derse herkes gider. Kazanan, çoğunluğun yapmadığını yapandır.
- **Ne zaman çıkar:** Oyuncu kârlı ama küçük bir pazara mal götürmeyi düşündüğünde.
- **Kaynak:** Arthur (1994); Challet & Zhang (1997).
- **Simülasyonda:** [D5](../experiments/D5.md) "en kârlı niş" sorunu; [D5b](../experiments/D5b.md) B1-B2: rakip bilgisi olmadan bütün tüccarlar Korfu'da biberle kilitleniyor, söylenti ve limandaki gemilerin görünmesiyle çözülüyor.

### Level-k thinking / cognitive hierarchy
- **Oyuncu metni:** Acemi tüccar fiyata bakar. Usta tüccar, acemilerin ne yapacağına bakar. Büyük tüccar, ustaların ne yapacağına bakar.
- **Ne zaman çıkar:** Oyuncu rakiplerin rotaları hakkında haber aldığında.
- **Kaynak:** Nagel (1995); Camerer, Ho & Chong (2004).
- **Simülasyonda:** [D5b](../experiments/D5b.md) B3: düzey 0 tüccarlar yılda −%5, düzey 1-2 tüccarlar +%37-39.

### Threshold models
- **Oyuncu metni:** Bazıları ilk kıvılcımla harekete geçer, bazıları herkes geçince. Kalabalığın ne yapacağı, bu eşiklerin nasıl dağıldığına bağlıdır; küçük bir fark, sakin bir limanı panikle doldurabilir.
- **Ne zaman çıkar:** Bir haberle birlikte ani bir toplu hareket olduğunda.
- **Kaynak:** Granovetter (1978).

### Overconfidence
- **Oyuncu metni:** Duyduğu habere fazla güvenen tüccar fazla risk alır. Bazen kazanır, çoğu zaman kaybeder.
- **Ne zaman çıkar:** Oyuncu güvenilmez bir kaynaktan gelen haberle büyük bir sefere çıktığında.
- **Kaynak:** Odean (1998); Daniel, Hirshleifer & Subrahmanyam (1998); Barber & Odean (2000).
- **Simülasyonda:** [D5b](../experiments/D5b.md) B3: aşırı güvenli tüccarlar biraz daha az kazanıyor.

### Noise traders
- **Oyuncu metni:** Piyasada yanlış haberle, sezgiyle, alışkanlıkla iş yapanlar hep vardır. Onlar fiyatları oynatır, akıllı tüccara da fırsat bırakır.
- **Ne zaman çıkar:** Fiyat, haberlerle açıklanamayan biçimde oynadığında.
- **Kaynak:** De Long, Shleifer, Summers & Waldmann (1990).

### Risk, servet ve kayıp kaçınması
- **Oyuncu metni:** Zengin tüccar bir gemiyi kaybetmeyi göze alabilir, yoksul tüccar alamaz; o kâr peşinde değil, batmamanın peşindedir. Zarar etmiş tüccar ise zararını kapatmak için daha büyük kumar oynar.
- **Ne zaman çıkar:** Oyuncunun servet düzeyi belirgin şekilde değiştiğinde.
- **Kaynak:** Arrow (1965), Pratt (1964), DARA; Roy (1952), safety-first; Kahneman & Tversky (1979), prospect theory.

### Survivorship bias
- **Oyuncu metni:** Limanda gördüğün zengin tüccarlar, batanları göremediğin için ticareti olduğundan kârlı gösterir.
- **Ne zaman çıkar:** Oyuncu bir işe "herkes zengin oluyor" diye girmeyi düşündüğünde.
- **Kaynak:** Wald (1943, uçak hasarı analizi; genel bilgi ⚠️); finans literatüründe yaygın.
- **Simülasyonda:** [D3b](../experiments/D3b.md).

### Anchoring ve "olağan fiyat"
- **Oyuncu metni:** Tüccarlar yılların deneyimiyle bir "olağan fiyat" bilir. Bir kıtlık yılı bu bilgiyi bozmamalı; bozarsa, kıtlık bittikten sonra da pahalı alır.
- **Ne zaman çıkar:** Kıtlıktan sonra fiyatlar normale dönerken.
- **Kaynak:** Tversky & Kahneman (1974), anchoring.
- **Simülasyonda:** [D1g](../experiments/D1g.md), medyan hafıza.

### Thin market (ince pazar)
- **Oyuncu metni:** Küçük bir kasabada biberin fiyatı yüksek görünebilir, çünkü az bulunur. Ama orada günde bir avuç biber satılır. Gemini doldurup oraya götürürsen yüksek fiyattan, ama yıllarca satarsın. Fiyat kadar pazarın derinliği de önemlidir.
- **Ne zaman çıkar:** Oyuncu küçük bir limana büyük bir kargo götürmeyi düşündüğünde.
- **Kaynak:** Piyasa derinliği ve likidite: Kyle (1985) ⚠️; genel bilgi.
- **Simülasyonda:** [D5b](../experiments/D5b.md) B1, B5: Korfu biber tuzağı.

### Fundamentalist ve chartist beklentiler
- **Oyuncu metni:** Bazı tüccarlar geleceği haberlerden okur: "Sicilya'da hasat kötü, buğday pahalanacak." Bazıları fiyatın gidişinden: "Son aylarda hep yükseldi, yükselmeye devam eder." İkisi de bazen haklı çıkar; piyasayı ikisinin karışımı yönetir.
- **Ne zaman çıkar:** Oyuncu bir hasat haberi aldığında ya da fiyatlar haberle çelişen bir yöne gittiğinde.
- **Kaynak:** Brock & Hommes (1998); Frankel & Froot (1990) ⚠️.
- **Simülasyonda:** [D5b2](../experiments/D5b2.md), yuva B.

### Optimal stopping ve bekleme maliyeti
- **Oyuncu metni:** Malını bugün mü satarsın, yoksa fiyat düzelsin diye bekler misin? Beklemek bedavaya gelmez: paran malda, gemin limanda yatıyor. Bekleyeceğin süre uzadıkça, bugünkü kötü fiyat daha iyi görünmeye başlar.
- **Ne zaman çıkar:** Oyuncunun malı bir limanda birkaç gündür satılamadığında.
- **Kaynak:** McCall (1970); Stigler (1961) arama teorisi.
- **Simülasyonda:** [D5b2](../experiments/D5b2.md), yuva S.

### Heuristic switching (kural değiştirme)
- **Oyuncu metni:** Hiçbir tüccar geleceği bilmez; herkesin bir alışkanlığı vardır. Kimi geçen ayın fiyatına güvenir, kimi gidişata, kimi haberlere. Bir alışkanlık birkaç kez yanıltınca tüccar ondan vazgeçer, işe yarayana döner.
- **Ne zaman çıkar:** Bir NPC tüccarın tahmini art arda tutmadığında ya da oyuncu bir tüccarın "tarzını" öğrendiğinde.
- **Kaynak:** Anufriev & Hommes (2012), AEJ: Micro 4(4); Hommes (2011), JEDC 35.
- **Simülasyonda:** Aday (framework A10, S-014). Henüz test edilmedi.

### Negatif ve pozitif geri besleme
- **Oyuncu metni:** Herkes "Venedik'te buğday pahalanacak" derse, herkes oraya buğday taşır ve buğday ucuzlar: kehanet kendini yalanlar. Ama herkes "buğday pahalanacak" diye ambarına buğday doldurursa, buğday gerçekten pahalanır: kehanet kendini doğrular. İlki ticarettir, ikincisi istifçilik.
- **Ne zaman çıkar:** Fiyat söylentileri yayıldığında; kıtlıkta istifçilik başladığında.
- **Kaynak:** Heemeijer, Hommes, Sonnemans & Tuinstra (2009), JEDC 33(5); Bao, Hommes, Sonnemans & Tuinstra (2012), JEDC 36(8).
- **Simülasyonda:** [07-expectation-formation §4](../research/simulation/07-expectation-formation.md). D5a'daki dükkân ratchet'i kontrolsüz bir pozitif geri beslemeydi.

### Learning from experience (yaşanmışlık)
- **Oyuncu metni:** '87 kıtlığını yaşamış yaşlı tüccar her bahar ambarını doldurur, gençler ona güler. Herkes kendi gördüğüne kitaptan okuduğundan çok inanır.
- **Ne zaman çıkar:** Farklı yaşlarda ya da geçmişte tüccarların aynı habere farklı tepki verdiğinde.
- **Kaynak:** Malmendier & Nagel (2016), QJE 131(1).
- **Simülasyonda:** Aday (beklenti tarzı kişilik boyutu).

### Diagnostic expectations (habere aşırı tepki)
- **Oyuncu metni:** "Sicilya'da çekirge!" haberi gelince herkes en kötüsünü bekler, buğday bir haftada ikiye katlanır. Sonra hasarın sanıldığı kadar büyük olmadığı anlaşılır. Paniğe kapılmayan kazanır.
- **Ne zaman çıkar:** Dramatik bir arz haberi limana ulaştığında.
- **Kaynak:** Bordalo, Gennaioli & Shleifer (2018), JF 73(1); Kahneman & Tversky, representativeness.
- **Simülasyonda:** Aday, sonra.

### Herkes aynı limana koşarsa (El Farol)
- **Oyuncu metni:** Rialto'da herkes İskenderiye biberinin Venedik'te iyi para ettiğini konuşuyorsa, o biber Venedik'e sel gibi akar ve fiyatı düşer. En iyi fırsat çoğu zaman herkesin en iyi saydığı fırsat değildir. Ustalar, kalabalığın gitmediği yeri arar ya da kendi ağının bildiği limana yönelir.
- **Ne zaman çıkar:** Oyuncu çok konuşulan bir rotaya yük aldığında; ya da varış limanında birçok geminin aynı malı boşalttığını gördüğünde.
- **Kaynak:** Arthur (1994), El Farol bar problemi; McKelvey & Palfrey (1995), quantal response; congestion game.
- **Simülasyonda:** [D5b3d](../experiments/D5b3d.md). Kalabalık filo büyüklüğünden bağımsız; herkes aynı argmax'ı seçiyor. S-018.

### En parlak umut en çok yanıltandır (optimizer's curse)
- **Oyuncu metni:** On limandan gelen fiyat haberleri önünde. Birinde biber, ötekilerin yarısı fiyatına satılıyor gibi görünüyor ve oraya yelken açıyorsun. Ama o haber belki eski, belki şişirilmiş; en yüksek görünen fiyat çoğu zaman en çok yanılan habere aittir. Varınca bulduğun fiyat, umduğundan biraz düşüktür. Usta tüccar uzak ve eski haberi kendiliğinden biraz kırpar.
- **Ne zaman çıkar:** Oyuncu birçok seçenek arasından beklentisi en yüksek olanı seçtiğinde; özellikle bilgi eski ya da tek kaynaklıyken.
- **Kaynak:** Smith & Winkler (2006), "The Optimizer's Curse", Management Science 52(3); açık artırmada winner's curse (Capen, Clapp & Campbell 1971).
- **Simülasyonda:** [M2 I0+I1](../experiments/M2.md): yön değiştirilen limanların %56-61'inde fiyat beklenenden düşük çıktı.
