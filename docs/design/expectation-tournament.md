# Beklenti Turnuvası (D5b4 tasarımı)
> Durum: taslak (uygulanmadı; taban = D5b3 OS)
> Son güncelleme: 2026-10-26
> İlgili: S-014, [07-expectation-formation](../research/simulation/07-expectation-formation.md), framework A10, [D5b2](../experiments/D5b2.md), [D5b3](../experiments/D5b3.md), [mechanism-registry](mechanism-registry.md)

**Kullanıcı yönü (2026-10-26):** Farklı tüccar havuzlarında farklı beklenti modelleri (ve kombinasyonları) uygulansın, simüle edilsin, sonuçlar değerlendirilsin. Bu, experiment-approach'taki "her yuva için akademik modeller yarışır" ilkesinin beklenti yuvasındaki uygulaması.

**Soru:**
1. Hangi beklenti modeli (ya da karışımı) piyasayı tarihsel olarak makul tutuyor? Ölçütler: ithalat ihtiyacı karşılıyor mu, kıtlık ve glut ne sıklıkta, fiyat salınımı ne kadar.
2. Hangi model sahibine kazandırıyor?
3. Kullanıcının ilkesi tutuyor mu: piyasa teknik analize göre çalışmıyor mu?

## Yarışan kurallar

Her kural, tüccarın hedef pazardaki fiyat beklentisini, varış günü için verir (h = bilginin yaşı + yol süresi).

| Kod | Kural | Formül (kaba) | Kaynak | Bizde |
|---|---|---|---|---|
| **NV** | Naive | E = son gözlem | Ezekiel (1938) | Yok (düzey 0 en yakını) |
| **AA** | Çapalama ve ayarlama (bugünkü C4) | log E = log m + (log p − log m) e^(−h/τ); m = son 20 gözlemin medyanı | Tversky & Kahneman (1974) | Var (C4) |
| **AD** | Adaptive | E ← E + λ(p − E), gözlem geldikçe | Cagan (1956); Nerlove (1958) | Yeni |
| **TR** | Trend (extrapolative) | E = p × (p / p_önceki)^(g × h / Δt) | Metzler (1941); Greenwood & Shleifer (2014) ⚠️ | Yeni |
| **FD** | Bilgi temelli temel (S-014 önerisi) | Hedefte bilinen arz günleri D = (limanda bekleyen + yoldaki bilinen kargo + bilinen stokçu stoğu) / günlük talep; E = m × (D / D*)^(−1/ε) | King-Davenant; tüccar mektupları | Yeni (D5b2-B'nin "temel"i bu değildi) |
| **HSM** | Kural değiştirme | Kurallar AA, AD, TR, FD; ağırlık ∝ exp(β × başarı); başarı = −(log tahmin hatası)², üstel ortalama | Anufriev & Hommes (2012); Brock & Hommes (1997) | Yeni |

Notlar:
- D* (olağan arz günü) ve ε (talep esnekliği) tüccarın bildiği "olağan" değerlerdir. D*, tüccarın kendi deneyiminin medyanı olabilir (learning from experience).
- FD'nin bilgisi tüccarın bildiği kadardır: gemi ve söylentiyle gelir, bayattır. Böylece FD de bilgi yapısına bağlıdır.
- Kendi kargosunun fiyat etkisi (B-imp, D5b2) bütün kurallarda ortak kalır; kural yalnızca fiyat beklentisini değiştirir.
- HSM başarısı her yeni gözlemde güncellenir. Her kural, bir önceki bilgiyle bugünkü fiyatı tahmin etmişti; hata bu tahminle gözlenen fiyat arasındadır.

## Kurulumlar (ilk tur)

Her biri D5b3'ün sonuç yapısının üstünde (GBSL·imp + D5b3 girişi, sonuca göre).

| Kurulum | Tüccar havuzu |
|---|---|
| AA (taban) | Herkes C4 |
| NV, AD, TR, FD | Herkes tek bir kural |
| AA+TR | Yarı yarıya |
| FD+TR | Yarı yarıya (Brock-Hommes klasiği) |
| HSM | Herkes HSM, başlangıç ağırlıkları eşit |
| HSM-karışık | Herkes HSM, başlangıç ağırlıkları kişiden kişiye farklı (Dirichlet) |

İkinci tur (birinci turun sonucuna göre): β (değiştirme yoğunluğu) taraması; diagnostic expectations; learning from experience.

## Ölçütler

- **Piyasa:**
  - İthalat / ihtiyaç; kıtlık (`dearth`) ve glut sıklığı.
  - Fiyat salınımı: log fiyat değişiminin standart sapması, otokorelasyon.
  - Arbitraj farkı / maliyet.
- **Kural başarısı:**
  - Kurala göre tüccar getirisi.
  - Tahmin hatası (yanlılık ve ortalama karesel hata).
  - D5b3.2'deki gibi sefer bazında beklenen ve gerçekleşen kıyası.
- **HSM:**
  - Kural paylarının zamanla seyri.
  - **Doğrulama testi:** tüccar piyasasında TR'nin payı sönmeli (negatif geri besleme; Hommes 2011). Sönmüyorsa motorda pozitif geri besleme sızıntısı var.
- **Pozitif geri besleme kanalı:** Stokçu da kural kullanırsa (ikinci tur) istifçilik dalgası çıkıyor mu?

## Beklenen sonuç (literatüre göre, test edilecek)

- Tüccar ticareti negatif geri beslemeli. Heemeijer ve ark. (2009) ve Bao ve ark. (2012) deneylerinde bu tür piyasalar dengeye hızla yakınsıyor.
  - Bu yüzden TR'li kurulumlar daha salınımlı olmalı, ama TR'li tüccarlar kaybetmeli.
  - HSM'de TR'nin payı sönmeli.
- Bunlar çıkarsa: "literatürde bilinen sonuç; simülasyon yeniden üretti". Çıkmazsa önce motor teşhisi.

## Köken

- **Fikir:** kullanıcı. Beklenti piyasayı yönetir ama TA yönetmemeli; farklı havuzlarda farklı modeller.
- **Kural listesi ve ölçütler:** Claude, literatürden.
- **FD'nin biçimi:** Claude önerisi (S-014). D5b2'deki başarısız "temel"in yerine.
