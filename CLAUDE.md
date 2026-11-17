# Medi — Çalışma Kuralları

16. yüzyıl Akdeniz'inde geçen tüccar RPG + strateji oyunu. Şu an araştırma ve tasarım aşamasındayız; kod yok.

## Temel kurallar

1. **Her şey markdown dokümanlarında yaşar.** Konuşmada üretilen her kalıcı bilgi (karar, araştırma bulgusu, fikir, açık soru) ilgili dokümana yazılır. Konuşma geçicidir, dokümanlar kalıcıdır.
2. **Ana doküman `docs/INDEX.md`'dir.** Her oturumun başında okunur. Yeni doküman eklendiğinde, taşındığında veya kapsamı değiştiğinde INDEX güncellenir.
3. **Kararlar `docs/decisions.md`'ye numaralı kaydedilir** (K-001, K-002…). Bir karar değişirse eskisi silinmez, "geçersiz — bkz. K-0xx" diye işaretlenir.
4. **Açık sorular `docs/open-questions.md`'de tutulur** (S-001…). Cevaplanınca ilgili karara bağlanıp kapatılır.
4b. **Kesinleşmemiş yönelimler `docs/design/framework.md`'de güven seviyeleriyle tutulur** (İlke / Yön / Aday / Ertelendi). Bir madde güçlenince decisions.md'ye taşınır.
4c. **Kullanıcı yorum dosyaları** (ör. kök dizindeki `yorumlar.md`) okunur, değerlendirilir ve ilgili dokümanlara işlenir. İşlendiği INDEX'te belirtilir; dosyanın kendisi kullanıcıya aittir ve değiştirilmez.
4d. **Süreç kaydı:** Her deney denemesi (başarısız olanlar dahil) `docs/process/experiment-log.md`'ye, her aşama geçişi `docs/process/timeline.md`'ye, her yeni genel ders `docs/process/lessons.md`'ye eklenir.
5. **Araştırma ile tasarım ayrı tutulur.** `docs/research/` = dünyada ne var / tarihte ne olmuş (kaynaklı). `docs/design/` = biz ne yapacağız.
6. **Araştırma dokümanlarında kaynak zorunludur.** Her iddianın yanında kaynak ya da "doğrulanmadı" notu olur. Her araştırma dokümanı "Oyun için çıkarımlar" bölümüyle biter.
7. **Dil:** Dokümanlar Türkçe. **Teknik, ekonomik ve modelleme terimleri çevrilmez, orijinal haliyle kullanılır** (ör. pork cycle, cobweb, herding, survivorship bias, market maker). Gerekirse ilk kullanımda kısa bir Türkçe açıklama eklenir. Tarihsel terimler (muda, colleganza, fattore…) de orijinal haliyle kalır. Hepsi `docs/glossary.md`'ye eklenir.
7b. **Atıf dürüstlüğü:** Literatürde bilinen bir sonuç (ör. giriş engeli → rant, tek fiyat yasası, cobweb, Grossman-Stiglitz) simülasyonda çıktığında "literatürde bilinen X (kaynak); simülasyon bunu yeniden üretti" diye yazılır. "Bulduk / biliyoruz" ifadesi yalnızca modele özgü bulgular (ör. motorumuzdaki bir artifact) için kullanılır.
7c. **Codex:** Simülasyonda ya da tartışmada ortaya çıkan her ekonomik, davranışsal ya da tarihsel kavram `docs/codex/` altına oyuncu metniyle birlikte eklenir (K-015).
7d. **Mekanizmaların kökeni kaydedilir:** Her mekanizmanın kimden geldiği (kullanıcı / Claude / literatürden uyarlama) ve hangi deneyde eklendiği tutulur. Claude'un eklediği mekanizmalar, deneyde çalışsa ve kullanıcı itiraz etmese bile "kesin" değil, "Claude ekledi, deneyle desteklendi" diye işaretlenir. Amaç: ileride her şeyi yeniden inceleyebilmek.
8. **Eleştirel ortaklık:** Claude, fikirleri uygulanabilirlik, istismar edilebilirlik ve anlaşılırlık açısından değerlendirir; gerekirse itiraz eder veya alternatif önerir.

## Doküman başlığı şablonu

Her dokümanın başında:

```
# Başlık
> Durum: taslak | gözden geçirildi | kararlaştı
> Son güncelleme: YYYY-AA-GG
> İlgili: [diğer-doküman](yol.md), K-00x, S-00x
```
