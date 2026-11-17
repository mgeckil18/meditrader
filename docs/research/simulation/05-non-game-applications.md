# 05 — Oyun Dışı Uygulamalar ve Araçlar
> Durum: taslak (derin araştırma, 2. tur)
> Son güncelleme: 2026-10-22
> İlgili: [03-akademik modeller](03-academic-abm.md), [00-sentez](00-synthesis.md)

Ekonomi simülasyonunun gerçek dünyada nerede kullanıldığı ve bizim için hangi araçların ve fikirlerin işe yarayacağı.

---

## 1. Merkez bankaları ve politika

### İngiltere Merkez Bankası: Birleşik Krallık konut piyasası ajan modeli (2016)
- Baptista, Farmer, Hinterschweiger, Low, Tang ve Uluc. Staff Working Paper No. 619. INET Oxford ile ortak proje. ([BoE PDF](https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2016/macroprudential-policy-in-an-agent-based-model-of-the-uk-housing-market.pdf), [INET](https://www.inet.ox.ac.uk/news/bank-of-england-wp))
- Merkez bankası politika yapımını desteklemek için kullanılan ilk ajan modellerinden biri.
- İlk kez ev alanlar, ev sahipleri, kiraya vermek için alanlar ve kiracılar ayrı ayrı modellenmiş. Kredi/gelir sınırı politikasının konut fiyat döngüsünü yumuşattığı gösterilmiş.

**Bizim için:** "Tipolojik ajanlar" yaklaşımı: aynı piyasada farklı amaçlara sahip ajan türleri (kendi kullanımı için alan, yatırımcı, spekülatör). Bizde de tahıl alan şehir ambarı, fırıncı, spekülatör ve ihracatçının hepsi aynı mala farklı nedenlerle talep eder.

### EURACE (AB projesi)
- Tam bir ekonominin ajan modeli: haneler (tüketici, işçi, yatırımcı), tüketim ve sermaye malı üreticileri, bankalar, hükümet ve merkez bankası; konut ve kredi dahil birçok piyasa. ([EURACE projesi](https://ideas.repec.org/p/ekd/002596/259600063.html), [Raberto vd.](https://www.siecon.org/sites/default/files/media_wysiwyg/raberto.pdf))
- Konut ve ipotek uzantısı: kredi güdümlü iş döngüleri.

**Bizim için:** **Kredi döngüleri** önemli bir ders. Kredi bollaşınca ticaret artar, fiyatlar yükselir, sonra bir şok gelince kredi daralır ve iflas dalgası olur. 16. yüzyılda Ceneviz fuarları ve İspanya iflasları tam da böyle döngüler yarattı. Kredi sistemi (geç oyun) bunu modellemeli.

## 2. Finansal piyasa simülatörleri

### ABIDES (JP Morgan / Georgia Tech)
- Açık kaynak ajan tabanlı etkileşimli ayrık olay simülasyonu (Agent-Based Interactive Discrete Event Simulation). Çekirdeği genel amaçlı bir ayrık olay simülatörü. NASDAQ protokollerini (ITCH/OUCH) taklit eden bir borsa ve gecikme modellemesi var. On binlerce tüccar ajanını simüle edebiliyor. ([arXiv 1904.12066](https://arxiv.org/pdf/1904.12066), [GitHub](https://github.com/abides-sim/abides))

**Bizim için en önemli fikir: ayrık olay simülasyonu (discrete event simulation, DES).**
- Her şeyi her tick'te güncellemek yerine olaylar bir **öncelik kuyruğunda** tutulur ("gemi X, 14 Mart'ta Korfu'ya varacak"). Simülasyon bir sonraki olaya atlar.
- **Gecikme modellemesi:** Mesajların varış zamanı var. Bu, bizim **haber gecikmesi** fikrinin mühendislik karşılığı.
- Bizim için hibrit öneri: günlük tick (pazarlar, toplu talep) + ayrık olay kuyruğu (gemi varışları, haber varışları, ajan karar anları). Bkz. [00-sentez](00-synthesis.md).

### Santa Fe Yapay Borsası
Bkz. [03 §2](03-academic-abm.md).

## 3. Tedarik zinciri ve yöneylem araştırması

### Bira Dağıtım Oyunu (MIT, Sterman 1989)
- Bkz. [01 §5](01-economic-fundamentals.md). Gecikmeler ve geri bildirim döngüleri kamçı etkisini yaratıyor. ([Forio](https://forio.com/store/mit-beer-game-supply-chain-simulation))
- 53 çalışmayı inceleyen bir derlemeye göre bu alandaki modellerin çoğu bira oyununu temel alıyor. ([GALA](https://gala.gre.ac.uk/id/eprint/32125))

**Bizim için:** Bira oyunu bir **eğitim oyunu**; insanların gecikmeli sistemleri kötü yönettiğini göstermek için tasarlanmış. Bizim oyunda bu zorluk bir **özellik**, ama oyuncuya araç vermeliyiz: yoldaki mallar, beklenen varışlar, eski bilgi uyarıları.

### Mekânsal fiyat dengesi modelleri (Takayama-Judge)
- Tarım ekonomisinde ve politika analizinde (Dünya Bankası gibi) bölgeler arası ticaret akışlarını hesaplamak için kullanılır. ([Dünya Bankası](https://documents1.worldbank.org/curated/pt/623561493321126110/pdf/DWC8402000A0sp0sh0equilibrium0model.pdf))

**Bizim için:** **Doğrulama aracı** olarak kullanılabilir. Simülasyonumuzun "denge" durumunu, Takayama-Judge tarzı bir optimizasyonla hesaplanan teorik dengeyle karşılaştırabiliriz. Ajanlar tam bilgiyle bu dengeye ulaşmalı; bilgi gecikmesi olunca **ne kadar uzaklaştıkları** ise "oyuncu fırsatı"nın ölçüsü olur.

## 4. Emtia ve tarım ekonomisi

- **Rekabetçi depolama modeli** (Deaton & Laroque): emtia fiyat tahmini ve gıda güvenliği politikasında kullanılıyor (IMF, FAO). Bkz. [01 §4](01-economic-fundamentals.md).
- **King-Davenant yasası:** Güvenilir üretim verisi olmayan dönemlerde fiyatlardan üretim tahmin etmek için hâlâ kullanılıyor (İngiliz buğdayı 1645-1761 çalışması). ([UB](https://diposit.ub.edu/dspace/handle/2445/142791))
  → Bizim için tersinden: üretim şokundan fiyat etkisini kalibre etmek.

## 5. Arkeoloji ve tarih

Bkz. [03 §10](03-academic-abm.md): MERCURY, Hansa, Ermeni tüccarlar. Bu alanda modeller genelde **NetLogo** ile yazılıyor ve **CoMSES Net** ([comses.net](https://comses.net)) üzerinden açık kod olarak paylaşılıyor. Bu, incelenebilecek hazır modeller havuzu demek.

## 6. Araçlar ve çerçeveler

| Araç | Dil | Ne işe yarar | Bizim için |
|---|---|---|---|
| **Mesa** | Python | Genel amaçlı ajan modelleme çerçevesi; ızgaralar, zamanlayıcılar, tarayıcıda görselleştirme. NetLogo'nun Python karşılığı olmayı hedefliyor. ([Mesa docs](https://mesa.readthedocs.io), [SciPy](https://proceedings.scipy.org/articles/Majora-7b98e3ed-009)) | Hızlı **araştırma prototipleri** için. Pazar modeli içermiyor, kendimiz yazarız. Sugarscape örneği var. |
| **NetLogo** | Kendi dili | Klasik ajan modelleme ortamı; tarihsel ve arkeolojik modellerin çoğu | Mevcut modelleri (MERCURY) okumak için |
| **ABIDES** | Python | Finansal piyasa mikroyapısı, ayrık olay | Mimarisi ilham verici; doğrudan kullanmak için fazla finansa özgü |
| **BazaarBot** | Haxe / Java / C# portları | Doran-Parberry uygulaması | Doğrudan inceleme ve karşılaştırma için ([Java portu](https://github.com/jeremywildsmith/bazaarbot-java)) |
| **Machinations** | Web | Kaynak akış diyagramları ve simülasyonu ([Dormans](https://en.wikipedia.org/wiki/Joris_Dormans)) | Erken tasarım aşamasında kaynak ve yutak denge analizi |

**Teknoloji önerisi (sadece araştırma aşaması için, kod kararı değil):**
- Simülasyon prototipini **Python** ile yazmak (Mesa'ya bağımlı olmadan veya hafifçe kullanarak), analiz için pandas ve matplotlib. Hızlı deneme ve yanılma, kolay grafik.
- Asıl oyun motoru kararı **ayrı bir tartışma**: simülasyon oturduktan sonra performans ve hedef platforma göre verilir. Python prototipi, nihai motor için bir "özellik belgesi" görevi görür.
- Bu bir öneri; karar kullanıcının (yeni açık soru S-010).

## 7. Oyun dışı uygulamalardan çıkan dersler

1. **Ajan modelleri tahmin için değil, "ne olurdu?" soruları için güçlüdür** (Farmer & Foley, BoE, tarihçiler). Bizim oyun da tam olarak "ne olurdu" oyunu.
2. **Ayrık olay + gecikme modellemesi** (ABIDES) bizim haber ve seyir sistemimizin mühendislik temeli.
3. **Tipolojik ajanlar** (BoE) aynı mala farklı nedenlerle gelen talebi modellemenin yolu.
4. **Kredi döngüleri** (EURACE) geç oyun finans sisteminin dinamiği.
5. **Teorik denge karşılaştırması** (Takayama-Judge) bir doğrulama aracı.
6. **Açık kod havuzları** (CoMSES) var; tekerleği yeniden icat etmeden önce bakılmalı.
