# D5b3i — Risk Modeli R1: Bacak ve Bölge Tehlikesi
> Durum: R1 sonuçlandı
> Son güncelleme: 2026-11-06
> İlgili: [risk-model](../design/risk-model.md), [maritime-risk-16c](../research/history/maritime-risk-16c.md), [D5b3h](D5b3h.md), K-030, S-021

**Taban:** WTA-UR-B (D5b3h, Ö1 dahil; K-031).

## Mekanizma (`hazard_model="leg"`)

- **Sefer başına kayıp,** rotanın bacakları (haritadaki kenarlar) boyunca birleşir: P = 1 − Π (1 − doğal) (1 − korsan). Gün sayısıyla orantılı değil (Ceccarelli 2007: mesafe değil bölge belirleyici).
- **Doğal tehlike:** bacak başına yazın %0,4; kışın (Kasım-Şubat) bölgenin kış çarpanıyla. Bir bacak birden çok bölgeden geçiyorsa en yüksek çarpan.
- **Korsan tehlikesi:** bölgenin sakin düzeyi × bugünkü korsan baskısı çarpanı.
- **Korsan baskısı:** her bölgede aylık log-AR(1) (ρ = 0,8, σ = 0,25) + seyrek sıçrama (ayda %5 olasılıkla +1,0, yani ~×2,7). Çarpanın uzun dönem ortalaması 1'e normalize edilir. Bölgedeki her gemiyi birlikte etkiler: ortak (sistematik) şok.
- **Tüccarın bilgisi (geçici):** Karar verirken bölgenin uzun dönem ortalamasını bilir, bugünkü şoku bilmez. R2'de haberden öğrenmeyle değişecek.
- **Kaybın nedeni** (batma veya korsan) bacakların payına göre çekilir; kayda girer.
- **Gemi kaybı (`ship_loss`):** kaybolunca ödenen yenileme bedeli. S-021'deki (a) seçeneği; R1S kurulumunda ¼ sermaye (60.000) ⚠️ vekil. Kullanıcı kararı bekliyor.

| Bölge | Bacaklar | Kış çarpanı | Sakin korsan (bacak başına) | Gerekçe |
|---|---|---|---|---|
| ADR Adriyatik | VEN-RAG, VEN-COR | 3,0 | %0,3 | Bora; Venedik devriyesi, Uskoklar |
| OTR Otranto, İyon | RAG-COR, VEN-COR | 2,0 | %0,8 | Berberi ve Uskok baskınları |
| AEG Mora, Ege | COR-CHI | 2,0 | %1,0 | Malta, San Stefano, Rum korsanlar |
| STR Kuzey Ege, Boğaz | CHI-IST | 2,0 | %0,2 | Osmanlı iç suları |
| LEV Doğu Akdeniz | CHI-ALE, COR-ALE | 1,0 | %1,0 | Malta Şövalyeleri; Levant'ta kış primi artmıyor (Del Treppo) |

Bütün sayılar Claude seçimi ⚠️. Kaynaklardaki örüntülere göre seçildi; bölge kaynakları (Tenenti 1967, Greene 2010) okunmadı.

**Kod:** `sim/world5.py` (`REGIONS`, `EDGE_REGIONS`, `route_legs`, `corsair_norm`, `_p_loss`, `_leg_hazards`, `_corsair_step`). Varsayılan `hazard_model="daily"` eski davranışı birebir veriyor (regresyon testi: giriş, çıkış, iflas, nakit aynı). Yeni alanlar varsayılandaysa snapshot hash'ine girmiyor (`_KEY_IF_SET`).

## Duman testi (VRS, soğuk başlangıç, 3 yıl, seed 1)

| | Eski (günlük) | R1 |
|---|---|---|
| Sefer başına kayıp | %3,0 (beklenen) | %1,9 (gerçekleşen) |
| Yaz / kış | %1,7 / %7,3 | |
| Korsan payı | yok | %74 |
| En yoğun rota ALE → VEN | | %2,8 |
| VEN ↔ COR | | %1,2-1,3 |
| Kış seferi payı | %24 (kış aylarının payı %33) | |
| Giriş / iflas | 28 / 14 | 37 / 17 |

## Kurulumlar

