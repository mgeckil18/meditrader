# 06 — Doğrulama, Ayar ve Belgeleme
> Durum: taslak (derin araştırma, 2. tur)
> Son güncelleme: 2026-10-22
> İlgili: [determinizm](../../design/determinism.md), [00-sentez](00-synthesis.md), K-009, K-010

"Simülasyon canlı mı?" sorusunu nasıl cevaplarız? Bu doküman, ilk turdaki metrik listesini ([economy-simulation-techniques §7](economy-simulation-techniques.md)) akademik yöntemlerle genişletiyor.

---

## 1. Neden önemli?

Ajan modelleri kaotiktir: Doran & Parberry modellerinde başlangıç koşullarına kaotik duyarlılık buldu. Tek bir çalıştırmaya bakıp "çalışıyor" demek yanıltıcıdır. Simpson'ın "Hacker Yasası"nı da unutmayalım: istismarlar düzeltmelerden hızlı bulunur. Yani **sistematik test** şart. Determinizm (K-010) bunun ön koşulu.

## 2. ODD protokolü: modeli belgelemek

**ODD (Overview, Design concepts, Details):** Ajan modellerini standart bir biçimde tanımlamak için 2006'da önerildi, 2010 ve 2020'de güncellendi. ([UFZ](https://www.ufz.de/index.php?en=40429), [USGS 2020](https://www.usgs.gov/publications/odd-protocol-describing-agent-based-and-other-simulation-models-a-second-update)) Ana bölümler (literatürden genel bilgi):
1. **Genel bakış:** Amaç, varlıklar ve durum değişkenleri, ölçekler, süreç özeti ve zamanlama.
2. **Tasarım kavramları:** Ortaya çıkış, uyum, hedefler, öğrenme, tahmin, algı, etkileşim, rastgelelik, kolektifler, gözlem.
3. **Ayrıntılar:** Başlatma, girdi verileri, alt modeller.

2020 güncellemesine göre ODD belgelerinde modelin amaca uygunluğunun nasıl değerlendirileceği bölümü eksik kalabiliyor.

**Bizim için öneri:** Simülasyon tasarım dokümanımızı (`docs/design/simulation-spec.md`, henüz yazılmadı) **ODD yapısında** yazalım. Faydaları:
- Akademik olarak tanınmış bir şablon; ileride yatırımcıya veya ekibe "ciddi" görünür.
- "Tasarım kavramları" listesi unuttuğumuz bir şeyi hatırlatır (algı nedir? ajan neyi görebilir?).
- Kod yazmadan önce her şeyin tanımlanmasını zorlar.

## 3. Desen odaklı modelleme (POM, Grimm vd. 2005)

Fikir (literatürden genel bilgi ⚠️): Model **tek bir sayıyı değil, birden fazla desenı aynı anda** yeniden üretebilmeli. Her desen tek başına zayıf bir test; birlikte güçlü bir test.

**Bizim için desen hedefleri (taslak):**

| # | Desen | Kaynak | Test |
|---|---|---|---|
| P1 | Hasat şokuna dışbükey fiyat tepkisi | King-Davenant (01 §2) | Hasat -%30 → tahıl fiyatı ~2-3 kat |
| P2 | Uzun sakin dönemler + ani sıçramalar | Deaton-Laroque (01 §4) | Fiyat değişim dağılımı kalın kuyruklu ve çarpık |
| P3 | Mevsimsellik | Seyir mevsimi, hasat | Kışın Levant malları pahalı, hasat sonrası tahıl ucuz |
| P4 | Kalıcı ama sınırlı limanlar arası fiyat farkı | Tek fiyat yasası + c (01 §3) | Fark çoğunlukla ±c bandı içinde, şoklarda dışında |
| P5 | Aynı limanda dealer'lar arası fiyat dağınıklığı | Kirman (03 §4) | Dağınıklık > 0 ama küçük |
| P6 | Sadakat ortaya çıkışı | Kirman | Ajanların bir kısmı tekrarlayan ortaklar edinir |
| P7 | Merkez limanların oluşumu | EVE, tarih | İşlem hacmi Venedik, İstanbul ve İskenderiye'de yoğunlaşır |
| P8 | Şoktan toparlanma | Doran-Parberry | Savaş veya kıtlık sonrası fiyatlar makul sürede yeni dengeye oturur |
| P9 | Arbitraj fırsatlarının ömrü | Bannerlord dersi | Fırsatlar ne anında kapanır ne sonsuza dek kalır |
| P10 | Kontrollü para arzı | UO dersi, fiyat devrimi | Yavaş ve tarihsel enflasyon; patlama yok |
| P11 | Servet dağılımı | Sugarscape | Eşitsizlik var ama tek bir ajan her şeyi yutmuyor |
| P12 | İflas ve yenilenme | Doran-Parberry | Sürekli ama düşük bir iflas oranı; meslek dağılımı uyum sağlıyor |

## 4. Kalibrasyon ve duyarlılık analizi

**Kalibrasyon:** Parametreleri desenleri yakalayacak şekilde ayarlamak.
- Literatürde ajan modelleri için kabul görmüş tek bir protokol yok. ([IIASA 2022](https://pure.iiasa.ac.at/id/eprint/18410/1/1-s2.0-S1364815222002596-main.pdf), [arXiv 2107.03619](https://arxiv.org/pdf/2107.03619))
- Bizim yaklaşımımız pratik olabilir: her desen için bir test fonksiyonu yazılır, parametre uzayı taranır, tüm testleri geçen bölge bulunur.

**Duyarlılık analizi:** Hangi parametre sonucu ne kadar etkiliyor?
- Önemli bir parametre küçük bir değişiklikle sistemi bozuyorsa, o parametre ya sabitlenmeli ya da oyuncuya görünür bir anlamı olmalı.
- **Ayar düğmeleri** (oyun zorluk seviyesi için): öğrenme hızı ve seçim yoğunluğu (β), bilgi yayılım hızı, şok sıklığı, NPC sayısı ve sermayesi.

**Çoklu seed:** Her test N farklı seed ile çalıştırılır (örneğin 100). Sonuçlar dağılım olarak raporlanır: ortalama, yüzdelikler, en kötü durum. Tek seed'e güvenilmez.

## 5. "Teorik denge" ile karşılaştırma

- Tam bilgiyle, gecikmesiz bir dünyada mekânsal fiyat dengesi Takayama-Judge tarzı bir optimizasyonla hesaplanabilir (bkz. 05 §3).
- Simülasyonumuz bilgi gecikmesi **sıfırlandığında** bu dengeye yaklaşmalı. Bu, ekonomi motorunun doğru çalıştığının testi.
- Gecikme açıldığında dengeden **ne kadar ve nasıl** uzaklaştığı, oyuncu için fırsatın ölçüsü. Bu sapma bir tasarım parametresi olur.

## 6. İstismar testi: "bot oyuncu"

Simpson'ın Hacker Yasası'na karşı:
- **Açgözlü bot:** Her an görünen en kârlı işlemi yapar.
- **Döngü botu:** Tek bir rotayı sonsuza kadar tekrarlar (Elite rota çiftçiliği).
- **Senet botu:** Tüm parayı senede koyup bekler (S-005).
- **Manipülatör bot:** Bir malı köşeleyip fiyatı şişirir.
- **Sigorta dolandırıcısı bot** (K-012).

Her bot simülasyonda bir oyuncu gibi çalıştırılır ve getirisi ölçülür. **Basit bir stratejinin getirisi düşünen oyuncununkine yakınsa, bir tasarım sorunu vardır.** Bu testler simülasyon geliştirmenin her aşamasında tekrarlanmalı.

## 7. Okunabilirlik testi

Space Rangers 1→2 ve Dwarf Fortress dersi: Sistem doğru çalışsa bile oyuncu **anlayamıyorsa** başarısızdır.
- Her fiyat hareketi için bir "neden" kaydı tutulmalı ("Ragusa'da tahıl +%40: Apulia hasadı kötü, 3 gemi korsanlara kayıp"). Bu hem hata ayıklama aracı hem de oyuncu için haber ve söylenti kaynağı.
- X4 dersi: Ajan kararları **izlenebilir** olmalı ("bu tüccar neden İskenderiye'ye gitti?").

## 8. Önerilen doğrulama düzeni (ileride kod yazarken)

```
sim_test/
  scenarios/      # başlangıç durumları (1560 Adriyatik-Levant, hasat şoku, savaş...)
  patterns/       # P1...P12 test fonksiyonları
  bots/           # istismar botları
  sweep.py        # parametre taraması × N seed
  report.py       # grafikler ve özet tablolar
```
Her simülasyon değişikliğinden sonra desen ve bot testleri çalıştırılır ve bir rapor üretilir. Bu, ekonominin "regresyon testi".
