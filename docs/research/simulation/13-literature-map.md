# 13 — Deneylerin Literatür Karşılıkları
> Durum: taslak (sürekli güncellenir)
> Son güncelleme: 2026-10-30
> İlgili: [experiments/README](../../experiments/README.md), [lessons](../../process/lessons.md), CLAUDE.md kural 7b

**Amaç (kullanıcı, 2026-10-30):** Yaptığımız işlerin akademik literatürdeki karşılıkları. Her satır "literatürde bilinen X; simülasyon yeniden üretti" ya da "yöntemin karşılığı" biçiminde okunur. ⚠️ = bu oturumda kaynağın kendisine bakılmadı, künye bellekten.

## 2026-10-23 (cuma) çalışmaları

| İş | Ne yaptık / bulduk | Literatürdeki karşılığı | Kaynak |
|---|---|---|---|
| Yöntem: "yapı, parametre değil"; yuva bazlı mekanizma yarışması; ML en sonda | Mekanizmalar niteliksel ölçütlerle (stylized facts) yarıştırılır, parametre ayarı sona bırakılır | **Pattern-oriented modeling**: Model, birden çok gözlenen örüntüyü aynı anda üretebilmesine göre seçilir. **ABM validation**: stylized facts ile doğrulama. **ML ile kalibrasyon** (surrogate) | Grimm ve ark. (2005), *Science* 310; Fagiolo, Moneta & Windrum (2007), *Computational Economics* 30; Lamperti, Roventini & Sani (2018), *JEDC* 90 |
| D2: iki liman, anlık bilgi | Tek fiyat yasası; anlık bilgi + verimli NPC = fırsat yok | **Law of one price**, **spatial price equilibrium** (fiyat farkı = taşıma maliyeti). **Grossman-Stiglitz paradoksu**: bilgi bedavaysa bilgiye yatırımın getirisi yoktur, fiyatlar fırsat bırakmaz | Samuelson (1952), *AER* 42; Takayama & Judge (1971); Grossman & Stiglitz (1980), *AER* 70(3) |
| Getiri çerçevesi: senet ~%4, baz ticaret = senet + risk | Normal kâr = fırsat maliyeti + risk primi | **Normal profit**, uzun dönem rekabetçi denge; **risk premium** | Standart mikroekonomi; Venedik devlet borcu getirisi: Pezzolo ⚠️ |
| D3: bilgi gecikmesi | Bilginin değeri yılda +11-23 puan; en iyi beklenti: dağılım + olağana dönüş | **Economics of information** (arama ve bilginin değeri). **Regressive expectations** (olağana dönüş). Tarih: tüccar mektupları ve price current'lar | Stigler (1961), *JPE* 69(3); Nerlove (1958), *J. Farm Econ.* ⚠️; McCusker & Gravesteijn (1991) ⚠️ |
| D3b: senede bağlı serbest giriş-çıkış | Yavaş giriş = rant; sürü girişi = domuz döngüsü; bilgi avantajı dengede korunuyor | **Cobweb / hog cycle** (gecikmeli arz). **Giriş engeli → rant**. Bilgi avantajının korunması yine Grossman-Stiglitz | Hanau (1928); Ezekiel (1938), *QJE* 52(2); Bain (1956), *Barriers to New Competition* |
| İ11: fenomen ≠ artifact | Gerçek fenomenler (pork cycle) hata sayılmaz, sınıflandırılır | ABM'de **stylized facts** yaklaşımı (gerçek dünyada da görülen dalgalanma bir başarıdır) | Fagiolo ve ark. (2007) |
| D4: çok mal, ortak bütçe | LES + CES kazandı; income ve substitution effect birlikte; Labrousse etkisi kendiliğinden | **Linear Expenditure System** (geçim + üstü). **CES**. **Slutsky ayrıştırması**. **Labrousse**: ekmek pahalanınca manifaktür talebi çöker (Ancien Régime krizleri) | Stone (1954), *Economic Journal* 64; Arrow, Chenery, Minhas & Solow (1961), *REStat* 43; Labrousse (1944), *La crise de l'économie française* |
| Tüketici profilleri, 16. yy | 5 sınıf şablonu, 6 kent | **Tarihsel tüketim sepetleri** ve welfare ratio | Phelps Brown & Hopkins (1956), *Economica*; Allen (2001), *Explorations in Economic History* 38 |
| D4b: kent sınıfları | Kıtlıkta mal yoksuldan zengine akıyor; sınıflar lüks çöküşünü önlüyor | **Entitlement approach**: kıtlık, malın yokluğundan çok satın alma gücünün dağılımıdır | Sen (1981), *Poverty and Famines* |
| D4c: üretim zinciri (yün → kumaş) | Reçeteler, üretici havuzları, ücret aşamaları | **Input-output** (girdi-çıktı). Tarih: **putting-out system** (Verlagssystem) | Leontief (1936), *REStat* 18; putting-out: Kriedte, Medick & Schlumbohm (1981) ⚠️ |
| D5: ilk entegrasyon başarısız, toptan katman eksik | Parçalar ayrı ayrı çalışıyor, birlikte çalışmıyor | Model geliştirmede **modüler doğrulama**. Kuramsal bir sonuç değil, yöntem dersi | Grimm ve ark. (2005) |
| K-013, D5a: kurumsal toptan pazar (kapan / loggia) | Kapan, D5'in dört el müdahalesinin yerini aldı | **Market microstructure**: merkezi pazar, **call auction / clearing**. Tarih: Osmanlı kapanı, Rialto | O'Hara (1995), *Market Microstructure Theory*; Osmanlı kapanı: İnalcık ⚠️ |
| K-014: tüccar çeşitliliği, söylentiyle yayılan rakip bilgisi | Rakip bilgisi sistemi kurtarıyor | **Heterogeneous agent models** (HSM). **Economics of rumours**. **El Farol** | Brock & Hommes (1998), *JEDC* 22; Banerjee (1993), *REStud* 60; Arthur (1994), *AER* 84(2) |
| K-016, D5a2: rekabetçi perakende (logit + Lerner) | Marj kuramsal değerde; aktarım simetrik; rockets and feathers çıkmadı | **Logit talep altında farklılaştırılmış rekabet**. **Lerner endeksi** (marj = 1 / esneklik). **Rockets and feathers** (fiyat artışı hızlı, düşüşü yavaş aktarılır; bizde çıkmadı) | Anderson, de Palma & Thisse (1992); Lerner (1934), *REStud* 1; Bacon (1991), *Energy Economics* 13; Peltzman (2000), *JPE* 108 |
| K-017, D5a3: malı olmayan pazarın fiyatı | Açık teklif + sınırlı tâtonnement | **Walras tâtonnement** (fiyat, fazla talebe göre ayarlanır). **Posted offer** pazarları | Walras (1874); Plott & Smith (1978), *REStud* 45 ⚠️ |

## 2026-10-26/27 çalışmaları (bu oturum, kısa)

| İş | Literatürdeki karşılığı | Kaynak |
|---|---|---|
| D5b3d-e: kalabalık, rota seçimi | Congestion game, El Farol, QRE | [10](10-route-choice-coordination.md) |
| D5b3f: giren kuşak iyimser | Optimizer's curse; aşırı güven ve fazla giriş; survivorship bias; regression to the mean | Smith & Winkler (2006), *Management Science* 52; Camerer & Lovallo (1999), *AER* 89 |
| D5b3g: ortak eşik + hızlı çıkış → döngü | Iraksak cobweb; hysteresis bandının yokluğu | Ezekiel (1938); Dixit (1989) |
| K-029: credibility ağırlığı | Credibility theory / empirical Bayes | Bühlmann (1967), *ASTIN Bulletin* 4 |
| K-029: snapshot başlangıcı | ABM'de burn-in / warm-up period | Law & Kelton, *Simulation Modeling and Analysis* (warm-up) ⚠️ |
