# 12 — Giriş Kararının Zamanlaması: Beklemek, Teyit, Bant
> Durum: taslak (tartışma açık)
> Son güncelleme: 2026-10-30
> İlgili: [D5b3g](../../experiments/D5b3g.md), [11-entry-barriers](11-entry-barriers.md), K-029, S-020

**Kullanıcı önerisi (2026-10-30, kesin değil):** Girmeye niyetli tüccar 3 ay arayla 3 kez değerlendirme yapsın (başta, ortada, sonda; toplam 6 ay). Üçünde de senet + riskten fazla kâr görüyorsa girsin. Amaç: giriş süreci 6 aya çıkar ve giriş için daha istikrarlı bir getiri beklenir.

## 1. Literatürdeki yeri

| Alan | Karşılık | Kaynak | Öneriyle ilişkisi |
|---|---|---|---|
| Ekonomi | **Real options / value of waiting:** Geri dönülemez yatırımda beklemenin bir değeri vardır. Optimal giriş eşiği, Marshall eşiğinin (tam maliyet) üstündedir; belirsizlik arttıkça yükselir | McDonald & Siegel (1986), *QJE*; Dixit & Pindyck (1994), *Investment under Uncertainty* | Önerinin kuramsal karşılığı. "Bekle ve gör"ün sezgisel bir uygulaması |
| Ekonomi | **Hysteresis bandı:** Batık maliyet + belirsizlikte giriş eşiği yukarıda, çıkış eşiği aşağıda; arada hareketsizlik bandı | Dixit (1989), *JPE* 97(3) | Çıkış tarafını da kapsayan genelleme |
| Ekonomi | **Time-to-build:** Yatırımın tamamlanması zaman alır; konjonktür dalgalanmalarını yayar ve uzatır | Kydland & Prescott (1982), *Econometrica* 50(6) | 6 aylık süreç, time-to-build'i uzatır |
| Ekonomi | **Cobweb:** Gecikmeli arz tepkisi salınım üretir. Arz tepkisi talepten esnekse salınım büyür | Ezekiel (1938), *QJE* 52(2); Hanau (1928) hog cycle | Gecikmeyi uzatmak tek başına sönümleme değildir |
| İstatistik | **Sequential sampling / SPRT:** Kanıt eşiği aşana kadar örneklem toplanır | Wald (1947), *Sequential Analysis* | "3 değerlendirmenin 3'ü de" ayrık bir sıralı test |
| Psikoloji | **Evidence accumulation / drift diffusion model:** Karar, biriken kanıt bir sınırı aşınca verilir. Sınır yükseldikçe karar yavaşlar ama doğruluk artar (speed-accuracy tradeoff) | Ratcliff (1978), *Psychological Review* 85(2) | Önerinin psikolojik karşılığı. "3'te 3", kesikli bir sınır |
| Psikoloji | **Status quo bias:** Durumu değiştirmek için daha fazla kanıt istenir | Samuelson & Zeckhauser (1988), *J. Risk Uncertainty* 1 | Mesleğe girmek bir durum değişikliği |
| Tarih | Sefere hazırlık mevsime bağlı: kışın uzun seferler kısıtlıydı (mare clausum), karar kışın, sefer baharda. Sermaye ortaklıkla (colleganza, gemi payları / carati) toplanır; gemi kiralanır ya da yaptırılır | ⚠️ genel tarih yazımı (Lane 1973), bu oturumda doğrulanmadı | Girişin aylar süren bir süreç olması tarihsel olarak doğru |

## 2. Öneri sorunu çözer mi? (Claude değerlendirmesi, test edilmedi)

**Güçlü yanları:**
- Geçici sıçramaları süzer. Gürültü kaynaklı girişler (D5b3f kaynak C) azalır.
- Kısa bir kâr dalgası artık giriş dalgası doğurmaz.

**Riskleri:**
1. **Gecikme artar.** Karar sinyali hâlâ son 12 ay. Ancak 6 ay boyunca yüksek kalan bir getiri girişi tetikler; gemi bir de 1-2 ay donatılır. Yeni gemi büyük olasılıkla dalganın tepesinden sonra gelir. Cobweb kuramında gecikmeyi uzatmak salınımı tek başına sönümlemez; dönemi uzatır.
2. **Yığılma.** Her ay yeni adaylar değerlendirmeye başlarsa, uzun bir yüksek dönemden sonra farklı aylarda başlamış adayların hepsi aynı anda testi geçer. Adaylar birbirini görmüyorsa bu yeni bir dalga olur.
3. **Çıkış tarafına dokunmuyor.** D5b3g-WTA'da çöküşü süren şey hızlı çıkış. Sicil eşiğin altına inince her gemi yılda ~9 kez çıkış kararı veriyor.

**Beklenti:** Kısmi çözüm. Giriş gürültüsünü azaltır; döngüyü tek başına durdurmaz. Test edilmeli.

## 3. Alternatif: real options bandı (Dixit 1989; Dixit & Pindyck 1994)

- Giriş tetiği = senet + prim + κ·σ
- Çıkış tetiği = senet + prim − κ·σ
- σ: kamu sicilinin oynaklığı (ör. son 24 ayın standart sapması); κ ≈ 1 ⚠️.

Neden:
- Kuramdaki optimal kurala en yakın basit biçim. Batık maliyet ve belirsizlik bandı açar.
- İki tarafı birlikte sönümler.
- Bant oynaklıkla kendiliğinden genişler: belirsiz dönemlerde (savaş, kıtlık) yatırımcı bekler. Tarihsel olarak da makul.
- Kullanıcının önerisiyle birleşebilir. "3 değerlendirmenin 3'ü de" giriş tetiğinin uygulanma biçimi olur (evidence accumulation); bant da çıkışı sönümler.
- Gemi piyasası (S-020) ileride gelince batık maliyetin kendisi olur. O zaman bant sabit bir κ yerine gemi fiyatından kendiliğinden doğar.

## Oyun için çıkarımlar

1. Kullanıcının önerisi literatürde iyi temellenmiş: real options (ekonomi), evidence accumulation (psikoloji), sefer hazırlığının aylar sürmesi (tarih, ⚠️).
2. Önerilen test (hepsi WTA üstüne):
   - U: kullanıcının 3 × 3 ay kuralı
   - R: real options bandı
   - U + R
3. Oyuncu için okunabilirlik: "Bu liman son 6 aydır kârlı; yatırımcılar ikna oluyor" gibi bir codex / haber metni bu mekanizmayı görünür kılar.
