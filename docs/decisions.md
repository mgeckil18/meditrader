# Karar Günlüğü
> Durum: canlı doküman
> Son güncelleme: 2026-10-23
> İlgili: [vision](vision.md), [open-questions](open-questions.md)

Format: **K-xxx — Başlık** (tarih) · karar · gerekçe · etkilediği yerler.

---

**K-001 — Tür: tüccar RPG + strateji, tycoon değil** (2026-10-22)
Oyuncu bir tüccardır; fabrika/şehir kurma odağı yoktur. Gerekçe: oyunun kimliği "acımasız bir ekosistemde hayatta kalan tüccar".

**K-002 — Gemisiz başlangıç** (2026-10-22)
Oyuncu sermaye ve itibarla, gemisiz başlar. Erken araçlar: yük payı/navlun, borç senetleri, kervan payı, yerel alım-satım. Tarihsel karşılıklar: commenda/colleganza, özel yelkenlilerde (navi) yük alanı kiralama, gemi hisseleri (carati).
*Düzeltme (2026-10-22):* Devlet kadırgası konvoyları (muda) 1533'te sona erdi; 1560 başlangıcında mekanik olarak değil atmosfer olarak yer alır. Bkz. [history/mediterranean-16c-overview.md §1](research/history/mediterranean-16c-overview.md).

**K-003 — Bölgesel itibar** (2026-10-22)
İtibar tek bir sayı değil, şehir/ağ bazlıdır. Gerekçe: coğrafi genişlemeyi anlamlı kılar, tek yerde itibar kasıp her yerde kullanma istismarını önler.

**K-004 — Oyuncu ekonomide sıradan bir ajandır** (2026-10-22)
NPC'ler (tüccar, lonca, kervan, korsan, sigortacı...) oyuncuyla aynı kurallara tabidir: aynı bilgi gecikmesi, risk ve sermaye kısıtı. Hile yapan yapay zekâ yok. Farklılık sadece başlangıç koşulları ve amaçlardan gelir.

**K-005 — Tarihsel başlangıç, tarihsel olaylar gerçekleşir** (2026-10-22)
Dünya seçilen tarihteki tarihsel durumla başlar. Tarihsel olaylar gerçekleşir; oyuncunun etkisi sınırlıdır. Olay envanteri ileride birlikte hazırlanacak. (İstismar riski ve çözümü: S-003.)

**K-006 — EU4 tarzı zaman** (2026-10-22)
Dünya sürekli akar; hız ayarı ve duraklatma var. Simülasyon iç yapıda sabit adımlı tick ile çalışır (günlük tick önerisi, S-004).

**K-007 — Çatışma dolaylı** (2026-10-22)
Oyuncu savaşmaz. Elindeki araçlar: rota ve mevsim seçimi, konvoy, refakat, bayrak, rüşvet, fidye, sigorta. İleride genişletilebilir.

**K-008 — Temsilciler (fattori) ile ölçeklenme** (2026-10-22)
Oyuncu başta her şeyi kendisi yapar; ilerledikçe kendi çıkarını gözeten, kısmen rasyonel ve risk taşıyan temsilciler tutup yönetir.

**K-009 — Önce simülasyon, sonra oyun** (2026-10-22)
Erken bir "oynanabilir prototip" yapılmayacak. İlk iş canlı ekosistem simülasyonunun oturtulması; genişleme onun üzerine kurulacak.

**K-010 — Simülasyon tekrarlanabilir (deterministik) olacak** (2026-10-22)
Rastgelelik var ama seed'li sözde-rastgele üreteçle (PRNG) yönetilir: aynı seed + aynı oyuncu girdileri = birebir aynı oyun. Gerekçe: hata ayıklama, ekonomi dengesini test etme, kayıt dosyaları, ileride çok oyunculu. Ayrıntı: [design/determinism.md](design/determinism.md).

**K-011 — Çalışma düzeni: markdown dokümanlar + INDEX** (2026-10-22)
Tüm çalışma `docs/` altında markdown olarak tutulur; ana harita `docs/INDEX.md`. Kurallar `CLAUDE.md`'de.

**K-012 — Sigorta dolandırıcılığı: oyunda mümkün ama riskli** (2026-10-22)
Sistem bunu engellemek yerine bedel ödetir: sigortacılar itibara göre fiyatlar, şüpheli hasarlar soruşturulur, yakalanmanın ağır sonuçları olur. ("Oyuncu çakalsa sigortacı kurt olur.") Detay tasarımı sonra.

