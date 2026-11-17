# 07 — Beklenti Oluşumu: Ekonomik ve Psikolojik Modeller
> Durum: taslak
> Son güncelleme: 2026-10-26
> İlgili: [D5b2](../../experiments/D5b2.md), S-014, [03-academic-abm](03-academic-abm.md), [codex/behavior](../../codex/behavior.md), [framework](../../design/framework.md)

**Soru (kullanıcı, 2026-10-26):**
1. Beklentilerin nasıl oluştuğuna dair ekonomik-psikolojik bir model var mı?
2. Tüccarların beklentisini literatürdeki modele göre kurarsak piyasalar teknik analiz kurallarıyla mı çalışır? (Kullanıcı: çalışmamalı.)

**Kısa cevap:**
1. Var, birkaç aile hâlinde. En güçlü deneysel destek **heuristic switching** modelindedir: insanlar birkaç basit kural kullanır (uyarlamalı, trend izleme, çapalama ve ayarlama) ve geçmişte iyi tahmin eden kurala kayar (Anufriev & Hommes 2012).
2. **Hayır, bizim piyasa türümüzde değil.** Belirleyici olan piyasanın **geri besleme yönü**dür. Laboratuvar deneylerinde:
   - Mal piyasalarında (negatif geri besleme: yüksek fiyat beklentisi daha çok arz getirir, fiyatı düşürür) fiyat hızla dengeye yakınsıyor; trend kuralları kaybediyor ve terk ediliyor.
   - Spekülatif varlık piyasalarında (pozitif geri besleme: yüksek fiyat beklentisi talebi artırır, fiyatı yükseltir) trend izleme yayılıyor; balon ve çöküş çıkıyor.

   Tüccar ticareti negatif geri beslemelidir. Pozitif geri besleme yalnızca stokçuluk ve istifçilikte vardır; bu tarihsel olarak da gerçektir.

## 1. Beklenti modelleri ailesi

| Model | Fikir | Kaynak | Güçlü / zayıf yanı |
|---|---|---|---|
| **Naive** | Beklenen fiyat = son fiyat | Ezekiel (1938), cobweb | Cobweb döngüsünü üretir; insanlar bu kadar saf değil |
| **Adaptive expectations** | Beklenti, son hatanın bir kısmı kadar düzeltilir: E_t = E_{t−1} + λ(p_{t−1} − E_{t−1}) | Cagan (1956); Nerlove (1958) | Basit, deneylerde sık görülüyor; sistematik hatayı hiç öğrenmiyor |
| **Rational expectations (REH)** | Ajanlar modelin kendisini bilir; beklenti, doğru modelin koşullu beklenen değeri | Muth (1961); Lucas (1972) | Kıyaslama noktası; bilgi ve hesap yükü gerçekçi değil |
| **Extrapolative / trend following** | Beklenti = son fiyat + g × (son değişim) | Metzler (1941); anket kanıtı: Greenwood & Shleifer (2014) ⚠️ | Yatırımcı anketleriyle uyumlu; pozitif geri beslemede balon üretir |
| **Anchoring and adjustment** | Uzun dönem ortalamasına (çapa) ve son fiyata ağırlık + trend | Tversky & Kahneman (1974); Pecora, Agliari & Hommes (2016) | Bizim C4 / medyan hafıza buna yakın |
| **Fundamentalist / chartist** | İki tip: temelci (değere dönüş bekler), chartist (trend izler); paylar geçmiş başarıya göre değişir | Brock & Hommes (1997, 1998); Frankel & Froot (1990) ⚠️ | D5b2-B'nin çerçevesi |
| **Heuristic switching model (HSM)** | Birkaç basit kural; her ajan kuralı geçmiş tahmin başarısına göre seçer (logit) | Anufriev & Hommes (2012), AEJ: Micro 4(4); Hommes (2011), JEDC 35 | **Deneysel olarak en iyi doğrulanmış.** Laboratuvardaki hem bireysel hem toplam davranışı yeniden üretiyor |
| **Learning from experience** | Kişi kendi yaşadığı fiyatlara, okuduğu tarihten daha çok ağırlık verir; gençler daha hızlı günceller | Malmendier & Nagel (2016), QJE 131(1) | Kişiliğe ve yaşa bağlı beklenti farkı; kıtlık yaşamış tüccar temkinli |
| **Diagnostic expectations** | Representativeness: yeni haber, onunla "en çok uyuşan" sonucu abartılı olası gösterir; habere aşırı tepki, sonra öngörülebilir dönüş | Bordalo, Gennaioli & Shleifer (2018), JF 73(1) | Habere aşırı tepkiyi açıklıyor; REH'i özel durum olarak içeriyor |
| **Sticky information / rational inattention** | Herkes bilgisini her gün güncellemez; güncelleme maliyetli | Mankiw & Reis (2002); Sims (2003) ⚠️ | Bizde zaten var: bilgi gemiyle gelir, eskir (K-014) |

