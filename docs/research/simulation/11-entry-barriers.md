# 11 — Sermaye Dışındaki Giriş Bariyerleri
> Durum: taslak (tartışma açık)
> Son güncelleme: 2026-10-27
> İlgili: [09-market-structure-entry](09-market-structure-entry.md), [10-route-choice-coordination](10-route-choice-coordination.md), [D5b3e](../../experiments/D5b3e.md) tam harita, S-012, S-020

**Soru (kullanıcı, 2026-10-27):** Büyük harita + giriş bariyeri denenmeli. Tarihte sermaye dışında hangi bariyerler vardı, koda nasıl uygulanır?

**Bağlam (D5b3e.5):** 45 pazarda rotalar kendiliğinden dağılıyor, ama filo 3 kat ve toplam getiri ~%0 (hedef ~%8, S-012).

## 1. Ekonomi: bariyerin türü sonucu belirler

| Bariyer türü | Dengede ne yapar | Kaynak |
|---|---|---|
| **A. Herkese eşit sabit / batık maliyet** (donatım, ruhsat ücreti) | Filoyu küçültür, brüt marjı yükseltir. Ama bariyer dahil yatırılan sermayenin getirisi yine sermaye maliyetine iner: **rant yaratmaz**. Asıl etkisi histerezis: giriş ve çıkış eşikleri ayrılır, aşırı giriş-çıkış (overshoot) azalır | Standart; Dixit (1989), *JPE* 97(3) ⚠️ |
| **B. Ajanlar arası maliyet farkı** (uyruğa göre gümrük, ağ içi/dışı komisyon, deneyim) | Marjinal giren sermaye maliyetinde kalır; düşük maliyetli eskiler inframarjinal rant kazanır. Toplam getiri hedefin üstüne çıkabilir | Ricardo rantı; Roy (1951) ⚠️ |
| **C. Miktar sınırı** (ruhsat sayısı, muda kadırgası, fondaco yeri, simsar sayısı) | Kapasite sınırlanır; rant, hakkı tutana ya da açık artırmayla devlete gider | Standart; bkz. 09 (incanto) |
| **D. Zamanla aşılan bariyer** (ağ kurmak, rota bilgisi, itibar) | B'nin dinamik hali: yeni giren ilk yıllarda dezavantajlı, eskiler korunur | Greif (1993), *AER* 83(3) (Maghribi koalisyonu) ⚠️ |
| **E. Sonlu, heterojen girişimci arzı** (her limanda belli sayıda aday, farklı servet ve risk tutumu) | Giriş arzı esnek değil. Filo büyüdükçe marjinal aday daha riskten kaçınan olur, getiri yükselir | Kihlstrom & Laffont (1979); bkz. 09 çıkarım 3 |

**Ana nokta:** Yalnızca A türü bir bariyer uzun dönemde getiriyi yükseltmez. Getiriyi yükselten B, C, D ya da E'dir.

## 2. Tarih: 16. yy Akdeniz (bu oturumda yeniden doğrulanmadı ⚠️)

| Bariyer | Örnek | Tür | Kaynak |
|---|---|---|---|
| Vatandaşlık / statü | Venedik *de intus et extra*: uzun ikamet şartı; yabancı daha yüksek gümrük öder | B (+ D: statü yıllar alır) | 09'daki kaynaklar |
| Ahidname ve uyruğa göre gümrük | Osmanlı'da gümrük oranı uyruğa ve ahidnameye göre değişir; yabancı tüccar konsolosa bağlıdır | B | ⚠️ genel tarih yazımı (İnalcık) |
| Zorunlu mekân ve simsar | Fondaco dei Tedeschi: Alman tüccar orada kalır, ruhsatlı simsar (sensale) aracılığıyla satar | B + C | ⚠️ genel tarih yazımı |
| Ayrıcalıklı hat | Muda + incanto (Venedik devlet kadırgaları) | C | Stöckly (1995) |
| Yasak / ruhsatlı mal | Osmanlı'da hububat, silah, at gibi mallar için ihraç yasağı ya da izin; Tolfa şapı (papalık tekeli) | C | ⚠️ |
| Ağ ve güven | Yabancı limanda fattore ya da muhabir; güven, aile ve diaspora üzerinden kurulur | D | Trivellato; Greif ⚠️ |
| Aile ortaklığı | Venedik'te *fraterna*: aile sermayesi ve adı | D + E | Lane (1944) ⚠️ |
| Gemi ve mürettebat kıtlığı | Gemi yapımı zaman alır, kereste kıt; denizci bulmak zor; kış mevsiminde sefer olmaz | A (+ C kısa dönemde) | ⚠️ genel |
| Savaş ve korsanlık | 1537-40 ve 1570-73 Osmanlı-Venedik savaşları, ambargo; korsan riski | Risk primi | ⚠️ |

