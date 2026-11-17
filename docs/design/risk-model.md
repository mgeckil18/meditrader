# Risk Modeli: Deniz Riski, Ticaret Riski, Sigorta ve Yatırımcı Primi
> Durum: taslak (öneri; kullanıcı yönü onayladı, ayrıntılar açık)
> Son güncelleme: 2026-11-02
> İlgili: [maritime-risk-16c](../research/history/maritime-risk-16c.md), [D5b3h](../experiments/D5b3h.md), [14-natural-entry-exit](../research/simulation/14-natural-entry-exit.md), K-030, S-021, İ12

## Kullanıcı yönü (2026-11-02, K-030)

- Risk yapılandırılmalı: rota ve mevsime bağlı batma ve korsana yakalanma, tarihsel doğrulukla.
- Kötü ticaret yapıp zarar etmek de bir risk.
- Risk aslında sefer ve gemi başına; ama bunu hesaplamak tüccar için çok zor. Bu yüzden tüccar sefer başına genel bir risk ortalaması kullanır. Bu ortalama ticaretin akışına göre dinamik belirlenir.
- Yatırımcı ve tüccar davranışı için **(c) seçeneği:** birkaç gemiye pay (carati) dağıtma + sigorta.
- γ: tüccar grupları buna göre sınıflandırılır; parametre en sonda ince ayarlanır.
- Kullanıcının sorusu: Eksik bilgiye dayalı zararlar da risk değerinin içinde olmalı mı? (Cevap aşağıda, §2.)

## 1. Risk katmanları

| Katman | Nedir | Sigortalanır mı | Çeşitlenir mi (carati) |
|---|---|---|---|
| **Fiziksel: doğal** | Fırtına, batma | Evet | Çoğunlukla evet (gemiye özgü) |
| **Fiziksel: korsan** | Yakalanma, el koyma | Evet | Kısmen: korsan baskısı bütün bölgeyi etkiler (ortak şok) |
| **Ticari** | Varışta fiyat düşük, alışta pahalı, kalabalık; eksik bilgiyle yanlış karar dahil | Hayır | Gemiye özgü kısmı evet; piyasa çapındaki kısmı (cobweb, herkesin aynı sinyale koşması) hayır |

## 2. Eksik bilgiden doğan zararlar riskin içinde mi? Cevap: evet, ayrıca eklemeden

1. **Yatırımcı kaynağı ayırt edemez.** Gördüğü şey seferin sonucu. Ö1'in duman testi bunu ölçtü: tüccarlar arası fark şanstan ayırt edilemiyor (k = ∞). Bilgi hatası ile kötü şans aynı dağılımın içinde.
2. **Ekonomik karşılık:** Knight (1921) ⚠️ ölçülebilir risk ile belirsizliği ayırır. Tahmin hatası (parameter uncertainty) beklenen getirinin varyansını büyütür; Bayesçi yatırımcı bunu toplam (predictive) varyans olarak görür (Kandel & Stambaugh 1996; Barberis 2000 ⚠️).
3. **Çift sayma olmamalı.** Ticari risk gerçekleşen sefer sonuçlarından ölçülürse bilgi hataları zaten içindedir. Ayrı bir "bilgi riski" terimi eklenmez.
4. **Ayrım önemli olduğu yer:** bilgi hatasının gemiye özgü kısmı carati ile çeşitlenir. Herkesin aynı eski fiyata koştuğu kısım (cobweb) çeşitlenmez; sistematik risktir. D5b3f/g'deki filo döngüsü bunun var olduğunu gösteriyor.
5. **Sigortalanmaz:** Poliçe deniz ve insan tehlikelerini kapsar, piyasa kaybını kapsamaz (⚠️ doğrulanacak).

## 3. Fiziksel tehlike (dünya tarafı)

**Bugünkü motor (Claude, ⚠️):** Günlük sabit olasılık, yazın %0,1, kışın %0,3; kışın sefer süresi × 1,5. 10 günlük yaz seferi ~%1, kış seferi ~%4,4. Mesafeyle orantılı. Yalnızca yük kaybolur; gemi kalır.

**Öneri (R1):**
- Tehlike **bacak** (haritadaki kenar) başına, sefer başına bir olasılık; gün sayısıyla orantılı değil.
- h_bacak(t) = 1 − (1 − d_bacak(ay)) · (1 − c_bölge(t) · v)
  - d_bacak(ay): doğal tehlike, bölgeye ve aya bağlı. Kış etkisi bölgesel (Adriyatik'te bora; Levant'ta küçük).
  - c_bölge(t): **korsan baskısı**, dinamik dünya değişkeni. Kalıcı bir seviye etrafında, kısa ömürlü şoklar (söylentiyle fiyatlanan sıçramalar). Biçim: log-AR(1) + seyrek sıçrama ⚠️ (Claude seçimi; tarihsel sıçrama verisine göre ayarlanacak).
  - v: geminin savunmasızlığı. Şimdilik herkes için 1. İleride gemi tipi, bayrak, konvoy (K-011).
