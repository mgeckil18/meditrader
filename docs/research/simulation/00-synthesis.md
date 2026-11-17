# 00 — Sentez: Ekonomi Simülasyonu için Önerilen Yaklaşım
> Durum: taslak öneri (tartışılacak, karar değil)
> Son güncelleme: 2026-10-22
> İlgili: [01](01-economic-fundamentals.md) · [02](02-market-mechanisms.md) · [03](03-academic-abm.md) · [04](04-games-deep-dive.md) · [05](05-non-game-applications.md) · [06](06-validation-and-tuning.md) · [ilk tur](economy-simulation-techniques.md) · K-004, K-006, K-009, K-010

Bu doküman, derin araştırmanın bizim oyuna dönüşmüş halidir. **Kesinleşmiş bir tasarım değil, tartışmaya açık bir öneridir.** Kararlar kullanıcıyla birlikte verilecek ve [decisions.md](../../decisions.md)'ye yazılacak.

---

## 1. Tek cümlede

**Fiziksel olarak taşınan mallar ve haberler, kitlesel arz ve talep havuzları, limanlarda stok tutan dealer tüccarlar ve bilgi yaşına göre inanç taşıyan heterojen ajanlar; hepsi deterministik, günlük tick ve olay kuyruğu üzerinde.**

## 2. Tasarımın dayandığı 8 ilke (araştırmadan)

| # | İlke | Dayanak |
|---|---|---|
| 1 | **Fırsatlar arbitraj bandının (c) içinden doğar.** c'yi büyük, değişken ve ajana özgü tut. | Mekânsal denge (01 §3), Bannerlord (04) |
| 2 | **Bilgi fiziksel olarak taşınır ve eskir.** Fiyat dağınıklığı cehaletin ölçüsüdür. | Stigler, Geertz (01 §6), EVE |
| 3 | **Piyasa kurumu, ajan zekâsından önemlidir.** Doğru eşleştirmeyle basit ajanlar yeter. | Gode-Sunder, ZIP (02 §3) |
| 4 | **NPC'ler inandırıcı ve çeşitli olsun, en iyi olmasın.** | Bannerlord, TAC-SCM (03 §8) |
| 5 | **Gecikmeler salınım yaratır.** Salınım iyidir, patlayan salınım kötüdür. | Örümcek ağı, Bira Oyunu (01 §5) |
| 6 | **Kaynaklar ve yutaklar muhasebelenir.** Kimse yoktan para basmaz. | Ultima Online, Victoria 2 |
| 7 | **İtibar ve sadakat ekonomik mekanizmalardır, süs değil.** | Kirman, Greif (01 §10, 03 §4) |
| 8 | **Her sistem okunabilir ve izlenebilir olsun.** | Space Rangers, Dwarf Fortress, X4 (04) |

## 3. Katmanlı mimari önerisi

```
┌─────────────────────────────────────────────────────────────────┐
│ 5. TARİH VE OLAYLAR   savaşlar, iflaslar, veba, ambargolar,      │
│                       hasat şokları (sabit ve olasılıksal)       │
├─────────────────────────────────────────────────────────────────┤
│ 4. KURUMLAR           devletler (vergi, gümrük, tahıl ambarı),   │
│                       loncalar, topluluklar (itibar ağları),     │
│                       finans (senet pazarı, sigortacılar,        │
│                       kambiyo)                                   │
├─────────────────────────────────────────────────────────────────┤
│ 3. AJANLAR            tüccarlar (oyuncu dahil), dealer'lar,      │
│                       armatörler, temsilciler, korsanlar,        │
│                       kervancılar, simsarlar                     │
│                       → inanç, sermaye, stok, ilişkiler, kişilik │
├─────────────────────────────────────────────────────────────────┤
│ 2. PAZARLAR           liman pazarı = dealer'lar + günlük çağrılı │
│                       açık artırma (dealer'lar arası)            │
├─────────────────────────────────────────────────────────────────┤
│ 1. KİTLE              kentsel talep havuzları (nüfus × sınıf ×   │
│                       mevsim), kırsal arz havuzları (hasat,      │
│                       maden, zanaat)                             │
├─────────────────────────────────────────────────────────────────┤
│ 0. DÜNYA              graf: limanlar ve kara noktaları; deniz ve │
│                       kara yolları (mesafe, mevsimsel risk);     │
│                       hava durumu; seed'li PRNG akışları         │
└─────────────────────────────────────────────────────────────────┘
          ↑ ZAMAN: günlük tick + ayrık olay kuyruğu ↑
```

