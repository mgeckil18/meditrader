# Deney D5b3d: Sefer Bazlı Alacaklı, Öz Sermayede Batma Riski, Gemi Masrafı
> Durum: tamamlandı (2026-10-26)
> Kod: [`sim/world5.py`](../../sim/world5.py) (`record_net_overhead`, `loan_pricing`, `lender_*`, `entry_ruin`, `entry_ruin_weight`, `ship_cost_day`; `_lender_view`, `_lender_quote`, `_ruin_price`, `_own_view`, `_finance`), [`experiments/d5b3d_lender_entry.py`](../../experiments/d5b3d_lender_entry.py); teşhis: [`experiments/d5b3d_return_gap.py`](../../experiments/d5b3d_return_gap.py)
> Yeniden üretmek: `python3 experiments/d5b3d_lender_entry.py 10` (~20 dk); `python3 experiments/d5b3d_return_gap.py OS 4`
> Çıktı: `experiments/out/d5b3d/table_raw.txt`, `summary.json`, `return_gap_OS.json`, `return_gap_Dp.json`
> İlgili: [K-023](../decisions.md), [K-024](../decisions.md), S-015, S-017, S-012, [D5b3c](D5b3c.md), [09](../research/simulation/09-market-structure-entry.md), [mechanism-registry](../design/mechanism-registry.md)

## Soru

Kullanıcı kararları (K-023, K-024). Kullanıcı notu: tasarımlar kesin değil.
1. **Sefer bazlı alacaklı (K-023):** Faiz, alacaklının sefer beklentisinden çıkar. Alacaklı başvuruları ve kamuya açık bilgiyi bilir. Riskli ya da getirisi düşük sefere pahalı borç verir ya da hiç vermez. Faiz, düşük bilgiliye bir sinyaldir.
2. **Öz sermayede batma riski (K-024):** Giriş ve kalma kararı kamuya açık iflas sıklığını tartar. Kullanıcı: "mantıklı ama denemeden bilemeyiz."
3. **Gemi masrafı (K-024):** "Kolayca eklenir ama çözüm olur mu?"
4. **Ölçüm düzeltmesi önce.** Brüt-ömür boyu getiri farkı tekrarlanırsa incelenir.

## Mekanizma

Ayrıntı ve köken: [mechanism-registry § D5b3d](../design/mechanism-registry.md).

## Kurulumlar

Hepsi D5b3c'nin D yapısında (OS + borç, kaldıraç ≤ 1, batma korkulu karar), 10 seed, son 5 yıl.