- Rota birden çok bacaktan geçiyorsa olasılıklar birleşir.
- Sonuç türleri: batma (yük ve gemi), yakalanma (yük ve gemi; fidye ileride). Ortak avarya (kısmi kayıp) sonraki adım.
- **Kalibrasyon:** Tek tek parametre ayarlamak yerine örüntüler ([maritime-risk-16c §6.7](../research/history/maritime-risk-16c.md)): sefer başına kayıp ~%2-4, bölgeler arası prim farkı %1-15 aralığında, korsan payı ≥ %50.

## 4. Risk tahmini (ajan tarafı): sefer başına dinamik ortalama

Tüccar, yatırımcı ve sigortacı gerçek olasılığı bilmez; kamuya açık haberden öğrenir.

- **Fiziksel:** Her bacak için kayıp sıklığı tahmini. Haber: batma ve yakalanma haberleri limana gecikmeyle ulaşır (Rialto, noter kayıtları).
  - Model: Beta-Binomial (Bayesçi oran tahmini), eski haberler unutulur (üstel ağırlık).
  - Bacak tahmini, bütün denizin ortalamasına credibility ile çekilir (Bühlmann, Ö1 ile aynı mantık; k veriden). Az sefer yapılan bacakta tahmin genel ortalamaya yakın kalır. Bu, kullanıcının "çoğunlukla genel bir ortalama çalışır" sezgisinin modeldeki karşılığı: genel ortalamadan ne kadar sapılacağını veri belirler.
- **Ticari:** Fiziksel kayıp dışındaki sefer getirisinin ortalaması ve varyansı. Kamu sicilinden, bütün seferler için tek bir genel ortalama (kullanıcı önerisi), son 12 ay.

## 5. Sigorta (R4)

- **Sigortacılar:** Cenova 1564-72 defterinde, birbirini sigortalayan kapalı bir tüccar grubu (Iodice 2023). Modelde: sermayeli tüccarlar ya da ayrı bir sigortacı havuzu.
- **Prim:** sigortacının beklenen kaybı + kendi risk primi. Kendi risk primi aynı Arrow-Pratt kuralından: γ_s · w_s · σ²_defter. Loading için ayrı bir parametre gerekmez; sigortacının ne kadar çeşitlendiğinden doğar.
- **Tüccarın kararı:** Prim, kaybın kendisi için kesinlik eşdeğerinden (certainty equivalent) düşükse sigorta yaptırır. Riskten kaçan tüccar daha çok sigortalar.
- Oyunda K-012 (sigorta dolandırıcılığı) için zemin.

## 6. Yatırımcının risk primi (Ö2, seçenek c)

- Gereken ek getiri ≈ γ · w · σ²_etkin
- σ²_etkin (yıllık) = sefer/yıl × [σ²_ortak + σ²_özel / N] + (sigortalanmayan fiziksel kayıp varyansı) / N
  - Sigortalanan kayıp varyanstan çıkar, prim maliyete girer.
  - N: yatırımcının kaç gemiye pay dağıttığı. w: servetinin ne kadarını denize koyduğu.
- **w ve N tarihsel kaynaktan** bulunacak (Venedik carati kayıtları; Lane). Bulunana kadar geçici vekil ⚠️.
- **γ:** tüccar ve yatırımcı grupları γ'ya göre sınıflanır; değer en sonda ayarlanır (kullanıcı kararı).

## 7. Uygulama sırası (öneri)

| Adım | İçerik | Ölçüt |
|---|---|---|
| R1 | Bacak + bölge tehlikesi, korsan baskısı süreci, gemi kaybı | Sefer başına kayıp oranı, bölgeler arası fark, kış seferi payı |
| R2 | Ajanların kayıp tahmini (Beta-Binomial + credibility) | Tahminin gerçek orana yakınsaması; şok sonrası gecikme |
| R3 | Ticari risk ayrıştırması (ortak ve özel) | σ_ortak, σ_özel ölçümü (aylık panel, survivorship düzeltmeli) |
| R4 | Sigorta | Prim dağılımı (%1-15), sigorta oranı |
| R5 | Ö2 eşiği: γ · w · σ²_etkin | Getiri ve filo örüntüleri |

## 8. Açık noktalar (S-021, S-022)

- **Kullanıcı yönü (2026-11-09, S-022):** Korsanlık başta düşük, ~1580'den sonra tarihsel olay olarak hızla artar. Yabancı gemi ucuz ama geç teslim. Karar araştırmadan sonra.

- Gemi kaybı: bugün gemi batmıyor (yalnızca yük gidiyor). Gemi bir sermaye olursa kaybı da olmalı. Bu, ertelenen Ö3 (gemi piyasası) ile bağlantılı.
- Bölge tehlike seviyeleri için 16. yy kaynağı eksik (Tenenti 1967, Greene 2010 okunmadı).
- w ve N için tarihsel kaynak.