⚠️ = künyesi bilinen ama bu oturumda tam metni doğrulanmamış kaynak.

## 2. Belirleyici bulgu: geri beslemenin yönü

**Learning-to-forecast experiments** (Amsterdam, CREED): Katılımcılar yalnızca fiyat tahmini yapar, piyasa fiyatı tahminlerden üretilir. Tahminleri ne kadar iyiyse o kadar ödeme alırlar.

- **Heemeijer, Hommes, Sonnemans & Tuinstra (2009)**, JEDC 33(5), 1052-1072. 13 piyasa × 6 kişi.
  - **Negatif geri besleme** (cobweb tipi mal piyasası): fiyat dengeye oldukça hızlı yakınsıyor.
  - **Pozitif geri besleme** (spekülatif varlık): kalıcı salınımlar; katılımcılar son trendi dışa vuruyor (extrapolate); sonuç başlangıç koşuluna bağlı. (Pozitif taraf ayrıntıları ikincil kaynaktan: Colucci & Valori 2014 sunumu. Tam metin doğrulanmadı.)
- **Bao, Hommes, Sonnemans & Tuinstra (2012)**, JEDC 36(8), 1101-1120. Temel fiyata büyük beklenmedik şoklar:
  - Negatif geri beslemede (strategic substitutes) piyasa yeni temele hızla yakınsıyor.
  - Pozitif geri beslemede (strategic complements) yakınsamıyor: kısa vadede eksik, uzun vadede aşırı tepki.
- **Hommes (2011)**, JEDC 35, 1-24. Bu deneylerin derlemesi. Aynı HSM (aynı kurallar, aynı seçim mekanizması) iki tür piyasayı da açıklıyor:
  - Negatif geri beslemede trend kuralları kötü tahmin ediyor, payları sönüyor; uyarlamalı ya da temelci kurallar kalıyor.
  - Pozitif geri beslemede trend kuralları kendini doğruluyor, yayılıyor.

**Sonuç:** Teknik analizin piyasayı yönetip yönetmemesi beklenti modelinin değil, **piyasanın yapısının** sonucu. Aynı insan davranışı mal piyasasında istikrar, spekülatif piyasada balon üretir.

## 3. Tarihsel karşılık: 16. yüzyıl tüccarı beklentisini neyle kurardı?

- **Haber, fiyattan önce gelir.** Tüccar mektupları (Datini arşivi, 14.-15. yy) fiyatların yanında gemi gelişlerini, hasat durumunu, savaş ve salgın haberlerini taşır. Fiyat beklentisi büyük ölçüde **arz haberinden** kurulur. ⚠️ Genel tarih yazımı; sayfa düzeyinde doğrulanmadı. Bkz. [mediterranean-16c-overview](../history/mediterranean-16c-overview.md).
- **Price currents:** Başlıca ticaret merkezlerinde (Venedik dahil) basılı mal fiyat listeleri çıkar. McCusker & Gravesteijn (1991), *The Beginnings of Commercial and Financial Journalism*, NEHA, Amsterdam: ticari ve mali gazetelerin kökeni c1540-c1775. Erken sayılar çok az kalmış, çünkü her sayı bir sonrakiyle değerini yitirir.
- **Örnek beklenti cümlesi:** "İskenderiye'de baharat kervanı gelmedi, Lizbon'a Hint filosu dönüyor." Baharat fiyatı beklentisi bir **arz olayından** kurulur, fiyat grafiğinden değil. ⚠️ Lane ve Braudel'deki genel anlatı; doğrulanmadı.

