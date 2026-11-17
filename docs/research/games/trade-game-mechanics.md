# Ticaret Oyunlarında Ekonomi Mekanikleri
> Durum: taslak (ilk tur araştırma)
> Son güncelleme: 2026-10-22
> İlgili: [simülasyon teknikleri](../simulation/economy-simulation-techniques.md), K-004, K-006

Amaç: Benzer oyunların ekonomiyi nasıl kurduğunu, neyin işe yaradığını ve neyin bozulduğunu çıkarmak. Kaynakların çoğu basın, wiki ve geliştirici günlükleri. Formüller genelde yayımlanmamış, o yüzden çoğu bulgu nitel.

---

## 1. Offworld Trading Company (2016, Soren Johnson / Mohawk)

**Model:**
- Her kaynağın **tek bir piyasa fiyatı** var. Alım fiyatı yükseltir, satış düşürür. Fiyat tamamen oyuncuların (ve yapay zekânın) arz ve talebinden oluşur.
- İlk sürümde Age of Kings'teki gibi ayrı alım ve satım fiyatları vardı. Bunlar tek değere indirilince oyuncular "ucuza al, pahalıya sat" oynamaya başladı. Piyasa, oyunun kuralları ve oyuncu stratejisi tarafından eşit ölçüde sürülür hale geldi. ([Designer Notes #2](https://www.designer-notes.com/otc-designer-notes-2-free-markets/))
- **Offworld market:** Yörüngeye gönderilen mallar, yerel fiyatın 10-20 katı seviyesinde, daha istikrarlı ve ayrı bir pazarda satılır. Bu, "büyük ve uzak ama yavaş" bir pazarın örneği. ([OTC Designer Notes #12](https://www.designer-notes.com/otc-designer-notes-12-offworld-market/))
- **Rastgele olaylar** (kıtlık, bolluk) piyasaya kaos katar, böylece fiyatlar sadece oyuncular tarafından sürülmez. ([Designer Notes #11](https://www.designer-notes.com/otc-designer-notes-11-hacker-array/))
- **Karaborsa:** Sabotaj araçları satılır (hacker array ile yapay kıtlık yaratmak gibi).
- **Borç:** Temel ihtiyaçlar parası yetmese bile otomatik alınır ve borç birikir. Borç büyüdükçe hisse fiyatı düşer ve şirket satın alınmaya açık hale gelir. (Topluluk özeti, [Penny Arcade forum](https://forums.penny-arcade.com/discussion/196462/offworld-trading-company-new-trading-rts-by-soren-johnson))
- **Kazanma koşulu:** Rakiplerin hisselerini satın almak.
- Johnson'ın ekibi her gün seed'li bir meydan okuma yayımlayıp sonuçları analiz etti. (Bizim K-010 determinizm kararına paralel.) ([Shacknews](https://www.shacknews.com/article/93533/offworld-trading-company-taking-stock-in-space))

**Bizim için:** "Fiyat tek, herkes etkiler" ilkesi doğrudan uygulanabilir. Offworld bir maç oyunu (20-30 dakika); bizimki uzun soluklu. Bu yüzden Offworld'ün yüksek oynaklığını doğrudan almak yerine yavaşlatılmış bir versiyonu gerekir.

## 2. Patrician III / Rise of Venice (Ascaron / Gaming Minds)

**Model (oyuncu deneyimlerinden):**
- Şehirlerin temel ihtiyaçları var: yiyecek, giyim, barınma, iş. Arz edildikçe şehir büyür. Kıtlıkta fiyat yükselir. ([Steam tartışmaları](https://steamcommunity.com/app/33570/discussions/0/1780513643845057494))
- Temel mallar (bira, tahıl, balık, kereste, yün) ekonominin omurgası. Yapay zekâ da stok tutup geri alım yapıyor.
- Aynı şehirde aynı türden işletme sayısı arttıkça üretim bonusu var.
- **Kaptan becerisi** alım-satım fiyatını etkiliyor. Bu bir RPG unsuru ve bizim temsilci (fattore) fikrine yakın.
- **Rise of Venice:** Doğu Akdeniz'de 25 liman. Oyuncu tek gemiyle başlar ve Doge olmaya doğru yükselir. Venedik'in On'lar Konseyi'ndeki 10 aile ile ilişkiler sosyal ilerlemeyi belirler. ([PC Gamer](https://pcgamer.com/rise-of-venice-review), [GameSpot](https://www.gamespot.com/reviews/rise-of-venice-review/1900-6415468/))
- **Eleştiriler:** Öğrenme eğrisi dik, yardım belgeleri zayıf. "10 saat sonra angarya" eleştirisi var ([GameGrin](https://www.gamegrin.com/reviews/rise-of-venice-review/)). Tipik sorun şu: otomatik rotalar kurulduktan sonra oyun bir tabloyu yönetmeye dönüşüyor.

**Bizim için:**
- Rise of Venice bize en yakın tema. Siyasi yükseliş (konsey, aileler) güzel bir katman.
- Ama tycoon'a kayışı ve geç oyundaki monotonluk, bizim kaçınmak istediğimiz şeyin ta kendisi (K-001).
- Ders: otomatik rotalar "kur ve unut" olmamalı. Temsilciler insan olmalı ve kendi sorunlarını getirmeli.

## 3. Victoria 3 (Paradox, 2022)

**Model:**
- Her malın bir **taban fiyatı** var. Fiyat, alım emirleri ile satım emirleri arasındaki dengeye göre bu tabandan sapar. Talep arzı aşarsa fiyat yükselir, tersi olursa düşer. (Fiyatın taban etrafında belirli bir bant içinde kaldığı biliniyor; tam yüzdeler doğrulanmadı.) ([Dev Diary #9](https://admin-forum.paradoxplaza.com/forum/developer-diary/victoria-3-dev-diary-9-national-markets.1484917))
- Yerel tüketim alım emri, yerel üretim satım emri üretir.
- **Pazar erişimi:** Bağlantısı zayıf bölgeler yerel mallara daha bağımlıdır. Yerel fiyat ile pazar fiyatı arasındaki fark erişimle orantılı kapanır.
- **Ticaret rotası fiyatı (Dev Diary #54):** İhraç pazarındaki alış fiyatı, o pazarın ticaretsiz ve ticaretli fiyatlarının ortalamasıdır. İthal pazarında da aynı hesap yapılır. ([Dev Diary #54](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-54-trade-revisions))

**Bizim için:**
- Taban fiyat + bant + emir dengesi modeli basit, öngörülebilir ve hata ayıklaması kolay. Ama "ajan" değil "toplu" (aggregate) bir model.
- Ana tüketiciler (şehir nüfusu, köyler) için toplu model, tüccarlar için ajan modeli kullanan bir hibrit iyi bir aday. Bkz. [simülasyon teknikleri](../simulation/economy-simulation-techniques.md).

## 4. EU4 ticaret sistemi (Paradox, 2013)

**Model:**
- Ticaret fiziksel mal değil, **ticaret değeri** olarak modellenmiş. Bu değer sabit bir düğüm ağında tek yönde (aşağı akış yönünde) akar.
- Bir düğümden alınan pay, oradaki ticaret gücü payıyla orantılıdır. Tüccarlar ya değeri toplar ya da aşağı akışa yönlendirir. ([Paradox forum rehberi](https://admin-forum.paradoxplaza.com/forum/threads/oooh-shinies-a-guide-to-the-eu4-trade-system.707915/latest), [Steam](https://steamcommunity.com/app/236850/discussions/0/2727382174628442937))

**Bizim için:**
- EU4'ün ticaret modeli bizim için **fazla soyut**. Bir tüccarın gözünden fiyat, mal ve gemi gerekir. Ama EU4'ün **zaman akışı, harita ve olay sistemi** bizim referansımız (K-006).
- EU4'ün günlük tick performans çalışmaları, yapay zekâ ajanlarının en pahalı bileşen olduğunu ve maliyetin oyun ilerledikçe arttığını gösteriyor. ([EU4 Dev Diary, Aralık 2017](https://admin-forum.paradoxplaza.com/forum/developer-diary/eu4-development-diary-5th-of-december-2017.1058829))
- Binlerce ajanlı bir simülasyonda **ajan başına maliyet** baştan düşünülmeli.

## 5. X4: Foundations (Egosoft, 2018)

**Model:**
- Yüzlerce istasyon ve binlerce gemi arasında **fiziksel olarak taşınan** mallar var. Arz ve talebe göre değişen fiyatlar ve çok aşamalı üretim zincirleri var. NPC ekonomisindeki her şey (gemiler, istasyonlar dahil) kaynaktan üretiliyor. ([Steam sayfası](https://store.steampowered.com/app/392160/X4_Foundations/))
- İstasyonlarda alış fiyatı tavan, satış fiyatı taban olarak ayarlanıyor. Ticaret istasyonları arz ve talebi dengeleyen tampon depolar gibi çalışıyor. ([Steam tartışması](https://steamcommunity.com/app/392160/discussions/0/3829788180807473669))
- Oyuncu deneyimi: otomatik tüccarlar zaman zaman takılıyor ve "ticaret aramaya" devam ediyor. Karmaşık ajan davranışı hata ayıklamayı zorlaştırıyor.

**Bizim için:**
- "Her şey fiziksel olarak taşınır" ilkesi bilgi gecikmesiyle birleşince çok güçlü olur.
- Ama ajan davranışlarının izlenebilir olması (neden bu kararı verdi?) baştan bir gereksinim olmalı.

## 6. EVE Online (CCP, 2003)

**Model:**
- Bölgesel pazarlar var. Oyuncular sadece bulundukları bölgenin fiyatlarını görebilir. Malı insanlar taşımak zorunda ve bu zaman ile risk demek. Bu yüzden bölgeler arası fiyat farkları kalıcı oluyor. ([somebits](https://www.somebits.com/weblog/culture/games/eve/economics.html), [Sydney Üniv.](https://internet-policy-meco.sydney.edu.au/2014/07/economics-for-orcs-how-can-virtual-world-economies-inform-national-economies-and-those-who-design-them/))
- Arbitraj zamanla farkları daraltıyor. 2007'deki bir analizde bölgeler arası fiyat farkının zamanla azaldığı görülmüş. ([Marginal Revolution](https://marginalrevolution.com/marginalrevolution/2007/09/the-future-of-m.html))
- Ticaret birkaç merkez limanda yoğunlaşıyor. ([Guild Order wiki](https://guildorder.com/games/eve/wiki/the-market-and-regional-trade))
- Gemilerin yok edilmesi en büyük "para/mal yutağı".

**Bizim için:**
- **Bilgi asimetrisi + taşıma riski = kalıcı fiyat farkları.** Tasarımımızın kalbi bu. EVE bunu 20 yıldır çalışır halde gösteriyor.
- Merkez limanların doğal olarak oluşması da beklenmeli. Venedik, İstanbul ve İskenderiye bunlar olur.
- Batan gemiler ve kayıp mallar bizim de doğal yutağımız.

## 7. Ultima Online (Origin, 1997): bir başarısızlık dersi

- Kapalı bir kaynak ekonomisi tasarlandı. Oyuncular ise devasa miktarda istifçilik yaptı (bir karakterde 10.000'den fazla aynı gömlek), istif edilen kaynaklar yeniden doğmadı ve sistem tıkandı. ([Simpson 1999](https://gwern.net/doc/economics/1999-04-07-simpson-theingameconomicsofultimaonline.html), [Koster](https://www.raphkoster.com/?p=16263))
- NPC dükkânları gerçek pazarı olmayan malları satın alarak ekonomiyi **sübvanse etti**. Bu, yoktan para üretmek demek.
- Bir hata yüzünden altın kopyalanabildi ve enflasyon oluştu. Simpson'ın "Hacker Yasası": istismarlar düzeltmelerden her zaman daha hızlı bulunur.
- **Musluk ve gider (faucet/drain) modeli:** Para ve mal sisteme nereden giriyor, nereden çıkıyor? İkisi dengelenmezse enflasyon ya da kıtlık kaçınılmaz.

**Bizim için:**
- Her para ve mal kaynağı ile her yutak açıkça listelenmeli ve izlenmeli.
- "NPC her şeyi her fiyattan alır" kesinlikle olmamalı. Bu, K-004 ile de uyumlu.

## 8. Mount & Blade II: Bannerlord (TaleWorlds, 2020): kritik bir uyarı

- Köyler üretiyor, kervanlar şehirler arası arbitraj yapıyor. ([Geliştirici blogu](https://www.taleworlds.com/en/Games/Bannerlord/Blog/14))
- **En sık şikâyet:** Yapay zekâ kervanları arbitrajı o kadar verimli yapıyor ki fiyatlar her yerde eşitleniyor ve oyuncuya kâr kalmıyor. ([Steam](https://steamcommunity.com/app/261550/discussions/0/4068391194362364023))
- Yamalarla fiyatlar topluca çöktü, geç oyunda enflasyon patladı. ([Steam](https://steamcommunity.com/app/261550/discussions/0/3038228835125437347))

**Bizim için:** Bu, K-004 için **en önemli risk**. NPC tüccarlar oyuncuyla aynı kurallarla ve verimli oynarsa fırsatları oyuncudan önce kapatırlar. Fırsatları canlı tutan şeyler:
- **Bilgi gecikmesi:** NPC de haberi geç alır.
- **Kapasite ve sermaye kısıtı:** Bir NPC her fırsatı aynı anda kovalayamaz.
- **Risk iştahının çeşitliliği:** Herkes aynı fırsata koşmaz.
- **Sürekli şoklar:** Yeni fırsatlar doğar.
- **Uzmanlaşma:** Her NPC her malı ve rotayı bilmez.

## 9. Taipan! (1979) ve Drug Wars (1984): metin tabanlı atalar

- Döngü: bir yere git, bir şey al, başka yerde daha pahalıya sat, tekrarla. "Oyunlardaki en iyi küçük döngülerden biri." ([dev.to](https://dev.to/57u/from-dope-wars-to-spice-wars-ha9))
- Drug Wars'ta fiyatlar rastgele olaylarla patlayıp çöküyor; elindeki her mal belirsizlik taşıyor. ([KN-86](https://kn86-docs-gca3d.kinsta.page/influences/inspiration/drug-wars/))
- Taipan'ın geliştiricisi olay dağılımını elle ayarlamış. Olayların temposu tasarımın bir parçası. ([PalmDB](https://palmdb.net/content/files/games-strategy/taipan/Taipan.txt))

**Bizim için:** Metin aşamasında bile bu döngü eğlenceli olmalı. Eğer değilse, simülasyon ne kadar derin olursa olsun oyun eğlenceli olmaz.

## 10. Uncharted Waters 2 (Koei, 1993)

- 16. yüzyıl. Her limanın indirimli bir özel malı var. Bir hizbe bağlı limanlarda her işlemde vergi alınıyor, hizbin liderinden muafiyet belgesi alınırsa vergi düşüyor. Muhasebeci (bookkeeper) mürettebatı fiyatların yüksek olup olmadığını ve fırsatları söylüyor. ([ruwiki](https://ru.ruwiki.ru/wiki/Uncharted_Waters_2:_New_Horizons))

**Bizim için:** Vergi muafiyeti ve imtiyazlar (kapitülasyonlara benzer) ile yetenekli personelin bilgi sağlaması iyi fikirler.

---

## Sentez: oyunlardan çıkarımlar

| Çıkarım | Kaynak oyun | Bizdeki karşılığı |
|---|---|---|
| Tek fiyat, herkes etkiler | Offworld | Liman başına mal fiyatı, her işlem fiyatı oynatır |
| Bilgi asimetrisi + taşıma riski = kalıcı fırsatlar | EVE | Haber gecikmesi, fiziksel taşıma (K-004'ün can simidi) |
| Verimli NPC arbitrajı fırsatları öldürür | Bannerlord | NPC'lere bilgi, kapasite ve risk kısıtları |
| Musluk ve giderler dengelenmeli | Ultima Online | Para/mal kaynak-yutak envanteri, izleme |
| Otomasyon monotonluk getirir | Patrician / Rise of Venice | Temsilciler insan olmalı, sorun çıkarmalı |
| Taban fiyat + bant, hata ayıklaması kolay | Victoria 3 | Toplu tüketiciler için kullanılabilir |
| Olay temposu tasarlanmalı | Taipan, Offworld | Şokların sıklığı ve büyüklüğü ayarlanabilir parametre |
| Siyasi yükseliş katmanı | Rise of Venice | Venedik vatandaşlık sınıfları, loncalar (araştırılacak) |

## Açık bırakılanlar / sonraki tur

- Offworld fiyat formülünün ayrıntısı (fiyat birim başına ne kadar oynuyor?)
- Victoria 3 fiyat bandı yüzdeleri
- Port Royale 4, Sunless Sea (metin ağırlıklı atmosfer ve risk), Star Traders: Frontiers (metin ağırlıklı RPG ticaret), Crusader Kings (hane ve varis) incelenmedi.