### Katman 0: Dünya
- **Graf:** Düğümler (limanlar, kara şehirleri), kenarlar (deniz ve kara yolları). Kenar özellikleri: mesafe, mevsime göre seyir süresi dağılımı, fırtına riski, korsan baskısı (dinamik).
- **PRNG akışları:** Her alt sistemin kendi seed'li akışı var (bkz. [determinizm](../../design/determinism.md)).

### Katman 1: Kitle (toplu model)
- **Kentsel talep havuzu** (şehir × mal): nüfus, sınıf dağılımı ve mevsime göre temel ihtiyaç; esnekliğe göre fiyat tepkisi. Dealer'lardan perakende alım yapar. (02 §6)
- **Kırsal arz havuzu** (bölge × mal): hasat ve üretim kapasitesi, verim şokları; arz eğrisine göre dealer'lara satış.
- **Kalibrasyon:** Tahıl için King-Davenant (01 §2).
- Bu katmanda ajan yok, sadece dağılımlar. Ucuz ve kararlı.

### Katman 2: Pazarlar
- Her limanda N dealer (02 §5). Her dealer stoğuna ve inancına göre alış ve satış fiyatı ilan eder (Amihud-Mendelson tarzı stok çarpıklığı).
- Dealer'lar arası **günlük çağrılı açık artırma** (Doran-Parberry tarzı takas odası): fazla stoğu olan satar, eksiği olan alır. Bu, liman içi fiyatları birbirine yaklaştırır ama tamamen eşitlemez.
- Gelen tüccarlar dealer'lara satar veya onlardan alır. Oyuncu da bunlardan biri.
- **Sonuç:** Liman başına mal başına tek bir "fiyat" yok, bir **fiyat dağılımı** var. Arayüzde "Rialto'da biber: 42-47 duka/kantar" gibi gösterilir.