| Kurulum | Fark |
|---|---|
| D' | D + ölçüm düzeltmesi (yeni taban) |
| V | D' + sefer bazlı alacaklı |
| VR | V + girişte ve kalmada batma bedeli |
| VS | V + gemi masrafı (günde 40 ⚠️, sermayenin yılda ~%6'sı) |
| VRS | V + ikisi |

## Koşu geçmişi

| # | Ne | Sonuç |
|---|---|---|
| 1 | Duman, seed 0 | Mekanizmalar çalışıyor; brüt-ömür boyu getiri farkı yeniden çıktı → teşhis T1 |
| 2 | T1, ilk deneme | 🐞 Python 3.14 `forkserver`: kurulum adı işçilere geçmedi, OS yerine D' koştu (sonuçlar birebir aynı çıkınca fark edildi). Ad argümanla geçirildi |
| 3 | T1, OS ve D' | Aşağıda |
| 4 | Asıl koşu, 5 × 10 seed | Aşağıda |

## Teşhis T1: brüt getiri ile ömür boyu getiri farkı (açıklandı)

4 seed, bütün tüccarlar (hayatta + çıkan + batan).

| Ölçüt | OS | D' |
|---|---|---|
| **Sermaye-yıl ağırlıklı toplam getiri** (Σ kâr / Σ sermaye × yıl) | **%12,8** | **%12,4** |
| Ömür boyu getiri medyanı | −%1,4 | −%0,5 |
| Ömür boyu getiri ortalaması | −%8,2 | −%9,7 |
| Zararlı tüccar payı | %52 | %52 |
| Hayatta kalanlar: toplam / medyan | %26 / %8 | %26 / %11 |
| 1 yıldan kısa yaşayanlar: toplam | −%53 | −%73 |
| En iyi %10'un kâr payı | %58 | %55 |
| Düzey 0 / 1 / 2 toplam getiri | %8 / %2 / %20 | %9 / %4 / %19 |

- **Para kaybı yok.** Brüt tahmin (~%12-16) ile toplam getiri tutarlı.
- Fark ölçütten geliyor. Medyan her kişiye bir oy veriyor. Kısa ömürlü başarısız girişler çok sayıda ve yıllığa çevrilince kayıpları patlıyor.
- **Sonuç:** D5b3, D5b3b ve D5b3c'deki "denge getirisi hedefin (%8) altında" yargısı yanıltıcıydı. Ticarete konan sermaye yılda ~%12-13 kazanıyor, ama kazanç çok çarpık dağılıyor.
- Literatürde bilinen bir benzerlik: girişimcilerin tipik getirisi düşük, getiri dağılımı çok çarpık (private equity premium puzzle; Moskowitz & Vissing-Jørgensen 2002 ⚠️; Hamilton 2000 ⚠️). Simülasyon benzer bir yapı üretti.

## Sonuçlar (10 seed medyanı, son 5 yıl)

### Getiri ve filo

| Kurulum | Toplam getiri (seed aralığı) | Ömür boyu medyan | Zararlı payı | Filo (son 5 yıl) | Giriş | Çıkış | İflas (öz sermaye / borç) |
|---|---|---|---|---|---|---|---|
| D' | %13,2 (10-15) | −%0,6 | %52 | 78 | 165 | 84 | 41 / 18,5 |
| V | %13,6 (8-17) | −%0,5 | %52 | 81 | 157 | 96 | 38 / 5,5 |
| VR | **%17,2** (10-26) | +%1,0 | %49 | **72** | **134** | 72 | 37 / 3 |
| VS | %12,4 (10-16) | −%2,5 | %54 | **71** | 152 | 83 | 43 / 3 |
| VRS | **%17,5** (13-21) | +%0,2 | %50 | **72** | 138 | 71 | 42 / 2,5 |

### Alacaklı

| Kurulum | Borç (5 yıl) | Reddedilen teklif | Borç seçimi | Temerrüt | Tahmini PD | Kalibrasyon | Alacaklı yıllık (seed aralığı) |
|---|---|---|---|---|---|---|---|
| D' | 80 | 0 | %15,6 | %12,7 | — | — | −%1,7 (−66 … +60) |
| V | 25,5 | 2.426 | %4,8 | %8,2 | %8,3 | 1,96 | **+%6,6** (−168 … +76) |
| VR | 21,5 | 2.105 | %4,3 | %6,4 | %8,9 | 1,11 | +%10,8 (−72 … +79) |
| VS | 21 | 2.117 | %4,2 | %9,0 | %7,7 | 1,65 | +%7,5 (−43 … +114) |
| VRS | 20,5 | 2.013 | %4,1 | %2,3 | %8,1 | 1,89 | +%54 (−59 … +115) |

Borç seçimi düzey 0 / 1 / 2: D' %7,9 / %24 / %18; V %2,6 / %10 / %4,9.

### Oynaklık ve kalabalık

| Kurulum | Marj sd | Derin zarar (< −%50) | Zararlı sefer | Kalabalık (talep günü) | Ambar doluluğu | Gemi başına yılda sefer |
|---|---|---|---|---|---|---|
| D' | 0,80 | %9,2 | %40 | 32,7 | %8,8 | 5,9 |
| V | 0,76 | %9,2 | %40 | 33,3 | %8,7 | 5,8 |
| VR | 0,82 | %9,1 | %38 | 32,8 | %9,0 | 6,0 |
| VS | 0,78 | %8,5 | %39 | 33,0 | %9,4 | 6,1 |
| VRS | 0,84 | %8,5 | %38 | 32,4 | %9,7 | 6,1 |

## Bulgular

**1. Sefer bazlı alacaklı borcu güvenli hâle getiriyor, ama borcu da büyük ölçüde kesiyor.**
- Borçtan iflas 18,5'ten 5,5'e, temerrüt %12,7'den %8,2'ye iniyor.
- Alacaklının medyan getirisi +%6,6, yani hedefi senet + %2 = %6 civarında.
- Ama borç seçimi %16'dan %5'e düşüyor ve alacaklı ~2.400 teklifi reddediyor (PD > %25).
- Alacaklının getirisi seed'den seede çok savruluyor, çünkü 5 yılda yalnızca ~25 borç var. Tek tek seed sonuçları istatistik olarak anlamsız.
- VRS'teki +%54, az sayıda borçta aşırı fiyatlamaya işaret ediyor ⚠️. Kalibrasyon ortalaması ~1,9: alacaklının ilk tahmini temerrütü yaklaşık yarı yarıya küçümsüyor ve defterden düzeltiyor.

**2. Alacaklı kalabalığı azaltmıyor.** Kalabalık 33 talep günü, değişmedi. Borçlu seferler bütün seferlerin küçük bir kısmı; sıralı fiyatlama yalnızca onları etkiliyor. Kullanıcının "pahalı borç yalnızca yanlış sefere" fikri borçlu seferlerde çalışıyor, ama piyasa ölçeğinde etkisi yok.

**3. Öz sermayede batma bedeli giriş friction'ı olarak çalışıyor (K-024 hipotezi desteklendi).**
- Giriş 157'den 134'e, filo 81'den 72'ye iniyor. Toplam getiri %13,6'dan %17,2'ye çıkıyor.
- Kamuya açık iflas fiyatı ~%4-5. Literatürde bilinen meslek seçimi mantığı (Kihlstrom & Laffont 1979): risk, son girenin istediği getiriyi yükseltir. Simülasyon yeniden üretti.

**4. Gemi masrafı filoyu küçültüyor, ama getiriyi yükseltmiyor.** Filo 81'den 71'e iniyor; masraf getiriden düşüyor (toplam getiri %12,4). Kullanıcının "çözüm olur mu" sorusunun cevabı: tek başına hayır. Boş kapasiteyi pahalı yapıyor ama kalabalığı değiştirmiyor.

**5. Asıl bulgu: kalabalık filo büyüklüğünden bağımsız (Claude teşhisi).**
- Filo %11 küçülse de kalabalık (33 gün), ambar doluluğu (%9-10) ve derin zarar (%9) neredeyse aynı kalıyor.
- Az gemi olunca her gemi biraz daha çok yüklüyor; varıştaki toplam arz aynı kalıyor.
- Yani kalabalık bir sayı sorunu değil, **koordinasyon ve beklenti sorunu**. Tüccarlar hedefin 30 günlük derinliğini doldurmayı hedefliyor ve başkalarının yükünü eksik görüyor.
- Bu, D5b4 beklenti turnuvasının (özellikle bilgi temelli "temel" kuralı FD: hedefte kaç günlük arz var) doğrudan konusu.

**6. Toplam getiri hedef %8'in üstünde (T1).**
- Bütün kurulumlarda %12-18. Ama tüccarların yarısı kaybediyor ve en iyi %10 kârın yarısından fazlasını alıyor.
- Düzey 2 ile düzey 0 arasında toplam getiri farkı belirgin: %20'ye karşı %8.
- S-012'deki hedefin hangi ölçütle kıyaslanacağı kullanıcıyla netleşmeli.

## Tasarıma etkileri ve açık sorular

- **K-023 sonucu:** Alacaklı güvenli, ama aşırı temkinli. Reddetme eşiği (PD %25) ve kalibrasyon ayarı borcu neredeyse bitiriyor. Örneklem küçük olduğu için alacaklı getirisi gürültülü.
- **K-024 sonucu:** Batma bedeli girişi kısıyor ve getiriyi yükseltiyor. Gemi masrafı filoyu kısıyor. İkisi de kalabalığı çözmüyor.
- **Kalabalık için sıradaki adım (öneri):** D5b4 beklenti turnuvası, bu teşhis eklenerek. Ölçüt: kalabalık ve derin zarar. Aday kurallar:
  - FD: bilinen arz günleri.
  - Kendi deneyiminden rota kalabalığını öğrenme (learning from experience).
  - Derinlik hedefinin (`depth_days`) kendisi tüccar tarafından öğrenilmeli mi?
- **S-012 ölçütü:** toplam sermaye getirisi mi, tipik tüccar mı, yeni girenin beklentisi mi? Kullanıcıya soruldu.
