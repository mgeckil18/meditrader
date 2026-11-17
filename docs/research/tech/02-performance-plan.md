# 02 — Motoru Hızlandırma: Ölçüm, Teşhis, Teknoloji Seçimi
> Durum: taslak (tartışma için; **migration kararı yok**, kullanıcı söylemeden yapılmaz)
> Son güncelleme: 2026-11-09
> İlgili: [01-simulation-engine-options](01-simulation-engine-options.md), [determinism](../../design/determinism.md), S-019, S-022

**Soru (kullanıcı, 2026-11-09):** İlk iş kodu hızlandırmak. 01'deki araştırmayı genişlet: hem teknoloji seçimi hem optimizasyon. Bu tür simülasyon oyunları genelde C ailesinden dillerle yazılıyor.

## 1. Bugünkü ölçüm (2026-11-09, bu makine, `F-B-R1-O3` ve `VRS-B-R1-O3`, seed 0, tek süreç)

| Dünya | Tüccar | Pazar (liman × mal) | 1 yıl | 3 yıl |
|---|---|---|---|---|
| VRS | 62-83 | 9 | 3,7 sn | 16,4 sn |
| F (tam harita) | 157-177 | 45 | 35,8 sn | 113,5 sn |

- Deney turu: F'de 10 seed × 10 yıl, 10 paralel süreçle koşu başına 500-600 sn. Bir kurulum ~10 dakika, üç kurulumluk bir tur ~30 dakika.
- Yıl başına süre zamanla artıyor: VRS'de 1 yılda 3,7 sn, 3 yılda yılda ~5,5 sn. Filo büyüyor ve tüccarların bildiği yük kayıtları birikiyor.

### Profil (cProfile, F, 2 yıl)
cProfile küçük fonksiyonları şişirir: gerçek süre ~74 sn, profilde 173 sn. Oranlar yine de yol gösterir.