**K-013 — Toptan ticaret kurumsal bir pazarla (kapan / loggia) modellenir** (2026-10-23)
Her limanda her mal için günlük toptan takas (tek fiyat). Köylüler, atölyeler, tüccarlar, stokçular ve dükkâncılar emir verir. Dükkâncılar perakendeye çekilir. Gerekçe: D5'teki darboğazların çoğu toptan katman eksikliğinden; tarihsel karşılığı kapan, Rialto, caricatori. Kural (kullanıcı): Sorunları çözmezse ve neden ajan eksikliğiyse, toptancı ajanlar eklenir. Ayrıntı: [wholesale-and-behavior](design/wholesale-and-behavior.md).

**K-014 — Tüccar çeşitliliği yapısaldır; rakip davranışı da söylentiyle yayılan bilgidir** (2026-10-23)
Tüccarlar düşünme derinliği (level-k), taklit eğilimi, servete bağlı risk tutumu, aşırı güven ve bilgi kaynakları bakımından çeşitlidir. "X, Y'ye Z yükledi" bilgisi, sonuçlarından önce söylentiyle yayılır; nasıl yorumlanacağını tüccarın kişiliği belirler. Kullanıcının sezgisi ve literatür (El Farol, minority game, cascades, level-k) uyumlu. Ayrıntı: [wholesale-and-behavior](design/wholesale-and-behavior.md).
*Doğrulama (2026-10-23, [D5b](experiments/D5b.md)):* Rakip bilgisi (yükleme söylentisi + limanda bekleyen kargo, hem planda hem rota değiştirmede) sistemi kurtaran şey; homojen düzey 1 tüccarlar bile yeterli. Çeşitlilik getirinin dağılımını belirliyor (düzey 0 zarar ediyor).

**K-015 — Codex: oyun içi bilgi pencereleri** (2026-10-23)
Simülasyonda karşılaşılan ekonomik, davranışsal ve tarihsel kavramlar oyuncuya, yeri geldiğinde açılan ve geçilebilen bilgi pencereleriyle anlatılır. Kavramlar ortaya çıktıkça [codex](codex/README.md)'e eklenir.

**K-016 — Perakende rekabetçidir; fiyatı rekabet indirir, el kuralı değil** (2026-10-23)
Dükkâncı fiyatı = yerine koyma maliyeti (açık toptan fiyat) × (1 + marj). Marj, dükkânın müşteri payından Lerner kuralıyla çıkar (logit rekabet). Müşteriler pahalı dükkânı atalet ile (≈30 gün) terk eder: fiyat yükseltmenin rekabetçi maliyeti budur. Dükkânın toptan alımı müşteri talebinden türer. Perakende giriş-çıkışı D3b mekanizmasıyla (işletme kârına göre); dükkâncının geçimi sabit giderdir (tüccarla eşit, K-004), dükkân sayısını pazar büyüklüğü belirler. D5a'nın mekanik iki yönlü çekişi kaldırıldı. Kullanıcı: örtük anlaşma (tacit collusion) bu kurulumda beklenmiyor, çünkü her dükkâncının çıkarı fiyat kırmak. Perakendede rant istenmiyor; oluşursa devlet müdahalesi eventi (narh vb.). Ayrıntı: [D5a2](experiments/D5a2.md), [wholesale-and-behavior §1b](design/wholesale-and-behavior.md).

**K-017 — Malı olmayan pazarın da fiyatı vardır: açık teklif ve tâtonnement** (2026-10-23)
Kapanda son oturumda işlem olmadıysa herkesin gördüğü (ve gemilerin taşıdığı) fiyat, en yüksek alış teklifidir; son işlem fiyatı değil. Müşterilerini geri çeviren dükkâncı teklifini her gün yükseltir (Walras tâtonnement); müşterilerinin son bir yılda ödediğini gördüğü en yüksek fiyatın üstüne çıkmaz. Gerekçe: D5a2-D5a3'te donmuş son işlem fiyatı, ithalatçı Venedik'i yılın üçte birinde yağsız bırakıyordu. Ayrıntı: [D5a3](experiments/D5a3.md).

**K-018 — Depocu ayrı bir roldür; oyuncuya dükkânla birlikte sunulabilir** (2026-10-26)
Depoculuk (zamanlar arası alıp satma, fazlayı emme) ile perakende aynı motivasyonla yapılmaz: perakendecinin marjını rekabet belirler, depocunun kârı fiyat dalgasından gelir. Modelde ayrı karar modülleri; oyunda "dükkâncının deposu" diye birlikte gösterilebilir. Kullanıcı kararı. Uygulama: stokçunun bütün mallara genişletilmesi (D5b2, yuva L).

**K-019 — Liman içinde gözle görülen her şey anında bilinir; niyetler söylentidir** (2026-10-26)
Kapan'daki alımlar açıktır: kim, hangi maldan, ne kadar aldı (kullanıcı: "alışverişler explicit"). Malın nereye gideceği ise liman içinde bile söylentidir (günlük duyma olasılığı korunur, kullanıcı: "bu kalsın"). Başka limanlar hakkındaki her şey gemi ve söylentiyle, gecikmeli gelir. Uygulama: D5b2, yuva G.

