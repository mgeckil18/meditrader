# Liman Uğrağı: Kısmi Satış, Zamana Yayılan Elleçleme, Karışık Yük
> Durum: taslak (tasarım önerisi; kullanıcı onayı bekleyen noktalar var)
> Son güncelleme: 2026-11-12
> İlgili: K-040, S-028, [M2](../experiments/M2.md), [ship-operating-costs-16c](../research/history/ship-operating-costs-16c.md), [shipping-scale-16c](../research/history/shipping-scale-16c.md)

## Neden
- Tarihte gemi yılda 80 günden az denizde (Jones 1998); modelde 265 gün.
- Fazla sefer, fazla kaybın da kaynağı: yıllık kayıp modelde %35, tarihte %4-12.
- Maliyet paketi (PC) gemi davranışını değiştirmedi, yalnızca filoyu küçülttü. Günlük maliyet her seçenekte aynı işliyor.
- Gemiler yarı boş geziyor (M2.1 snapshot): yoldaki gemilerin medyan yükü buğdayda ~700, biberde ~15 birim; ambar 2.000. Yük, varış pazarının derinliğiyle sınırlı ve gemide tek mal var.

## Şu anki durum (kod)
- Gemide tek mal var (`m.good`, `m.qty`).
- Varışta iki seçenek var:
  - yükün tamamını burada satmak: boşaltılan kısım kapan'da günlük takasla, reservation price ile satılır;
  - tamamını başka limana götürmek (yön değiştirme).
- Kısmen satıp kalanını götürmek mümkün değil.
- Yeni mal ancak yük tümüyle satılınca alınabiliyor (durum `Buying`).
- Tüccar, satmanın gemide yer açtığını ve bu yerin doldurulabileceğini hesaba **katmıyor**.

## Önerilen işleyiş (K-040; biçim Claude)

1. **Ambar, parti listesi olur.** Her parti: mal, miktar, maliyet, yüklenme günü (bozulma partiye göre). Kısıt: Σ miktar × hacim ≤ kapasite.
2. **Varışta uğrak planı.** Tüccar şunları birlikte seçer:
   - her partiden burada ne kadar satılacağı (0, %25, %50, %75, %100);
   - sonraki hedef;
   - boşalan ve boş yere bu limandan hangi malın, ne kadar alınacağı.

   Amaç, toplam net değerin toplam döngü süresine oranı:
   - toplam net değer = burada satış + kalan yükün hedefteki değeri + yeni yükün hedefteki değeri − maliyetler;
   - toplam döngü süresi = boşaltma + yükleme + yolculuk.

   Bugünkü "sat ya da yön değiştir" bu planın iki ucu olur (her şeyi sat / hiçbir şey satma).
3. **Satış anlaşması.** Satılacak miktar varışta, belli bir fiyattan anlaşılır. Teslim, boşaltma hızıyla günlere yayılır; para teslimle gelir. Ayrı bir bekleme kalemi yok.
4. **Elleçleme sırası.** Önce boşaltma, sonra yükleme. Süre hacim / liman hızı (bugünkü `handling` büyük 250, orta 150, küçük 100 hacim birimi/gün). Kalkış, ikisi bitince olur.
5. **Yük alma**, bugünkü kalkış arz eğrisinden (`origin_curve`) yapılır. Yeni parti, gemideki partilerle aynı hedefe gider (tek gemi, tek rota).
6. **Yön değiştirme** = hiçbir şey satmayan ve hiçbir şey almayan plan. Boşaltma süresi yok; maliyeti uğrak resmi ve gemi zamanı.

## Kullanıcıya açık sorular

### S1. Anlaşmanın karşı tarafı kim?
- **(a) Yerel toptancı (depocu, storer).** Fiyatı, kendi beklediği satış fiyatı eksi iskonto (`storer_shade`); miktarı kasasıyla sınırlı. Malı teslim aldıkça kapan'da satar.
  - Tarihsel karşılık: gelen tüccarın partiyi yerel grossiste numuneyle satması ⚠️.
  - Bekleme yok, fiyat sabit.
  - Yan etki: tüccar arzı kapan'a toptancıdan geçer, fiyat oluşumu değişir.
- **(b) Kapan.** Tüccar yalnızca ne kadarını karaya çıkaracağını seçer. Çıkan mal günlük takasla satılır (bugünkü gibi).
  - Fiyat teslim süresince değişebilir.
  - Alıcı azsa bekleme olur; kullanıcının "ayrı bekleme yok" isteğine uymuyor.
- **Önerim (a).** Kullanıcının örneğine uyuyor ve depocuya tarihsel bir rol veriyor. Ama kapan'ın fiyat oluşumuna dokunduğu için büyük bir değişiklik.

### S2. Hafif ve değerli mal ne kadar sürede boşalır?
- Bugün hız hacme bağlı. 1.000 birim biber 50 hacim birimi, büyük limanda bir günden kısa sürede boşalır.
- Kullanıcının örneğinde günde 50 birim biber var.
- Tarihte değerli mal tartılır, gümrükte sayılır ve mühürlenir (pesa, tartı) ⚠️. Hızı hacimle değil, tartıyla (adet/gün) sınırlıydı.
- **Önerim:** her mal için iki sınır olsun: hacim hızı ve değer ya da tartı hızı. Hangisi yavaşsa o geçerli. Değerler kaba vekil olur ⚠️.

### S3. Kâr kaydı nasıl tutulur?
- Bugün tüccarın track record'u sefer başına tutuluyor (giriş-çıkış ve kredi buna bakıyor).
- Karışık yükte "sefer" tek bir alım-satım değil.
- **Önerim:** dönemlik (aylık) kayıt. Kasa + gemideki yükün piyasa değeri, yani mark-to-market.

