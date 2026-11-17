# Deniz Riski ve Sigorta: Akdeniz, 14.-16. yy
> Durum: taslak
> Son güncelleme: 2026-11-02
> İlgili: [risk-model](../../design/risk-model.md), [mediterranean-16c-overview](mediterranean-16c-overview.md), [08-trade-finance-contracts](../simulation/08-trade-finance-contracts.md), [D5b3h](../../experiments/D5b3h.md), K-030

Amaç: Rota ve mevsime bağlı batma ve korsana yakalanma riskinin tarihsel yapısını ve büyüklüğünü toplamak. Simülasyondaki risk modeli ([risk-model](../../design/risk-model.md)) buna dayanacak.

## 1. Primin yapısı: riski ne belirliyordu?

Ana kaynak: Ceccarelli (2007), Datini arşivi (Prato) ve ikincil derlemeler; geç Orta Çağ. 16. yy için doğrudan karşılığı Cenova verisi (§2).

| Bulgu | Sayı / örnek | Kaynak |
|---|---|---|
| **Mesafe ana belirleyici değil.** Kazaların çoğu açık denizde değil, kıyıda, limanda ve korsanlıkta oluyordu. | İspanya kıyısı → Kuzey Denizi (~4.000 km): %5,5-8. Toskana → Roma limanları (~250 km): %8,5-12, tepe %14 (korsan bölgesi). | Ceccarelli 2007, s. 10, Del Treppo 1972 ve Edler de Roover 1945'e dayanarak |
| **Risk belirli bölgelerde toplanıyordu.** Rotanın geri kalanı primi pek değiştirmiyordu. | Kuzey Denizi → La Rochelle ile Kuzey Denizi → Akdeniz limanları: %10-14 ile %8-14,5 | aynı |
| **Korsanlık ve savaş primin en az yarısı.** | Silahsız gemide prim, kadırgadakinin yaklaşık iki katı. 1470-73, Yukarı Tiren → Kuzey Denizi: kadırga %4-6, gemi %7-12. | Ceccarelli 2007, s. 16 ve 20 |
| **Gemi tipi en tutarlı yapısal etken.** | Venedik → Balear: gemi %3-4, Venedik kadırgası %1,5. Silahlı gemi %1,25'e karşı gemi %3. | Ceccarelli 2007, s. 9 |
| **Mevsim etkisi primde küçük ve bölgesel** (geç Orta Çağ). | Barselona'da 1.500'den fazla sözleşme: kış artışı yalnız bazı rotalarda, en çok %13. Katalonya → Provence ~%5. Levant rotasında yaz primi kıştan yüksek. Kötü hava yalnızca Lion Körfezi ve Yukarı/Orta Tiren gibi bölgeleri etkiliyor. | Ceccarelli 2007, s. 12, Del Treppo 1972'ye dayanarak |
| **Seçilim etkisi.** Tüccarlar kışın ve tehlikeli rotalarda kıyı taşımacılığına (cabotage) geçiyordu. Yani küçük kış primi, kış riskinin küçük olduğunu değil, riskli seferlerin yapılmadığını da gösterebilir. | Datini, Cenova/Savona → Pisa: cabotage gemileri baskın | Ceccarelli 2007, s. 12 ve dipnot 33 |
| **18. yy'da mevsimsel prim farkı açıkça kanıtlanmış.** | — | Spooner 1983 ⚠️ (Ceccarelli üzerinden) |
| **Haberle ani sıçramalar.** Yapısal etkenler aynıyken prim söylentiyle değişiyordu. | Barselona → Messina 1461: 26 Haziran %3,5; 1 Temmuz %10-12; 10 Temmuz %4. Aynı sözleşmede aynı gün %6, %5,47, %8. | Ceccarelli 2007, s. 16 |
| **Fiyatlama istatistik değil, deneyim ve haber.** Yavaş değişen etkenler (gemi tipi) tutarlı fiyatlanıyor; hızlı değişenler (korsan) sübjektif. | — | Ceccarelli 2007, sonuç |
| **İnsan kaynaklı risk doğal riskten daha çok fiyatlanıyor; rota mesafeden önemli.** 7.000'den fazla sözleşme, 6 arşiv, 1340-1500. | Katsayılar özette yok ⚠️ | Botticini, Buri & Marinacci 2023 (JEEA) |

