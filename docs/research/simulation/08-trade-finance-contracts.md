# 08 — Ticaret Finansmanı: Borç, Özsermaye ve Hibrit Sözleşmeler
> Durum: taslak
> Son güncelleme: 2026-10-26
> İlgili: [D5b3b](../../experiments/D5b3b.md), K-021, S-015, framework A12, [codex/economics](../../codex/economics.md)

**Soru (kullanıcı, 2026-10-26):** Likidite sıkıntısı çeken tüccar, senet getirisi + risk primi faizle vadeli borç alsa ("tersine senet"), colleganza yalnızca çok güvenilir tüccarların hacmini artırmak için kullanılsa? Bu modeli ve başka hibrit modelleri araştır.

## 1. Teori: hangi koşulda borç, hangi koşulda özsermaye?

| Sonuç | Fikir | Kaynak |
|---|---|---|
| **Costly state verification** | Sonuç yalnızca tüccarca biliniyor ve doğrulamak pahalıysa optimal sözleşme **standart borçtur**: sabit geri ödeme; ödenemezse alacaklı her şeye el koyar (yalnızca o durumda doğrulama yapılır). Kâr paylaşımı (özsermaye), sonucun ucuza doğrulanmasını gerektirir | Townsend (1979), *J. Econ. Theory* 21, 265-293 |
| **Credit rationing** | Faizi yükseltmek riskli borçluları çeker (sınırlı sorumlulukta kötü sonuç borçlunun değil alacaklının sorunudur). Alacaklı faizi yükseltmek yerine kredi miktarını kısar | Stiglitz & Weiss (1981), *AER* 71(3) |
| **Teminat ile ayıklama** | Teminat isteyen sözleşme, kendini iyi bilen borçluyu seçer; kötü borçlu teminat koymak istemez | Bester (1985), *AER* 75(4) ⚠️ (bu oturumda doğrulanmadı) |
| **Signaling** | Girişimcinin kendi projesine kendi parasını koyması kalite sinyalidir | Leland & Pyle (1977), *JF* 32(2) ⚠️ |
| **Asset substitution / moral hazard** | Borçlu, borç aldıktan sonra daha riskli işe kayar (kazanç onun, kayıp alacaklının) | Jensen & Meckling (1976) ⚠️ |
| **Aşırı güven ve finansman** | Aşırı güvenli yöneticiler borcu dış özsermayeye tercih eder | Malmendier, Tate & Yan (2011), *JF* 66(5) ⚠️ |

**Kullanıcı önerisiyle ilişkisi:** "Riski ve yeteneği düşük tüccar borç almaya daha az motive olmalı" ancak **tam sorumluluk** (borç, tüccarın bütün servetinden ve itibarından ödenir) ve **teminat / kaldıraç sınırı** varsa kendiliğinden olur (Bester; Leland & Pyle). Sınırlı sorumlulukta tersi olur: kötü ve riskli borçlu borca daha hevesli (Stiglitz & Weiss). Aşırı güvenli tüccar da borca daha hevesli (Malmendier ve ark.).

## 2. Tarih: Venedik'te sea loan'dan commenda'ya

