# Rust Çekirdek: Mimari ve Taşıma Yöntemi
> Durum: gözden geçirildi (taşıma tamam; deneyler Rust'la koşuyor)
> Son güncelleme: 2026-11-09
> İlgili: [tech/02-performance-plan](../research/tech/02-performance-plan.md), [determinism](determinism.md), S-019

**Kullanıcı kararı (2026-11-09):**
- Çekirdek Rust.
- Aşama A (Python'da algoritma) atlanıyor: önce var olan model daha hızlı bir dilde çalışsın.
- Model geliştirme bundan sonra da sürecek. Kod, sık değişikliği kolay kaldıracak biçimde yazılmalı.
- Nihai hedef:
  - 1 tick = 1 ya da 2-3 saat; gece işlem yok.
  - ~100 yıl süren bir dünya.
  - Simülasyon maliyeti oynanış süresine yayılır (amortize edilir).
  - Model geliştirilirken günlük tick devam ediyor.

## 1. Kapsam
- **Taşınan:** bugünkü taban kurulumun (`*-B-R1-O3`, VRS ve F) koştuğu kod yolunun tamamı:
  - `D5World._step_wholesale` ve çağırdığı her şey
  - `D1Sim` pazar motoru (`external_wholesale`)
  - dükkân, stokçu, köylü, üretici havuzu
  - kapan ve rekabetçi perakende
  - debt ve alacaklı fiyatlaması (`loan_pricing="voyage"`)
  - giriş-çıkış (K-029, U, Bühlmann)
  - R1 risk modeli
  - Ö3 gemi piyasası
  - snapshot üretimi
  - D5b3f teşhis kayıtları
- **Taşınmayan:** kapalı ablation dalları; Python motorunda (oracle) kalırlar. Örnekler: `houses`, `network`, `colleganza`, `reputation`, `wholesale=False` günlük adımı, `retail_rule="pull"`.
  - Rust yapılandırması bu değerleri görünce açık bir hatayla durur; sessizce yanlış koşmaz.
  - Gerekirse sonra taşınır.

## 2. Doğrulama: bit düzeyinde eşdeğerlik
Yeni motor, Python motoruyla **aynı başlangıç durumundan aynı sayıları** üretmeli. İstatistiksel benzerlik yeterli sayılmaz.
- **Durum dökümü:** Python'da dünya durumunun tamamı (RNG akışlarının iç durumu dahil) kanonik JSON'a dökülür. Rust aynı biçimi okur ve yazar.
- **Gün izi:** iki motor her günün sonunda durum özetini (hash) yazar. İlk ayrışan gün bulunur, o günün tam dökümleri alan alan karşılaştırılır.
- **Sayısal kurallar:** Python ve NumPy'ın kesin davranışı, `pymath` modülünde tek tek kopyalanır ve testle doğrulanır:
  - `sum()` (3.12+: Neumaier telafili toplam)
  - `round()` (çifte yuvarlama, banker's rounding)
  - `%` ve `//` (bölenin işareti)
  - `max`/`min` (eşitlikte ilk eleman; `0.0` / `-0.0`)
  - `np.mean` / `np.std` (pairwise toplama)
  - `np.median`
  - `exp`/`log`/`pow`/`erf`: Rust kendi matematiğini kullanmaz; Python gibi glibc `libm` çağrılır
- **RNG:** NumPy `PCG64` + `SeedSequence` + dağılım algoritmaları birebir yeniden yazılır:
  - `random`, `normal` (ziggurat), `uniform`, `integers` (Lemire), `poisson` (PTRS), `beta` (Marsaglia-Tsang gamma), `permutation`/`shuffle`
  - Her biri NumPy çıktısıyla binlerce çekilişte karşılaştırılır.
- **Sözlük sırası:** Python sözlükleri ekleme sırasını korur. Rust'ta `IndexMap`, silmede `shift_remove`.

## 3. Mimari
```
core/                    Rust workspace
  medi-core/src/         saf Rust kütüphane (Python'a bağımlı değil; oyun motoru da bunu kullanır)
    config.rs            D5Config karşılığı; validate() taşınmayan dalları reddeder
    consts.rs            liman, mal, bölge (enum), rota tabloları
    pymath.rs            Python/NumPy-uyumlu sayısal yardımcılar (glibc libm, black_box)
    rng/                 NumPy-uyumlu PCG64 + dağılımlar
    date.rs, ledger.rs, digest.rs, prof.rs
    market.rs            D1Sim: köylü, stokçu, dükkân, hasat
    world/mod.rs         Core + World, günlük adım (_step_wholesale sırası)
    world/info.rs        gözlem, söylenti, varış, donatılan gemi
    world/trade.rs       beklenti, rakipler, seçenekler, kalkış, satış
    world/kapan.rs       kapan, perakende fiyat ve pay, kent talebi, üretici havuzları
    world/finance.rs     borç, alacaklı, ödeme
    world/entry.rs       giriş-çıkış, sicil, Bühlmann, aylık işler
    world/ships.rs       R1 risk, korsan baskısı, Ö3 gemi piyasası
    world/types.rs       durum parçaları (tüccar, yük, havuz...), PortMap, IdSet, IdMap
    world/init.rs        soğuk başlangıç (D5World.__init__, D1Sim.__init__)
    world/snapshot.rs    snapshot üretimi, sıcak başlangıç (_load_warm, _rebase)
    world/diag.rs        D5b3f teşhis kayıtları ve deney çıktısı
    bin/medi.rs          deney koşucusu (snapshot, run)
    bin/trace.rs         gün izi (eşdeğerlik); bin/bench.rs hız ölçümü
  tools/state_io.py      Python durum dökümü + gün izi + yapılandırma
  tools/run_rs.py        deneyi Rust'la koşturan düzenleyici; Python ile karşılaştırma
  fixtures/              NumPy'dan üretilmiş sayısal test fikstürleri
```
- **Değişiklik kolaylığı için kurallar:**
  - Python'daki fonksiyon adları ve sırası korunur, böylece iki motor yan yana okunabilir.
  - Her mekanizma kendi dosyasında. Yapılandırma seçenekleri `enum`; dize karşılaştırması yok.
  - Tüccarlar bir arena'da (`Vec<M5>`), kimlikle anılır; listeler kimlik tutar.
  - Liman ve mal küçük tamsayı kimlikleri; adlar yalnızca girdi/çıktıda.
- **Python oracle:** `sim/world5.py` dondurulmaz, ama taşıma bitene kadar değiştirilmez. Taşıma bitince yeni mekanizmalar önce Rust'ta yazılır.

## 4. Durum (2026-11-09)
- [x] iskelet + pymath + RNG (NumPy karşılaştırma testleri: `cargo test`, fikstür `core/fixtures/`)
- [x] Python durum dökümü ve gün izi (`core/tools/state_io.py`; Rust: `src/bin/trace.rs`)
- [x] pazar motoru, dünya, tüccar, kapan, perakende, kent (`market.rs`, `world/{info,trade,kapan}.rs`)
- [x] finans, giriş-çıkış, Ö3, R1 (`world/{finance,entry,ships}.rs`)
- [x] snapshot'tan eşdeğerlik: **bit düzeyinde aynı**
  - VRS-B-R1-O3 seed 0: 400 gün
  - VRS-B-R1-O3 seed 1: 1100 gün (3 yıl)
  - F-B-R1-O3 seed 0: 150 gün
  - Her gün, durumun her alanı (RNG iç durumu dahil) aynı.
  - 10 yıllık koşu hata ve ledger ihlali olmadan bitiyor (VRS, F).
- [x] soğuk başlangıç (`world/init.rs`): 0. gün bütün alanlarıyla aynı; VRS 400 gün, F 200 gün bit düzeyinde aynı
- [x] snapshot üretimi ve sıcak başlangıç (`world/snapshot.rs`): Rust'ın ürettiği snapshot Python'un pickle'ıyla alan alan aynı (VRS, F; seçilen ay ve meta da aynı)
- [x] D5b3f teşhis kayıtları (`world/diag.rs`: elog, xlog, born; slog bu kurulumlarda boş) ve deney koşucusu (`medi` CLI + `core/tools/run_rs.py`)
- [x] **Uçtan uca eşdeğerlik:** D5b3j deneyinin tamamı (VRS/F × O3/O3-noU × 10 seed × 10 yıl = 40 koşu) Rust'ta yeniden üretildi; çıktı dosyaları Python'unkilerle birebir aynı
  - Tek istisna: `ship_log`'daki fiyat sütunu. D5b3j koşularından sonra Python'da yapılan, yalnızca kaydı etkileyen düzeltmeden (işlem olmayan ayda fiyat sökümle tabanlı) geliyor. Rust güncel Python'u izliyor.
  - Ayrıca güncel Python ile doğrudan karşılaştırıldı (`run_rs.py compare`): VRS seed 0 (2 yıl), seed 1 (6 yıl), noU seed 8 (10 yıl), F seed 0 (2 yıl).
- PyO3 bağı gerekmedi: Python yalnızca yapılandırmayı kurup işleri dağıtıyor, koşu `medi` ikilisinde. `core/medi-py/` iskeleti GitHub hazırlığında (2026-11-17) ölü kod olarak kaldırıldı.

### Hız (tek çekirdek, aynı makine, seed 0, snapshot'tan)
| Kurulum | Python | Rust | Kat |
|---|---|---|---|
| VRS (3 liman, ~75 tüccar) | 3,7 sn/yıl | 0,12-0,14 sn/yıl | ~30× |
| F (tam harita, ~120-170 tüccar) | 35,8 sn/yıl | 0,58-0,79 sn/yıl | ~45-60× |

10 yıllık F koşusu: Python ~6 dk, Rust ~6-9 sn (teşhis kayıtlarıyla). Snapshot üretimi (10 yıl soğuk ön koşu): VRS ~1 sn, F ~12 sn (Python'da dakikalar).

**Paralel koşu (bu makine):** Intel Core Ultra 7 155H dizüstü işlemcisi; 6 performans + 10 verimlilik çekirdeği, güç sınırlı. Aynı VRS koşusu tek başına 1,3 sn sürüyor. Toplam verim: 2 paralelde saniyede 1,1 koşu, 4 paralelde 1,5, 8 paralelde 1,2. Yani 4'ten fazla süreç verimi artırmıyor; `run_rs.py` varsayılanı `NPROC=4`. Python'da görülen paralel yavaşlamanın (D5b3e.2b) açıklaması da bu.

Faz profili (`MEDI_PROF=1 bench DURUM.json GÜN`, perf bu makinede yetkisiz):
- Hızlandırmalar sonuçları değiştirmez; her biri gün iziyle yeniden doğrulandı:
  - (1) `heard` kümeleri bit kümesi, tamsayı anahtarlı sözlüklerde FxHash
  - (2) `p_loss(actual=False)` liman çifti × mevsim tablosu
  - (3) tek tüccar kararı süresince önbellek (`Ctx`): medyan, risk tutumu, pazar başına bilinen yüklemeler
  - (4) `0.03 ** 2` gibi sabit `pow` çağrıları bir kez
- Kalan maliyet F'de: `reposition` (5 liman × `options`), `plan_merchant`, kapan, söylenti.

### Eşdeğerlik sırasında bulunanlar
- **LLVM libm çağrılarını sabit üslü ifadelere çeviriyor.** `pow(x, -1.0)` → `1.0 / x` dönüşümü yapılıyor. glibc `pow` her zaman doğru yuvarlanmadığı için sonuç 1 ulp farklı çıktı: `363.59… ** -1.0 ≠ 1 / 363.59…`.
  - Etkisi: VEN zeytinyağı talebi 107. günde 1 ulp saptı. Fark yalnızca dükkân `op_profit` alanında göründü, çünkü nakit tamsayıya yuvarlanıyor ve stok farkı yutuyor.
  - Düzeltme: `pymath` argümanları `black_box` ile derleyiciden gizliyor.
  - Yan etkisi: sabit `pow` çağrıları pahalılaştı. Bu yüzden sabit `pow` değerleri önceden hesaplanıyor.
- **Dükkân kimliği benzersiz değil.** Yeni dükkânın kimliği `sk{shop_entries}e`. `_rebase` sayacı sıfırladığı için snapshot sonrası aynı pazarda iki `sk99e` olabiliyor. Python dükkânı nesne kimliğiyle siliyor (`list.remove`). Rust kimlik dizgisiyle eşleştirdiği için yanlış dükkânı sildi: VRS-noU seed 8, 9. yılda ayrıştı. Düzeltme: fonksiyon boyunca geçici etiket (`Shop::tag`, dökümde yok).
  - Python davranışı modelde bir kusur sayılmaz (kimlik yalnızca etiket), ama kayıtlarda iki dükkân aynı adla görünebilir ⚠️.
- **`_retail_entry_exit` RNG akışını koşulsuz oluşturuyor** (soğuk başlangıcın 1. gününde görüldü). Rust da öyle yapıyor; akışın varlığı durumun parçası.
- **`serde(flatten)` tamsayı anahtarlı sözlükleri okuyamıyor.** JSON'da anahtarlar dizgi olarak geliyor. Bu yüzden `World` (Core + tüccarlar) elle birleştiriliyor.

### Deney koşmak
```
cd core && cargo build --release
YEARS=10 DIAG_OUT=d5b3k NPROC=4 python3 core/tools/run_rs.py 10 VRS-B-R1-O3,F-B-R1-O3
python3 core/tools/run_rs.py compare VRS-B-R1-O3 0 2        # Python run() ile birebir karşılaştırma
```
- Kurulumlar `experiments/d5b3f_entry_diag.py`'deki `SETUPS`'tan gelir; çıktı aynı klasöre aynı adla yazılır (analiz betikleri değişmez).
- Rust snapshot'ları `experiments/out/snapshots/<anahtar>_<k>.rs.json`; anahtar Python'un `snapshot_path` hash'i (yapılandırma değişince yeni snapshot üretilir).
- Rust'ın taşımadığı bir dal (`validate`) açık hatayla durur; o kurulumlar Python betiğiyle koşar.

### Değişiklik yaparken
**Harita (M0, 2026-11-10):** Limanlar, bölgeler, bacaklar, arz planı ve kumaş havuzları `core/maps/<ad>.json`'da (`map.rs`). Yapılandırmada `map` alanı (boş = `classic6`, Python oracle'ının haritası). Bir süreçte tek harita kurulur. Yeni harita `core/tools/mapgen.py` ile üretilir. Teşhis aracı: `dbg_opts CFG SNAP LİMAN` (bir limandaki tüccarların seçenek bileşenleri).

**K-033 (2026-11-09):** Yeni mekanizmalar yalnızca Rust'a eklenir; Python motoru bugünkü modelin oracle'ı olarak donar. Her yeni mekanizma bir yapılandırma bayrağıyla gelir. Bayrak kapalıyken (varsayılan) `run_rs.py compare` EŞİT vermeli; bu, her değişiklikten sonra çalıştırılan regresyon sınamasıdır. Bayrak açıkken ayrışma beklenir. Python yapılandırmasında olmayan yeni alanlar Rust'ta `#[serde(default)]` ile gelir (Python'un `cfg_json` çıktısı onları içermez).

**K-038 (2026-11-10):** Python koşusu bırakıldı. Regresyon: bayraklar kapalıyken Rust'ın önceki çıktısıyla birebir aynı sonuç (ör. M1.4'te M2 s0).

Aşağıdaki iki-motor yöntemi, eski modelde bir port hatası aranırken kullanılır:
- **Python ve Rust motoru yan yana değiştirilecekse:** önce Python'da değişiklik yapılır. Sonra Rust'ta aynısı yapılır. Ardından `trace` ile eşdeğerlik yeniden sınanır:

  ```
  python3 core/tools/state_io.py trace KURULUM SEED GÜN py.jsonl 0
  core/target/release/trace py.jsonl.day0.json GÜN rs.jsonl
  python3 core/tools/state_io.py cfg KURULUM@cold SEED cfg.json   # soğuk başlangıç: trace cold:cfg.json ...
  ```
  `TRACE_FROM=N` ortam değişkeni N. günden önce özet yazmaz (geç ayrışmalarda Python'u hızlandırır). Uçtan uca: `run_rs.py compare`.

  İlk farklı gün ve alan, gün özetlerinin karşılaştırmasından bulunur. Aynı günün tam dökümü (`GÜNLER` argümanı) alan alan karşılaştırılır.
- **Python'a yeni durum alanı eklenirse:** `state_io.py` dökümü durur ("Rust'ta karşılığı olmayan öznitelik"). Alan iki tarafa da eklenmeden döküm çalışmaz. Sessiz kayma bu yüzden olmaz.
