# Medi — Ana Doküman
> Son güncelleme: 2026-10-23

Bu doküman projenin haritasıdır: hangi bilgi nerede, ne neyle ilişkili. Her oturumun başında okunur. Çalışma kuralları için: [CLAUDE.md](../CLAUDE.md).

## Proje durumu

**Aşama:** Faz 1, çerçeve. Araştırmanın 1. ve 2. turu tamamlandı; kullanıcı yorumları (`yorumlar.md` (yerel dosya, repoda yok)) işlendi.
**Aşama güncellemesi:** Faz 3 sürüyor. **D1 serisi kapandı** (D1 → D1f → D1g). Tek limanlı modelin önerilen hali: ön ayar `H`, κ=0,01 ([D1g özet tablosu](experiments/D1g.md)).
**D2 tamamlandı** → [D2](experiments/D2.md): tek fiyat yasası ✅; anlık bilgiyle fırsatlar ölüyor (Bannerlord) → fırsatlar sürtünmeden gelmeli.
**D3 tamamlandı** → [D3](experiments/D3.md): bilgi gecikmesi fırsatları canlı tutuyor (%0,3 → %20-40 gün); bilginin değeri +11-23 puan/yıl; en iyi beklenti: dağılım + olağana dönüş.
**D3b tamamlandı** → [D3b](experiments/D3b.md): kullanıcının "senet + risk" dengesi orta hızlı girişte kendiliğinden oluşuyor (sektör %6-11, bilgili tüccar %13-17); giriş hızı = rant düğmesi.
**D4 tamamlandı** → [D4](experiments/D4.md): LES + CES talebi; kıtlık lüksü vuruyor (Labrousse), buğday-arpa ikamesi; kent sınıfları gerekli.
**D4b tamamlandı** → [D4b](experiments/D4b.md): kumaş salınımı artifact'tı (düzeltildi); 3 sınıf kıtlıkta lüks çöküşünü önlüyor; kumaş ikiye ayrılmalı.
**D4c tamamlandı** → [D4c](experiments/D4c.md): yün → kaba ve ince kumaş; ortak hammadde aktarımı ✅; Labrousse çarpanı kapalı tek kentte zayıf (ihracat gerekli).
**D5 (ilk entegrasyon) durduruldu** → [D5](experiments/D5.md): kararlı duruma ulaşılamadı; asıl bulgu **toptan ticaret katmanının eksikliği**.
**D5a tamamlandı** → [D5a](experiments/D5a.md): kapan, D5'in el yamalarının yerini aldı (0/5 patlama, 0 tuzak). Kalan: ticaret yoğunluğu düşük.
**D5a2 tamamlandı** → [D5a2](experiments/D5a2.md): rekabetçi perakende (K-016) mekanik çekişin yerini aldı; marj kuramsal değerde, dükkân sayısı geçim gideriyle pazar büyüklüğüne göre; aktarım simetrik; kıtlık artık fiyatla paylaştırılıyor. Açık: kıtlık zirveleri ve Venedik'te malsız günler (arz tarafı → D5b).
**D5a3 tamamlandı** → [D5a3](experiments/D5a3.md): Venedik'in yağsız kalmasının nedeni donmuş son işlem fiyatıydı; açık teklif + tâtonnement (K-017) ile ithalat ihtiyaca yetişti. Açık: hasat öncesi buğday zirveleri (tüccar tarafı → D5b).
**D5b tamamlandı** → [D5b](experiments/D5b.md): rakip bilgisi (söylenti + limandaki gemiler) herding'i çözüyor; rakip bilgisi olmadan biber nişi bütün tüccarları kilitliyor. Düzey 0 tüccarlar zarar ediyor; taklit çağlayan doğurmadı. Kalan: ince pazar tuzağı (satış kararı → D5b2), yavaş giriş (rant).
**D5b2 tamamlandı** → [D5b2](experiments/D5b2.md): G/B/S/L faktöriyel. İki motor artifact'ı bulundu: Zeno (kırıntı kargo tüccarı kilitliyordu; D5b'nin "kalan ince pazar tuzağı" buydu) ve ısınma (14 tüccarla başlangıç, ilk yıl giriş yok). L (depocu) en etkili tek yuva. S fazla gönderim üretiyor, B'nin kendi-etki parçası dengeliyor. İleriye bakan temel beklenti bu hâliyle yarar getirmiyor → S-014. Önerilen yapı: GBSL·imp.
**Beklenti araştırması** → [07-expectation-formation](research/simulation/07-expectation-formation.md): tüccar ticareti negatif geri beslemeli, literatüre göre teknik analiz bu piyasayı yönetmez. Öneriler: S-014 / A10 (HSM + bilgi temelli temel), S-012 / A11 (sermaye havuzu + kamuya açık fırsatla giriş + spin-up).
**D5b3 tamamlandı** → [D5b3](experiments/D5b3.md): fırsata bağlı giriş rantı eritiyor (%33 → %1-5; hedef %8'in altında, kalibrasyon); spin-up çalışıyor; colleganza adverse selection'la zarar ediyor (itibar adayı). Bulunan hata: bütçesiz dükkân teklifi pazarı donduruyordu.
**D5b3b tamamlandı** → [D5b3b](experiments/D5b3b.md): itibar kapısı colleganza kaybını −%24'ten −%4'e indirdi; sıralama formülü fark etmiyor (skill vs luck, rastgele ablasyon); denge getirisi %5-6, hedefin altında. Kullanıcıyla konuşulacak: giriş friction'ı, yatırımcı öğrenmesi, sözleşme biçimi.
**D5b3e (devam):** [D5b3e](experiments/D5b3e.md) E1, E2, E3 ve tam harita (45 pazar) koşuldu. Büyük haritada rotalar kendiliğinden dağılıyor; ağ ve ev etkisiz; getiri ~%0, filo 3 kat: sorun fazla giriş. Giriş teşhisi: [D5b3f](experiments/D5b3f.md). Filo döngüde (cobweb), soğuk başlangıç artifact'ı, yavaş çıkış. Sıradaki: düzeltme ve bariyer seçimi ([11](research/simulation/11-entry-barriers.md), S-020). K-027: ev = büyük tüccar. Araştırma [10](research/simulation/10-route-choice-coordination.md). K-025: getiri ölçütü = toplam sermaye getirisi.
**D5b3d tamamlandı** → [D5b3d](experiments/D5b3d.md): sefer bazlı alacaklı (K-023) borçtan iflası azaltıyor ama borcu da kesiyor; öz sermayede batma bedeli (K-024) girişi kısıyor ve getiriyi yükseltiyor; **kalabalık filodan bağımsız** (koordinasyon → D5b4). T1: "denge %0" yargısı yanıltıcı ölçütten; toplam sermaye getirisi ~%12-13, dağılım çok çarpık.
**D5b3c tamamlandı** → [D5b3c](experiments/D5b3c.md) (K-022 hibrit finansman): borçlanma kararı istenen yönde (düzey 0 ve temkinli tüccar az borçlanıyor), ama alacaklı senedin altında kazanıyor; kök neden sefer getirisinin oynaklığı (sd %40-90). Araştırma [08](research/simulation/08-trade-finance-contracts.md). Teşhis T2: oynaklığın ~%40'ı ölçüm, gerçek kaynak varıştaki kalabalık; sıfır-kâr boş kapasiteyle geliyor (ambar %9 dolu). Tartışılıyor: sefer bazlı alacaklı (A13, S-015) ve perfect competition (S-017, A14; araştırma [09](research/simulation/09-market-structure-entry.md)).
**Sonraki adım:** D5b4 beklenti turnuvası ([tasarım](design/expectation-tournament.md)), taban OS → D5c (tam dilim). Tasarım: [wholesale-and-behavior](design/wholesale-and-behavior.md).
**GitHub vitrini (2026-11-17):** Proje `mgeckil18/meditrader` olarak (önce private) yayına hazırlandı. İngilizce özet katmanı [`../showcase/`](../showcase/) ve kök [`../README.md`](../README.md): vizyon, tasarım, 5 seçilmiş deney (D2, D3, D3b, D4b, M2), codex, mühendislik, araştırma. Türkçe dokümanlar asıl kaynak; showcase onları özetler. Grafikler: `showcase/experiments/make_figures.py`. CI: `.github/workflows/ci.yml` (fmt, clippy, test, parity). Lisans: all rights reserved.
**Projenin güncel yön haritası:** [design/framework.md](design/framework.md) (güven seviyeli: ilke / yön / aday / ertelendi)

## Doküman haritası

### Çekirdek
| Doküman | İçerik |
|---|---|
| [vision.md](vision.md) | Oyunun vizyonu: ne, ne değil, temel deneyim |
| [decisions.md](decisions.md) | Numaralı karar günlüğü (K-001...) |
| [open-questions.md](open-questions.md) | Açık sorular (S-001...) |
| [glossary.md](glossary.md) | Tarihsel ve teknik terimler sözlüğü |

### Codex (`codex/`): oyun içi bilgi pencereleri (K-015)
| Doküman | İçerik |
|---|---|
| [codex/README.md](codex/README.md) | Amaç, giriş biçimi, kurallar |
| [codex/economics.md](codex/economics.md) | Piyasa ve fiyat kavramları (30 giriş) |
| [codex/behavior.md](codex/behavior.md) | Davranışsal ekonomi ve bilgi (15 giriş) |
| [codex/institutions.md](codex/institutions.md) | Tarihsel kurumlar (15 giriş) |

### Araştırma (`research/`): dünyada ne var, tarihte ne olmuş
| Doküman | İçerik |
|---|---|
| [games/trade-game-mechanics.md](research/games/trade-game-mechanics.md) | Offworld, Patrician, Rise of Venice, Victoria 3, EU4, X4, EVE, UO, Bannerlord, Taipan, Uncharted Waters: mekanikler ve dersler |
| [simulation/economy-simulation-techniques.md](research/simulation/economy-simulation-techniques.md) | (1. tur) Toplu ve ajan tabanlı modeller, Doran-Parberry, kaynak-yutak, başarısızlık kalıpları, tick yapısı, ölçüm metrikleri |
| **Ekonomi simülasyonu derin araştırma (2. tur):** | |
| [simulation/00-synthesis.md](research/simulation/00-synthesis.md) | ⭐ **Sentez:** önerilen katmanlı mimari, bilgi sistemi, ayar düğmeleri, riskler, deney planı |
| [simulation/01-economic-fundamentals.md](research/simulation/01-economic-fundamentals.md) | Arz-talep (rezervasyon fiyatları), esneklik (King-Davenant), mekânsal denge ve arbitraj bandı, depolama, örümcek ağı ve gecikmeler, bilgi ve arama (Stigler, Geertz), beklentiler, fiyat ayarlama, para, itibar (Greif) |
| [simulation/02-market-mechanisms.md](research/simulation/02-market-mechanisms.md) | Fiyat oluşum mekanizmaları: formül, toplu emir, çağrılı ve sürekli açık artırma, ikili pazarlık, **dealer modeli**, kitle havuzları, bilgi yaşına dayalı inanç |
| [simulation/03-academic-abm.md](research/simulation/03-academic-abm.md) | ACE, Santa Fe borsası, Brock-Hommes, Kirman balık pazarı, Sugarscape, Gintis, söylenti modelleri, tarihsel ajan modelleri (MERCURY, Hansa), stilize gerçekler |
| [simulation/04-games-deep-dive.md](research/simulation/04-games-deep-dive.md) | Victoria 2, Starsector, Space Rangers 2, Port Royale 4, Prosperous Universe, RuneScape GE, Eco, Dwarf Fortress; tekrarlayan kalıplar; 7 ders |
| [simulation/05-non-game-applications.md](research/simulation/05-non-game-applications.md) | Merkez bankaları (BoE, EURACE), ABIDES, Bira Oyunu, mekânsal denge modelleri, araçlar (Mesa, NetLogo, BazaarBot) |
| [simulation/06-validation-and-tuning.md](research/simulation/06-validation-and-tuning.md) | ODD protokolü, desen odaklı doğrulama (P1-P12), kalibrasyon, istismar botları, okunabilirlik |
| [simulation/15-macro-abm-methods.md](research/simulation/15-macro-abm-methods.md) | Büyük ölçekli ekonomi ABM'leri (EURACE, K+S, CATS/Mark-0, IIASA), gemi piyasası ABM'leri, kalibrasyon (SMD, Bayesçi/ABC, ML surrogate), ergodiklik, devrilme noktaları; bizim için dersler |
| [tech/01-simulation-engine-options.md](research/tech/01-simulation-engine-options.md) | Simülasyon motoru: Python'un sınırı (profil, paralel ölçek), büyük simülasyon oyunları (Victoria 3 tick task, DF), alternatifler (PyPy, Numba, Rust/C++/Julia/C# hibrit); migration kararı yok |
| [tech/02-performance-plan.md](research/tech/02-performance-plan.md) | Motoru hızlandırma: tam harita ölçümü ve profili (`_rivals` %40), algoritma düzeltmeleri (3-5× tahmin), oyunlar (Victoria 3, Factorio, RimWorld), seçenekler, aşamalı öneri (Python algoritma → taşınabilirlik → Rust çekirdek); S-019 |
| [simulation/10-route-choice-coordination.md](research/simulation/10-route-choice-coordination.md) | Rota seçimi ve kalabalık: congestion game, El Farol, QRE / random utility, correlated equilibrium, Roy modeli; tüccar ağları (Trivellato), şubeli evler (Datini); S-018 |
| [simulation/11-entry-barriers.md](research/simulation/11-entry-barriers.md) | Sermaye dışındaki giriş bariyerleri: türler (eşit batık maliyet / maliyet farkı / miktar sınırı / zamanla aşılan / sonlu girişimci arzı), 16. yy örnekleri, motordaki karşılıklar; S-020 |
| [simulation/12-entry-decision-timing.md](research/simulation/12-entry-decision-timing.md) | Giriş kararının zamanlaması: kullanıcının 3 × 3 ay teyit önerisi; real options, hysteresis bandı, time-to-build, SPRT, drift diffusion, status quo bias; alternatif: real options bandı |
| [simulation/13-literature-map.md](research/simulation/13-literature-map.md) | Deneylerin literatür karşılıkları (2026-10-23 ve sonrası); sürekli güncellenir |
| [simulation/09-market-structure-entry.md](research/simulation/09-market-structure-entry.md) | Piyasa yapısı ve giriş: uzun dönem rekabetçi denge, tarife yükü, fazla giriş, giriş eşikleri, meslek seçimi; Venedik vatandaşlığı, muda/incanto, iflas; Rialto bilgi merkezi; S-017 |
| [simulation/08-trade-finance-contracts.md](research/simulation/08-trade-finance-contracts.md) | Ticaret finansmanı: costly state verification, credit rationing, teminat; Venedik sea loan → commenda (González de Lara), sınırda borç (Williamson); para vakıfları; supplier credit, cambio; S-015 / A12 |
| [simulation/07-expectation-formation.md](research/simulation/07-expectation-formation.md) | Beklenti oluşumu: adaptive, REH, trend, fundamentalist/chartist, heuristic switching, learning from experience, diagnostic; learning-to-forecast deneyleri: geri besleme yönü (negatif → yakınsama, pozitif → balon); 16. yy tüccarının haber temelli beklentisi |
| [history/mediterranean-16c-overview.md](research/history/mediterranean-16c-overview.md) | 16. yy Akdeniz: aktörler, mallar, rotalar, riskler, finans, kritik olaylar |
| [history/consumer-profiles-16c.md](research/history/consumer-profiles-16c.md) | 16. yy kent tüketici profilleri: bütçe çapaları (Pamuk, Drelichman-González, Allen), 5 sınıf şablonu, 6 kent tablosu, D4b için 3 sınıflı LES parametreleri |
| [history/maritime-risk-16c.md](research/history/maritime-risk-16c.md) | Deniz riski ve sigorta: prim yapısı (bölge ve korsan > mesafe, mevsim küçük), 16. yy primleri, kayıp sıklığı, bizim haritanın bölgeleri |
| [history/shipping-scale-16c.md](research/history/shipping-scale-16c.md) | Gemi işletmesinin ölçeği: yılda 2-4 sefer (modelde 8-15), yıllık kayıp %4-12, gemi bedeli (Gluzman), ömür; limanda geçen zaman eksik |
| [history/ship-operating-costs-16c.md](research/history/ship-operating-costs-16c.md) | Gemi işletme maliyetleri (S-028): maliyet gemi başına ve limanda birikiyor (Jones 1998), mürettebat + kumanya yılda gemi değerinin ~%30-60'ı (modelde %12), navlun mal değerinin %15-20'si, uğrak resimleri küçük, gümrük karaya çıkarken |
| [history/ship-life-piracy-16c.md](research/history/ship-life-piracy-16c.md) | S-022 araştırması: gemi ömrü ~10 yıl (Gluzman; 15 değil), yıllık kayıp ~%10-13 (savaşlar dahil), yabancı gemi ucuzdu (koloni −%17; engel yasa), korsanlık 1580-1620 patlaması (Fontenay, Tenenti); time-to-build (Kalouptsidi 2014), ikinci el / yeni gemi fiyatı |
| [history/port-hierarchy-16c.md](research/history/port-hierarchy-16c.md) | K-034 araştırması: Cenova'nın doğusunda liman hiyerarşisi (bölge bölge büyük/orta/küçük), liman = fiziksel + pazar + kurum, gemi tipleri (nave, marciliana, caramusal, tartana), gemi boyunun ekonomisi, Taaffe-Morrill-Gould, Fujita-Mori, central place |
| [history/reading-list.md](research/history/reading-list.md) | Okuma listesi (Braudel ve diğerleri) |

### Tasarım (`design/`): biz ne yapacağız
| Doküman | İçerik |
|---|---|
| [design/framework.md](design/framework.md) | ⭐ **Genel çerçeve v0:** ilkeler, yönler, adaylar, ertelenenler; dükkâncı modeli, dinamik kurumlar, zorluk gürültüsü, ajan dağılımı; yol haritası |
| [design/simulation-spec.md](design/simulation-spec.md) | ⭐ **Simülasyon spesifikasyonu v0** (ODD formatı): ilk dilim (6 liman, 8 mal), varlıklar, günlük süreç, alt modeller, metrikler, deneyler D1-D5 |
| [design/port-call-mixed-cargo.md](design/port-call-mixed-cargo.md) | **Liman uğrağı (K-040):** kısmi satış, zamana yayılan elleçleme, karışık yük, birleşik uğrak planı; açık sorular S1 karşı taraf, S2 değerli mal hızı, S3 kâr kaydı |
| [design/mechanism-registry.md](design/mechanism-registry.md) | **Mekanizma kaydı:** her mekanizmanın kökeni (kullanıcı / Claude / literatür), eklendiği deney ve durumu (CLAUDE.md 7d) |
| [design/product-assessment.md](design/product-assessment.md) | Ürün değerlendirmesi: satılabilirlik, fark (bilgi oyunun malı), öğrenme eğrisi, tema, en büyük risk (eğlence sınanmadı → erken oynanabilir dilim) |
| [design/expectation-tournament.md](design/expectation-tournament.md) | D5b4 tasarımı: beklenti turnuvası (naive, çapalama/C4, adaptive, trend, bilgi temelli temel, HSM), kurulumlar ve ölçütler; TR'nin sönmesi doğrulama testi |
| [design/wholesale-and-behavior.md](design/wholesale-and-behavior.md) | **Kararlaştı (K-013, K-014, K-016):** kurumsal toptan pazar (kapan), rekabetçi perakende, tüccar çeşitliliği (level-k, taklit, risk, aşırı güven, bilgi kaynakları), rakip bilgisinin söylentiyle yayılması; D5a-c planı |
| [design/production-chains.md](design/production-chains.md) | **Öneri:** hammadde → son ürün zincirleri, ortak hammadde (yün → kaba ve ince kumaş), üretici havuzları (bireysel ajan değil), ücretler ve Labrousse çarpanı, D4c deney planı |
| [design/information-model.md](design/information-model.md) | Fiyat bilgisinin olasılık dağılımı olarak tutulması ve gösterilmesi (log-normal, eskime, bilgi birleştirme, zorluk modları) |
| [design/risk-model.md](design/risk-model.md) | **Taslak (K-030):** risk katmanları (doğal, korsan, ticari), bacak bazlı tehlike, ajanların dinamik risk tahmini, sigorta, yatırımcı primi (c); R1-R5 |
| [design/determinism.md](design/determinism.md) | Deterministik simülasyon ve rastgelelik (K-010) |
| [design/rust-core.md](design/rust-core.md) | Rust çekirdek: kapsam, bit düzeyinde eşdeğerlik yöntemi (durum dökümü + gün izi + uçtan uca karşılaştırma), mimari, durum (taşıma tamam: soğuk başlangıç, snapshot, teşhis, koşucu), hız (VRS ~30×, F ~45-60×), deney koşma (`core/tools/run_rs.py`), port sırasında bulunanlar; kod `core/` |
| [design/trade-structure.md](design/trade-structure.md) | Ticaretin yapısı: kârlılığın boyutları (dışsal/içsel), oynanış (gönderi ve portföy), taşıma boyutları, liman hiyerarşisi kararı (K-034, K-035), liman = fiziksel + pazar + kurum, yol haritası M0-M6 |
| [design/map-v1.md](design/map-v1.md) | Tam harita v1 (M1): 20 liman (Cenova'nın doğusu, büyük ve orta), bacaklar, bölgeler, arz planı; kaba veri, `core/tools/mapgen.py` |

### Süreç kaydı (`process/`): ne denendi, ne bulundu (kronolojik, başarısız denemeler dahil)
| Doküman | İçerik |
|---|---|
| [process/README.md](process/README.md) | Süreç kaydının kuralları |
| [process/timeline.md](process/timeline.md) | Kronolojik akış: araştırma, kararlar, deneyler |
| [process/experiment-log.md](process/experiment-log.md) | Deneme deneme günlük: hipotez → değişiklik → sonuç → karar |
| [process/lessons.md](process/lessons.md) | Başarısızlık kalıpları, tasarım ilkeleri, yöntem dersleri |

### Deneyler (`experiments/`): simülasyon deneylerinin sonuç raporları
| Doküman | İçerik |
|---|---|
| [experiments/D1.md](experiments/D1.md) | D1: tek liman, tek mal. v0 hiperenflasyonu → v3 kararlı; 3 patlama mekanizması; kötü hasat tepkisinin gecikmesi ve stokçu rolü ihtiyacı |
| [experiments/README.md](experiments/README.md) | ⭐ **Deney stratejisi:** neden yapıyoruz (yapı, parametre değil), mekanizma yarışması yöntemi, ölçütler, durma kuralı, ML kalibrasyonu, gereksinim listesi, yol haritası D2-D5 |
| [experiments/D5b.md](experiments/D5b.md) | D5b: tüccar kişiliği (level-k, taklit, aşırı güven, DARA, ağ) ve rakip bilgisi; El Farol herding'i; kişiliklere göre getiri; ince pazar tuzağı (D5b2: kalan kısmı kırıntı artifact'ıydı) |
| [experiments/D5b2.md](experiments/D5b2.md) | D5b2: görünürlük, ileriye bakan beklenti, satış kararı, likidite (G/B/S/L) faktöriyel; Zeno ve ısınma artifact'ları |
| [experiments/D5b3e.md](experiments/D5b3e.md) | D5b3e planı: rota kalabalığı (ablation, muhabir ağı, çok gemili ev); ölçütler ve tasarım soruları |
| [experiments/D5b3f.md](experiments/D5b3f.md) | D5b3f giriş teşhisi: filo döngüsü (cobweb), soğuk başlangıç artifact'ı, kuralın durma noktası, yavaş çıkış, survivorship, bonus; düzeltme adayları |
| [research/simulation/14-natural-entry-exit.md](research/simulation/14-natural-entry-exit.md) | Giriş-çıkışı doğal mekanizmalara bağlama önerileri (İ12): ölçüm, veriden credibility, eşik bileşenleri (Arrow-Pratt, tarihsel senet), gemi piyasası (Dixit, shipping cycles, Lane), bilgi temelli sicil |
| [process/durum-2026-11-02.md](process/durum-2026-11-02.md) | Durum özeti (2026-11-02): son 5 iş (D5b3e tam harita, bariyerler + K-028, D5b3f teşhis, K-029 + D5b3g, U / R / U + R), modelin sağlamlığı, uyarılar, bekleyen kararlar |
| [experiments/D5b3g.md](experiments/D5b3g.md) | D5b3g (K-029): snapshot başlangıcı, ortak eşik (senet + prim), sefer sonunda çıkış, batanlar dahil kamu sicili, credibility; öz sermaye ölçüm düzeltmesi; sönümleme ablation'ları; U / R / U + R (bant sönümlüyor, U tek başına değil) |
| [experiments/D5b3h.md](experiments/D5b3h.md) | D5b3h: Ö0 ölçüm (güven aralığı, örüntüler), Ö1 Bühlmann credibility (kendi sicil bilgi taşımıyor: k = ∞), Ö2 senet getirisi doğrulaması (%3,7-4,0) |
| [experiments/D5b3i.md](experiments/D5b3i.md) | D5b3i: risk modeli R1, bacak ve bölge tehlikesi, dinamik korsan baskısı, gemi kaybı bedeli |
| [experiments/D5b3j.md](experiments/D5b3j.md) | D5b3j (Ö3, K-032): gemi piyasası; Tobin's q değerlemesi, ikinci el çağrılı pazar, tersane kuyruğu, yabancı gemi, yaşlanma; band (R) kaldırıldı |
| [experiments/M1.md](experiments/M1.md) | M0 (harita veriden; Python ile eşit) ve M1 (20 liman) koşuları; hayalet seçenekler ve kalkış arzı (M1.2); gemi kaybı diagnostiği (M1.3); üç kayıp düzeltmesi (M1.4) |
| [experiments/M2.md](experiments/M2.md) | M2 planı (limanda zaman, gemi tipleri, liman fiziği); limanda zamanın tarihsel dayanağı; M2.1 (elleçleme, doldurma kararı, gemi riski) koşuları ve teşhis |
| [experiments/D5b3d.md](experiments/D5b3d.md) | D5b3d: sefer bazlı alacaklı, öz sermayede batma riski, gemi masrafı, ölçüm düzeltmesi; T1 getiri farkı (medyan ile toplam getiri) |
| [experiments/D5b3c.md](experiments/D5b3c.md) | D5b3c: hibrit finansman; borç, deniz ödüncü, batma korkusu ablasyonu, denetlenebilir colleganza, yatırımcı öğrenmesi; sefer getirisi oynaklığı teşhisi |
| [experiments/D5b3b.md](experiments/D5b3b.md) | D5b3b: colleganza + itibar (kullanıcı skoru, credibility, rastgele ablasyon); skill vs luck; sıfır-kâr + asimetrik sözleşme |
| [experiments/D5b3.md](experiments/D5b3.md) | D5b3: spin-up, liman sermaye havuzu, fırsata bağlı giriş, colleganza; optimizer's curse; tahmin yanlılığı ölçümü; bütçesiz teklif hatası |
| [experiments/D5a3.md](experiments/D5a3.md) | D5a3: malı olmayan pazarda fiyat keşfi; donmuş fiyat artifact'ı; açık teklif + sınırlı tâtonnement |
| [experiments/D5a2.md](experiments/D5a2.md) | D5a2: rekabetçi perakende (logit + Lerner + türetilmiş talep + giriş); teşhis; fiyatla vs. kuyrukla paylaştırma; rockets and feathers neden çıkmadı |
| [experiments/D5a.md](experiments/D5a.md) | D5a: kurumsal toptan pazar (kapan); A/B/C karşılaştırması; el yamaları gereksiz; ticaret yoğunluğu sorunu |
| [experiments/D5.md](experiments/D5.md) | D5 ilk entegrasyon (durduruldu): 9 sorun ve düzeltme zinciri; toptan katman eksikliği; herding, likidite tuzağı; yuva yuva entegrasyon önerisi |
| [experiments/D4c.md](experiments/D4c.md) | D4c: üretim zinciri (yün → kaba / ince kumaş), üretici havuzları, ücretler; ortak hammadde etkileri; Labrousse çarpanı ve ihracat ihtiyacı |
| [experiments/D4b.md](experiments/D4b.md) | D4b: kumaş salınımı ablasyonla artifact olarak sınıflandırıldı; 3 kent sınıfı; kıtlıkta sınıflar arası akış; kaba/ince kumaş ayrımı |
| [experiments/D4.md](experiments/D4.md) | D4: çok mal, ortak bütçe. Talep modeli yarışması: LES + CES kazandı; income ve substitution effect; Labrousse etkisi; kent sınıfları gerekli |
| [experiments/D3b.md](experiments/D3b.md) | D3b: senete bağlı serbest giriş-çıkış. Kullanıcının dengesi ✅; giriş hızı = rant/rekabet düğmesi; domuz döngüsü; hayatta kalanlar yanılgısı; bilgi avantajı dengede korunuyor |
| [experiments/D3.md](experiments/D3.md) | D3: bilgi gecikmesi. Fırsatlar canlı ✅; bilginin değeri ölçüldü; sürü/örümcek ağı salınımı; dağılım + olağana dönüş en iyi; rakip farkındalığı başarısız |
| [experiments/D2.md](experiments/D2.md) | D2: iki liman, gezgin tüccarlar, anlık bilgi. Tek fiyat yasası ✅; Bannerlord sorunu ölçüldü; kural seçimi = fırsat rejimi; kıtlık yayılımı ve ihracat yasağı gerekçesi |
| [experiments/D1g.md](experiments/D1g.md) | D1g: mevsim deseni. İntegral gecikmesi → PI fiyat kuralı; köylünün hasat sonrası nakit ihtiyacı; medyan "olağan fiyat"; **D1 serisinin son hali (H)** |
| [experiments/D1f.md](experiments/D1f.md) | D1f: stokçu + köylünün kendi tüketimi + yerine koyma maliyeti. Anında kıtlık tepkisi ✅, King-Davenant'a yakın eğri ✅; kirlenen hafıza, roket ve tüy asimetrisi, simetri ilkesi |

### Kod
| Yol | İçerik |
|---|---|
| `sim/` | Simülasyon çekirdeği (Python): `rng.py` (seed'li akışlar), `ledger.py` (muhasebe), `model.py` (havuzlar, dükkâncı, stokçu), `engine.py` (tek liman motoru; ön ayarlar V0-V3, F, G, **H**), `world.py` (D2-D3b: iki liman + tüccarlar, bilgi, giriş-çıkış), `multigood.py` (D4-D4b: çok mal, sınıflı ortak talep), `production.py` (D4c: üretim zinciri, üretici havuzları), `world5.py` (D5: tam dilim, deneysel) |
| `experiments/` | Deney betikleri; çıktılar `experiments/out/` (git dışı) |

### Kullanıcı notları
| Doküman | İçerik |
|---|---|
| `yorumlar.md` (yerel dosya, repoda yok) | Kullanıcının araştırma raporlarına yorumları (2026-10-22). İşlendi → framework.md, information-model.md |

## İlişki haritası (kavramlar arası)

```
Bilgi gecikmesi ─────┬─→ Kalıcı fiyat farkları (EVE dersi) ─→ Oyuncuya fırsat
(tarih: Sardella,    │                                         ↑
 Braudel, ~40 gün)   └─→ Fiyat inancı aralıkları (Doran-Parberry)
                                                               │
NPC = oyuncu ile aynı kurallar (K-004) ─→ Risk: fiyat eşitlenmesi (Bannerlord)
                                          Çözüm: bilgi gecikmesi + kapasite + heterojenlik + şoklar

Senetler (S-005) ←── Monte senetlerinin piyasa fiyatı, İspanya iflasları
Bölgesel itibar (K-003) ←── Tüccar diasporaları (Yahudi, Rum, Ragusalı, Ceneviz)
Dolaylı çatışma (K-007) ←── Ragusa tarafsız bayrağı, korsanlık, fidye, sigorta
Zaman (K-006) ─→ Hibrit: günlük tick + ayrık olay kuyruğu (00-sentez §3, ABIDES)
Determinizm (K-010) ─→ Çoklu seed testleri, desenler P1-P12, istismar botları (06)

Bölgesel itibar (K-003) ←── Kirman sadakati + Geertz müşterileşmesi + Greif koalisyonları (01 §6, §10; 03 §4)
Temsilciler (K-008)     ←── Greif'in Mağribi tüccarları, asil-vekil problemi, Ermeni tüccarlar (01 §10; 03 §10)
Liman pazarı            ←── Dealer modeli (Amihud-Mendelson) + kitle havuzları (02 §5-6)
Haber sistemi           ←── Daley-Kendall söylenti modeli + bilgi yaşına dayalı inanç (02 §7; 03 §9)
Senetler (S-005)        ←── Santa Fe tahvil alternatifi = ticaretin fırsat maliyeti (03 §2)
```

## Klasör yapısı

```
medi/
├── CLAUDE.md                 Çalışma kuralları
└── docs/
    ├── INDEX.md              ← buradasın
    ├── vision.md
    ├── decisions.md
    ├── open-questions.md
    ├── glossary.md
    ├── research/
    │   ├── games/
    │   ├── history/
    │   └── simulation/
    └── design/
```