| Kurulum | İçerik |
|---|---|
| `-WTA-UR-B-R1` | R1 (VRS ve F) |
| `-WTA-UR-B-R1S` | R1 + gemi kaybı bedeli (VRS) |

10 seed, 10 yıl, `out/d5b3h/`. Ölçütler D5b3h'dekiler + `loss_rate`, `loss_corsair_share`, `winter_dep_share`, `loss_rate_winter`, `voyages_per_ship_year`.

## Önemli bir sınır (Claude)

Modelde bir tüccar = bir gemi = bütün yük. Tarihte tüccar yükünü birkaç gemiye böler ve sigortalatır. Bu yüzden R1 tek başına kaybı fazla yıkıcı gösterebilir. (Düzeltme, sonuçlar: kayıpların çoğu iflasa yol açmıyor; aşağıya bakın.) Tarihsel risk düzeyi ancak R4 (sigorta) ve carati ile birlikte anlamlı olur.

## Sonuçlar: VRS (2026-11-06)

10 seed, 10 yıl, ortalama ± %95 güven aralığı. Karşılaştırma: WTA-UR-B (D5b3h).

| Ölçüt | Taban (eski tehlike) | R1 |
|---|---|---|
| Toplam getiri | 0,156 ± 0,014 | 0,140 ± 0,012 |
| Yerleşikler | 0,125 ± 0,029 | 0,114 ± 0,024 |
| Zarar edenlerin payı | 0,41 | 0,24 |
| Giriş / gemi-yıl | 0,24 | 0,10 |
| Çıkış / gemi-yıl | 0,15 | 0,07 |
| İflas / gemi-yıl | 0,046 ± 0,010 | 0,027 ± 0,011 |
| Filo ortalaması | 56 ± 11 | 47 ± 11 |
| Filo CV | 0,39 | 0,26 |
| Tepe / dip | 8,1 ± 5,2 | 5,7 ± 6,2 |
| Sefer başına kayıp | ~0,030 (duman testi) | 0,020 ± 0,002 |
| Korsan payı | — | 0,68 ± 0,03 |
| Kışın sefer başına kayıp | ~0,073 | 0,025 (yazın ~0,018) |
| Kış seferlerinin payı | 0,24 | 0,245 |
| Sefer / gemi-yıl | | 8,4 |

Rota bazında (10 seed toplamı): ALE ↔ VEN %3,0 (iki bölge: Levant + Adriyatik-Otranto), COR → VEN %1,6, ALE ↔ COR ve VEN → COR %1,3-1,4. Korsan payı rotaya göre %53-77.

**Örüntü kontrolü (maritime-risk-16c §6.7):**
- Sefer başına kayıp %2,0: hedef aralığın (%2-4) alt ucu ✓
- Korsan payı ≥ %50 ✓ (%68)
- Kış etkisi küçük ve bölgesel ✓ (kış/yaz ≈ 1,4; eski modelde ≈ 4,3). Kaynakta primde kış artışı ≤ %13; bizimki biraz büyük ama seçilim düzeltmesi yok.
- **Kış seferi payı değişmedi (%24,5):** Tüccarın kışın riskli rotadan kaçması bugün kendiliğinden çıkmıyor. Kışın düşük sefer payı riskten değil, mevsimlik ticaretten (hasat) geliyor. Seçilim etkisi R2 (öğrenilen risk) ve R4 (sigorta fiyatı) ile sınanmalı.

**Etkiler:**
- Ortalama kayıp eski modelden düşük (%3,0 → %2,0). Getiri biraz düştü (%15,6 → %14,0; eşik bandının üst ucu), iflas azaldı, devir yarıya indi, filo daha sakin (CV 0,39 → 0,26).
- Getiri düşüşüyle iflas düşüşü birlikte: kaybın daha az, ama riskin daha az da ödüllendirilmesi. Ayrı ölçülmeli.

