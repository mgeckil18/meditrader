# Ekonomi Simülasyonu Teknikleri
> Durum: taslak (ilk tur araştırma)
> Son güncelleme: 2026-10-22
> İlgili: [oyun mekanikleri](../games/trade-game-mechanics.md), [determinizm](../../design/determinism.md), K-004, K-009, K-010

Amaç: "Canlı ekosistem" simülasyonunu kurmak için bilinen teknikleri ve tuzakları toplamak.

---

## 1. İki temel yaklaşım

| | Toplu (aggregate) model | Ajan tabanlı model |
|---|---|---|
| Fikir | Her pazar/mal için arz-talep denklemi; fiyat formülle güncellenir | Her tüccar/üretici kendi kararını verir; fiyat işlemlerden doğar |
| Örnek | Victoria 3, EU4 | Doran & Parberry, BazaarBot, X4, EVE (oyuncular) |
| Artı | Hızlı, öngörülebilir, dengelenmesi kolay | Gerçekten "canlı"; şaşırtıcı ortaya çıkan davranış |
| Eksi | Mekanik hissettirir; ajan yok, hikâye yok | Kaotik, dengelenmesi zor, pahalı, hata ayıklaması zor |

**Önerim: hibrit.**
- Şehir nüfusu, köyler, çiftçiler, zanaatkârlar gibi **kitle** üretim ve tüketimi toplu modelle yürür. Bunlar "Venedik'in günlük tahıl ihtiyacı X, stok Y" gibi talep ve arz kaynaklarıdır.
- **Tüccarlar, temsilciler, korsanlar, sigortacılar, bankacılar** gibi karar vericiler ajan olarak modellenir. Oyuncu da bunlardan biridir (K-004).
- Böylece ajan sayısı (yüzler ile birkaç bin arası) yönetilebilir kalır, kitlesel davranış ise tutarlı olur.

## 2. Doran & Parberry: "Emergent Economies for Role Playing Games" (2012)

