# Deney Stratejisi: D Serisini Neden Yapıyoruz?
> Durum: taslak (kullanıcı sorusu sonrası, 2026-10-23)
> İlgili: [simulation-spec](../design/simulation-spec.md), [06-doğrulama](../research/simulation/06-validation-and-tuning.md), [D1](D1.md), [D1f](D1f.md), [D1g](D1g.md)

## Amaç: parametre değil, yapı

Deneylerin amacı **parametre bulmak değil**, simülasyonun **yapısını** bulmak:
- Hangi ajan türleri var?
- Her ajan neye bakarak karar veriyor?
- Hangi geri besleme döngüleri var ve hangileri tehlikeli?

Parametre ayarı en sona, toplu ve otomatik olarak yapılır (aşağıda §5).

**D1 serisinin kanıtı:** Bulunan her önemli sorun yapısaldı, hiçbiri yanlış bir katsayı değildi:
- Dükkâncının stok/hedef yerine stok/talep oranına bakması
- Kent bütçesi
- Stokçu rolü
- Köylünün önce kendini doyurması ve hasat sonrası nakit ihtiyacı
- PI fiyat kuralı
- Medyan "olağan fiyat"

Hiçbir parametre ayarı bunların eksikliğini telafi edemezdi.

**Öz eleştiri:** D1g'nin sonunda (P, marj ve sermaye taramaları) ince ayara kaydık. Bu aşamada gereksizdi.

## Deneylerden elde edilenler

1. **Mekanizma kararları:** Hangi kural işe yarıyor, hangisi sistemi bozuyor.
2. **Başarısızlık kataloğu:** Mandal, beklenti kovalama, likidite sarmalı, kirlenen hafıza, integral gecikmesi, roket ve tüy. Bunlar ileride oyuncunun da tetikleyebileceği şeyler.
3. **Test altyapısı:** Determinizm, para ve mal muhasebesi, desen metrikleri, ablasyon, çoklu seed. Bu altyapı oyunun ömrü boyunca kullanılacak.
4. **"Yeterince iyi" bir taban:** Üzerine bir sonraki katmanın kurulabileceği kararlı bir model.

## Yöntem: mekanizma yarışması

Kullanıcı önerisi: akademik modelleri yerine koyarak değerlendirmek.

**Değerlendirme:** Doğru yaklaşım, ama bir uyarıyla. Akademik modellerin çoğu bizim tüm sistemimizi değil, **bir parçasını** modelliyor. Genelde tek ve merkezi bir pazar, coğrafya ve bilgi gecikmesi yok. Bu yüzden "bir modeli olduğu gibi alıp çalıştırmak" yerine, simülasyonu **yuvalara** bölüp her yuvaya aday modelleri takarak yarıştırıyoruz.

| Yuva | Aday modeller (literatür) |
|---|---|
| Fiyat oluşumu (liman içi) | Dükkâncı PI kuralı (bizim, D1), Doran-Parberry takas odası, Amihud-Mendelson dealer, Walras el yordamı |
| Tüccar karar kuralı | Açgözlü arbitraj, Doran-Parberry fiyat inancı aralığı, fayda tabanlı yapay zekâ (utility AI), Brock-Hommes strateji değiştirme |
| Beklenti oluşumu | Naif, uyarlamalı, temelci (medyan), Brock-Hommes karışımı |
| Bilgi yayılımı | Anlık ve global (kontrol), fiziksel taşıma, Daley-Kendall söylenti |
| İlişki ve sadakat | Yok (kontrol), Kirman-Vriend pekiştirme |
| Depolama | Deaton-Laroque eşik kuralı, stokçu (bizim, D1f) |

**Yarışma kuralları:**
- Her deney bir yuvaya odaklanır. Diğer yuvalar o anki en iyi aday ile sabitlenir.
- Adaylar **aynı ölçütlerle** karşılaştırılır (§4).
- Parametreler literatürdeki ya da makul varsayılan değerlerde bırakılır. **Ayar yok**, sadece "makul aralıkta kararlı mı?" kontrolü.

## Değerlendirme ölçütleri

| Grup | Ölçüt | Örnek |
|---|---|---|
| **Kararlılık** | Patlama yok, muhasebe tutarlı, determinizm | 0/20 patlama |
| **Tarihsel desenler** (niteliksel) | Doğru yön ve şekil; tam rakam değil | Kıtlıkta dışbükey artış, hasat sonrası ucuzluk, kalıcı ama sınırlı liman farkları |
| **Oyun için kritik** | Fırsatların ömrü, fırsat sayısı, oynaklığın okunabilirliği, istismar botlarının getirisi | Bannerlord sorunu yok |
| **Maliyet** | Hesaplama süresi, kodun karmaşıklığı, izlenebilirlik | 10 yıl < birkaç saniye |

