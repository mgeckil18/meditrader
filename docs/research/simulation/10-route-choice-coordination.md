# 10 — Rota Seçimi ve Kalabalık: Herkes Aynı En Kârlı İşi Seçemez
> Durum: taslak
> Son güncelleme: 2026-10-26
> İlgili: [D5b3d](../../experiments/D5b3d.md) bulgu 5, S-018, [07-expectation-formation](07-expectation-formation.md), [expectation-tournament](../../design/expectation-tournament.md), framework A15

**Soru (kullanıcı, 2026-10-26):** Tüccarlar en kârlı işi seçiyor, hepsi aynı işe yığılıyor ("A Beautiful Mind"daki bar sahnesi). Dağılım gerekiyor. Kullanıcının önerileri:
1. Tüccar ağı yönlendirmesi (kullanıcı: "game theoretic olarak incelenirse hiçbir etkisinin olmaması lazım")
2. Tüccar hesaplarına noise
3. Tüccarların bir kısmı limana bağlı: yalnızca bazı rotalarda ticaret yapabilen tüccarlar, herkesin Venedik'e biber göndermesini engeller

Mekanizma hem tarihsel hem ekonomik olarak doğru olmalı.

**Teşhis (D5b3d):** Filo %11 küçülse de varıştaki kalabalık (33 talep günü), ambar doluluğu (%9) ve derin zarar (%9) değişmiyor. Sorun sayı değil, seçim kuralı: herkes aynı bilgiyle aynı argmax'ı seçiyor.

## 1. Ekonomi: congestion game

| Kavram | Kaynak | Ne diyor |
|---|---|---|
| **Congestion / market entry game** | Selten & Güth (1982) ⚠️; Wardrop (1952) ⚠️ (trafik) | Bir seçeneğin getirisi onu seçenlerin sayısıyla düşer. Simetrik Nash dengesi karma stratejidir: herkes rastgele seçer ve beklenen getiriler seçenekler arasında eşitlenir. Saf "herkes en iyisini seçer" bir denge değildir |
| **El Farol bar problemi** | Arthur (1994), *AER* 84(2), 406-411 | Tümdengelim çöker, çünkü herkes ötekilerin ne yapacağını tahmin etmek zorunda. Ajanlar farklı tahmin kuralları kullanır ve başarısız olanı bırakır. Bireysel inançlar hiç durulmaz, ama toplam katılım kapasite civarında bir dengeye yakınsar. **Kalabalığı dağıtan, tahmin kurallarının çeşitliliğidir** |
| **Laboratuvarda market entry oyunları** | Kahneman (1988) "magic" ⚠️; Kirman, Laisney & Pezanis-Christou (2018); Fischbacher & Thöni (2008) | Katılımcılar iletişim olmadan bile toplamda karma dengeye yakın davranıyor ("magic"). Sapmalar quantal response ya da öğrenmeyle açıklanıyor; küçük kapasitede fazla giriş |
| **Quantal response equilibrium (QRE)** | McKelvey & Palfrey (1995), *GEB* 10(1) | Seçim olasılığı beklenen getiriyle artar ama kesin değildir (logit). λ = 0'da rastgele, λ → ∞'da Nash. Logit QRE en yaygın sürüm |
| **Random utility (rastgele fayda)** | McFadden (1974) ⚠️ | Logit'teki "gürültü" keyfî değildir: dışarıdan gözlenmeyen kişisel faktörlerdir (özel bilgi, ilişki, tercih) |
| **Correlated equilibrium** | Aumann (1974) ⚠️ | Bir koordinasyon aracı (öneri, sinyal) congestion oyunlarında Nash'ten daha iyi sonuç verebilir. Yani ağ yönlendirmesinin etkisi sıfır olmak zorunda değil |
| **Roy modeli / karşılaştırmalı üstünlük** | Roy (1951) ⚠️ | Maliyetleri ve becerileri farklı ajanlar kendiliğinden farklı işlere ayrışır. Herkesin argmax'ı farklı olur |

Not: Filmdeki bar sahnesindeki çözüm ("kimse sarışına gitmesin") aslında bir Nash dengesi değil, çünkü herkes sapmak ister. Doğru kavram karma denge ya da congestion game. Genel bilgi, kaynak gerekmez.

## 2. Tarih: 16. yy tüccarları nasıl dağılıyordu?