## 2. 16. yy primleri

| Yer, dönem | Bulgu | Kaynak |
|---|---|---|
| Cenova 1564-72 | 757 poliçelik defter. Örnek primler: mal üzerine %8,25; köle üzerine %5,75. 1570'te bir gemi için sözleşme ortasında %4 → %5. | Iodice 2023 (APJRI), arama özetinden ⚠️ |
| Cenova 1564-72 | Sigortacılar kapalı bir tüccar grubu; birbirlerini sigortalıyorlar (syndicate, mutual). Kazanç ve kayıplar küçük; sigorta bir risk paylaşım aracı. | Iodice 2023, özet |
| Cenova 1575-1624 | Primler rotaya göre %1-15. 1622-24: Napoli %2, Amsterdam'dan %14. Sigortalanan değer primi etkilemiyor, rota etkiliyor. | Arama özeti ⚠️ (birincil kaynak doğrulanmadı) |
| Cenova ve Venedik | Ortalama prim Cenova %5,28 (335 gözlem), Venedik %2,46 (88 gözlem). Fark Venedik donanmasının devriyesine bağlanıyor. | Arama özeti ⚠️ (kaynak makale belirlenemedi) |
| Floransa (Rönesans) | Toskana-Liguria %2 (en düşük). Kuzey Tiren → Güney İtalya %4-9. Kuzey Denizi → Akdeniz %14-17. | *Risky Markets* (Brill 2020), arama özetinden ⚠️ |
| Londra, 16.-18. yy | Deniz sigortası fiyatları yarıdan fazla, bazen %75 düştü. | Leonard ([overview](mediterranean-16c-overview.md)) |

## 3. Kayıp sıklığı

- **Venedik 1592-1609 (Tenenti 1959):** Noter kayıtlarından 1.000'den fazla olay; yaklaşık 660'ı batma ya da korsana yakalanma, yılda ~37. Kalanı daha hafif kazalar. Braudel üzerinden ikincil özet ⚠️.
  - Bu sayıyı yıllık kayıp oranına çevirmek için Venedik'te sigortalanan gemi-sefer sayısı gerekiyor. Bulunamadı. Lane (1973) ve Gluzman (2021) okunacak.
- **Prim ile kayıp ilişkisi:** 1780-1820 İngiliz verisinde rota bazında kayıp oranı ile prim birlikte hareket ediyor (UCD WP19/25 ⚠️, metne erişilemedi). Yani prim, beklenen kaybın iyi bir göstergesi. Ama loading (kâr payı) bilinmiyor.
- **Kaba çıkarım (Claude, ⚠️):** Ortalama prim %2,5-5 ve loading %20-50 ise, sefer başına kayıp olasılığı ~%2-4.

## 4. Sigortanın kapsamı

- Deniz sigortası 14. yy ortasından itibaren var (González de Lara 2004; [08](../simulation/08-trade-finance-contracts.md)).
- Poliçeler deniz ve insan tehlikelerini (fırtına, korsan, el koyma) kapsıyordu; piyasa fiyatı kaybını kapsamıyordu. ⚠️ Genel bilgi, tek kaynakla doğrulanmadı.
- Ortak avarya (general average): yükü kurtarmak için denize atılan malın bedeli, gemi ve yük sahipleri arasında paylaşılır. Akdeniz'de 1500-1700 arası yaygın (Iodice; OAPEN *General Average and Risk Management*) ⚠️.

## 5. Bölgeler (bizim harita için)

Haritadaki bacaklar: VEN-RAG, RAG-COR, VEN-COR, COR-CHI, CHI-IST, CHI-ALE, COR-ALE.

