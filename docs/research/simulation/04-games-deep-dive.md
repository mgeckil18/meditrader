# 04 — Oyunlarda Ekonomi: Derinlemesine
> Durum: taslak (derin araştırma, 2. tur)
> Son güncelleme: 2026-10-22
> İlgili: [ilk tur oyun incelemesi](../games/trade-game-mechanics.md), [00-sentez](00-synthesis.md)

İlk turda incelenen oyunlara (Offworld, Patrician, Rise of Venice, Victoria 3, EU4, X4, EVE, Ultima Online, Bannerlord, Taipan, Uncharted Waters) ek olarak yeni oyunlar ve ekonomi tasarımının tekrarlayan kalıpları.

---

## 1. Yeni incelenen oyunlar

### Victoria 2 (Paradox, 2010)
- Dünya pazarı arz-talep modeli var. Kapitalistler, her eyalette üretilebilir malların kârlılığını hesaba katarak yatırım yapıyor. ([Giant Bomb](https://www.giantbomb.com/victoria-2/3030-27917/))
- **Bilinen sorun:** Oyuncu anlatımlarına göre büyük bir zanaatkâr nüfus (Çin örneği) dünya pazarına bağlandığında hammaddeyi tüketiyor ve küresel talebi çökertiyor. Kök neden olarak dünyadaki sabit para miktarı gösteriliyor ([AH forum](https://www.alternatehistory.com/forum/threads/victoria-ii.160516/page-338)). Bu bir forum anlatımı, doğrulanmamış.
- **v1.3 yaması:** Fiyatlar taban fiyatın %20'si ile %500'ü arasına sınırlandı; bazı malların talebi arz-talep dengesini düzeltmek için düşürüldü. ([Gamepressure](https://www.gamepressure.com/download/victoria-ii-v13-patch/zf7f20))

**Ders:** Ekonomideki **tek bir büyük oyuncu** (Çin zanaatkârları gibi) tüm sistemi bozabilir. Bizim için bu oyuncu İstanbul olabilir: dev bir tüketim merkezi. Ölçek parametreleri dikkatle ayarlanmalı. Sabit para miktarı da bir tuzak: para arzı ekonomiyle birlikte büyümeli (bkz. 01 §9).

### Starsector (Fractal Softworks)
- Pazar nüfusu arz ve talebin büyüklüğünü belirler. Sanayiler hangi malların üretileceğini belirler ve mallar ihtiyacı olan pazarlara ihraç edilir.
- **Kıtlık ve fazlalık:** Ticaret filoları saldırıya uğrayıp kargoyu kaybederse ya da erişim zayıfsa (talep 5, ithal edilebilen 3 gibi) kıtlık oluşur. Oyuncu kıtlıkta sınırlı miktarı çok yüksek fiyata satabilir.
- %30 açık pazar gümrüğü var. Karaborsa gümrükten kaçınır ama şüphe uyandırır: aranma ve itibar kaybı riski.
- Düşük istikrar karaborsayı büyütür ve pazarı baskınlara açık hale getirir.
- ([Starsector wiki: Market](https://starsector.wiki.gg/wiki/Market), [Commodities](https://starsector.wiki.gg/wiki/Commodities), [Fractal Softworks blog](https://fractalsoftworks.com/2016/04))
- Geliştirici: "Gayet basit arz-talep işleri, ama gerçekten çalışmasını sağlamak hiç de öyle değil."

**Dersler:**
- **Fiziksel ticaret filoları + saldırı = kıtlık** zinciri bizim korsanlık mekaniğiyle birebir uyumlu. NPC gemilerinin batması gerçek kıtlıklar yaratmalı.
- **Karaborsa ve kaçakçılık:** Gümrükten kaçmanın riski şüphe ve itibar kaybıdır. 1594 Osmanlı tahıl yasağı sonrası kaçakçılık tarihsel karşılığı.
- **"Erişilebilirlik"** soyut bir parametre olarak kullanışlı: liman kapasitesi, güvenlik, mesafe.

### Space Rangers 2 (Elemental Games, 2004)
- Yüzlerce gezegende fiyatlar basit arz-talebe, yerel saldırılara ve **Galaksiler Arası Haber Ağı'nda** duyurulan rastgele olaylara (kıtlık, salgın) göre değişiyor. ([Wikipedia](https://en.wikipedia.org/wiki/Space_Rangers_(video_game)), [GameSpot](https://www.gamespot.com/space-rangers-2-rise-of-the-dominators/user-reviews/2200-459489/))
- NPC gemileri kendi işlerinde dolaşıyor. Savaşlar senaryosuz; oyuncu karışsa da karışmasa da sürüyor. Her NPC'nin kendi yetenekleri, hedefleri ve ilişkileri var.
- İlk oyunda oyuncunun ve yapay zekâ gemilerinin alımları fiyatı yükseltiyordu. Bir forum görüşüne göre 2. oyunda ekonomi değişimleri azaltıldı, böylece bir malı alıp satan yakın gezegeni bulmak kolaylaştı.

**Dersler:**
- **Haber ağı + rastgele olaylar + fiyat etkisi** bizim oyunun neredeyse bire bir prototipi. "Dünya senin yokluğunda da yaşıyor" hissi bu oyunun en çok övülen yanı.
- 1'den 2'ye geçişte oynaklığın **azaltılması** önemli bir ders: çok oynak ekonomi oyuncuyu yorar. Okunabilirlik bir tasarım hedefi.

### Port Royale 4 (Gaming Minds, 2020)
- Ayrıntı: [02 §2](02-market-mechanisms.md).
- İşletmeler her gün üretip yerel pazarda o anki fiyattan satıyor; kâr edemeyen işletme kapanıyor. Yapay zekâ rakipleri aynı pazarlarda üretim yapıyor.
- Hazine filosu geçtikten hemen sonra, pazar boşken başkentte sömürge malı satmak çok kârlı (tek bir forum kaynağı). Bu, **tahmin edilebilir olayların fırsat yaratması** örneği.
- Eleştirmenler: varsayılan alış-satış değerleri neredeyse her zaman kâr için yeterli. Yani **derinlik eksik**.

**Ders:** Fiyat sistemi derin olsa bile, "varsayılan davranış kârlıysa" oyuncunun düşünmesine gerek kalmaz. Bizde de kârın kolay olmaması lazım: K-001'deki "acımasız" sözünün ekonomik anlamı bu.

### Prosperous Universe (Simulogics)
- Tamamen oyuncu güdümlü ekonomi; NPC ve senaryolu olay yok. Her malzeme ya üretilmeli ya da başka oyuncu şirketlerinden satın alınmalı. Fiyatlar 7/24 gerçek zamanlı borsalarda arz ve talebe göre belirleniyor. ([Worthplaying](https://worthplaying.com/article/2018/12/17/news/112232-prosperous-universe-enters-early-access-screens-trailer/), [press kit](https://press.simulogics.games/prosperousuniverse/))
- Borsası olmayan gezegende üretim yapıyorsan malı pazara taşımak zorundasın. ([QT3](https://forum.quartertothree.com/t/best-games-with-production-chains/143887/117))
- Bir güncellemeyle iş ortakları arasında fiyatın önceki ortalamadan sapmasını sınırlayan **fiyat garantileri** eklendi. ([MassivelyOP](https://massivelyop.com/?p=240405))

**Ders:** Saf oyuncu ekonomisi MMO'da çalışıyor, ama tek oyunculu oyunda bu rolü NPC'ler doldurmalı. Fiyat garantisi bir **sözleşme** mekaniği; bizim vadeli sözleşmelerimiz (commenda, ön ödemeli alım) için ilham kaynağı.

### RuneScape Grand Exchange (Jagex)
- Merkezi emir eşleştirme borsası. Kılavuz fiyatlar günde en fazla %5 değişebiliyor. ([RS Wiki](https://runescape.wiki/w/User:PointyBot))
- Düşük hacimli malların fiyatları birkaç günde, hatta haftada bir güncelleniyor ve yanlış olabiliyor. ([OSRS Wiki](https://oldschool.runescape.wiki/w/Grand_Exchange))
- Jagex büyük çaplı manipülasyon olduğunda müdahale hakkını saklı tutuyor.
- Bir geliştiriciye göre NPC dükkân fiyat tavanları manipülasyona karşı bir güvenlikti, ama birçok mal tavanda takılı kaldı. ([RS Wiki: Shop](https://runescape.fandom.com/wiki/Shop))

**Dersler:**
- **İnce piyasa (az işlem) = güvenilmez fiyat.** Bizde nadir mallarda (örneğin bir limanda nadiren görülen bir baharat) fiyat inançları geniş olmalı.
- Sert tavanlar fiyatların tavana yapışmasına yol açar. Yumuşak sınır önerimizi (01 §8) destekler.
- **Manipülasyon** tek oyunculu oyunda bir "özellik" olabilir. Geç oyunda pazar köşeleme (cornering) oyuncu stratejisidir. Ama sistem buna tepki vermeli: rakipler, devlet müdahalesi, itibar.

### Eco (Strange Loop Games, 2018)
- Simüle edilmiş bir ekosistemde medeniyet kurmak. Kirlilik ve aşırı hasat kalıcı etkiler bırakıyor. Uzmanlaşma ticareti zorunlu kılıyor. Oyuncular kendi para birimleriyle dükkân açıyor, sözleşme imzalıyor, parlamentoda yasa çıkarıyor; sunucu bu yasaları otomatik uyguluyor. ([TechRaptor](https://techraptor.net/content/indie-interview-john-krajewski-strange-loop-games-eco), [Gamedeveloper](https://www.gamedeveloper.com/design/building-a-global-survival-game))
- Tasarımcı: "Neden ekosistem simülasyonu izlenimi verelim ki, gerçekten bir tane yaratabiliyorsak?"

**Ders:** "Gerçekten simüle et, sahte yapma" felsefesi bizimkine yakın. Ama Eco'nun oyuncuları simülasyon verisini kanıt olarak kullanıyor, yani **simülasyonun okunabilir olması** oyunun parçası. Bizde de oyuncu "neden tahıl pahalı?" sorusunun cevabını bulabilmeli (haberler, defterler).

### Dwarf Fortress (Bay 12 Games)
- Bir dönem cüce ekonomisi (para, maaş, kira) eklendi, sonra kaldırıldı. Topluluk anlatımlarına göre gerekçeler oyunu eğlencesiz yapması ve cücelerin sürekli beş parasız ve mutsuz kalması. ([Steam](https://steamcommunity.com/app/975370/discussions/0/7093810789008385736)) Resmî bir açıklama bulunamadı.

**Ders:** Ekonomi **oyuncunun hissetmediği** bir yük oluşturuyorsa kaldırılır. Her ekonomi mekaniği "oyuncu bunu nasıl yaşar?" testinden geçmeli.

## 2. Tekrarlayan tasarım kalıpları (oyunlardan)

| Kalıp | Oyunlar | Açıklama | Bizim için |
|---|---|---|---|
| **Stok → fiyat formülü** | Patrician, Port Royale, Starsector, Elite | Fiyat = f(stok/hedef) | Kitlesel talep katmanında kullanılabilir |
| **Taban fiyat + bant** | Victoria 2/3, RuneScape | Fiyat bir aralıkta tutulur | Yumuşak sınır olarak |
| **Fiziksel taşıma** | X4, EVE, Starsector, Prosperous Universe | Mal gerçekten gemide; batarsa kaybolur | ✅ Çekirdek ilke |
| **Haber ve olay ağı** | Space Rangers 2, Offworld | Olaylar duyurulur, fiyatı etkiler | ✅ Haberler gecikmeli ve fiziksel taşınır |
| **Kıtlık primi** | Starsector, Patrician | Kıtlıkta sınırlı miktar çok yüksek fiyata gider | ✅ King-Davenant ile kalibre |
| **Karaborsa** | Starsector, Offworld | Yasak veya vergisiz ticaret, risk karşılığı | ✅ Kaçakçılık, ambargo |
| **Uzak, büyük ve istikrarlı pazar** | Offworld (offworld market) | Yüksek ama yavaş fiyat | Venedik veya İstanbul "merkez" pazarları |
| **Otomatik rota** | Patrician, Port Royale, X4 | Kur ve unut | ⚠️ Temsilciler insan olmalı, monotonluk riski |
| **Rakip yapay zekâ işletmeleri** | Port Royale, Offworld | Aynı kurallarla rekabet | ✅ K-004 |
| **Sabit para miktarı** | Victoria 2 | Para arzı sabit | ❌ Tuzak; para arzı büyümeli |
| **NPC yoktan alır veya satar** | Ultima Online | Sınırsız NPC alıcı | ❌ Tuzak |

## 3. Oyunlardan çıkan en önemli 7 ders

1. **Bilgi asimetrisi + fiziksel taşıma + risk = kalıcı fırsatlar** (EVE, Starsector). Bu bizim çekirdeğimiz.
2. **Verimli NPC arbitrajı fırsatları öldürür** (Bannerlord). NPC'leri kısıtla: bilgi, sermaye, kapasite, risk iştahı.
3. **Çok oynak ekonomi oyuncuyu yorar** (Space Rangers 1→2). Okunabilirlik hedefi.
4. **Varsayılan davranış kârlıysa derinlik kaybolur** (Port Royale 4). Kâr, düşünmeyi gerektirmeli.
5. **Kaynak ve yutak dengesi** (Ultima Online, Victoria 2). Para ve mal muhasebesi baştan kurulmalı.
6. **Ölçek tuzağı** (Victoria 2'deki Çin). Dev aktörler sistemi bozabilir; İstanbul'a dikkat.
7. **Hissedilmeyen karmaşıklık değersizdir** (Dwarf Fortress). Her mekanik oyuncu deneyimine bağlanmalı.

## 4. İncelenmeyi bekleyenler

- **Sunless Sea** (metin ağırlıklı atmosfer, risk ve keşif; anlatı ile ticaretin birleşimi)
- **Star Traders: Frontiers** (metin ağırlıklı RPG ticaret, mürettebat yönetimi)
- **Crusader Kings 3** (hane, varis, karakter özellikleri; S-002 için)
- **Kenshi** (bölgesel ekonomi, NPC kervanları)
- **Holdfast / Merchant of Venice gibi küçük indie ticaret oyunları** (Steam'de "trading sim" etiketi taranabilir)