**Dinamik sınıflandırma adımı (Y16):** Beklenmeyen bir dinamik görüldüğünde düzeltmeden önce sınıflandırılır. Fenomen mi (gerçek dünyada görülür, gerçekçi mikro-davranıştan doğar) yoksa artifact mı? Dört ölçüt: mikro-davranış gerçekçiliği, tarihsel büyüklük, yapay sınıra dayanma, oyuncu için okunabilirlik. Fenomenler korunur, artifact'lar düzeltilir. Sınıflandırma [lessons](../process/lessons.md) kataloğuna yazılır.

**Durma kuralı:** Bir aday kararlılık ve desen ölçütlerini **niteliksel olarak** geçiyorsa yeterlidir. Bir sonraki yuvaya geçilir. Sayısal yakınlık (ör. King-Davenant'a %10 uyum) bu aşamanın hedefi değil.

## Parametre ayarı: en sonda, makine öğrenmesiyle

Kullanıcı önerisi: en sonda tüm parametreleri ML ile ayarlamak. **Katılıyorum.** Simülasyon deterministik ve hızlı olduğu için bol veri üretmek kolay. Ajan modellerinin kalibrasyonu için yerleşik yöntemler var:
- Bayesçi optimizasyon
- Vekil (surrogate) modeller
- Yaklaşık Bayesçi hesaplama (ABC)

Literatür ayrıntısı ikinci tur araştırmanın konusu.

**Üç uyarı:**
1. **ML yapıyı düzeltemez.** D1'deki sorunların hiçbiri parametre taramasıyla çözülemezdi. Önce yapı doğru olmalı.
2. **Asıl zor iş hedef fonksiyonunu tanımlamak.** Neyi optimize ediyoruz? Seyrek tarihsel fiyat serileri, stilize desenler ve "oyun hissi" metrikleri birlikte. Bu tanım kullanıcının tarih okumalarına ve oyun tasarımı kararlarına bağlı.
3. **Eğlence veride yok.** Son ayar, oyuncu testleriyle (insan ya da bot) birlikte yapılmalı.

## Gerçekçi ve canlı bir ekonomi için gerekenler

| # | Gereksinim | Durum | Hangi deney |
|---|---|---|---|
| 1 | Liman içi fiyat oluşumu (kararlı, mevsimli, kıtlığa tepkili) | ✅ yeterli | D1 serisi |
| 2 | Limanlar arası taşıma ve arbitraj | ✅ (tek fiyat yasası kendiliğinden çıkıyor) | [D2](D2.md) |
| 3 | **Fırsatların hayatta kalması** (Bannerlord sorunu) | ✅ bilgi gecikmesiyle çözüldü (D2'de ❌) | [D2](D2.md) → [D3](D3.md) |
| 4 | Bilgi gecikmesi ve inanç | ✅ fırsatları canlı tutuyor; bilginin değeri +11-23 puan/yıl | [D3](D3.md) |
| 5 | Çok mal, ortak bütçe, ikame, kent sınıfları | ✅ LES + CES, 3 sınıf | [D4](D4.md), [D4b](D4b.md) |
| 6 | Ajan çeşitliliği, giriş ve çıkış (iflas, yenilenme) | ⏳ | D2-D5 boyunca |
| 7 | Şoklar ve olaylar | kısmen (hasat) | D3-D5 |
| 8 | Kapalı para devresi | ⏳ ertelendi | D4 sonrası |
| 9 | Üretim zincirleri | ✅ ilk zincir (yün → kaba / ince kumaş) | [D4c](D4c.md) |
| 10 | Kurumlar | ⏳ ertelendi | sonra |
| 11 | Ölçeklenebilirlik (6+ liman, yüzlerce ajan) | ⏳ | D5 |
| 12 | Oyuncu açısından: okunabilirlik, istismar direnci | ⏳ | D5 + botlar |

## Yeniden düzenlenmiş yol haritası

| Deney | Soru | Yarışan yuva |
|---|---|---|
| **D2** | İki liman arasında taşıma, fiyat farklarını taşıma maliyetine yaklaştırıyor mu? Fırsatlar kalıcı mı, yoksa NPC'ler hepsini yiyor mu? | Tüccar karar kuralı (açgözlü / Doran-Parberry / fayda tabanlı) |
| **D3** | Bilgi gecikmesi fırsatları canlı tutuyor mu? Salınım (herkes aynı habere koşuyor) patlıyor mu? | Bilgi yayılımı + beklenti oluşumu |
| **D3b** ✅ | Senet getirisine bağlı serbest giriş-çıkış, "baz ticaret = senet + risk" dengesini kendiliğinden üretiyor mu? Tüccar sayısı içsel hale gelince fırsat rejimi nasıl değişiyor? | Tüccar nüfusu dinamiği |
| **D4** | Çok mal ve ortak bütçe: kıtlık lüks malları vuruyor mu? | Talep yapısı |
| **D5** | Tam dilim (6 liman, 8 mal) + istismar botları | Hepsi bir arada; ölçek ve istismar |
| Sonra | Parametre kalibrasyonu (ML) | — |
