# Determinizm ve Rastgelelik
> Durum: taslak
> Son güncelleme: 2026-10-22
> İlgili: K-010, [decisions](../decisions.md)

## Yanlış anlaşılma: "deterministik = rastgelelik yok" değil

Oyun rastgelelik dolu olacak: gemi batar mı, korsan çıkar mı, hasat iyi mi, veba nerede başlar... Deterministik olan **rastgelelik değil, rastgeleliğin tekrarlanabilirliği**.

Bilgisayarda "rastgele" sayılar aslında sözde-rastgele bir üreteçten (PRNG) gelir. Üreteç bir başlangıç sayısıyla (seed) başlatılır ve o seed'den hep **aynı sayı dizisini** üretir:

```
seed = 42  →  0.73, 0.12, 0.98, 0.45, ...
seed = 42  →  0.73, 0.12, 0.98, 0.45, ...   (her seferinde aynı)
seed = 7   →  0.31, 0.88, 0.05, 0.67, ...   (başka bir dünya)
```

## Örnek

1563 Mart'ında bir gemi Korfu açıklarında ilerliyor. O gün fırtına riski %4.

- Simülasyon üreteçten bir sayı çeker: 0.027.
- 0.027 < 0.04 → fırtına çıkar.

Oyuncu ve NPC'ler için bu tamamen rastgele bir olaydır, sonucu önceden bilemezler. Ama aynı seed ve aynı oyuncu kararlarıyla oyunu baştan oynatırsak, o gün yine 0.027 çekilir ve yine fırtına çıkar.

Oyuncu farklı bir karar verirse (gemiyi bir gün geç yollarsa) zincir değişir ve sonuç da değişir. Yani dünya oyuncunun kararlarına tepki verir. Sadece **aynı girdiler aynı çıktıyı verir.**

## Neden istiyoruz?

1. **Ekonomi dengesini test etmek.** Simülasyonu oyuncusuz 1000 kez farklı seed'lerle çalıştırıp "fiyatlar çöküyor mu, kaotik mi, canlı mı" ölçeceğiz. Bir sorun bulunca aynı seed'le tekrar oynatıp tam olarak nerede bozulduğunu göreceğiz. Determinizm yoksa hatayı bir daha yakalayamayız.
2. **Hata ayıklama.** "37. yılda Ragusa'da tahıl fiyatı negatif oldu" gibi bir hata birebir tekrar üretilebilir.
3. **Kayıt dosyaları ve tekrar izleme (replay).** Kayıt dosyası, başlangıç seed'i ile oyuncu komutlarının listesinden ibaret olabilir.
4. **Kayıt yükleme istismarına karşı (isteğe bağlı).** Üretecin durumu kayıtta saklanırsa, "gemi battı, kaydı yükle, tekrar dene" aynı sonucu verir. Oyuncu ancak farklı bir karar vererek farklı sonuç alır.
5. **İleride çok oyunculu.** Strateji oyunlarında yaygın olan "lockstep" yöntemi buna dayanır: herkes aynı simülasyonu çalıştırır, ağdan sadece komutlar gönderilir.

## Teknik gereksinimler (ileride kod yazarken)

- Tüm rastgelelik **tek bir merkezi üreteç sisteminden** gelir. Dil kütüphanesinin global `random()` fonksiyonu kullanılmaz.
- Alt sistemlere ayrı üreteç akışları verilebilir (hava durumu, korsanlar, pazar...). Böylece birine eklenen yeni bir zar atışı ötekilerin dizisini kaydırmaz.
- Simülasyon gerçek saatten bağımsızdır. Oyun hızı sadece tick'lerin ne sıklıkla çalıştığını değiştirir; tick'in sonucunu değiştirmez.
- İşlem sırası sabittir. Ajanlar her tick'te belirli bir sırayla işlenir; bu sıra gerekiyorsa üreteçle karıştırılır, ama karıştırma da seed'lidir.
- Ondalık sayılara dikkat: farklı makinelerde farklı sonuç verebilirler. Çok oyunculu gelirse sabit noktalı sayılar (fixed-point) veya tamsayı para birimi gerekebilir. Para zaten en küçük birimde tamsayı tutulmalı (ör. soldi / denari).