| Fonksiyon | Kümülatif pay | Ne yapıyor |
|---|---|---|
| `_options` | **%67** | Bir tüccar için (köken liman, mal, hedef) seçeneklerini değerlendirir |
| ↳ `_rivals` | **%40** | Her (hedef, mal) için tüccarın duyduğu **bütün** yük kayıtlarını baştan tarar. 250 milyon `len()` çağrısı bu taramadan |
| ↳ `_expect` → `np.median` | %18 | Her seçenekte son 20 fiyatın medyanı. NumPy küçük dizide pahalı (754 bin çağrı) |
| ↳ `_p_loss` → `_leg_hazards` | %9 | Rota tehlikesi her seçenekte yeniden hesaplanıyor; oysa mevsim içinde sabit |
| `_reposition` + `_best_from` | %48 (`_options`'ın içinde) | Boştaki tüccar ve kamu sicili **her köken limanı** için `_options` çağırıyor |
| `_hear`, `_kapan`, `_shop_schedule` | %5-10 | Söylenti, pazar takası, dükkân |

## 2. Teşhis: sorun önce algoritmada

01'deki VRS profilinde zaman dağınıktı. Tam haritada tablo farklı: **tek bir yapı baskın.**

- Bir tüccarın bir kararı ≈ köken × mal × hedef × (duyduğu yük sayısı).
- Yeniden konumlanma ve kamu sicili, kökeni de bütün limanlar üzerinde dolaşıyor. Karar başına iş **liman² × mal × yük**.
- Kaba büyüme tahmini (⚠️ hesap, ölçülmedi):
  - 45 → 100 pazar, tüccar 165 → 1.000 olsun.
  - Liman² ile ~5×, tüccar sayısı ile ~6×, duyulan yük sayısı da tüccarla artıyor.
  - Toplamda ≥ 30-100×. Python'da **simülasyon yılı başına 20-60 dakika** eder.
- Derlenmiş dil bu çarpanı değiştirmez, yalnızca sabiti küçültür (~30-100×).
- **Algoritma düzeltmesi ile derlenmiş dil birbirinin yerine geçmez; ikisi çarpılarak hızlandırır.** 01'de anılan "algoritma değişikliği dil değişikliğinden fazla kazandırabilir" bulgusu (FHNW tezi) burada da geçerli görünüyor.

### Python'da yapılabilecek algoritma düzeltmeleri (davranışı değiştirmeden)

| # | Düzeltme | Beklenen etki (⚠️ profilden tahmin) |
|---|---|---|
| A1 | `_rivals`: yük kayıtları her `_options` çağrısında bir kez (hedef, mal) anahtarına toplanır, sonra okunur | %40'lık payın çoğu gider |
| A2 | Medyan: son 20 fiyat için NumPy yerine düz Python (`sorted`), ya da fiyat geçmişi değişince önbelleğe alınır | %18 → ~%2 |
| A3 | Rota tehlikesi (`actual=False`): (köken, hedef, mevsim) için bir kez hesaplanıp saklanır | %9 → ~0 |
| A4 | Günlük ortak rota tablosu: süre, tehlike ve navlun bütün tüccarlar için aynı; tüccara özel olan yalnızca beklenti | `_options`'ın sabit kısmı |
| A5 | Kamu sicili ve yeniden konumlanma: yalnızca liman konuşmasının değiştiği günlerde ya da tüccarın bildiği limanlarda | Liman² çarpanını hafifletir |

- A1-A3 davranışı birebir korur. Doğrulama: aynı seed'de aynı sonuç (bugünkü regresyon testi).
- Toplam beklenti tam haritada **3-5×** (⚠️ tahmin). Yalnızca ölçülünce kesinleşir.
- A4-A5 mimari değişiklik. Doğrudan yeni motorun tasarımına geçer.

## 3. Büyük simülasyon oyunları ne yapıyor (01'e ek)

| Oyun | Dil ve motor | Performans yaklaşımı | Kaynak |
|---|---|---|---|
| **Victoria 3** | C++ (Clausewitz/Jomini) | İş "tick task"lara bölünür; her birinin sıklığı (yıllık, aylık, haftalık, günlük, 6 saatlik) ve bağımlılıkları var. En pahalı işler haftalık. Sonraki sürümlerde akıllı önbellek ve çok thread'li hesap neredeyse oyunun tamamına yayıldı. Maliyeti nüfusun büyüklüğü değil, **pop (ajan grubu) sayısı** belirliyor | Dev Diary #76, #105, #142 |
| **Factorio** | C++, kendi motoru | Özel bir mimari değil; sıradan nesne güncellemeleri, aşırı optimize. Boştaki varlık güncelleme döngüsünden tamamen çıkar ve bir olay onu uyandırana kadar uyur. Bağımsız "adalar" ayrı thread'lerde; ekranda görünmeyenler daha seyrek tick'lenir | Geliştirici yanıtları (Reddit, forum; resmî değil) |
| **RimWorld** | C#; Unity'den kendi motoruna (Waylith) geçti, 2026 | Unity'de büyük ölçüde tek çekirdek. Kendi motorunda geliştiricinin testlerinde 2-4× hız. Mod topluluğu değişken tick hızıyla seyrek güncelleme yapıyor | Ludeon duyurusu (80.lv, PC Gamer) |
| **Dwarf Fortress** | C++ | Büyük ölçüde tek thread; darboğaz önbellek ıskaları ve varlık sayısı | 01 |
| **EU4** | C++ | En pahalı bileşen yapay zekâ ajanları; maliyet oyun ilerledikçe artıyor | [economy-simulation-techniques](../simulation/economy-simulation-techniques.md) |

**Ortak dersler:**
1. Dil C ailesi (C++, C#). Kazancın büyük kısmı yine de mimariden geliyor:
   - seyrek ya da olay güdümlü güncelleme
   - uyuyan varlıklar
   - önbellek
   - bağımsız parçaların paralel hesabı
2. Maliyeti **ajan sayısı ve karar sıklığı** belirliyor. Bizde karşılığı: tüccar sayısı × karar başına iş.
3. Profil sürekli ölçülüyor (Paradox'ta "ortalama tick süresi"). Biz de bir hız ölçüm betiği tutmalıyız.

**ABM çatıları (karşılaştırma):** JuliaDynamics karşılaştırmasında (Agents.jl geliştiricilerinin; temkinli okunmalı) Mesa (Python) Agents.jl'den 9-160× yavaş, MASON (Java) 1,4-5×. Python'da saf ajan döngüsü bir mertebe geride.

## 4. Seçenekler (bizim koda göre değerlendirme)

| Seçenek | Bizde beklenen kazanç ⚠️ | Maliyet | Değerlendirme |
|---|---|---|---|
| **P1. Python'da algoritma** (§2 A1-A5) | 3-5× | Günler | Hemen yapılabilir. Davranış korunur. Ölçek sorununun çarpanını hafifletir. Her durumda gerekli |
| **P2. Numba** | Sıcak döngüde 10-100×, bütünde az | Orta | Kodumuz dataclass, sözlük ve dize anahtarlı; Numba bunlarla zayıf. Önce veri düzenini değiştirmek gerekir, ki bu zaten yeniden yazmanın yarısı |
| **P3. Cython / mypyc** | 1,5-3× (yorumlayıcı yükü) | Düşük-orta | mypyc tip ipuçlarıyla derler, kodu az değiştirir. Sınırlı ama ucuz bir deneme |
| **P4. Python 3.14 free-threading** | Tek koşuda yok | Düşük | Tek thread'de daha yavaş; JIT ile birlikte çalışmıyor. Bize gereken paralellik zaten seed'ler arasında, süreçlerle var |
| **P5. PyPy** | Saf Python'da 3-10× | Çok düşük | NumPy ağırlığı yüzünden belirsiz. Bir öğleden sonralık deneme |
| **R. Rust çekirdek + Python deneyler (PyO3)** | 30-100× (P1 ile çarpılır) | Yüksek | Ayrıntı §5 |
| **C. C++ çekirdek + Python (pybind11)** | 30-100× | Yüksek | Sektör standardı. Bellek hatası riski yüksek, derleme altyapısı zahmetli |
| **S. C# (.NET)** | 15-50× | Orta-yüksek | Unity ya da Godot-C# arayüzü seçilirse doğal. Python'dan çağırmak zayıf; deney akışı ayrı süreçle kurulur |
| **J. Julia** | 20-80× | Orta | Bilimsel hesapta en hızlı prototip. Oyun olarak dağıtım ve arayüz ekosistemi zayıf |

**PyO3 notu:** Python ile Rust arasındaki her çağrının onlarca nanosaniyelik bir sınır maliyeti var. Python'dan her tüccar için ayrı ayrı Rust çağırmak kazancı yer. Doğru yapı: **simülasyonun tamamı Rust'ta koşar.** Python yalnızca kurar, çalıştırır ve sonuç dizilerini okur.

## 5. Öneri (karar kullanıcıyla)

### Aşama A: Python'da algoritma ve ölçüm (migration değil, şimdi yapılabilir)
1. **Hız ölçüm betiği:** sabit seed; VRS ve F için 1 ve 3 yıl; sonuç `experiment-log`'a.
2. A1-A3: davranış birebir korunur, regresyon testi aynı kalır.
3. A4-A5 tasarım olarak yazılır. Davranışı biraz değiştirebilirler; o zaman deneyle karşılaştırılır.

### Aşama B: taşınabilirlik hazırlığı (Python'da, migration'dan önce)
Amaç: yeni çekirdeğin Python motoruyla **bit düzeyinde aynı** sonucu verdiğini sınayabilmek. İstatistiksel eşdeğerlik testi çok daha zayıf bir testtir.
1. **RNG:** Bugün NumPy'ın PCG64 + SeedSequence + kendi normal dağılım algoritması (ziggurat) kullanılıyor.
   - PCG64'ün çıktı fonksiyonu Rust'taki `rand_pcg::Pcg64` ile aynı. Ama tohumlama (SeedSequence) ve dağılım dönüşümleri farklı.
   - İki yol:
     - (a) Python'da kendi küçük RNG katmanımızı yazmak: ham PCG64, kendi uniform ve normal dönüşümümüz. Sonra Rust'ta aynısını yazmak.
     - (b) NumPy'ın algoritmalarını Rust'ta birebir yeniden yazmak.
   - (a) daha basit ve denetlenebilir. Dezavantajı, bugünkü sonuçları bir kez kaydırması: bütün regresyon sayıları değişir, deneylerin seed ortalamaları değişmemeli.
2. **Durum ile mantığı ayırmak:** tüccar durumu düz alanlar; `getattr` ile isteğe bağlı alanlar kaldırılır.
3. **Gün sonu durum özeti (hash):** her gün tüccar nakdi, yükler, fiyatlar. İki motorun ilk ayrıştığı gün ve alan bulunur.

### Aşama C: çekirdeği derlenmiş dile taşımak (kullanıcı kararı)
**Eğilimim: Rust.**
- **Neden:**
  - Hız C++ ile aynı sınıfta. Rust ABM çatısı krABMaga için "C'ye yakın" deniyor (JASSS 2024).
  - Bellek hatası ve tanımsız davranış derleyicide yakalanıyor. Kodun büyük kısmını ben yazacağım; bu hataların sessizce sonucu bozmasını önlemek, C++'a göre en büyük artı.
  - `cargo` ile derleme kolay.
  - Determinizm için açık kurallar var: platforma bağlı `usize` yerine sabit genişlikli tipler, RNG'nin sabit sürümü.
  - Seed'ler ve ileride bağımsız bölgeler `rayon` ile güvenle paralel koşar.
  - PyO3/maturin ile `import medi_core`: deney betikleri, analiz ve dokümantasyon akışı aynen kalır.
- **C++ ne zaman daha iyi?** Unreal ya da Godot'nun C++ modülüyle derin bütünleşme istenirse, ya da ileride C++ bilen bir ekip gelirse.
- **C# ne zaman daha iyi?** Arayüz Unity ya da Godot-C# ile yapılacaksa ve deney akışının Python'dan çıkması kabul edilirse.
- **Arayüz kararı henüz yok.** Rust çekirdek bir kütüphane olarak yazılır. Godot'ya `gdext` ile, başka motora C ABI ile, ya da ayrı süreç olarak bağlanabilir. Arayüz kararı çekirdek dilini kilitlemez.
- **Önce küçük bir deneme (spike):** Tam geçişten önce tek bir çekirdek (ör. `_options` + `_rivals` + beklenti) Rust'a yazılır ve aynı girdilerle Python'la karşılaştırılır. Gerçek hız kazancı ölçülür. 1-2 günlük iş. Sonuç kötüyse karar değişir.
- **Geçiş yöntemi (01 §4.3):**
  - Python motoru "oracle" olarak kalır.
  - Modül modül taşınır. Her modül gün sonu hash'iyle Python'la karşılaştırılır.
  - D-serisinin ana sonuçları yeni motorda yeniden üretilmeden geçiş bitmiş sayılmaz.
- **Zamanlama riski:** Mekanizmalar hâlâ haftalık değişiyor (Ö3, limanda zaman, R2-R5, S-022). Erken taşırsak her mekanizma iki dilde yazılır.
  - Öneri: Aşama A hemen. Aşama B, limanda zaman ve S-022 ile birlikte. Aşama C, D5b3 serisi bir oturma noktasına gelince.
  - Ya da kullanıcı isterse şimdi: yeni mekanizmalar bundan sonra doğrudan Rust'ta, Python oracle donar.

### Donanım (kullanıcının sistem ayarı)
- CPU governor `powersave`. `performance` modu tek koşuyu hızlandırabilir ⚠️ (ölçülmedi).
- 6 P-core + 8 E-core: 10 paralel süreç, bazı koşuları E-core'a düşürüyor. Tek süreçte 37 sn/yıl, 10 paralelde koşu başına ~55 sn/yıl.
- Uzun deney turları için bulut makinesi (32-64 çekirdek) ayrı bir seçenek.

## Oyun için çıkarımlar
- **Oynanabilirlik ölçütü:** Oyunda hızlı ilerlemede bir yıl birkaç saniyede geçmeli ⚠️ (Paradox oyunlarında en yüksek hızda bir yıl kabaca bir dakikanın altında).
  - Bugün tam harita 37 sn/yıl. Harita ve filo büyüyünce Python'da dakikalar olur.
  - Algoritma + derlenmiş çekirdek ile hedef: yıl başına < 1 sn ⚠️.
- **Hız tasarımı da etkiler.** Tüccar her gün her limanı yeniden değerlendirmek yerine olay olduğunda karar verirse oyun hem daha hızlı hem daha tarihsel olur. 16. yy tüccarının bilgisi de, zamanı da sınırlı (S-018 ağ ve uzmanlaşma; liman konuşması).
- **Bit düzeyinde determinizm** yalnızca test için değil; oyunda kayıt ve tekrar oynatma (replay) ile hata ayıklamayı da mümkün kılar.

## Kaynaklar
- Paradox, *Victoria 3 Dev Diary #76: Performance*. https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-76-performance
- Paradox forum, Dev Diary #105 (Migration in 1.6), #142 (2024 in retrospect). https://forum.paradoxplaza.com/forum/threads/victoria-3-dev-diary-105-migration-in-1-6.1624226/ ; https://admin-forum.paradoxplaza.com/forum/developer-diary/victoria-3-dev-diary-142-2024-in-retrospect.1726056/page-3
- M. Ropert, *What makes a game tick? Part 5* (2025). https://mropert.github.io/2025/06/17/making_games_tick_part5
- Factorio geliştirici yanıtları (r/factorio, 2023; ayna): https://lr.in.psf.lt/r/factorio/comments/13bsf3s/technical_questions ; forum: https://forums.factorio.com/viewtopic.php?p=594439
- RimWorld 1.7 / Waylith motoru: https://80.lv/articles/rimworld-runs-2-4-times-better-on-new-in-house-engine/ ; https://www.pcgamer.com/gaming-industry/game-development/rimworld-drops-unity-for-its-own-in-house-engine-says-your-saves-still-work-so-do-most-mods-and-the-whole-thing-runs-twice-as-fast/
- Antelmi ve ark., *Reliable and Efficient Agent-Based Modeling and Simulation* (krABMaga), JASSS 27(2) 4, 2024. https://www.jasss.org/27/2/4.html
- Rust-AB (AsiaSim 2019). https://iris.unito.it/bitstream/2318/1949576/2/_ASIASIM2019__ABM_with_Rust.pdf
- EpiRust dağıtık ABM (2023). https://www.scitepress.org/publishedPapers/2023/117170/pdf/index.html
- Rust ve C++ fizik simülasyonu karşılaştırması (arXiv 2410.19146). https://www.arxiv.org/abs/2410.19146
- JuliaDynamics, ABMFrameworksComparison. https://github.com/JuliaDynamics/ABMFrameworksComparison
- Python 3.14 free-threading ve JIT: The Register (2025). https://theregister.com/software/2025/10/08/python-314-released-with-cautious-free-threaded-support/349336 ; M. Grinberg kıyası (ayna): https://fooqux.com/article/89
- mypyc + free-threading, EuroPython 2026. https://programme.europython.eu/europython-2026/talk/PWGSJQ/
- PyO3 çağrı maliyeti: https://pycoders.com/link/6235/web ; https://github.com/PyO3/pyo3/issues/3787
- NumPy PCG64. https://numpy.org/devdocs/reference/random/bit_generators/pcg64.html ; rand_pcg `Lcg128Xsl64`. https://docs.rs/rand_pcg/latest/rand_pcg/struct.Lcg128Xsl64.html
- Rust RNG taşınabilirliği. https://rust-random.github.io/book/crate-reprod.html
- Godot arayüz seçenekleri (gdext / C# / GDExtension; topluluk kaynakları, düşük güven). https://forum.godotengine.org/t/performance-implications-of-using-native-code-instead-of-gdscript/120365