**İki yeni bulgu (modele özgü):**
1. **Yıllık kayıp yüksek.** Gemi yılda 8,4 sefer yapıyor; sefer başına %2 ile yılda geminin ~%16'sı kayıp. Tarihte bir gemi yılda 1-2 büyük sefer (mude takvimi) yapıyordu ⚠️ (doğrulanmadı). Primden çıkarılan sefer başına olasılık, bizim kısa seferlerimize doğrudan uygulanınca yıllık kayıp şişiyor. Sefer süresi ve sefer sıklığı tarihsel değerlerle karşılaştırılmalı.
2. **Kayıpların çoğu iflasa yol açmıyor.** Gemi-yıl başına 0,17 kayıp, 0,027 iflas: yaklaşık altı kayıptan biri iflas. D5b3i'deki "tek kayıp = iflas" beklentim (Claude) yanlıştı. Aday neden: yerleşiklerin birikmiş boş sermayesi (D5b3h Ö0 bulgusu) kaybı karşılıyor. Doğrulanmadı ⚠️.

## Sonuçlar: R1S (gemi kaybı bedeli, VRS)

| Ölçüt | R1 | R1S |
|---|---|---|
| Toplam getiri | 0,140 ± 0,012 | 0,152 ± 0,012 |
| İflas / gemi-yıl | 0,027 ± 0,011 | 0,049 ± 0,010 |
| Zarar edenlerin payı | 0,24 | 0,38 |
| Filo | 47 ± 11 | 53 ± 5 |
| Tepe / dip | 5,7 ± 6,2 | 3,4 ± 0,7 |

Gemi kaybı bedeli iflası iki katına çıkarıyor (kayıp artık daha çok tüccarı bitiriyor) ve getiri biraz artıyor (riskin bedeli). Filo daha düzenli; güven aralığı dar. Beklentim (Claude) "fark küçük olur" idi: yanlış, fark belirgin.

## Sonuçlar: tam harita (F)

| Ölçüt | F taban (WTA-UR-B) | F + R1 |
|---|---|---|
| Toplam getiri | 0,131 ± 0,024 | 0,130 ± 0,014 |
| İflas / gemi-yıl | 0,012 ± 0,003 | 0,022 ± 0,014 |
| Filo | 140 ± 19 | 152 ± 12 |
| Filo CV | 0,22 | 0,39 |
| Tepe / dip | 3,3 ± 2,1 | **72 ± 88** |
| Kayıp / sefer | | 0,020 ± 0,001 |
| Korsan payı | | 0,58 |
| Sefer / gemi-yıl | | 14,9 (yıllık kayıp ~%26) |

**Üç seed çöküyor (1, 4, 7; hepsi snapshot 1'den başlıyor).** Filo 1-4 gemiye iniyor, sonra 300'e (`max_merchants` tavanı) çıkıyor; döngü ~3 yılda bir tekrarlanıyor. Kalan 7 seed'de filo sakin (min 71-127). Aynı snapshot'tan başlayan taban seed'leri de (1, 7) 27-300 arasında salınıyordu; R1 bunu büyüttü.

**Teşhis: R bandının kendini besleyen döngüsü (modele özgü bulgu).**
- Seed 7'de patlama sırasında kamu sicili %300'e çıkıyor (az sayıda hayatta kalan tüccar çok kazanıyor). Bandın σ'sı = son 24 ayın kamu sicili sd'si; 0,03'ten 0,7-1,3'e çıkıyor.
- Çıkış eşiği = senet − κσ ≈ %4 − %100'ün altı. Getiri 2 yıl boyunca yılda −%5 ile −%11 arasında kalıyor ama kimse çıkmıyor (Ö1'le kendi sicil de çıkış sinyali vermiyor).
- Sonunda toplu iflas: filo 270 → 4. Sonra az sayıda tüccar yine çok kazanıyor, σ yine büyüyor.
- Yani bant genişliği, döngünün kendi ürettiği oynaklıktan besleniyor: döngü bandı genişletiyor, geniş bant döngüyü büyütüyor. Bant (R) zaten geçici vekil (İ12); doğal yerine geçecek olan Ö3 (gemi piyasası).
- R1'in rolü: başlatıcı değil (kayıp oranı çöküş öncesi olağan). Daha düşük ortalama kayıp girişi artırıyor; tavana çarpma daha sık.

**Sefer sıklığı:** Tam haritada gemi yılda 14,9 sefer yapıyor (kısa bacaklar; CHI-IST 4 gün). Sefer başına %2 ile yılda filonun ~%26'sı kayboluyor. Bu, D5b3i.1'deki ölçek sorununu büyütüyor.