| Mekanizma | Ne | Kaynak |
|---|---|---|
| **Ağ ve uzmanlaşma** | Tüccarlar muhabirleri ve vekilleri olan limanlarda ticaret yapardı. Ağ kurmak zaman, güven ve akrabalık isterdi. Sefarad tüccarları vekillerini kendi diasporalarından seçerdi (ama güven otomatik değildi) | Trivellato, *The Familiarity of Strangers* (Livorno-Halep, 1706-1746) |
| **Şubeli ticaret evleri** | Datini şirketi her şubesi ayrı bir şirket olan bir holding gibiydi (Pisa, Cenova, Avignon, Barselona, Valensiya, Mallorca). Koordinasyon mektupla yapılırdı: ~300 şehir arasında 143.000 mektup. Şubesi olmayan yerde (Mağrip) vekil kullanılırdı | Encyclopedia.com "Datini"; Florence Univ.; Michienzi, *Datini, Majorque et le Maghreb* |
| **Gemi türü ve yerel taşıyıcılar** | Kısa kıyı rotalarında küçük gemiler (kabotaj), uzun rotalarda büyük gemiler. Rota, gemi türüne göre ayrışırdı | ⚠️ genel tarih yazımı |
| **Devletin hat takvimi** | Muda: her hatta sınırlı sayıda kadırga, sabit takvim | Stöckly (1995); bkz. [09](09-market-structure-entry.md) |
| **Komisyon** | Ağın dışındaki limanda yerel bir komisyoncu kullanılır, ücret ödenir | ⚠️ oranlar bu oturumda bulunamadı |

## 3. Motorumuzda bugün ne var (`sim/world5.py` `_rivals`, 2026-10-26 kontrolü)

Tüccarlar rakip yüklemeleri zaten kısmen hesaba katıyor, ama:
- **Seviye 0 rakipleri hiç saymıyor** (`crowd = 0`). Seviye 1 bildiği yükün tamamını, seviye 2 yarısını sayıyor.
- **Imitation bonus:** kalabalık bir rotaya ek çekim (`imitation · 0.10 · known/depth`) veriyor. Bu herding'i kendisi üretiyor (D5 mirası).
- **Yalnızca geçmişi görüyor:** bilinen yüklemeler, yani zaten yola çıkmış olanlar. Kendisinden sonra aynı karara varacak tüccarları öngörmüyor. El Farol'daki asıl sorun budur: herkes "şu an boş" görüp aynı anda gidiyor.

Bu yüzden yeni bir mekanizmadan önce bu üç noktanın kalabalığa katkısı ölçülmeli (ablation).

## Oyun için çıkarımlar

1. **Kullanıcının başlangıç teşhisi doğru:** Saf argmax, congestion oyununda denge değildir. Literatürde bilinen sonuç (karma denge; Arthur 1994). Simülasyon bunu yeniden üretiyor (D5b3d: kalabalık filodan bağımsız).
2. **Noise (öneri 2) doğru biçimde: logit seçim (QRE / random utility).** Gürültü, gözlenmeyen kişisel faktör olarak yorumlanır. Ekonomik dayanağı var ve laboratuvar verisine uyuyor. Kesinlik (λ) bilgi düzeyine bağlanabilir.
3. **Limana bağlılık (öneri 3) doğru biçimde: ağ ve uzmanlaşma, yumuşak maliyetle.**
   - Her tüccarın bildiği limanlar var (ana liman + muhabirleri). Orada bilgisi taze, işlem maliyeti düşük.
   - Ağın dışında komisyoncuya ücret öder, bilgisi bayattır. Ağ zamanla, deneyimle genişler.
   - Bu, sert bir yasaktan daha tarihsel ve istismara daha dayanıklı. Roy mantığıyla herkesin argmax'ını farklılaştırır.
4. **Ağ yönlendirmesi (öneri 1):** Bağımsız tüccarlar arasında yalnızca bilgi paylaşımıysa etkisi sınırlı, ama sıfır değil (correlated equilibrium). Asıl etkili biçimi **şubeli ticaret evi**: birkaç gemiye sahip bir ev kendi gemilerini aynı rotaya yığmaz, çünkü kalabalığın bedelini kendisi öder. Tarihsel (Datini), ama yeni bir varlık (firma) ister; sonraya.
5. **Önce mevcut kaynakları ölç:** seviye 0'ın kör olması, imitation bonus ve yalnızca geçmişi görmek (§3). Bunlar kendi motorumuza ait; literatürden değil.
6. **Tahmin kuralı çeşitliliği (D5b4):** El Farol'un dersi. Beklenti turnuvası bu teşhisle birlikte yürümeli. Ölçütler: kalabalık, derin zarar, rotalar arası getiri eşitlenmesi.

**Kullanıcı değerlendirmesi (K-026):** Rakipler arası bilgi paylaşımı reddedildi (bedava bilgi yok, bilgi satışı yok). Gürültü yalnızca son çare. Muhabir ağı ve çok gemili ev uygulanacak. Plan: [D5b3e](../../experiments/D5b3e.md).