## Uygulama sırası (öneri)
1. Kısmi satış + zamana yayılan boşaltma, tek mal. Ambar değişmez; yalnızca satılmayan kısım gemide kalır.
2. Karışık yük: ambar parti listesi, boşalan yere alım, birleşik uğrak planı.
3. Kayıt (S3) ve teşhis araçları (`rr_log`, `dep_log`, `flows`) karışık yüke uyarlanır.

Her adım bayrak arkasında; kapalıyken PC çıktısı birebir aynı olmalı (regresyon).

## Beklenen etkiler (Claude, sınanacak)
- Gemi başına yük artar; aynı ticaret için gereken gemi ve sefer sayısı düşer.
- Limanda geçen zaman artar, kayıp oranı düşer.
- Kısmi satış yön değiştirmenin yerine geçer: tüccar fiyat ne kadar düşükse o kadar az satar, kalanını götürür. Churn azalır.
- Risk: plan araması pahalı (hedef × satış payı × doldurma malı). Seçenek sayısı sınırlı tutulmalı.

## Karışık yük: uygulama tasarımı (2026-11-12, K-040 madde 7-9)
Bayrak `mixed`: `{lot_fee, lot_setup_days, stowage_loss}` (düzeyler kaba ⚠️).

**Ambar:**
- Etkin parti, bugünkü `good` / `qty` alanlarıdır: limanda satılan ya da alınan parti.
- Gemide taşınan öteki partiler `hold` listesinde durur. Her parti kendi maliyetini, yüklenme gününü (bozulma), sefer kaydını (`voy`), nakit akışını ve gider payını taşır.
- Kapasite: kapasite × (1 − `stowage_loss` × (parti sayısı − 1)) − ambardaki partilerin hacmi (broken stowage).

**Limanda akış:**
1. Varışta etkin parti satılmaya başlar (bugünkü gibi).
2. Satış kararı (`sell_plan`) başka limanı daha iyi bulursa, gemi artık kalkmaz. Satılmayan kısım ambara konur (karaya çıkmış kısım için yeniden yükleme ücreti) ve sıradaki partiye geçilir. Bu, kısmi satıştır.
3. Etkin parti bitince ambardaki, bu limanda henüz değerlendirilmemiş partilerden burada satmaya en uygun olanı etkin olur. Kalmazsa tüccar alıma geçer.
4. Alım: boş yere bu limandan yeni parti. Seçenek skoru, yeni partinin kârına ambardaki partilerin o hedefte kazanacağı değeri (hedefteki değer − buradaki değer) ekler. Hedef, gemideki her şey için birlikte seçilir.
5. Uygun yeni parti yoksa ve ambar doluysa, ambarın en değerli olduğu hedefe kalkılır.

**Satmanın yer açma değeri:**
- Varışta bu limandan alınabilecek en iyi seçeneğin hacim başına kârı hesaplanır (`fill_val`).
- Burada satmanın değerine birim başına `fill_val × hacim` eklenir. Tüccar, satışın açtığı yeri hesaba katar (kullanıcı, K-040 madde 4).

**Parti başına maliyetler (K-040 madde 8):**
- Her parti, karaya çıkarken ya da yüklenirken `lot_fee` öder (gümrük beyanı, tartı, simsar).
- Her parti elleçlemeye `lot_setup_days` ekler.
- Broken stowage: her ek parti ambarın `stowage_loss` payını israf eder.

**Kâr kaydı (K-040 madde 9):**
- Her partinin nakit akışı ayrı tutulur: satış geliri eksi o partiye düşen ücretler.
- Gemi zamanı giderleri (geçim, gemi maliyeti), gemideki partilere maliyet payıyla bölünür.
- Parti bitince kaydı yazılır.

**Bilinçli sadeleştirmeler:**
- Satış hâlâ kapan'da, günlük takasla (S1 sonraya).
- Değerli malın tartı hızı yok (S2 sonraya).
- Ambardaki partiler o limanda yalnızca bir kez değerlendirilir.

## S1 + S2 uygulaması (2026-11-12, kullanıcı: "1 ve 2 beraber")

**S2, tartı hızı (`weigh_rate`):**
- Elleçleme hızı mala göre: liman hızı (hacim/gün) ile tartı hızı (birim/gün × hacim) arasında yavaş olan.
- Büyük limanda biber 100, kaba ve ince kumaş 400 birim/gün. Orta ve küçük limanlarda `handling` oranıyla düşer. Kaba ⚠️.
- 1.000 birim biber büyük limanda ~10 günde boşalır.

**S1, satış anlaşması (`sale_contract`):**
- Tüccar bir partiyi burada satmaya karar verince, o pazardaki depocular teklif fiyatına göre sıralanır.
- Teklifi tüccarın kabul fiyatının (bekleyerek pazarda satmanın, bekleme maliyetleri düşülmüş değeri) üstünde olan depocularla anlaşılır; miktar, depocunun kasası ve yeriyle sınırlı.
- Para anlaşmada ödenir; %1 komisyon (kapan ücretiyle aynı).
- Mal, karaya çıktıkça depocuya teslim edilir. Anlaşmalı mal pazarda satılmaz, ambara konmaz; teslim bitmeden parti ambara konmaz.
- Anlaşmanın dışında kalan kısım bugünkü gibi pazarda satılır ya da ambara konur.
- Depocu malı kendi kuralıyla pazarda satar.
