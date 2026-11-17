# 01 — Simülasyon Motoru: Python'un Sınırı ve Alternatifler
> Durum: taslak (tartışma için; migration kararı yok)
> Son güncelleme: 2026-10-26
> İlgili: [D5b3e](../../experiments/D5b3e.md), [simulation-spec](../../design/simulation-spec.md)

**Soru (kullanıcı, 2026-10-26):**
- Bu motor Python'da koşamaz. Harita büyüyor; ileride tick saat seviyesine inecek.
- Alternatifleri ve büyük metin tabanlı simülasyon oyunlarının nasıl çalıştığını anlat.
- Kullanıcı söylemeden migration yapılmayacak.

## 1. Bugünkü ölçümler (2026-10-26, bu makine)

| Ölçüm | Değer |
|---|---|
| Makine | Intel Core Ultra 7 155H (dizüstü): 6 P-core + 8 E-core + 2 LP-core, 22 thread; CPU governor `powersave` |
| Tek koşu, 3 liman × 3 mal, ~70 gemi, günlük tick | 1 yıl ≈ 1,1-1,6 sn (spinup hariç); 10 yıl + spinup ≈ 64 sn |
| Profil (cProfile, 1 yıl) | Tek bir sıcak nokta yok. Zaman yüzlerce küçük Python fonksiyonuna dağılmış: `_kapan` %31 (kümülatif), `_options` %22, `_expect` %16, `sum/max/min` çağrıları, `np.median` (küçük listelerde pahalı) |
| Paralel ölçek (2 yıllık koşu) | 1 süreç 3,7 sn; 4 süreç 9,6 sn; 20 süreç 38 sn duvar saati. **20 paralel koşu, tek koşunun ancak ~2 katı iş çıkarıyor.** `OMP_NUM_THREADS=1` fark etmedi. Neden: dizüstü güç/ısı sınırı ve E-core'lar (çıkarım, ölçülmedi) |

**Anlamı:**
- (a) Bu makinede daha fazla süreçle hız kazanamayız; kazanç çekirdek başına verimden gelmeli.
- (b) Zamanın dağınık olması, "bir fonksiyonu Numba ile hızlandır" türü çözümlerin 10× vermeyeceğini gösteriyor. Sorun yorumlayıcı yükü (interpreter overhead) ve nesne tabanlı veri düzeni.

### Kaba ölçek tahmini (⚠️ çıkarım, ölçülmedi)
- Bir tüccarın karar maliyeti ~ liman × mal.
- Tam harita varsayımı: ~15 liman × ~10 mal, ~500 gemi. 3 × 3 ve 70 gemiye göre yaklaşık 16 × 7 ≈ 100× iş.
- Saatlik tick: günlüğe göre 24×.
- Toplam: ~2.400× → Python'da **simülasyon yılı başına ~1 saat**. Deney (10 seed × 10 yıl × birkaç kurulum) imkânsız; oyun da oynanamaz.

## 2. Büyük simülasyon oyunları nasıl çalışıyor?

| Oyun / sistem | Nasıl | Kaynak |
|---|---|---|
| **Victoria 3** (Paradox, Clausewitz/Jomini motoru, C++) | Tick 6 saat. İş "tick task"lara bölünmüş; her birinin sıklığı (yıllık, aylık, haftalık, günlük, tick) ve bağımlılıkları var. En pahalı işler: istihdam güncellemesi, pop ihtiyaç önbelleği, modifier güncellemesi. Performans "ortalama tick süresi" ile ölçülüyor | Paradox, *Victoria 3 Dev Diary #76: Performance* |
| **Dwarf Fortress** (C++) | Büyük ölçüde tek thread. Darboğaz çoğunlukla önbellek ıskaları (cache miss) ve dünya geçmişindeki varlık sayısı. Oyuncular küçük dünya ve az uygarlıkla hızlanıyor | DF wiki, *System requirements*; Steam tartışmaları (anekdot) |
| **Agent-based model çatıları** | Julia (Agents.jl) ile C++ tek thread'de yakın (C++ biraz önde). Python çatıları ağır işi derlenmiş koda (Polars/Rust, JAX) devrederse yaklaşıyor. **Algoritma değişikliği dil değişikliğinden fazla kazandırabiliyor** (bir tezde 5×) | FHNW tezi (Julia vs C++ işgücü piyasası ABM); AMBER (arXiv 2601.16292); JuliaDynamics ABMFrameworksComparison (Agents.jl geliştiricilerinden, temkinli okunmalı) |
| **EVE Online** | Oyun mantığı Stackless Python, ağır kısımlar C++ | ⚠️ genel bilgi, bu oturumda doğrulanmadı |

**Ortak dersler:**
1. **Her şey her tick'te hesaplanmaz.** Çok sıklıklı (multi-rate) tick: fiyat oluşumu sık, nüfus ve üretim seyrek. Bizim için: saatlik tick'te bile denizdeki geminin hesaplanacak bir şeyi yok.
2. **Event-driven (olay güdümlü) simülasyon:** Tüccar yalnızca bir olay olduğunda karar verir: limana varış, yeni haber, satışın bitmesi. Saatlik tick'te bile iş, olay sayısıyla orantılı kalır, tick sayısıyla değil.
3. **Veri düzeni:** Ajanlar nesne listesinde değil, dizilerde (struct of arrays, ECS) tutulur. Önbellek dostu. DF'nin darboğazı tam da bu.
4. **Ağır çekirdek derlenmiş dilde,** çevresi (betik, mod, analiz) yüksek seviyeli dilde.

