# D5b3e — Rota Kalabalığı: Plan
> Durum: taslak (plan; uygulama yok)
> Son güncelleme: 2026-10-26
> İlgili: [D5b3d](D5b3d.md), [10-route-choice-coordination](../research/simulation/10-route-choice-coordination.md), K-026, S-018, A15

## Amaç
Tüccarlar aynı en kârlı rotaya yığılıyor. D5b3d'de kalabalık, doluluk ve derin zarar filodan bağımsızdı. Bu planın amacı rotaları **tarihsel olarak doğru bir yapıyla** dağıtmak; ince ayar yapmak değil.

## Sıra (K-026)

| Adım | Ne | Köken | Not |
|---|---|---|---|
| **E1 Ablation** | Kalabalığa motorun kendi katkısı: (a) seviye 0 rakip yükleri görsün, (b) imitation kapalı (`imitation_on=False`, flag zaten var), (c) a+b. Taban: VRS | C (motor kontrolü) | Ucuz. Mekanizma eklemeden önce kendi artifact'ımızı temizlemek |
| **E2 Muhabir ağı** (limana bağlı tüccar, yumuşak) | Her tüccarın ağı var: ana liman + birkaç muhabir limanı. Ağdaki limanda bilgi taze, işlem maliyeti düşük. Dışında komisyon ödenir, bilgi bayat. Ağ deneyimle genişler | **K** (limana bağlı tüccar) + C (yumuşak biçim) + L (Trivellato; Datini; Roy 1951) | Bilgi tüccarın kendi muhabirinden gelir; rakipten bedava bilgi yok, bilgi satışı yok (K-026) |
| **E3 Çok gemili tüccar evi** | Büyük tüccarın birden çok gemisi olur ve seferlerini çeşitlendirir: kendi gemileri birbirinin pazarını yemez, ortak sermaye riski dağıtır | **K** + L (Datini; portföy çeşitlendirmesi) | Giriş mekanizmasıyla etkileşir (aşağıda) |
| **E4 D5b4 beklenti turnuvası** | Tahmin kuralı çeşitliliği (El Farol) | K (sıra), L (Arthur 1994) | Yapı oturduktan sonra |
| **Son çare: gürültü** | Logit seçim (QRE) | K: "her zaman seçenek, ilk seçenek asla" | Yalnızca E1-E4'ten sonra kalabalık hâlâ yüksekse |

**Sıra değişikliği (Claude itirazı, 2026-10-26):** Önceki öneride turnuva 2. adımdı; E2 ve E3'ün arkasına alındı. Gerekçe: turnuva, tahmin kurallarını belirli bir bilgi yapısında sıralar. Muhabir ağı her tüccarın ne bildiğini değiştiriyor. Ağdan önce yapılan turnuvanın sıralaması sonra geçersiz kalabilir. Bu, "önce yapı, sonra ayar" yaklaşımıyla tutarlı.

## Ölçütler (tüm adımlar)
- **Kalabalık:** varıştaki rakip yükü (talep günü cinsinden medyan)
- **Ambar doluluğu**
- **Derin zarar payı:** < −%20, yaşam gideri net
- **Rotalar arası ex-post getiri dağılımı:** sefer sayısıyla ağırlıklı ortalamadan sapma. Yeni ölçüt: dengede eşitlenmeli
- **Toplam sermaye getirisi** (K-025) ve filo büyüklüğü
- **Rota çeşitliliği:** aktif rota sayısı; en kalabalık 5 rotanın sefer payı

## E2 tasarım soruları (uygulamadan önce)
1. Başlangıç ağı nasıl dağıtılır? Önerim: ana liman + mesafeye ağırlıklı 1-2 rastgele liman.
2. Komisyon oranı nedir? Tarihsel veri bulunamadı; bir aralık önerip doğrulanmadı diye işaretlemek gerekiyor.
3. Ağ nasıl genişler? Önerim: bir limanda başarılı N sefer → muhabir edinilir. Ağ zamanla kapanmalı mı?
4. Ağ dışındaki bilgi ne kadar bayat? Avvisi gecikmesi (mevcut haber mekanizması) mi kullanılsın?

