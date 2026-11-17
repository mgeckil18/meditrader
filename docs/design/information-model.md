# Bilgi Modeli: Fiyat Bilgisinin Olasılıksal Gösterimi
> Durum: fikir aşaması (kullanıcı önerisi, olumlu değerlendirildi; kesin değil)
> Son güncelleme: 2026-10-22
> İlgili: `yorumlar.md` (yerel dosya, repoda yok), [02 §7](../research/simulation/02-market-mechanisms.md), [00-sentez §4](../research/simulation/00-synthesis.md), [framework](framework.md)

## Fikir (kullanıcıdan)

"Edirne'de buğday kilosu 3 lira" bilgisi bir hafta sonra, 3 liranın etrafında bir olasılık dağılımı olarak (renk tonlarıyla) gösterilir. Bu oyuncu için de tüm ajanlar için de geçerlidir. Farklı tarihlerden gelen iki bilgi birleşerek yeni bir dağılım oluşturur. Zor modda bu gösterim kapanabilir.

## Değerlendirme

**Çok güçlü bir fikir,** çünkü üç şeyi birden yapıyor:
1. **Mekanik:** Ajanların zaten taşıyacağı "inanç aralığı" (02 §7) doğrudan oyuncuya görünür hale geliyor. Oyuncunun gördüğü şey ile NPC'nin karar verdiği şey **aynı veri**. Bu K-004 ile tam uyumlu ve tek bir sistem hem yapay zekâyı hem arayüzü besliyor.
2. **Anlatım:** "Bu bilgi eski" demek yerine eskimeyi **görsel olarak hissettiriyor**. Okunabilirlik hedefine hizmet ediyor.
3. **Zorluk ayarı:** Gösterimi kapatmak, mekaniği değiştirmeden oyunu zorlaştırıyor. Temiz bir zorluk düğmesi.

## Teknik öneriler

### 1. Normal (Gauss) değil, log-normal dağılım *(not: kullanıcıyla mutabık, ama ince ayar sonranın konusu)*
Fiyatlar negatif olamaz ve oransal hareket eder: 3 liralık buğdayın 6 lira olma ihtimali, 0 lira olma ihtimalinden çok daha yüksektir. Bu yüzden belirsizliği **logaritmik ölçekte** tutmak daha doğru.
- Kısa sürede neredeyse simetrik görünür; Gauss sezgisi bozulmaz.
- Uzun sürede yukarı doğru uzun bir kuyruk oluşur, bu da kıtlık riskini doğru yansıtır.

### 2. Belirsizliğin büyümesi
```
σ(yaş) = √( σ_kaynak² + v_mal × yaş )
```
- `v_mal`: malın oynaklığı. Tahılda hasat zamanı yüksek, tuzda düşük.
- `σ_kaynak`: kaynağın güvenilmezliği. Kendi gözün ≈ 0, liman söylentisi yüksek.
- `√yaş`: Belirsizlik zamanla artar ama yavaşlayarak (rastgele yürüyüş).

### 3. İki bilginin birleşmesi
Kullanıcının "iki hafta önceki ve bir hafta önceki bilgi birleşsin" önerisi, istatistikte **hassasiyet ağırlıklı birleştirme** (Kalman filtresinin en basit hali) ile yapılır:
```
Her gözlemi bugüne "ilerlet":   ortalama aynı kalır, σ² yaşla büyür
Hassasiyet:                     w = 1 / σ²
Birleşik ortalama:              μ = (w1·μ1 + w2·μ2) / (w1 + w2)
Birleşik belirsizlik:           σ² = 1 / (w1 + w2)
```
- Yeni ve güvenilir bilgi ağır basar, eski bilgi az katkı yapar.
- İki bilgi birbirini doğrularsa belirsizlik **daralır**.
- **Dikkat:** İki eski bilgi tek bir taze bilgiyi asla yenemez. Aynı fiyat 14 gün önce ve 7 gün önce 3 lira idiyse, bugünkü fiyat hakkında 7 günlük bilgiden çok az daha fazla şey biliriz. Bunun nedeni, iki gözlemin aynı "geçmiş yürüyüşü" paylaşması: tam bağımsız değiller. İlk sürümde basitçe "en yeni bilgi + kaynak güvenilirliği" ile başlamak da yeterli olabilir; birleştirmeyi asıl farklı kaynaklar için (temsilci raporu + liman söylentisi) kullanırız.

### 4. Haberler ortalamayı da kaydırır
Sadece genişleme yetmez. "Apulia'da kötü hasat" haberi Ragusa'daki tahıl inancının **ortalamasını yukarı kaydırır**, fiyat gözlemi gelmemiş olsa bile. Bu, olay haberlerinin fiyat inancına çevrilmesi demek; ajanın "yorumlama" yeteneği kişiliğe ve deneyime bağlı olabilir.

### 5. Gösterim seçenekleri

| Mod | Gösterim |
|---|---|
| Kolay | Renk tonlu bant + "muhtemelen 2.6-3.5 lira" metni + bilgi yaşı |
| Normal | Renk tonlu bant + bilgi yaşı |
| Zor | Sadece ham bilgi: "3 lira — 7 gün önce, Edirne'den gelen kervancı" |

Metin tabanlı aşamada bant şöyle görünebilir:
```
Edirne · buğday   ░▒▓█▓▒░░      ~3.0 lira  (7 gün, kervancı)
İstanbul · buğday     ▒█▒       ~3.4 lira  (1 gün, kendi gözün)
```

### 6. Okunabilirlik riski
Haritada her liman × her mal için bir dağılım göstermek görsel gürültü yaratır. Öneri: Varsayılan görünümde sadece **ilgilenilen mallar** ve **seçili limanlar** gösterilir, ayrıntı talep üzerine açılır.

## Deney sonucu (D3)

Bu modelin "dağılım + olağan fiyata dönüş" hali [D3](../experiments/D3.md)'te test edildi ve yarışan beklenti kuralları arasında en iyi sonucu verdi: sürü salınımını sönümledi, kıtlığı ve iflasları azalttı, fırsatları canlı tuttu.

## Açık kalanlar
- Ajanlar bu dağılımı kararlarında nasıl kullanacak? (Risk iştahına göre dağılımın hangi yüzdeliğini esas alacakları; örneğin temkinli ajan %20'liği, cesur ajan ortalamayı.)
- Zorluk moduna göre ajanların bilgisine gürültü eklemek (kullanıcı fikri) bu modelin doğal uzantısı: bkz. [framework](framework.md) §3.