## 3. Seçenekler

| Seçenek | Hız kazancı (⚠️ tahmin) | Maliyet | Artı | Eksi |
|---|---|---|---|---|
| **A1. Python'da algoritma** (olay güdümlü karar, önbellek, `np.median` yerine düz hesap) | 3-10× | Düşük | Hemen; dil değişmez | Saatlik tick ve tam harita için yetmez |
| **A2. PyPy** (Python JIT) | Saf Python döngülerinde 3-10× | Çok düşük (kod değişmez) | Deneme bedava | NumPy PyPy'de yavaş; bizde NumPy küçük işlerde çok kullanılıyor. Kurulu değil |
| **A3. Numba / Cython** | Sıcak döngülerde 10-100× | Orta | Kademeli | Nesne (dataclass) ağırlıklı kodla zayıf; zaman dağınık olduğu için kazanç sınırlı |
| **B. Hibrit: çekirdek derlenmiş dilde, deneyler Python'da** (Rust + PyO3 ya da C++ + pybind11) | Çekirdekte 30-100× | Yüksek (çekirdeği yeniden yazmak) | Deney betikleri, analiz ve dokümantasyon akışı korunur | İki dil; sınırda veri aktarımı |
| **C1. Rust** | 30-100× | Yüksek | Hız, bellek güvenliği, determinizm kolay, çok çekirdek güvenli (rayon); Bevy ECS; PyO3 ile Python bağı | Öğrenme eğrisi dik; prototipleme yavaşlar |
| **C2. C++** | 30-100× | Yüksek | Sektör standardı (Paradox, DF); en geniş kütüphane | Hata riski (bellek); derleme altyapısı |
| **C3. Julia** | 20-80× | Orta-yüksek | Bilimsel hesapta Python'a en yakın sözdizimi; Agents.jl; hızlı prototip | Oyun olarak dağıtım zayıf; ilk çalıştırma (JIT) gecikmesi; oyun ekosistemi yok |
| **C4. C#** (.NET) | 15-50× | Orta-yüksek | Godot/Unity ile doğal; kolay dil; iyi araçlar | Simülasyon kütüphanesi az; GC duraklamaları (yönetilebilir) |
| **C5. Go** | 15-50× | Orta | Basit; eşzamanlılık kolay | Sayısal ekosistem zayıf; jenerik ve oyun ekosistemi sınırlı |

Hız kazancı sütunu genel deneyime dayanıyor (yorumlanan Python döngüsü ile derlenmiş döngü farkı), bizim kodda ölçülmedi.

## 4. Öneri (karar kullanıcıyla verilecek)

1. **Hangi dil olursa olsun mimari değişmeli:**
   - olay güdümlü tüccar kararları
   - çok sıklıklı tick
   - dizi tabanlı veri düzeni

   Saatlik tick, dil değişikliğinden bile çok mimariye bağlı. Bu, Python'da da şimdi denenebilir (A1) ve yeni motorun tasarımına doğrudan geçer.
2. **Uzun vade için eğilimim: B (hibrit), çekirdek Rust.**
   - Deney betikleri ve analiz Python'da kalır (PyO3 ile `import medi_core`).
   - Rust determinizmi (aynı seed → aynı sonuç) ve ledger değişmezlerini (para ve mal korunumu) güvenle taşır; çok çekirdeği güvenle kullanır.
   - Oyun bir gün Godot veya Unity arayüzü alacaksa C# ciddi rakip. Hız öncelikse ve dağıtım önemsizse Julia.
3. **Migration stratejisi (zamanı gelince):**
   - Python motoru "spec / oracle" olarak kalır.
   - Yeni çekirdek modül modül yazılır. Her modül için aynı girdilerle Python sonucuyla karşılaştırma testi yapılır; RNG farkı yüzünden istatistiksel eşdeğerlik aranır.
   - Mevcut deney sonuçları (D-serisi) yeni motorda yeniden üretilmeden migration bitmiş sayılmaz.
4. **Donanım:**
   - Dizüstü makine paralel deneyde ~2× ile sınırlı. CPU governor `performance` modunda bir deneme yapılabilir; bu kullanıcının kararı, sistem ayarı.
   - Uzun deney turları için bulut makinesi (ör. 32-64 çekirdekli) ayrı bir seçenek.

## Oyun için çıkarımlar
- Saatlik tick hedefi, motorun **olay güdümlü** olmasını zorunlu kılıyor. Bu bir tasarım kararı, yalnızca performans değil. Tüccarın "ne zaman düşündüğü" oyunun ritmini de belirler.
- Paradox'un multi-rate tick'i bizim katmanlara doğal uyuyor:
  - saatlik: gemi hareketi, kapan
  - günlük: kent talebi
  - aylık: giriş-çıkış, finans
  - yıllık: hasat
- **Kullanıcı kararına kadar Python'da devam** (2026-10-26). Bu sırada eklenen her mekanizma, olay güdümlü bir tasarıma taşınabilir biçimde yazılmalı. Gizli global durumdan ve "her gün herkes her şeyi yeniden hesaplar" varsayımından kaçınılmalı.

**Kaynaklar:**
- https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-76-performance
- https://dwarffortresswiki.org/index.php/DF2014:System_requirements
- https://steamcommunity.com/app/975370/discussions/0/3935643263189389366
- https://studierendenprojekte.wirtschaft.fhnw.ch/en/view/4899
- https://arxiv.org/pdf/2601.16292
- https://github.com/JuliaDynamics/ABMFrameworksComparison
- https://www.jasss.org/27/2/4.html