| Bölge | Tarihsel tehlike | Kaynak durumu |
|---|---|---|
| Adriyatik (VEN-RAG) | Uskok korsanları (Senj), özellikle 1570 sonrası. Venedik devriyesi. Kışın bora. | Tenenti 1967 ⚠️ (okunmadı) |
| Otranto ve İyon (RAG-COR, VEN-COR) | Berberi ve Uskok baskınları | ⚠️ |
| Mora ve Ege (COR-CHI, CHI-IST) | Malta ve Floransa (San Stefano) korsanları, Rum korsanlar; Osmanlı gemisi için tehlikeli. 1570-73 savaşı. | Greene 2010 ⚠️ (okunmadı) |
| Doğu Akdeniz (CHI-ALE, COR-ALE) | Malta Şövalyeleri Müslüman gemilerini vuruyor; İskenderiye-İstanbul hattı hedef. | Greene 2010 ⚠️ |

## 6. Oyun için çıkarımlar

1. **Tehlike bacağa ve bölgeye bağlı olmalı, mesafeye değil.** Bugünkü motor günlük sabit olasılık kullanıyor (yaz %0,1, kış %0,3; Claude seçimi). Bu, uzun rotayı orantısız cezalandırıyor ve korsan bölgelerini görmüyor.
2. **İki ayrı tehlike:** doğal (mevsimle değişir, bölgesel) ve korsan (zamanla değişen, şoklu, haberle fiyatlanan). Kaynaklara göre primin en az yarısı korsan ve savaş.
3. **Korsan baskısı dinamik bir dünya değişkeni olmalı.** Primdeki sıçramalar (%3,5 → %12 → %4) kalıcı olmayan şokları gösteriyor.
4. **Mevsim etkisinin bir kısmı davranıştan gelir:** Tüccar kışın riskli rotadan kaçar. Bu, modelde kendiliğinden çıkmalı; tepeden yasaklanmamalı.
5. **Gemi tipi (silahlı veya silahsız) riskin en tutarlı belirleyicisi.** İleride gemi tipi bir seçim olabilir (K-011: refakat, konvoy).
6. **Fiyatlama deneyimle ve haberle yapılır.** Tüccar ve sigortacı, sefer başına ortalama kaybı kamuya açık kayıp haberlerinden öğrenmeli; doğru olasılığı bilmemeli.
7. **Kalibrasyon hedefleri (örüntü):**
   - Prim dağılımı %1-15; ortalama %2,5-5
   - Primin en az yarısı korsandan
   - Kışın prim artışı küçük, ama kış seferi sayısı düşük
   - Haberle geçici prim sıçramaları

## Kaynaklar
- Ceccarelli, G. (2007). *The Price for Risk-Taking: Marine Insurance and Probability Calculus in the Late Middle Ages.* JEHPS 3(1). https://www.jehps.net/Juin2007/Ceccarelli_Risk.pdf (okundu)
- Botticini, M., Buri, C., Marinacci, M. (2023). *The Beauty of Uncertainty.* JEEA 21(6). https://ideas.repec.org/a/oup/jeurec/v21y2023i6p2287-2326..html (özet)
- Iodice, A. (2023). *Marine Insurance in Early Modern Genoa (1564-1571).* APJRI 17(2). https://www.degruyterbrill.com/document/doi/10.1515/apjri-2022-0037/html (özet; tam metne erişilemedi)
- Tenenti, A. (1959). *Naufrages, corsaires et assurances maritimes à Venise 1592-1609.* https://www.persee.fr/doc/ehess_0079-4074_1959_mon_8_1 (okunmadı; Braudel özeti: https://www.scribd.com/doc/82821007/BRAUDEL-the-Mediterranean-I)
- *Risky Markets: Marine Insurance in Renaissance Florence* (Brill 2020). https://dokumen.pub/risky-markets-marine-insurance-in-renaissance-florence-brills-studies-in-maritime-history-8-2020046140-9789004399129-9004399127.html (arama özeti)
- Iodice, A. *Managing Shipping Risk: General Average and Marine Insurance in Early Modern Genoa.* https://www.academia.edu/49554609/
- UCD WP19/25 (İngiliz kayıp ve prim serileri, 1780-1820). https://www.ucd.ie/economics/t4media/WP19_25.pdf (erişilemedi)