## 3. Bizim motorda bugün ne var

- **Giriş anonim bir yatırımcı havuzunun kararı.** Havuz büyük (`pool_mult` = 6 × gereken filo). Giriş arzı neredeyse tam esnek, yani E türü bariyer yok.
- **A:** donatım gecikmesi var (30-60 gün), batık maliyet yok.
- **B:** komisyon var (E2), ama küçük (hacmin %1,3'ü). Uyruk farkı yok.
- **C:** yok. **D:** ağ öğrenme var (E2), itibar ve colleganza var (D5b3b).
- **Doğrulanmamış:** 3 × 3'te getiri %17,5 iken aynı giriş kuralı 45 pazarda %0 veriyor. Neden belli değil. Adaylar: (i) kamu getirisi sinyali büyük haritada iyimser; (ii) havuz gereken filoyla ölçekleniyor; (iii) batma bedeli (filo başına bir oran) yeterli değil.

## 4. Fırsat maliyeti neden yığılmayı durdurmuyor? (kullanıcı sorusu, 2026-10-27)

**Kullanıcı:** Herkes aynı limana aynı malı getirirse fiyat düşer. Gemi ya başka limana gider ya da ucuza depocuya satar. Bu fırsat maliyeti yığılmayı engellemeliydi.

**Motorda bu mekanizma var:**
- Varışta fiyat etkisi.
- Reroute (`_merchant_sell`, `_after_kapan`).
- Depocuya toptan satış (`_kapan`).
- Büyük haritada rotaların kendiliğinden dağılmasını (ilk 5 payı 0,17) bu sağlıyor.

**Ama iki ayrı karar var:**
1. **Hangi rota?** Fırsat maliyeti burada çalışır: kalabalık rotanın getirisi düşer, gemiler başka rotaya kayar. Sonuç: rotalar arası getiri eşitlenir.
2. **Tüccar olmak mı, senet mi?** Bütün rotalar birlikte kötüleşince gidecek daha iyi bir rota yoktur. Tek alternatif senettir (%4). Bu karar giriş-çıkış kuralında verilir. Rota düzeyindeki fırsat maliyeti bunu sınırlamaz.

**Veri (F, 10 seed medyanı, 10 yıl):**

| Ölçüt | Değer |
|---|---|
| Filo | 214 → 228 (başlangıç filosu spinup'tan, yani giriş kuralının kendi dengesi) |
| Giriş / çıkış / iflas | 293 / 200 / 85 |
| Gerçekleşen sicil (track) | %2,9 |

Gerçekleşen getiri senedin altında olduğu halde yılda ~29 gemi giriyor ve filo küçülmüyor.

**Aday neden (Claude, doğrulanmadı): optimizer's curse seçenek sayısıyla büyür** (Smith & Winkler 2006).
- Giriş inancı = sicil + limanın "şu anki en iyi fırsatı".
- En iyi fırsat 9 seçenekten değil ~40 seçenekten seçildiğinde daha yukarı yanlıdır.
- Aynı yanlılık kalanların "önümde fırsat var" deyip çıkmamasını da besliyor olabilir.
- 3 × 3'te aynı kuralın %17,5, 45 pazarda %0 vermesini açıklayabilir.
- Test: giriş anındaki inanç ile gerçekleşen getiri, harita boyutuna göre.

## Oyun için çıkarımlar

1. **Önce teşhis, sonra bariyer.** Yeni girenin giriş anındaki beklentisi (`entry_log` belief) ile gerçekleşen getirisi karşılaştırılmalı. Fark büyükse sorun bariyer eksikliği değil, sinyal; bariyer bunu yalnızca gizler.
2. **Yalnızca eşit sabit maliyet (A) eklemek getiriyi kalıcı düzeltmez.** Ama overshoot'u azaltır. Ucuz, ilk deneme olarak ablation'a uygun.
3. **En yapısal aday E + B:** Her limanda sonlu, heterojen aday tüccar (servet, risk tutumu, uyruk ve statü). Statüye göre gümrük ve ağa göre komisyon. Eskiler rant kazanır, yeni giren marjinaldir. Tarihsel ve RPG için doğal (oyuncu da bu adaylardan biri).
4. **C (ruhsat, muda, yasak mal) temel denge için değil, içerik katmanı olarak.** Bu katmanda oyuncu açık artırmaya girer ve ayrıcalık kazanır. Rant devlete ya da hak sahibine gider.
5. **Risk:** Sonradan zamanla aşılan bariyerler (D), oyuncu için "ilk 2 yıl her şey pahalı" hissi yaratabilir. Anlaşılırlık açısından bu, oyunda açıkça gösterilmeli.