## E3 tasarım soruları
1. Ev nasıl doğar? Seçenekler:
   - (a) Başarılı tüccar kârını yeni gemiye yatırır.
   - (b) Yeni girişin bir kısmı mevcut evlere eklenir.
   - Tarihsel olan (a): Datini büyüyerek şubelendi. Ama giriş şu an anonim yatırımcı havuzundan geliyor (K-024); (a) bu kurala ikinci bir kanal ekler.
2. Ev planlaması: gemiler sırayla mı planlanır (her gemi evin önceki gemilerini rakip değil kendi yükü sayar), yoksa birlikte mi?
   - Önerim sırayla: basit, ve evin kendi pazar etkisini içselleştirmesi için yeterli.
3. Sermaye ortak mı? Bir geminin zararı diğerlerini batırır mı?
   - Tarihsel: sınırsız sorumluluk, ama Datini şubeleri ayrı şirketti.
4. Ev sayısı azsa etki küçük kalır. E3'ün kalabalığa etkisi evlerin filo payına bağlı.

## Durum (2026-10-26)
- Kullanıcı onayladı (K-027).
- **E1:** `experiments/d5b3e_crowd_ablation.py` hazır. Motora `l0_counts_rivals` bayrağı eklendi. 4 kurulum × 10 seed koşusu arka planda; çıktı `experiments/out/d5b3e/table_e1.txt`, `summary.json`. Tek seed VRS: kalabalık 32,6, en kalabalık 5 rota seferlerin %66'sı, 18 aktif rota.
- **E2 + E3 kodu** `sim/world5.py` içinde, bayraklar varsayılan kapalı (`network`, `houses`, ilgili parametreler). Komisyon %2,5 ⚠️ (Claude seçti). 2 yıllık duman testi çalıştı: 5 ev, komisyon tahsil ediliyor. **Ledger kontrolü henüz yapılmadı.** Doğru çağrı: `w.ledger.check(w._money_total(), w._goods_totals())`.
- **Önemli:** Test dünyası (BASE) yalnızca 3 liman (VEN, COR, ALE) ve 3 mal. Bu yüzden `net_init_k=1` (ana liman + 1 muhabir). Kalabalık sorununun bir kısmı bu dar dünyadan kaynaklanıyor olabilir; tam haritada rota sayısı çok daha fazla.
- **Bilinen basitleştirme:** Ev üyesinin limanda bekleyen kargosu `harbor` üzerinden rakip olarak da sayılabiliyor (küçük çift sayım).
- **Sıradaki:** E1 sonuçlarını raporla; E2/E3 için ledger kontrolü; ardından `d5b3e` E2/E3 koşuları.
- **Hız:** Tek seed 10 yıl ≈ 64 sn; paralel koşuda belirgin yavaşlama var. Optimizasyon kullanıcıyla birlikte yapılacak, şimdilik öncelik değil.

## E1 sonuç (10 seed, medyan; 2026-10-26)

| Kurulum | Kalabalık (gün) | Doluluk | Derin zarar | Toplam getiri | Filo | Rota sapması | İlk 5 rota payı |
|---|---|---|---|---|---|---|---|
| VRS | 32,4 | 0,097 | 0,085 | 17,5% | 72 | 0,31 | 0,67 |
| L0 | 32,9 | 0,086 | 0,094 | 17,1% | 76 | 0,27 | 0,70 |
| NI | 31,6 | 0,091 | 0,085 | 17,6% | 70 | 0,31 | 0,66 |
| L0NI | 33,5 | 0,084 | 0,097 | 20,2% | 76 | 0,28 | 0,70 |

**Yorum (bulgu, modele özgü):** Kalabalık, seviye 0'ın körlüğünden ve imitation'dan kaynaklanmıyor. Üç değişiklik de kalabalığı değiştirmedi (31,6-33,5 gün, seed gürültüsü içinde). Rotalar arası sapma biraz azaldı (0,31 → 0,27), ama ilk 5 rotanın payı arttı. Rakibi görmek, tüccarları çeşitlendirmek yerine aynı birkaç iyi rotaya daha dikkatli yığıyor. Sonuç: sorun bilgi yapısında (herkes aynı limanları aynı bilgiyle görüyor) ve 3 limanlı dar dünyada. E2 ve E3 doğru hedef. Imitation kaldırmanın bir faydası görülmedi; kalabilir.