### Katman 3: Ajanlar
Her ajanın durumu:
```
sermaye, stok (konum bazlı), borçlar ve alacaklar
inançlar:  {(liman, mal) → (fiyat_gözlemi, tarih, kaynak_güvenilirliği)}
ilişkiler: {ajan → güven/sadakat puanı}, {topluluk → itibar}
kişilik:   risk_iştahı, beklenti_türü (temelci/trend/uyarlamalı), λ, sabır, dürüstlük
uzmanlık:  bildiği mallar ve rotalar
```
- **Karar anları** (her gün değil): limana varış, haber gelişi, sözleşme vadesi, periyodik gözden geçirme. Olay kuyruğuna planlanır.
- **Karar yöntemi:** Fayda tabanlı yapay zekâ (utility AI). Her seçeneğe (rota × mal × miktar) puan verilir: beklenen kâr, risk, inanç belirsizliği, kişilik çarpanları. Mevcut planı sürdürmeye **atalet bonusu** verilir, böylece ajan sürekli fikir değiştirmez ([Dave Mark IAUS](https://gameai.com/iaus.php), [Wikipedia](https://en.wikipedia.org/wiki/Utility_system)).
- **Beklenen fiyat** bilgi yaşına göre genişleyen inanç aralığından gelir (02 §7). Temkinli ajan aralığın kötü ucuna, cesur ajan ortasına göre karar verir.
- **Rakip tahmini (isteğe bağlı, akıllı ajanlar için):** "Bu haberi kaç kişi duydu?" tahmini, örümcek ağı salınımını yumuşatır.
- **Strateji değiştirme:** Kârlılığa göre lojit kuralı (Brock-Hommes), ama tarihsel ve sosyal sınırlar içinde.
- **İflas ve yenilenme:** İflas eden ajan dünyadan çıkar. Yeni ajanlar nüfus ve fırsatlara göre doğar (Doran-Parberry'nin tarihsel sınırlı versiyonu).
- **Oyuncu:** Aynı veri yapısı. Tek fark, kararları bir insan veriyor.

### Katman 4: Kurumlar
- **Devletler:** gümrük oranları (bayrak ve imtiyaza göre), ihracat yasakları, tahıl ambarları (kıtlıkta satan, bollukta alan dengeleyici NPC), vergiler (para yutağı).
- **Topluluklar** (Venedikli, Ragusalı, Yahudi, Rum, Ceneviz...): itibar ağları; dedikodu ve yaptırım (Greif).
- **Finans:**
  - *Senetler:* İkincil piyasada fiyatlanır; savaş ve kriz haberleriyle değer kaybeder (S-005).
  - *Sigortacılar:* Dealer gibi fiyat veren ajanlar. Prim = algılanan risk × itibar çarpanı + marj (K-012).
  - *Kambiyo ve poliçe* (geç oyun): uzak mesafeye para transferi, kur riski.

### Katman 5: Tarih ve olaylar
- Sabit büyük olaylar (Kıbrıs 1570) ve olasılıksal küçük olaylar (S-003).
- Olaylar doğrudan fiyatı değiştirmez. Alt katmanları değiştirir: hasadı, rotaların riskini, gümrükleri, tüccarlara el koymayı. **Fiyat etkisi kendiliğinden ortaya çıkar.** Bu, "her şeyi gerçekten simüle et" ilkesi (Eco) ve okunabilirlik için bir "neden zinciri" bırakır.

### Zaman: hibrit
```
Günlük tick:
  1. Kitle: üretim ve tüketim (havuzlar dealer'larla işlem yapar)
  2. Pazar: dealer'lar arası takas (çağrılı açık artırma)
  3. Fiyat istatistikleri ve "neden" kayıtları
Olay kuyruğu (zaman damgalı, deterministik sıralı):
  - gemi ve kervan varışları → mal ve haber teslimi
  - ajan karar anları
  - sözleşme vadeleri
  - tarihsel ve rastgele olaylar
Aylık / mevsimlik:
  - hasat, nüfus, vergiler, kurum güncellemeleri
```
Bu, EU4 tarzı akışa (K-006) uyar: oyuncu hızı değiştirdiğinde sadece tick'lerin gerçek zamanda ne sıklıkla çalıştığı değişir.

## 4. Bilgi sistemi: tasarımın kalbi

```
Olay (Apulia'da kötü hasat)
  → yerel olarak bilinir (Bari dealer'ları, inançlarını günceller)
  → giden her gemi ve kurye haberi taşır (haber paketi: içerik, tarih, kaynak)
  → varılan limanda haber yayılır (Daley-Kendall benzeri: bazıları hemen, bazıları geç, bazıları hiç duymaz)
  → ajanlar inançlarını günceller ve karar anlarını tetikler
  → herkes bildiğinde haberin ticari değeri sıfırlanır
```
- **Fiyat bilgisi de haberdir:** "14 Mart'ta İskenderiye'de biber 38'di."
- **Kaynak güvenilirliği:** kendi gözün > temsilcin > tanıdık tüccar > liman söylentisi.
- **Yanlış haber:** Olasılıklı bozulma veya kasıtlı söylenti (geç oyun: "algı yaratma").
- **Oyuncu araçları:** Haber defteri (ne, ne zaman, kimden), "bu bilgi X günlük" uyarıları, yoldaki mallar ve beklenen haberler görünümü (Bira Oyunu dersi).

## 5. Ölçek tahmini (ilk dilim için, S-006)

| Varlık | Sayı (kaba) |
|---|---|
| Limanlar | 6-8 |
| Mallar | 8-10 |
| Dealer'lar | Liman başına 3-6 → ~30-40 |
| Gezgin tüccarlar | 50-150 |
| Armatörler, gemiler | 30-80 gemi |
| Korsanlar | Rota bazlı baskı + birkaç ajan |
| Günlük tick sayısı | 10 yıl ≈ 3.650 |

Bu ölçekte Python prototipi bile saniyeler içinde 10 yıllık simülasyon çalıştırabilir (tahmin, ⚠️ ölçülmeli). Çoklu seed testleri için yeterli.

## 6. Ayar düğmeleri (oynaklık ve zorluk)

| Düğme | Etki | Kaynak |
|---|---|---|
| Bilgi yayılım hızı | Fiyat dağınıklığı ve fırsat ömrü | Stigler, EVE |
| Seçim yoğunluğu β / öğrenme hızı | Oynaklık, balonlar | Brock-Hommes, Santa Fe |
| Arbitraj maliyeti c bileşenleri | Ticaret hacmi, fırsat sayısı | Mekânsal denge |
| NPC sayısı ve sermayesi | Rekabet yoğunluğu | Bannerlord |
| Şok sıklığı ve büyüklüğü | Kaos | Offworld, Taipan |
| Dealer stok hassasiyeti κ | Piyasa derinliği | Amihud-Mendelson |
| Fiyat ayarlama hızı α (kitle) | Kararlılık | Tâtonnement |

## 7. Riskler ve açık konular

| Risk | Açıklama | Önlem |
|---|---|---|
| Fırsat ölümü | NPC'ler çok verimli olur | İlke 1, 2, 4; bot testleri (06 §6) |
| Patlayan salınımlar | Gecikmeler artı naif beklentiler | Ortalama penceresi, farklı karar zamanları, rakip tahmini |
| Para ve mal birikimi | Musluk ve yutak dengesizliği | Muhasebe, P10 testi |
| İstanbul gibi dev aktörlerin sistemi bozması | Victoria 2'deki Çin örneği | Ölçek ayarı; büyük şehirlere ayrı tedarik kurumları |
| Okunmazlık | Oyuncu nedenleri göremez | "Neden" kayıtları, haber defteri |
| Kapsam şişmesi | Her katman kendi başına bir proje | İlk dilimde katman 4-5 minimal tutulur |
| Tarihsel veri eksikliği | Fiyatlar, hacimler, süreler | "Makul mekanizma, birebir rakam değil" ilkesi; Braudel ve Lane'den kalibrasyon |

## 8. Önerilen sonraki adımlar

1. **Kullanıcıyla tartışma:** Bu sentezdeki önerilerden hangileri karara dönüşsün? (Özellikle: dealer modeli, hibrit zaman, bilgi sistemi.)
2. **MERCURY kodunu okumak** (NetLogo, açık). En yakın akademik model.
3. **BazaarBot kodunu okumak:** Doran-Parberry'nin pratik sorunları.
4. **Simülasyon spesifikasyonu (`design/simulation-spec.md`):** ODD formatında (06 §2).
5. **Mini deneyler** (kod, onaydan sonra):
   - D1: Tek liman, 1 mal, kitle + 3 dealer. Fiyat kararlı mı?
   - D2: 2 liman, 1 mal, 10 tüccar, haber gecikmesi 0 → teorik dengeye yakınsıyor mu?
   - D3: Aynı deney, gecikme 40 gün → fiyat dağınıklığı ve salınım ne kadar?
   - D4: Hasat şoku → King-Davenant testi.
   - D5: Açgözlü bot ve döngü botu → istismar testi.

Bu deneyler kod yazmayı gerektirir ve K-009'daki "önce simülasyon" ilkesinin ilk somut adımı olur. Teknoloji seçimi için bkz. S-010.