Kaynak: [IJIGS Vol.7 No.3](https://ianparberry.com/pubs/econ.pdf). Bu alanda en çok atıf alan ve uygulanan çalışma. Açık kaynak uygulaması BazaarBot. ([gamedev.net](https://gamedev.net/tutorials/programming/general-and-gameplay-programming/bazaarbot-an-open-source-economics-engine-r3206))

**Mekanizma:**
1. Her ajanın bir **mesleği** var (üretim kuralları: girdi sepeti → çıktı sepeti) ve sınırlı bir envanteri var.
2. Her ajan her mal için bir **fiyat inancı** tutar. Bu bir aralıktır [alt, üst]: ortası tahmini, genişliği belirsizliği temsil eder. Teklif verirken bu aralıktan rastgele bir değer seçilir.
3. **Teklif miktarı:** Ajan, piyasa ortalamasının kendi gözlemlediği işlem aralığındaki konumuna bakar (ucuz mu, pahalı mı?) ve buna göre ihtiyacının daha azını ya da fazlasını teklif eder.
4. **Takas odası (clearing house):** Her turda tüm alış ve satış teklifleri toplanır. Teklif defterleri karıştırılır, fiyata göre sıralanır, en yüksek alış en düşük satışla eşleştirilir. İşlem fiyatı iki teklifin ortalamasıdır (çift taraflı açık artırma / double auction).
5. **İnanç güncellemesi:** Kabul edilen teklif inancı daraltır (güven artar). Reddedilen teklif inancı genişletir ve ortalamaya doğru kaydırır. Stoğu çok azalmış bir ajan agresif şekilde yükseltir. Büyük arz-talep dengesizliği varsa önceden kaydırır.
6. **Sabit gider / boşta kalma vergisi:** Verimsiz ajanlar yavaşça batar.
7. **İflas ve yerine koyma:** İflas eden ajan, son 8-15 turun ortalamasına göre en kârlı meslekteki yeni bir ajanla değiştirilir. Böylece meslek dağılımı piyasa koşullarına uyum sağlar.

**Bulgular:**
- Fiyatlar ortak bir inanca yakınsar. Şoklar yeni bir dengeye kaydırır.
- 5 yıllık günlük simülasyonlar kararlı çıkmış.
- Başlangıç koşullarına **kaotik duyarlılık** var: aynı kurallar, farklı seed, farklı ama benzer genel davranış.
- **Kapalı olmayan ekonomiler** (bir mal tüketiliyor ama hiç üretilmiyor) hiçbir sistemle iyi sonuç vermez.

**Bizim için değerlendirme:**
- ✅ Fiyat inancı aralığı, bizim **bilgi gecikmesi** fikrine birebir uyuyor. Eski haber = geniş ve kaymış inanç aralığı.
- ✅ İflas, yerine koyma ve meslek değiştirme, "acımasız ekosistemi" doğal olarak üretir.
- ⚠️ Model **tek bir merkezi pazar** varsayıyor. Bizde çok sayıda liman ve aralarında taşıma var. Bu yüzden her limanın kendi takas odası olur ve tüccarlar arasında hareket eder.
- ⚠️ "En kârlı mesleğe dönüşen yeni ajan" bizde **tarihsel olarak sınırlanmalı**. Bir Venedikli köylü bir gecede Ceneviz bankacısı olmaz.
- ⚠️ Toplu talep tarafı (şehir nüfusu) bu modelde yok. Hibrit yaklaşımla eklenir.

## 3. Basit öğrenen alıcı-satıcı modeli (Jason Fantl)

Kaynak: [Simulated Economy (1)](https://jasonfantl.com/posts/Simulated-Economy-(1)/)

- Her aktörün bir **kişisel değeri** ve bir **beklenen piyasa fiyatı** var. Kişisel değer beklenenden yüksekse alıcıdır, değilse satıcı.
- Başarılı işlemden sonra alıcı beklentisini düşürür, satıcı yükseltir. Başarısızlıkta tersi olur.
- Fiyatlar kişisel değerlerin **medyanına** yakınsıyor, ortalamasına değil.
- **Ders:** Çok basit bireysel kurallar bile piyasa benzeri yakınsama ve uyum üretiyor. İlk prototip için iyi bir başlangıç noktası.

## 4. Musluklar, giderler, dönüştürücüler (Machinations / Dormans)

Kaynaklar: [Dormans AAAI](https://cdn.aaai.org/ojs/12477/12477-52-16005-1-2-20201228.pdf), [Adrian Crook](https://adriancrook.com/?p=8170)

- Oyun ekonomisi şu dört işlevle tanımlanabilir:
  - **kaynaklar (sources / musluklar):** sisteme bir şey katar
  - **yutaklar (sinks / giderler):** sistemden bir şey çıkarır
  - **dönüştürücüler (converters):** bir şeyi başka bir şeye çevirir
  - **tüccarlar (traders):** el değiştirtir
- **Pozitif geri besleme** başarıyı büyütür (zengin daha zengin olur). **Negatif geri besleme** dengeler.
- Bizim oyunda pozitif geri besleme doğal olarak güçlü: sermaye ve itibar kâr getirir, kâr da daha çok sermaye ve itibar getirir. **Geç oyunda dengeleyici negatif geri beslemeler** şart:
  - büyüdükçe dikkat çekmek (vergiler, kıskanç rakipler, devletin ilgisi)
  - temsilci güvenilirliği sorunları
  - yönetim maliyeti

**Bizim oyun için ilk kaynak-yutak envanteri (taslak):**

| Tür | Para | Mal |
|---|---|---|
| Musluk | Yeni gümüş (Amerika → İspanya → Ceneviz), devlet harcamaları, maaşlar | Hasat, madenler, zanaat üretimi, Doğu'dan gelen baharat ve ipek |
| Yutak | Vergiler, gümrükler, haraçlar, fidyeler, rüşvetler, lüks tüketim, Doğu'ya akan gümüş (ticaret açığı) | Tüketim, batan gemiler, çürüme ve bozulma, savaş yağması, yangın |
| Dönüştürücü | Kredi, senet, sigorta (risk ↔ para) | Zanaat (yün → kumaş, ipek → kadife), gemi inşası |

Not: Akdeniz'in Doğu ile ticareti tarihsel olarak **kronik bir gümüş açığıydı**. Avrupa gümüşü Doğu'ya akıyordu. Bu, bizim doğal ve tarihsel para yutağımız olabilir.

## 5. Bilinen başarısızlık kalıpları

| Kalıp | Örnek | Önlem |
|---|---|---|
| Fiyat eşitlenmesi (fırsat ölümü) | Bannerlord kervanları | Bilgi gecikmesi, kapasite kısıtı, heterojen ajanlar, şoklar |
| Enflasyon | Ultima Online, Bannerlord geç oyun | Kaynak-yutak dengesi, izleme panosu |
| İstifçilik ve tıkanma | Ultima Online | Depolama maliyeti, bozulma, sermayenin fırsat maliyeti |
| Yoktan sübvansiyon | Ultima Online NPC dükkânları | NPC'ler sadece gerçekten ihtiyaç duyduğunu alır |
| Ekonominin eğlenceyi öldürmesi | Dwarf Fortress cüce ekonomisi (kaldırıldı; [topluluk anlatımı](https://steamcommunity.com/app/975370/discussions/0/7093810789008385736), resmî açıklama bulunamadı) | Oyuncunun hissetmediği karmaşıklığı ekleme |
| Tek optimal rota | Elite Dangerous rota çiftçiliği | Talebin satılan miktarla düşmesi (ED'de talebin %25'inden fazlası satılınca fiyat düşüyor), olaylar |
| Bayat bilgiyle zarar | Elite Dangerous üçüncü parti araçlar | Bizde bu bir **özellik**: bilgi riski oyunun parçası |

## 6. Zaman ve tick yapısı

- EU4 günlük tick kullanır. Profil çalışmalarında en pahalı bileşen yapay zekâ ajanları; maliyet oyun ilerledikçe artıyor. ([EU4 Dev Diary 2017](https://admin-forum.paradoxplaza.com/forum/developer-diary/eu4-development-diary-5th-of-december-2017.1058829))
- **Öneri: çok hızlı tick sistemi:**
  - Günlük: seyir ve konum, haber yayılımı, pazar işlemleri (her limanın takas odası), olay kontrolleri
  - Haftalık: ajanların stratejik kararları (rota ve mal seçimi), inanç güncellemeleri
  - Aylık / mevsimlik: üretim ve hasat, nüfus, vergiler, fiyat istatistikleri
- Ajanlar her gün değil, kendi "karar anlarında" düşünür (limana vardığında, haber aldığında). Bu hem performans hem gerçekçilik için iyi. Olay güdümlü (event-driven) bir zamanlayıcı gerekir.

## 7. Ölçme ve izleme (simülasyonun "canlı" olduğunu nasıl anlarız?)

Oyuncusuz çalıştırmalarda izlenecek metrikler (taslak):

- **Fiyat oynaklığı:** Mal ve liman başına günlük ve aylık değişim. Hedef bandı belirlenecek: ne ölü ne kaotik.
- **Fiyat yayılımı:** Aynı malın limanlar arasındaki fark. Sıfıra yakınsa fırsat yok demek (Bannerlord sorunu).
- **Fırsat ömrü:** Bir arbitraj fırsatının açılmasından kapanmasına geçen süre.
- **Toplam para arzı ve mal stokları:** Enflasyon ve istif kontrolü.
- **Ajan iflas ve doğum oranları, meslek dağılımı.**
- **Servet dağılımı:** Gini katsayısı. Bir ajan her şeyi yutuyor mu?
- **Şoklardan toparlanma süresi.**

## Sonraki tur için

- Bilgi yayılımı modelleri (dedikodu / rumor propagation, ajanlar arası haber paylaşımı)
- Fiyat inancı ile bilgi yaşının birleştirilmesi (Doran-Parberry'nin bizim versiyonu)
- Ajan karar mimarisi seçenekleri: fayda tabanlı yapay zekâ (utility AI), hedef odaklı planlama (GOAP), basit kurallar
- Benzer açık kaynak projeler (BazaarBot portları, Mesa / agent-based modeling kütüphaneleri)