## E2 + E3 sonuç (10 seed, medyan; hatalar düzeltildikten sonra; 2026-10-26)

| Kurulum | Kalabalık (gün) | Derin zarar | Toplam getiri | Filo | Rota sapması | İlk 5 rota payı | Sondaki ev gemisi payı |
|---|---|---|---|---|---|---|---|
| VRS (taban) | 32,4 | 0,085 | 17,5% | 72 | 0,31 | 0,67 | — |
| N (muhabir ağı) | 30,6 | 0,090 | 16,9% | 65 | 0,28 | 0,66 | — |
| H (ev, %30) | 31,4 | 0,090 | 13,9% | 69 | 0,32 | 0,66 | 9% |
| H6 (ev, %60) | 31,6 | 0,093 | 11,9% | 70 | 0,29 | 0,67 | 17% |
| NH | 31,3 | 0,086 | 14,4% | 69 | 0,28 | 0,67 | 11% |

Seed aralığı: kalabalık her kurulumda ~27-35 gün. Komisyonun toplam ticaret hacmine oranı %0,5; ağ ortalama 2,6 liman.

**Yorum:**
1. **Hiçbir mekanizma kalabalığı anlamlı değiştirmedi** (en iyi düşüş N: 32,4 → 30,6, seed gürültüsü içinde).
2. **Muhtemel neden: dünya çok dar (bulgu, modele özgü, doğrulanmadı).** 3 liman × 3 mal = 9 varış pazarı, ~70 gemi. Dağılacak yer yok. Ağ 3 limanın 2'sini zaten kapsıyor; komisyon hacmin %0,5'i, yani ağ dışına çıkmak nadir ve ucuz. Bu dünyada dağılım mekanizmalarının etkisi yapısal olarak sınırlı.
3. **Evler toplam getiriyi düşürdü ve eriyor.** Ev gemilerinin payı %30'dan %9'a, %60'tan %17'ye iniyor. Yeni girişler tek gemili; ev gemileri ise ev getirisi bonodan düşük kalınca çıkıyor. Neden düşük getiri? İki aday:
   - (a) Ev kendi kargosunu tam sayıyor ve bu dar dünyada ikinci en iyi rotaya kayıyor. Rakipler ise bunu hesaba katmayıp boşluğu dolduruyor (literatürde bilinen: Cournot'da birleşme paradoksu, Salant, Switzer & Reynolds 1983; doğrulanmadı, yeniden üretilmiş olabilir).
   - (b) Ortak kasa, boştaki gemiye nakit yığıyor.
   - Ayrıştırılmadı.
4. **Sonraki adım: tam harita.** Tam harita (bütün limanlar ve mallar) bu kurulumla şu an çalışmıyor (`_update_shares`: `Shopkeeper` nesnesinde `stocked_out` alanı yok). Önce bunun düzeltilmesi gerekiyor. Hız sorunu da orada belirleyici olacak.

## Tam harita (6 liman × 9 mal = 45 pazar)

**Düzeltme:** `_update_shares`, kent talebi olmayan mallarda (dükkâna hiç müşteri gelmeyen) `stocked_out` alanı tanımsız olduğu için hata veriyordu → `getattr(..., False)`. `d5b3c_finance.run` artık kurulumun BASE alanlarını (ports, goods) ezmesine izin veriyor (davranış değişmedi).

**Duman testi, F, seed 0 (10 yıl, 12,5 dk):**

| | 3 × 3 (VRS) | Tam harita (F) |
|---|---|---|
| Aktif rota | 18 | 147 |
| İlk 5 rotanın sefer payı | 0,67 | **0,17** |
| Kalabalık (talep günü) | 32,4 | **41,0** |
| Derin zarar | 0,085 | 0,049 |
| Filo | 72 | **229** |
| Toplam sermaye getirisi | 17,5% | **−0,3%** |

**İlk okuma (tek seed, ⚠️):**
- Tam haritada rotalar kendiliğinden dağılıyor: herkes aynı rotaya gitmiyor.
- Ama pazar başına kalabalık daha yüksek ve getiri sıfıra iniyor. Bu, D5b3d'nin "kalabalık filodan bağımsız" bulgusunun büyük haritadaki karşılığı: dağılım iyi, ama **giriş fazla** (filo 3 kat).
- K-024'teki batma bedeli küçük haritada girişi frenliyordu. Büyük haritada iflas sıklığı filoya bölündüğü için seyreliyor olabilir (aday açıklama, doğrulanmadı).

**Tam koşu, 4 kurulum × 10 seed (medyan; `out/d5b3e/table_full.txt`, 2026-10-27):**

| Kurulum | Kalabalık | Derin zarar | Filo | Toplam getiri | İlk 5 payı | Aktif rota | Not |
|---|---|---|---|---|---|---|---|
| F | 41,0 | 0,052 | 228 | −0,1% | 0,166 | 146 | |
| FN (ağ) | 42,0 | 0,056 | 227 | −0,8% | 0,167 | 146 | ağ 4,2 liman, komisyon hacmin %1,3'ü |
| FH (ev) | 41,4 | 0,051 | 233 | −1,0% | 0,167 | 149 | ev gemisi payı %30 → %12 |
| FNH | 40,0 | 0,052 | 225 | −1,2% | 0,166 | 144 | |

- Duman testi doğrulandı: büyük haritada rotalar kendiliğinden dağılıyor (ilk 5 payı 0,17), ama getiri sıfırda ve filo 3 kat.
- Ağ ve ev büyük haritada da kalabalığı değiştirmiyor. Dağılım sorunu büyük haritada kendiliğinden çözülüyor; kalan sorun **fazla giriş**.
- Literatürde bilinen sonuç: serbest girişte getiri sermaye maliyetine iner (bkz. [09](../research/simulation/09-market-structure-entry.md)). Ama bizde hedefin (S-012, ~%8) altına iniyor. Simülasyon bunu yeniden üretti; hedefin altına inmesi bizim giriş kuralımıza ait.

## E3 ayrıştırma: ev neden getiri kaybettiriyor? (3 × 3, 10 seed)

| Kurulum | Toplam getiri | Kalabalık | Sondaki ev gemisi payı |
|---|---|---|---|
| VRS (ev yok) | 17,5% | 32,4 | — |
| H (ortak kasa + kendi kargosunu sayar) | 13,9% | 31,4 | 9% |
| H-nopool (kasa ayrı) | 15,4% | 31,7 | 5% |
| H-noint (kendi kargosunu rakip gibi sayar) | 14,4% | 31,4 | 10% |

Seed'ler arası yayılma ~±2-3 puan; 10 seed medyanında standart hata ~1 puan (⚠️ kaba).

**Yorum:**
- İki aday da kaybı tek başına açıklamıyor. Kasa ayrı olunca kayıp biraz azalıyor (−3,6 → −2,1 puan), ama ev gemileri daha hızlı eriyor (%5).
- Kalan ortak öğeler:
  - (a) Ev üyeleri başkanın kişiliğini paylaşıyor (aynı düzey, aynı risk tutumu) ve aylık olarak aynı bilgiyi alıyor. Bu, bilgi çeşitliliğini azaltıyor; El Farol'un tersi.
  - (b) Çıkış kararı ev getirisiyle veriliyor. Kötü giden gemi ev ortalamasına saklanıp daha geç çıkıyor.
- Ayrıştırılmadı; sıradaki aday test bu.
- **Tarihsel not:** Gerçek bir evde başkan bilgiyi birleştirir ama gemileri farklı bilgiyle yönetir (her şubede ayrı fattore). Ortak bilginin kendisi değil, **ortak kararın** çeşitliliği öldürmesi sorun olabilir.