- **Sea loan (foenus nauticum, prestito marittimo):** Borç sözleşmesi, ama gemi batarsa geri ödeme yok; alacaklı deniz riskini üstlenir (borç + sigorta). Deniz riski açıkça yazıldığı için faiz yasağından kaçınabildi. 12. yy Venedik'inde en yaygın ticari sözleşme. Kaynak: Wisconsin Univ. Library dijital metni, *Venice and the Crusades* ⚠️ (ikincil). Gregory IX'un *Naviganti* dekretali (c. 1236, X 5.19.9) deniz ödüncünü tefecilik saydı ⚠️ (arka plan bilgisi, metin doğrulanmadı).
- **Cambium maritimum:** Faiz döviz kuruna gizlenmiş deniz ödüncü. Cenova'da 17.-18. yy'a kadar sürdü. Kaynak: "A Contract for All Seasons: The Flexibility and Functionality of the Cambium Maritimum (Genoa, XVII–XVIII c.)", *J. of Management and Financial Sciences* (SGH).
- **González de Lara (2000, EUI tezi; JEH 61(2) 2001 özet; EREH 6(2) 2002):** Sea loan (borç) ve commenda (özsermaye), enforcement ve verifiability kısıtları altında optimal sözleşmelerdir. Commenda, verifiability kısıtı **ortadan kalktığı zaman ve yerde** sea loan'ın yerini aldı. Bunu sağlayan, Venedik "devletinin" otoritesine dayalı kurumlardı (konvoy, devlet gemileri, kayıt). Deniz sigortası 14. yy ortasına kadar gelişmedi.
- **Williamson, "The Financial Structure of Commercial Revolution" (SIOE 2011 tebliği; Venedik 1190-1220 ve Venedik Girit'i 1278/1303-1400, 1.600-1.800 sözleşme):** Ticaretin **sınırlarını** (yeni ve uzak pazarları) commenda değil **borç** finanse etti. Ticaretin çoğu tekrarlı değil **tek seferlik ilişkilerle** yapıldı. Yalnızca özet okundu.

**Çıkarım:** Tarihsel seçim tüccarın itibarına değil, **sonucun doğrulanabilirliğine** bağlı. Devletin gözetimindeki rotalarda (muda konvoyu, kayıt) özsermaye; gözetimin zayıf olduğu yerlerde borç. Williamson'un "tek seferlik ilişki" bulgusu, itibarın (tekrarlı ilişkinin) sanıldığı kadar merkezî olmadığını düşündürüyor.

## 3. Osmanlı tarafı

- **Para vakıfları (cash waqf):** Vakıf sermayesi kredi olarak verilir, getirisi vakfa gider. 16. yy'da İstanbul, Edirne ve Bursa'da yaygın. Kaynaklar: Çizakça (1993, 1995) özetleri; Islamic Markets eğitim sayfaları (ikincil).
  - 15. yy'da bir Edirne vakfı yıllık %10'la borç veriyordu.
  - Bursa'da 1.563 vakıf (1667-1805) %9-12 aralığında sabit getiri sağladı (Çizakça).
  - Bu getirinin faiz olup olmadığı tartışmalı (Mandaville 1979; Çizakça 1993).
  - 16. yy Bursa oranı: Çiftçi, *Belleten* (1544-1588 kadı sicilleri) okunmadı ⚠️.
- **Mudaraba:** İslam hukukundaki commenda karşılığı. Kâr paylaşılır, zararı sermayedar taşır. Udovitch (1970), *Partnership and Profit in Medieval Islam* ⚠️.

## 4. Başka hibrit araçlar (16. yy)

| Araç | Ne çözer | Not |
|---|---|---|
| **Supplier / trade credit** (veresiye alım; ödeme sonraki fuarda ya da satıştan sonra) | Likidite; yeni alacaklı gerektirmez, satıcı finanse eder | Çok yaygındı ⚠️ (genel tarih yazımı) |
| **Bill of exchange (lettera di cambio)** | Bir limanda para alınır, başka limanda başka parayla ödenir; faiz kura gizli. Hem havale hem kredi | Cenova'nın Besançon / Piacenza fuarları ⚠️ |
| **Gemi payları (carati)** | Venedik'te gemi 24 paya bölünür; gemi sermayesi ortaklaşa | ⚠️ |
| **Compagnia** | Aile ve ortaklık şirketi, sınırsız sorumluluk | Floransa ⚠️ |
| **Deniz sigortası (sicurtà)** | Risk transferi, likidite değil | 14. yy ortasından itibaren (González de Lara 2004) |

## Oyun için çıkarımlar

1. **Borç aracı tarihsel olarak sağlam ve teoriyle uyumlu.** Kullanıcının "tersine senet"i aslında deniz ödüncü / cambio'nun deniz riski taşımayan hâli. Faiz için gerçekçi bant: senet (≈%4-5) + prim; vakıf kredisi %9-12 bir referans ⚠️.
2. **Borcun ayıklama gücü sorumluluk kuralına bağlı.** Tam sorumluluk, kaldıraç sınırı ve kötü borçlunun limanlar arası söylentiyle karalistelenmesi olmazsa düşük yetenekli tüccar borca daha hevesli olur (aşırı güven). Bu bir hata değil gerçekçi bir dinamik: acemi tüccar borçla batar. Ama alacaklının kaldıraç sınırı bunu sınırlamalı.
3. **Colleganza'nın ölçütü itibardan çok doğrulanabilirlik olabilir.** Venedik muda'sı ve konvoyu gibi gözetimli rotalarda özsermaye mümkün, uzak / gözetimsiz rotalarda borç. Bu oyunda bir kurum katmanı açar: "Venedik'te colleganza bulursun, Trablus'ta bulamazsın."
4. **Itibarın ağırlığı:** Williamson'un bulgusu (çoğu ilişki tek seferlik) ve D5b3b'nin bulgusu (sicil beceriyi ayırt etmiyor) aynı yöne işaret ediyor. Sermayenin önce teminat ve sorumlulukla, sonra itibarla dağıtılması daha tarihsel olabilir.
5. **Supplier credit ayrı bir yol.** Likiditeyi yeni bir alacaklı yaratmadan çözer; stokçu ya da toptancı satıcı finanse eder. Sonra değerlendirilebilir.

---

## 5. Ek (2026-10-26): Tüccar başına kredi skoru ve risk bazlı faiz

**Kullanıcı önerisi (kesin değil):**
- Devlet gibi güvenli yapılar senet faiziyle borçlanır, tüccar borçlanamaz.
- Tüccar başına kredi skoru hesaplanıp faiz ona göre belirlenirse, alacaklının getirisi (batma mahsup edildikten sonra) senede yaklaşır.
- Pahalı borç, likidite sıkıntısı çeken tüccarın davranışını değiştirir.
- Belki ticaret hacmi düşer, ticaret kârlılaşır. Fiyatlara etkisi ne olur?
- Bu, itibarın işe yaramaması sorununu da çözebilir.

| Konu | Literatür | Ne diyor |
|---|---|---|
| **Risk bazlı fiyatlama ve skor** | Einav, Jenkins & Levin (2013), *RAND J. Econ.* 44(2), 249-274 | Büyük bir oto kredi şirketinde otomatik kredi skoru alacaklının kârını kredi başına ~1.000 $ artırdı. Kazancın yaklaşık yarısı yüksek riskli borçluyu ayıklamaktan, yarısı düşük riskliye daha iyi koşul sunmaktan geldi |
| **Spread = beklenen kayıp + risk primi** | Merton (1974) ⚠️; credit spread puzzle: Huang & Huang (2012) ⚠️ | Gerçek kredi spread'leri beklenen temerrüt kaybından büyüktür. Alacaklı, mahsuptan sonra senedin üstünde kazanır |
| **Skor neden işe yarar, ne zaman yaramaz** | Stiglitz & Weiss (1981) | Credit rationing gözlenemeyen risk yüzünden ortaya çıkar. Skor riski gözlenebilir kıldığı ölçüde adverse selection azalır. Skorun bilmediğini borçlu biliyorsa, her skor diliminde sorun yeniden doğar |
| **İtibarın borç piyasasındaki rolü** | Diamond (1989), *JPE* 97(4), 828-862 | Borçlunun aşırı riskli proje seçme eğilimi vardır. Kısa sicilde itibar teşvikleri iyileştirmez; iyi sicil biriktikçe kaybedilecek bir şey (ucuz kredi) oluşur ve borçlu daha güvenli seçer. **İtibar beceriyi göstermekten çok davranışı disipline ederek çalışır** |
| **Finansman ve ticaret hacmi** | Manova (2013), *REStud* 80(2), 711-744; Amiti & Weinstein (2011), *QJE* ⚠️ | Kredi kısıtları ihracatı üretimden fazla düşürür (firma seçimi + firma başına daha az ihracat). Etki, finansmana bağımlı sektörlerde güçlü |
| **Finansmanın önemsizliği ve istisnaları** | Modigliani & Miller (1958) ⚠️; pecking order: Myers & Majluf (1984) ⚠️ | Mükemmel piyasada finansman yapısı değeri değiştirmez. Değiştiren iflas maliyeti ve bilgi asimetrisidir. Tercih sırası: iç fon, borç, dış özsermaye |
| **Fazla giriş** | Mankiw & Whinston (1986), *RAND J.* ⚠️; Camerer & Lovallo (1999), *AER* 89(1) ⚠️ | İş çalma (business stealing) varsa serbest giriş toplumsal olarak fazla firma üretir; rant, kopyalanan sabit maliyetlerle erir. Deneyde aşırı güvenli katılımcılar fazla girer |

**Tarihsel faiz düzeyleri (hepsi ⚠️, ikincil):**
- 16. yy Venedik'inde faiz yılda %6,75-9,62, Cenova'da %1,88-4,38 (Ferguson, *The Cash Nexus*'tan bir gazete yazısı aktarıyor; kitap doğrulanmadı).
- 12. yy Venedik'inde basit ticari borç %20, tehlikeli deniz seferlerinde %50'ye kadar (Wisconsin Univ. Library, *Venice and the Crusades*).
- Osmanlı para vakıfları %10 civarı (bkz. §3).
- Deniz sigortası primleri rota ve mevsime göre değişirdi. Cenova'da 1564-1572'ye ait 757 poliçelik bir defter var (Iodice, Exeter). Venedik 1592-1609 oranları (Tenenti) bulunamadı.

**Çıkarım:** Tarihte de borç fiyatı **sefere göre** (rota, mevsim, tehlike) belirlenirdi, yalnızca kişiye göre değil. Bu, D5b3c teşhisiyle uyumlu: zararı tüccarın becerisi değil, seferin koşulları (varıştaki kalabalık) belirliyor.
