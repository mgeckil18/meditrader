# Tam Harita v1 (M1): Cenova'nın Doğusu, Büyük ve Orta Limanlar
> Durum: taslak (kaba veri; K-035 gereği geçici vekiller)
> Son güncelleme: 2026-11-10
> İlgili: [trade-structure](trade-structure.md), [port-hierarchy-16c](../research/history/port-hierarchy-16c.md), [M1](../experiments/M1.md), [rust-core](rust-core.md), K-034, K-035, S-023

**Kaynak dosya:** `core/tools/mapgen.py` (veri burada) → `core/maps/east-med-v1.json` (üretilir; elle düzenlenmez). Eski harita `core/maps/classic6.json` (Python oracle'ı, değişmez).

**Köken (kural 7d):** Liman seçimi, nüfuslar, arz planı, bölge tehlikeleri, seyir hızı: **Claude tahmini ⚠️**. Tarihsel dayanaklar [port-hierarchy-16c](../research/history/port-hierarchy-16c.md)'de; sayıların çoğunun kaynağı yok (K-035: arşiv verisi yok, kaba değer). Hepsi geçici vekil (İ12).

## Limanlar (20)

| Kimlik | Liman | Tür | Nüfus ⚠️ | Not |
|---|---|---|---|---|
| GEN | Cenova | büyük | 65 bin | finans, transit |
| CVV | Civitavecchia | orta | 8 bin | Tolfa şapı (ALM tek kaynağı) ⚠️ |
| NAP | Napoli | büyük | 230 bin | büyük tüketici |
| PAL | Palermo | orta | 90 bin | Sicilya tahılı (ihracatçı) |
| MES | Messina | orta | 60 bin | ipek (henüz mal yok) |
| TUN | Tunus | orta | 50 bin | zeytinyağı; korsan bölgesi |
| VEN | Venedik | büyük | 170 bin | ev limanı; ince kumaş (CLF) |
| ANC | Ancona | orta | 20 bin | Venedik'in rakip kapısı |
| RAG | Ragusa | orta | 30 bin | |
| BAR | Bari-Barletta (Apulia) | orta | 30 bin | buğday, zeytinyağı, yün ihracatı |
| COR | Korfu | orta | 18 bin | |
| ZAN | Zante | orta | 15 bin | yağ, şarap (kuru üzüm henüz yok) |
| CAN | Kandiye (Girit) | orta | 15 bin | malvasia şarabı (ana ihracatçı) |
| CHI | Sakız | orta | 15 bin | 1566'da Osmanlı |
| SAL | Selanik | orta | 30 bin | buğday, yün, kaba kumaş (CLC) |
| IST | İstanbul | büyük | 450 bin | yün ihracatı, kaba kumaş |
| RHO | Rodos | orta | 10 bin | |
| FAM | Magosa (Kıbrıs) | orta | 8 bin | 1571'e kadar Venedik |
| TRI | Trablusşam | orta | 15 bin | Halep'in limanı; biber (kervan vekili) |
| ALE | İskenderiye | büyük | 40 bin | buğday, biber |

Sınıf payları ve şarap çarpanı (Müslüman kentlerde düşük) `mapgen.py`'de.

## Bacaklar ve süreler
- Süre = büyük daire mesafesi × 1,2 (kıyı dolanımı) / 45 deniz mili/gün; yarım güne yuvarlanır ⚠️. Hız, eski haritanın günlerinden kabaca çıkarıldı (VEN-RAG 8 gün tutuyor).
- Kara engeli olan bacaklarda ek çarpan: Zante-Sakız × 1,45 (Malea), Tunus-Messina × 1,35, Palermo-Messina × 1,25.
- 31 bacak. Mesafeler 102-356 deniz mili, 2,5-9,5 gün.

## Bölgeler (tehlike)
| Bölge | Kış çarpanı | Sakin korsan olasılığı / bacak | Gerekçe ⚠️ |
|---|---|---|---|
| TYR (Ligurya-Tiren) | 2 | 0,005 | Berberi baskınları |
| SIC (Sicilya kanalı, Tunus) | 2 | 0,012 | Berberi merkezi |
| ADR (Kuzey Adriyatik) | 3 | 0,003 | classic6 ile aynı |
| OTR (Güney Adriyatik) | 2 | 0,008 | classic6 ile aynı |
| ION (İyon, Mora) | 2 | 0,008 | Berberi, Malta |
| AEG (Ege) | 2 | 0,010 | classic6 ile aynı |
| STR (Boğazlar) | 2 | 0,002 | classic6 ile aynı |
| LEV (Levant, Kıbrıs, Mısır) | 1 | 0,010 | classic6 ile aynı |

## Arz planı (mevcut 9 mal)
- **Buğday ihracatçıları:** Palermo, Apulia, İskenderiye (ağırlık 1), Selanik (0,4), Magosa (0,3).
- **Zeytinyağı:** Apulia (1), Kandiye (0,4), Tunus (0,4), Korfu ve Zante (0,3).
- **Şarap:** Kandiye (1), Napoli (0,4), Sakız (0,4), Korfu, Zante, Magosa (0,3).
- **Yün:** İstanbul (1), Selanik (0,6), Apulia (0,4).
- **Şap:** Civitavecchia. **Biber:** İskenderiye (1), Trablusşam (0,4).
- **Kumaş havuzları:**
  - Venedik CLF (bütün limanlara),
  - Venedik CLC (İtalya, Adriyatik, İyon, Girit, Kıbrıs),
  - İstanbul CLC (Osmanlı limanları),
  - Selanik CLC (kendisi).

## Bilerek dışarıda bırakılanlar
- Küçük limanlar (M3).
- Karadeniz, kervan sınırları (M5).
- Yeni mallar (ipek, kuru üzüm, tuz, kereste, şeker, pamuk).
- Liman fiziksel özellikleri ve gemi tipleri (M2).
- Tarihsel olaylar (M6).