**K-020 — Simülasyon kararlı duruma yakın başlar; giriş fırsata ve sermayeye bağlıdır** (2026-10-26)
Kullanıcı kararı. (1) Başlangıç filosu ve durumu kararlı duruma yakın kurulur; ısınma dönemi sonuçları bozmamalı (D5b2'de 14 tüccarla başlangıç ve ilk yıl giriş yokluğu kıtlık patlamaları üretti). (2) Tüccar girişi taşıma kapasitesine değil fırsata bakar: "kârlı bir ticaret varsa ve bu genel biliniyorsa tüccar girişi olmalı". Giriş hızı toplam halk sermayesine ve fırsata bağlıdır. Modelleme yolu açık: Claude önerisi framework A11 (sermaye havuzu, colleganza; kamuya açık price current; yatırımcı eşik dağılımı; spin-up), ayrıntı S-012.
*Ek karar (2026-10-26):* Sermaye havuzu **liman başına**. Giriş iki yoldan: yeni tüccar ve mevcut tüccara yatırımcı sermayesi (**colleganza**). Uygulama: D5b3.

**K-021 — Yatırım sermayesi itibara göre dağıtılır** (2026-10-26)
Kullanıcı kararı: colleganza sermayesi tüccarın siciline (itibarına) göre verilir; yatırımcılar tüccarları skora göre yukarıdan aşağı sıralayıp seçer. D5b3'te itibarsız colleganza adverse selection yüzünden yatırımcıya sözleşme başına −%17/−%19 kaybettirdi. Kullanıcının ilk skoru: bir yıllık işlem hacmi × kâr oranı × kârlı işlem oranı. Claude alternatif önerdi: credibility (shrinkage) tahmini, yani sefer getirisi ortalamasının nüfus ortalamasına çekilmesi ve belirsizlikle indirilmesi. İkisi D5b3b'de yarışıyor. Serbest girişe friction: kullanıcı mantıklı buluyor, ama önce itibarın etkisine bakılacak ("birincisini yapınca ikincisine ihtiyaç kalmayabilir"). Denge getirisi için şimdilik bir şey yapılmıyor.
*Sonuç (2026-10-26, [D5b3b](experiments/D5b3b.md)):* İtibar kapısı yatırımcı kaybını sözleşme başına −%24'ten −%4'e indirdi. Kazanç skor sıralamasından değil: rastgele sıralama aynı sonucu verdi. Kazanç, tüccarın ex-ante tahmini yerine gerçekleşmiş sicile bakılmasından ve kârlı sicil kapısından geliyor. Skor A ile B arasında fark yok, çünkü sicil sonraki seferi tahmin etmiyor (skill vs luck). Kalan kayıp yapısal (sıfır-kâr dengesi + asimetrik sözleşme). Denge getirisi %1'den %4,5-6,5'e çıktı, hedef %8'e ulaşmadı → kullanıcıyla konuşulacak (friction, yatırımcı öğrenmesi, sözleşme biçimi).

**K-022 — Hibrit tüccar finansmanı: likidite için borç, denetlenebilir rotada colleganza** (2026-10-26)
Kullanıcı kararı, S-015 / A12 tartışmasından. Kullanıcı notu: bu tasarımlar emin olmadan öneriliyor ya da onaylanıyor; deneyle sınanacak, kesin değil.
1. **Borç (vadeli, "tersine senet"):** Nakdi gemisini doldurmaya yetmeyen tüccar liman havuzundan borç alabilir. Faiz = senet + kredi primi. **Kaldıraç sınırı 1** (borç ≤ özsermaye).
2. **Tam sorumluluk ve iflas:** Borcunu ödeyemeyen tüccar batar. "Battı" diye işaretlenir, başka hiçbir faaliyet yapamaz, denklemden çıkar. Kalan bütün nakdi alacaklıya gider.
3. **Batma korkusu karar ağırlığıdır ("hassas denge"):** Borç alma kararı batma olasılığını ve batmanın bedelini tartar. Risk iştahı düşük ve sicili kötü tüccar daha az borçlanır. Kullanıcı hipotezi: batma endişesi bir giriş friction'ı olarak da işleyebilir.
4. **Colleganza** yalnızca çok düşük riskli ve denetlenebilir rota-mal çiftlerinde kullanılır (Claude önerisi, kullanıcı onayı). Kullanıcının sicile göre sıralama önerisi geri çekildi (manipüle edilebilir; D5b3b'de bilgi taşımadı).
5. **Yatırımcı öğrenmesi:** Havuzun colleganza'ya ayırdığı pay, limanın gerçekleşen colleganza getirisine göre değişir.
6. **Sonraya:**
   - Batan gemi riski: istenen, ama zor olursa bu iş bitince eklenir (S-015).
   - Daha karmaşık finansal araçlar: ihtiyaç oldukça.
   - **Dinamik senet getirisi** akılda tutulsun; nasıl yapılacağı düşünülmedi (S-016).
   - Giriş friction'ı ve kâr marjı: sonra konuşulacak.

Uygulama: D5b3c.
*Sonuç (2026-10-26, [D5b3c](experiments/D5b3c.md)):*
- Karar mekanizması istenen yönde çalışıyor. Düzey 0 ve risk tutumu yüksek tüccar 3-4 kat az borçlanıyor; batma korkusu kapatılınca borç ve alacaklı kaybı artıyor.
- Borç alacaklı için sürdürülemez: temerrüt %10, alacaklı senedin altında kazanıyor. Kök neden: sefer getirisinin oynaklığı (sd %40-90).
- Düşük riskli rota olmadığı için colleganza nadir ve yine zararlı.
- Friction hipotezi desteklenmedi (giriş borçla finanse edilmiyor).
- Denge getirisi değişmedi.

**K-023 — Sefer bazlı alacaklı (Rialto bilgi merkezi)** (2026-10-26)
Kullanıcı kararı ("borç konusunda mutabıkız, onu öyle kuralım"). Framework A13, S-015.
- Alacaklı faizi kendi sefer sonucu beklentisine göre verir.
- **Bilgisi:** kendisine yapılan başvurular (rota, mal, miktar, gün) + kamuya açık bilgi (price current, limanda görünen yüklemeler) + kendi borç defteri. Borçlanmayan tüccarın planını bilmez.
- **Tahmin yöntemi** iyi bir tüccarınkiyle aynı (düzey 2 benzeri). Kurum daha iyi tahmin etmez, yalnızca daha çok yük görür.
- **Sıralı fiyatlama:** önceki başvurular kalabalık sayılır.
- Getiri/risk yetersizse borç verilmez (credit rationing). Kurum, borç defterinden kendi tahmin yanlılığını öğrenir.
- Faiz bir sinyaldir: gerekçe söylenmez; düzey 1-2 tüccar yüksek faizden sonuç çıkarabilir.
- Liman başına tek kurum (kullanıcının "lonca" çerçevesi; Claude varsayılanı, kullanıcı bu soruyu ayrıca cevaplamadı).

Kullanıcı notu geçerli: parametreler ve bilgi işleme yöntemi hassas denge ister, kesin değil. Uygulama: D5b3d.
*Sonuç (2026-10-26, [D5b3d](experiments/D5b3d.md)):* Borçtan iflas 18,5'ten 5,5'e indi; alacaklı medyanda senet + marj civarında kazanıyor (çok gürültülü). Ama borç seçimi %16'dan %5'e düştü ve kalabalık değişmedi.

**K-024 — Serbest giriş: öz sermayede batma riski + gemi masrafı; sonlu tüccar havuzu yok** (2026-10-26) — *batma bedeli kısmı değişti, bkz. K-029 madde 6*
Kullanıcı kararı. S-017, framework A14 (sonlu havuz hariç).
- Batma cezası öz sermaye için de geçerli. Yeni girişin ve kalmanın kararı batma riskini tartar: kamuya açık iflas sıklığı × risk tutumu. Kullanıcı: "mantıklı ama denemeden bilemeyiz."
- Gemi masrafı + amortisman eklenir. Kullanıcı sorusu: "çözüm olur mu?" Ablasyonla ayrıca ölçülecek.
- **Sonlu potansiyel tüccar havuzu kurulmaz.**
- **Ayrıcalıklar şimdi kurulmaz.** En kârlı hatların rantına devletin el koyması (muda / incanto) bir **araç** olarak kaydedilir. Çok kârlı bir rota oyun bug'ı gibi bir sorun çıkarırsa uygulanır.
- Ölçüm düzeltmesi önce yapılır (kullanıcı: "üstüne kurulan hesaplar hatayı büyütür"). Brüt-ömür boyu getiri farkı tekrarlanırsa incelenir.

Uygulama: D5b3d.
*Sonuç (2026-10-26, [D5b3d](experiments/D5b3d.md)):*
- Batma bedeli girişi kıstı: filo 81 → 72, toplam getiri %13,6 → %17,2. Kullanıcı hipotezi desteklendi.
- Gemi masrafı filoyu kıstı (71), getiriyi yükseltmedi.
- Kalabalığı ikisi de çözmedi; kalabalık filo büyüklüğünden bağımsız.
- Getiri farkı tekrarlandı ve açıklandı: ömür boyu medyan yanıltıcı ölçüt, toplam sermaye getirisi ~%12-13 (T1).

**K-025 — Getiri hedefinin ölçütü: toplam sermaye getirisi; alacaklı temkinli kalır** (2026-10-26)
Kullanıcı kararı (D5b3d sonrası):
1. S-012'deki getiri hedefi (senet + risk ≈ %8) **sermaye-yıl ağırlıklı toplam sermaye getirisi** ile kıyaslanır (batanlar dahil). Kullanıcı: "çok iyi bir ölçüt."
2. **Alacaklı temkinli kalır.** Borcun amacı likidite: beklentisini doğru kurup doğru sefere çıkan tüccar her durumda borç alabilir ve faizi yüksek olmaz. Borç hacminin az olması sorun değil; ileride sorun çıkarsa ayarlanır.
3. Sıradaki adım D5b4 beklenti turnuvası. Önce rota seçimi ve kalabalık mekanizması üzerinde anlaşılacak (S-018).

**K-026 — Rota kalabalığı: yapı yolu ve sıra** (2026-10-26)
Kullanıcı kararı (S-018 tartışması). Kullanıcı tasarım önerilerini "emin olmadan" yapıyor; aşağıdakiler yön kararıdır, kesin değildir.
1. **Ağ yönlendirmesi (rakipler arası bilgi paylaşımı) reddedildi.** Tüccardan bedava bilgisini vermesi beklenmemeli; bilgi satma işine de girilmeyecek.
2. **Gürültü (logit) her zaman bir seçenek, ama asla ilk seçenek değil.** Yalnızca son çare.
3. **Limana bağlı tüccar → muhabir ağı (yumuşak maliyet) doğru yön.** Gerçek bir tarihsel olgu ve sorunu çözebilir.
4. **Çok gemili büyük tüccarlar seferlerini çeşitlendirir.** Uygulanacak; tarihsel olarak doğru.
5. **Sıra:** E1 ablation → E2 muhabir ağı → E3 çok gemili ev → E4 D5b4 turnuvası → gürültü (gerekirse). Turnuvayı E2-E3'ün arkasına alma önerisi Claude'un. Plan: [D5b3e](experiments/D5b3e.md).

**K-027 — Çok gemili tüccar ve komisyon: ilk biçim** (2026-10-26)
Kullanıcı kararı (D5b3e tasarım soruları). Kullanıcı "emin olmadan" öneriyor; kesin değil.
1. **"Ev" = büyük tüccar.** Başlangıçta büyük sermayeli tüccarların birden çok gemisi olur. Sermaye büyüklüğüne göre tüccar grupları fikrine çok gemi idaresi eklenir.
2. **Gemi alma şimdilik yok.** Gemi alma ileride bir yatırım aracı olarak sunulacak: gemi maliyeti, işletme gideri ve amortisman hesaba katılacak. Kullanıcı bunu önce düşünecek (Ertelendi).
3. **Ortak sermaye:** bir geminin zararı tüccarın diğer gemilerini de etkiler.
4. **Evin etkisi küçük olabilir ama bir etkisi olmalı.** Kullanıcı tarihte "çok az değildir" diye düşünüyor; test edilecek.
5. **Komisyon oranı:** Claude geçici bir değer seçer. Kullanıcı arşiv araştırmasıyla düzeltecek. Genel ilke: tarihsel veriler bulunup konulacak, kalanlar en sonda onlara göre ayarlanacak.

**K-028 — Yedek tüccar havuzu sınırlanmayacak** (2026-10-27)
Kullanıcı kararı (S-020).
1. **Sınırlı aday tüccar arzı (bariyer türü E, [11](research/simulation/11-entry-barriers.md)) uygulanmayacak.** Yatırımcı havuzu sınırsız kalır.
2. **Diğer bariyerler uygulanmalı.** Kullanıcı bunu "hissediyorum" diyerek öneriyor; kesin değil.

**K-029 — Giriş-çıkış kuralının düzeltilmesi** (2026-10-27)
Kullanıcı kararı ([D5b3f](experiments/D5b3f.md) değerlendirmesi üzerine). Kullanıcı: bu kısımlar **gelecek hafta ekonomik literatüre uyarak doğrulanacak.** Doğrulanana kadar hepsi deneme; "kesin" değil.
1. **Başlangıç anı (snapshot):** Uzun bir ön koşudan nesnel kuralla seçilen an başlangıç durumu olur. Birkaç snapshot kullanılır; yapılandırma hash'ine bağlıdır; ölçüm penceresi birkaç döngüyü kapsar. (Kullanıcı önerisi, Claude koşulları.)
2. **Giriş ve çıkış eşiği ortak: senet + risk primi** (bugün %4 + %4 = %8). Yatırımcı heterojenliği yalnızca hızı belirler. Sabit %8 denemek için kullanılabilir. ⚠️ **Düzeltilecek:** eşiğin bileşenleri (senet getirisi, risk primi) tarihsel ve ekonomik olarak bağlanmalı.
3. **Çıkış kararı her seferin sonunda verilir.** Bugünkü aylık kontrol + boş ambar + %10 olasılık kuralı kalkar. (Claude önerisi.)
4. **Kamuya açık sicil = batanlar ve çıkanlar dahil toplam sermaye getirisi** (K-025 ölçütü, son 12 ay). (Kullanıcı önerisi.)
5. **Kişisel beklenti = kendi sicili ile kamu ortalaması arasında credibility ağırlığı** (w = n / (n + k)). (Kullanıcının "kişisel sicil ortalamayla karşılaştırılsın" önerisinin Claude yorumu, kullanıcı onayladı.)
6. **K-024 değişir:** Batma bedeli beklenen kayıp olarak eşiğe eklenmez; kayıp artık sicilin içinde. Batmaya karşı risk tutumu risk priminin içinde kalır. (Claude önerisi, kullanıcı onayladı.)
7. **Girişteki "şu anki en iyi fırsat" bonusu kalkar.** (Claude önerisi.)

**Doğrulama listesi (gelecek hafta):**
- Eşik bileşenleri.
- Giriş-çıkış eşiklerinin batık maliyetle ayrışması (Dixit).
- Credibility ağırlığı (Bühlmann; k değeri).
- Kamuya açık sicilin tarihsel karşılığı (16. yy'da yatırımcı neyi biliyordu).
- Snapshot seçim kuralı.


**K-030 — Risk yapılandırılacak; yatırımcı modeli (c)** (2026-11-02)
Kullanıcı kararı (Ö2 şüpheleri üzerine). Tasarım: [risk-model](design/risk-model.md); kaynaklar: [maritime-risk-16c](research/history/maritime-risk-16c.md).
1. **Fiziksel risk** rota ve mevsime göre, tarihsel doğrulukla modellenecek: batma, korsana yakalanma.
2. **Ticari risk** (kötü ticaretten zarar) da riskin parçası.
3. **Risk aslında sefer ve gemi başına;** ama tüccar bunu hesaplayamaz (tarihte daha da zor). Tüccar, ticaretin akışından dinamik öğrenilen **sefer başına genel bir ortalama** kullanır.
4. **Eksik bilgiden doğan zarar:** Kullanıcı sordu; Claude önerisi: gerçekleşen sonuçtan ölçülen riskin içinde, ayrıca eklenmeden ([risk-model §2](design/risk-model.md)). Kullanıcı onayı bekleniyor.
5. **Yatırımcı ve tüccar davranışı: seçenek (c)** (birkaç gemiye pay dağıtma + sigorta). Kullanıcı: tarihsel olarak doğru, mantıklı ve oynanabilirlik için iyi.
6. **γ:** Tüccar grupları γ'ya göre sınıflandırılır; parametre en sonda ince ayarlanır.

**K-031 — Ö1 taban** (2026-11-06)
Kullanıcı kararı ([D5b3h](experiments/D5b3h.md)): Credibility k veriden (Bühlmann-Straub, `cred_rule="buhlmann"`) doğru yaklaşım; sonraki adımlar onun üstüne kurulur. Taban kurulum: WTA-UR-B. Bant (R) geçici vekil olarak kalıyor (İ12).

**K-032 — Gemi kaybı ve gemi piyasası (Ö3 öne çekildi)** (2026-11-06)
Kullanıcı kararı ([D5b3i](experiments/D5b3i.md), [D5b3j](experiments/D5b3j.md)):
1. Gemi kaybı modellenecek: Batan ya da yakalanan gemi sermaye olarak gider (S-021 seçenek a).
2. Ö3 (gemi piyasası) öne çekiliyor. Bandın (R) kendini besleyen çöküş sorununun doğal yoldan düzelmesi bekleniyor; R kaldırılıp test edilecek.
3. Uygulama ayrıntıları Claude'a bırakıldı ("doğru olacağını bildiğin şekilde"). Seçimler [D5b3j](experiments/D5b3j.md) ve mechanism-registry'de; hepsi Claude kaynaklı, kesin değil (kural 7d).
4. Ölçek araştırması (sefer sıklığı, kayıp oranı) ikincil kaynaklardan yapılacak; finalize etmeden önce kesinlik gerekmiyor, motoru doğru yöne yönlendirmesi yeterli ([shipping-scale-16c](research/history/shipping-scale-16c.md)).

**K-033 — Geliştirme Rust'ta; Python doğrulama için kalır** (2026-11-09)
Kullanıcı kararı ([rust-core](design/rust-core.md)):
1. Model geliştirme bundan sonra doğrudan Rust çekirdeğinde (`core/medi-core`) yapılır. Yeni mekanizmalar Python'a eklenmez.
2. Python motoru (`sim/world5.py`) bugünkü modelin **doğrulama oracle'ı** olarak donar. Rust'ın bu modeli birebir taşıdığı `run_rs.py compare` ve `trace` ile sınanır.
3. Uygulama kuralı (Claude): her yeni mekanizma bir yapılandırma bayrağıyla gelir; bayrak kapalıyken (varsayılan) Rust, Python ile bit düzeyinde aynı kalmalı. Bayrak açıkken ayrışma beklenen sonuçtur. Böylece eski deneyler yeniden üretilebilir kalır.

**K-034 — Ticaret çeşitliliği liman hiyerarşisiyle başlar** (2026-11-10)
Kullanıcı kararı:
1. Ticaret çeşitliliğinin ilk adımı **liman çeşitliliği**: büyük (antrepo), orta, küçük (kasaba, iskele). Tarihsel olarak incelenecek.
2. Liman çeşitliliğine **gemi çeşitliliği** eşlik eder: küçük limanlara giremeyen ya da orada pahalıya çalışan büyük gemi, kıyı taşımacılığı yapan küçük gemi.
3. Hedef örüntüler (kullanıcı):
   - büyük kargoyu kısa rotalarda dağıtan küçük-yerel tüccar kesimi;
   - büyük gemilerle sipariş ve navlun taşıma;
   - yakın limanlar arasında fiyat farkının daralması, uzak rotalarda hacmin artması.
4. Harita küçük değil: **Cenova'nın doğusundaki Akdeniz'in geniş bir kopyası**. Büyük şehirler, küçük şehirler ve kasabalar, kendi liman türleriyle.
5. Önce araştırma, sonra tasarım konuşması.
6. Claude notu: Serbest girişte uzak rota marjı kalıcı yükselmez; yükselen hacim ve fiyat katmanlarıdır. Kalıcı marjın kaynağı engellerdir (sermaye, bağlantı, staple).

**K-035 — Harita ölçeği ve veri politikası** (2026-11-10)
Kullanıcı kararı ([trade-structure §6](design/trade-structure.md)):
1. Önce **tam harita**: Cenova'nın doğusundaki Akdeniz, büyük ve orta limanlar. Küçük yerel limanlar sonra, bölge bölge.
2. Küçük limanlar büyük şehirlerden daha ufak bir ekonomi yapısıyla modellenir.
3. Karadeniz dahil edilecek (sonra). Karasal sınırlar kervan yollarında dış arz ve talep olarak (sonra).
4. Liman nüfusu, üretimi ve fiziksel özellikleri için şimdilik **kaba değerler**. Liste veren bir kaynak yok, arşiv araştırması gerekir. Değerler geçici vekil olarak işaretlenir (İ12).

**K-036 — Kalkış arzı, fiyat tavanı, güvenlik sınırı** (2026-11-10)
Kullanıcı kararı ([M1](experiments/M1.md)):
1. **Kalkış limanındaki gerçek arz** tüccarın kararına girer. Sıra:
   - (a) bulunduğu limanda arz eğrisi (miktar ve fiyat birlikte);
   - (b) uzak limanlarda inanılan arz, bilgi yayılma modeliyle (gecikme, eskime);
   - (c) kıtlık ve bolluk haberleri genel bilgi olarak yayılır.
   
   Tüccar bu bilgiyi kendisi değerlendirir.
2. **Fiyat tavanı** yalnızca hayati mallar için, özel koşullarda; bir kurum olarak (calmiere, narh; A4), sonra. Kullanıcı: problemler çözüldükçe fiyatlar doğru noktalara çekilecektir. Claude notu: bütçe sınırı (tüketici gelirinden fazla ödeyemez) bir kural değil, talep modelinin özelliği; teşhis edilir.
3. **Güvenlik sınırı** (`max_merchants`) yeni haritada kaldırılır; gemi maliyeti mekanikleri doğal sınır koyar. Yerine filo alarmı (Claude).
4. Şerh (kullanıcı): tüccarlar bu bilgileri ve sınırları yeteneklerine göre farklı değerlendirmeli; yetenekler bilgi işleme yöntemlerine göre ayrık kategoriler (A19, S-024). Şimdilik not.

## K-037 — Talep: reservation price ara çözümü; toplu varış M3 sonrasına
> Tarih: 2026-11-10. Kaynak: kullanıcı; ara çözüm önerisi Claude.

1. Talep "her fiyattan kaç alıcı" temelinde yapılandırılır; tüketiciler agent olmaz. Ara çözüm: sınıf başına lognormal reservation price dağılımı (S-025). Literatürdeki modellerin derlenip eklenmesi ileride yapılacak (not).
2. Toplu ve seyrek varış sorunu M3'ten sonra yeniden değerlendirilir (S-026).
3. Öncelik: önce simülasyondaki gemi kaybı analizi (M1.3), sonra M2.

## K-038 — Tamamen Rust; üç kayıp düzeltmesi
> Tarih: 2026-11-10. Kaynak: kullanıcı ("artık python koşusu yapmana gerek yok, full rust devam edelim").

1. Python koşusu artık yapılmaz. K-033'teki "bayrak kapalıyken `compare` EŞİT" sınaması yerine regresyon Rust'ın kendi önceki çıktısıyla yapılır. Yeni mekanizmalar yine bayrakla gelir.
2. M1.3'te bulunan üç artifact düzeltildi (M1.4): süreye bağlı tehlike, balast riski, korsan ganimeti piyasaya.

## K-039 — Bilgi sistemi: aktarma, açık liman bilgisi, gemisiz yayılım
> Tarih: 2026-11-10. Kaynak: kullanıcı; tasarım ayrıntıları Claude.

1. Tüccarın bir limana varınca öğrenebileceği bilgi, o limanda herkesin bildiği (public) bilgidir. Limanlar çevre limanlar hakkında daha isabetli bilgi taşır.
2. Gemiler bildikleri bütün bilgiyi taşır (tek atlamalı fiyat haberi kalkar).
3. Doğrudan sefer olmasa da fiyat bilgisi komşu limanlara yayılır.
4. Hedef: daha karmaşık ama doğru bir bilgi yayılımı sistemi. Claude'un önerdiği katmanlar sırayla eklenir: aktarma (I1), miktar bilgisi ve kıtlık haberi (I2, K-036 adım 4), kaynağa göre doğruluk (I3), yetenekle okuma (A19/S-024), yön değiştirme kararında belirsizlik ve maliyetler (I4).
5. Kullanıcı notu: Yanılan tüccar için düşük fiyattan satmak da bir seçenek olmalı. Karar elleçleme maliyeti, liman kirası, bağlanan sermayenin fırsat maliyeti ve malın bozulmasıyla tartılmalı (I4).

## K-040 — Gemi maliyetleri temel olur; limanda zaman elleçlemeyle ve kısmi satışla
> Tarih: 2026-11-12. Kaynak: kullanıcı; tasarım ayrıntıları Claude. İlgili: S-028, [M2](experiments/M2.md), [ship-operating-costs-16c](research/history/ship-operating-costs-16c.md)

1. **PC yeni temel.** `ship_cost_day` 130 + `port_costs` (uğrak resmi, elleçleme ücreti, girişte gümrük, gemi zamanı kararlarda). Bundan sonraki deneyler PC (ya da çift navlun sınamasının sonucuna göre PF) üzerine kurulur.
2. **Limanda zaman, alıcıyla anlaşma faslı uzatılarak değil, yükleme ve boşaltma zamana yayılarak** gelir. Örnek (kullanıcı): 1.000 birim biberle gelen gemi 250 birimi belli bir fiyattan satmak için anlaşır; bunu 5 gün boyunca günde 50 birim boşaltarak teslim eder. Ayrı bir bekleme kalemi gerekmez (kullanıcı görüşü).
3. **Boşalan yere o limandan mal alınabilir** (en azından seçenek olarak), yükleme süresiyle birlikte. Bu, karışık yük demek.
4. **Tüccar kısmi satışın avantajını hesaplar:** yükün bir kısmını burada satmak gemide yer açar, yer bu limanda ucuz olan bir malla doldurulabilir. Satış, taşıma ve doldurma kararları birlikte tartılır.
5. Sözleşme ve örgüt yapısı (sefer sözleşmesi, limanda oturan tüccar + acente) önemli ama öncelik değil. Atölyeler (S-027) bütün seçenekleri içeren bir modelle sonra.
6. **(2026-11-12, kullanıcı) Temel PF olur:** PC + `sea_wear` (navlun vekili yerine gemi başına deniz aşınması). Gerekçe: maliyet gemi başına; vekil çift sayıyordu.
7. **(2026-11-12, kullanıcı) Sıra: önce karışık yük.** Gemi birden fazla mal taşır. Mal çeşidi sınırsız olmasın. Kullanıcı önerisi: 2 çeşide kadar baz lojistik yönetim maliyeti, sonraki her çeşitte üstel artış (baz × 1,03^(n−2)). Biçim tartışmaya açık (Claude alternatif önerdi; bkz. [port-call-mixed-cargo](design/port-call-mixed-cargo.md)).
8. **(2026-11-12, kullanıcı) Çeşit maliyeti parti başına kalemlerle:**
   - parti başına uğrak masrafı (gümrük beyanı, tartı, simsar);
   - parti başına ek elleçleme süresi;
   - broken stowage (her ek parti ambarın bir kısmını israf eder).

   Üstel yönetim maliyeti yok. Sınır kendiliğinden oluşmalı. Düzeyler kaba ⚠️.
9. **(2026-11-12, kullanıcı) Kâr kaydı parti başına:** her parti satılınca o partinin kârı kaydedilir. Gemi zamanı ve sabit maliyetler partilere bölünür.