## 4. Bizim piyasamızda geri besleme yönü

| Ajan / karar | Beklenti yükselince ne yapar | Fiyata etkisi | Geri besleme |
|---|---|---|---|
| Tüccar: hedefe mal götürme | Oraya daha çok mal götürür | Hedef fiyatı düşer | **Negatif** → trend kuralları kaybeder |
| Tüccar: limanda bekleme / satma (S) | Satmayı erteler | Bugünkü arz azalır, fiyat yükselir | Zayıf pozitif (bekleme maliyeti sınırlar) |
| Stokçu / istifçi | Bugün alır, sonra satar | Bugünkü fiyat yükselir | **Pozitif** → spekülatif dönemler mümkün |
| Dükkâncı | Envanter biriktirir | Toptan fiyat yükselir | Pozitif (D5a'daki ratchet bunun kontrolsüz hâliydi) |
| Köylü (hasat sonrası satış) | Satışı erteler | Arz azalır | Pozitif (front_load nakit ihtiyacıyla sınırlı) |

Pozitif geri besleme kanalları tarihsel olarak gerçek: kıtlıkta buğday istifçiliği, narh, ihtikâr yasakları. Bunları silmek değil, **sınırlarını gerçekçi tutmak** gerekiyor: depo kapasitesi, taşıma maliyeti, sermaye maliyeti, devlet müdahalesi.

## Oyun için çıkarımlar

1. **Beklenti modeli olarak HSM kullanılabilir, piyasa teknik analize teslim olmaz.** Tüccar kararı negatif geri beslemeli. Trend kuralları bu piyasada kötü tahmin eder ve payı söner. Literatürde bilinen sonuç (Heemeijer ve ark. 2009; Bao ve ark. 2012; Hommes 2011); simülasyonda ayrıca test edilmeli.
2. **"Temel" kural fiyat geçmişi değil, bilgi temelli olmalı (S-014).** 16. yüzyıl tüccarı beklentisini arz haberinden kurar: hasat, filo, bekleyen gemi, ambar durumu. Önerilen temel kural: hedefte kaç günlük arz var (bilinen stok + yoldaki ve gelecek kargo + hasat haberi) ve talep esnekliğiyle bu ne fiyat ima eder. D5b2'nin temel kuralı (gözlem medyanı) aslında bir çapalama kuralıydı, temel değildi.
3. **Kurallar kişiliğe bağlanabilir.** Her tüccarın kural ağırlıkları kendi tahmin başarısıyla güncellenir (HSM, kişi düzeyinde). Malmendier & Nagel: kendi deneyimine fazla ağırlık. Bu D5b'nin kişilik boyutlarına bir "beklenti tarzı" boyutu ekler; oyuncu NPC'leri bu tarza göre tanıyabilir ("o hep trende biner").
4. **Spekülasyon stokçu kanalında yaşar.** Balon ve istifçilik istenirse stokçunun beklentisinde ortaya çıkar. Sınırlayıcılar gerçekçi tutulmalı: kapasite, carry maliyeti, narh / ihtikâr eventi. Bu, kullanıcının "rant oluşursa devlet müdahalesi" ilkesiyle uyumlu (K-016).
5. **Diagnostic expectations bir oyun anı olarak değerli.** Habere aşırı tepki ve ardından dönüş, oyuncuya "herkes paniğe kapıldığında sakin kal" fırsatı verir. Bu, yetenekli oyuncunun kalıcı avantajı olarak bilgi işleme (S-012 not 1) ile uyumlu. Önce temel HSM test edilmeli.
6. **Doğrulama testi önerisi:** Kural payları zamanla ölçülsün. Tüccar piyasasında trend kuralının payı sönmeli; sönmüyorsa motorda pozitif geri besleme sızıntısı var demektir (D5a ratchet'i gibi). Bu, artifact bulmak için de bir teşhis aracı olur.
