"""Map generator (M1): rough port data -> core/maps/<name>.json. Usage: python3 core/tools/mapgen.py

(Original notes in Turkish below.)

Harita üreticisi (M1, docs/design/map-v1.md): kaba liman verisinden `core/maps/<ad>.json`.

Deniz günleri koordinatlardan: büyük daire mesafesi × kıyı dolanım çarpanı / ortalama seyir hızı.
Hız, eski haritanın günlerinden (VEN-RAG 8, VEN-COR 12, COR-ALE 14, CHI-IST 4) kabaca ~45 deniz mili/gün çıkar ⚠️.
Bütün sayılar Claude'un kaba tahmini (K-035: arşiv verisi yok); kaynakları map-v1.md'de.

Kullanım: python3 core/tools/mapgen.py            # east-med-v1.json yazar
"""
import json
import math
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "maps"

NM_PER_DAY = 45.0     # ortalama seyir (bekleme dahil, yaz) ⚠️
DETOUR = 1.2          # kıyı boyu dolanım çarpanı ⚠️

# id: (ad, tür, enlem, boylam, nüfus, sınıf payları (zengin, orta, yoksul), şarap çarpanı)
PORTS = {
    "GEN": ("Cenova", "büyük", 44.41, 8.93, 65_000, (0.10, 0.20, 0.70), 1.0),
    "CVV": ("Civitavecchia", "orta", 42.09, 11.79, 8_000, (0.06, 0.20, 0.74), 1.0),
    "NAP": ("Napoli", "büyük", 40.84, 14.25, 230_000, (0.07, 0.20, 0.73), 1.0),
    "PAL": ("Palermo", "orta", 38.12, 13.36, 90_000, (0.07, 0.20, 0.73), 1.0),
    "MES": ("Messina", "orta", 38.19, 15.55, 60_000, (0.08, 0.22, 0.70), 1.0),
    "TUN": ("Tunus", "orta", 36.81, 10.18, 50_000, (0.05, 0.20, 0.75), 0.2),
    "VEN": ("Venedik", "büyük", 45.44, 12.33, 170_000, (0.10, 0.20, 0.70), 1.0),
    "ANC": ("Ancona", "orta", 43.62, 13.51, 20_000, (0.08, 0.22, 0.70), 1.0),
    "RAG": ("Ragusa", "orta", 42.64, 18.11, 30_000, (0.12, 0.23, 0.65), 1.0),
    "BAR": ("Bari-Barletta (Apulia)", "orta", 41.13, 16.87, 30_000, (0.06, 0.20, 0.74), 1.0),
    "COR": ("Korfu", "orta", 39.62, 19.92, 18_000, (0.08, 0.20, 0.72), 1.0),
    "ZAN": ("Zante", "orta", 37.78, 20.90, 15_000, (0.06, 0.20, 0.74), 1.0),
    "CAN": ("Kandiye (Girit)", "orta", 35.34, 25.13, 15_000, (0.08, 0.20, 0.72), 1.0),
    "CHI": ("Sakız", "orta", 38.37, 26.14, 15_000, (0.10, 0.20, 0.70), 1.0),
    "SAL": ("Selanik", "orta", 40.64, 22.94, 30_000, (0.06, 0.22, 0.72), 0.6),
    "IST": ("İstanbul", "büyük", 41.01, 28.98, 450_000, (0.06, 0.24, 0.70), 0.3),
    "RHO": ("Rodos", "orta", 36.44, 28.22, 10_000, (0.05, 0.20, 0.75), 0.6),
    "FAM": ("Magosa (Kıbrıs)", "orta", 35.12, 33.94, 8_000, (0.06, 0.20, 0.74), 1.0),
    "TRI": ("Trablusşam", "orta", 34.44, 35.84, 15_000, (0.05, 0.20, 0.75), 0.2),
    "ALE": ("İskenderiye", "büyük", 31.20, 29.92, 40_000, (0.05, 0.20, 0.75), 0.2),
}

# Bölge: (kış çarpanı, sakin dönem korsan olasılığı / bacak) ⚠️ (classic6 değerleri genişletildi)
REGIONS = {
    "TYR": (2.0, 0.005),   # Ligurya-Tiren: Berberi baskınları
    "SIC": (2.0, 0.012),   # Sicilya kanalı ve Tunus: Berberi korsan merkezi
    "ADR": (3.0, 0.003),   # Kuzey Adriyatik: Venedik devriyesi, bora
    "OTR": (2.0, 0.008),   # Güney Adriyatik, Otranto: Uskok, Berberi
    "ION": (2.0, 0.008),   # İyon, Mora: Berberi, Malta
    "AEG": (2.0, 0.010),   # Ege: Malta, San Stefano, Rum korsanlar
    "STR": (2.0, 0.002),   # Boğazlar: Osmanlı denetimi
    "LEV": (1.0, 0.010),   # Levant, Kıbrıs, Mısır: Malta şövalyeleri
}

# Bacaklar: (a, b, bölgeler). Gün koordinatlardan. Kara engeli olan bacaklarda ek dolanım çarpanı (DETOUR_X).
EDGES = [
    ("GEN", "CVV", ("TYR",)), ("CVV", "NAP", ("TYR",)), ("NAP", "PAL", ("TYR",)), ("NAP", "MES", ("TYR",)),
    ("PAL", "MES", ("TYR",)), ("PAL", "TUN", ("SIC",)), ("TUN", "MES", ("SIC",)),
    ("VEN", "ANC", ("ADR",)), ("VEN", "RAG", ("ADR",)), ("ANC", "RAG", ("ADR",)), ("ANC", "BAR", ("ADR", "OTR")),
    ("RAG", "BAR", ("OTR",)), ("RAG", "COR", ("OTR",)), ("BAR", "COR", ("OTR",)),
    ("MES", "COR", ("ION",)), ("MES", "ZAN", ("ION",)), ("COR", "ZAN", ("ION",)),
    ("ZAN", "CAN", ("ION", "AEG")), ("ZAN", "CHI", ("ION", "AEG")), ("CAN", "CHI", ("AEG",)),
    ("CHI", "SAL", ("AEG",)), ("CHI", "IST", ("STR",)), ("SAL", "IST", ("AEG", "STR")),
    ("CAN", "RHO", ("AEG",)), ("CHI", "RHO", ("AEG",)), ("CAN", "ALE", ("LEV",)),
    ("RHO", "FAM", ("LEV",)), ("RHO", "ALE", ("LEV",)), ("FAM", "TRI", ("LEV",)), ("FAM", "ALE", ("LEV",)),
    ("TRI", "ALE", ("LEV",)),
]

DETOUR_X = {("ZAN", "CHI"): 1.45,   # Mora'nın etrafından (Malea burnu)
            ("TUN", "MES"): 1.35,   # Sicilya'nın güneyinden
            ("PAL", "MES"): 1.25}   # Sicilya'nın kuzey kıyısı

# Arz planı: mal → {liman: ("own", oran) | ("exp", ağırlık)}. Listede olmayan liman: kendine yeterlilik 0.
O, X = "own", "exp"
SUPPLY = {
    "WHT": dict(GEN=(O, 0.2), CVV=(O, 0.8), NAP=(O, 0.5), PAL=(X, 1.0), MES=(O, 0.4), TUN=(O, 0.8),
                VEN=(O, 0.4), ANC=(O, 0.8), RAG=(O, 0.1), BAR=(X, 1.0), COR=(O, 0.4), ZAN=(O, 0.3),
                CAN=(O, 0.5), CHI=(O, 0.3), SAL=(X, 0.4), IST=(O, 0.6), RHO=(O, 0.4), FAM=(X, 0.3),
                TRI=(O, 0.7), ALE=(X, 1.0)),
    "BRL": dict(GEN=(O, 0.4), CVV=(O, 0.9), NAP=(O, 0.7), PAL=(X, 0.6), MES=(O, 0.6), TUN=(O, 0.9),
                VEN=(O, 0.6), ANC=(O, 0.9), RAG=(O, 0.3), BAR=(X, 0.6), COR=(O, 0.6), ZAN=(O, 0.5),
                CAN=(O, 0.7), CHI=(O, 0.5), SAL=(X, 0.4), IST=(O, 0.8), RHO=(O, 0.6), FAM=(O, 1.0),
                TRI=(O, 0.9), ALE=(X, 1.0)),
    "OIL": dict(GEN=(O, 0.3), CVV=(O, 0.5), NAP=(O, 0.6), PAL=(O, 0.5), MES=(O, 0.5), TUN=(X, 0.4),
                VEN=(O, 0.0), ANC=(O, 0.4), RAG=(O, 0.5), BAR=(X, 1.0), COR=(X, 0.3), ZAN=(X, 0.3),
                CAN=(X, 0.4), CHI=(O, 0.8), SAL=(O, 0.3), IST=(O, 0.3), RHO=(O, 0.6), FAM=(O, 0.3),
                TRI=(O, 0.6), ALE=(O, 0.2)),
    "WIN": dict(GEN=(O, 0.4), CVV=(O, 0.8), NAP=(X, 0.4), PAL=(O, 0.6), MES=(O, 0.6), TUN=(O, 0.0),
                VEN=(O, 0.2), ANC=(O, 0.6), RAG=(O, 0.5), BAR=(O, 0.8), COR=(X, 0.3), ZAN=(X, 0.3),
                CAN=(X, 1.0), CHI=(X, 0.4), SAL=(O, 0.5), IST=(O, 0.5), RHO=(O, 0.6), FAM=(X, 0.3),
                TRI=(O, 0.0), ALE=(O, 0.0)),
    "WOL": dict(GEN=(O, 0.2), NAP=(O, 0.3), VEN=(O, 0.3), BAR=(X, 0.4), SAL=(X, 0.6), IST=(X, 1.0)),
    "ALM": dict(CVV=(X, 1.0)),                       # Tolfa şapı (papalık) ⚠️
    "PEP": dict(ALE=(X, 1.0), TRI=(X, 0.4)),         # Kızıldeniz ve Halep kervanları ⚠️
}

# Kumaş havuzları: (liman, mal) → beslediği limanlar
POOLS = [
    ("VEN", "CLF", ["VEN", "GEN", "CVV", "NAP", "PAL", "MES", "ANC", "RAG", "BAR", "COR", "ZAN", "CAN", "CHI",
                    "SAL", "IST", "RHO", "FAM", "TRI", "ALE", "TUN"]),
    ("VEN", "CLC", ["VEN", "ANC", "RAG", "BAR", "COR", "ZAN", "CAN", "FAM", "GEN", "CVV", "NAP", "PAL", "MES"]),
    ("IST", "CLC", ["IST", "CHI", "RHO", "TRI", "ALE", "TUN"]),
    ("SAL", "CLC", ["SAL"]),                         # Selanik Yahudi yün dokumacılığı ⚠️
]


def nm(a, b):
    """Büyük daire mesafesi, deniz mili."""
    la1, lo1, la2, lo2 = map(math.radians, (PORTS[a][2], PORTS[a][3], PORTS[b][2], PORTS[b][3]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 3440.065 * math.asin(math.sqrt(h))


def build(name="east-med-v1"):
    ports = [dict(id=k, name=v[0], tier=v[1], lat=v[2], lon=v[3], pop=v[4], classes=list(v[5]), wine_factor=v[6])
             for k, v in PORTS.items()]
    regions = [dict(id=k, winter_mult=v[0], corsair=v[1]) for k, v in REGIONS.items()]
    edges = []
    for a, b, regs in EDGES:
        d = max(1.0, round(nm(a, b) * DETOUR * DETOUR_X.get((a, b), 1.0) / NM_PER_DAY * 2) / 2)
        edges.append(dict(a=a, b=b, days=d, regions=list(regs), nm=round(nm(a, b))))
    supply = [dict(good=g, plan=[{"port": p, kind: v} for p, (kind, v) in plan.items()]) for g, plan in SUPPLY.items()]
    pools = [dict(port=p, good=g, serves=s) for p, g, s in POOLS]
    m = dict(name=name, doc="Tam harita v1 (M1): Cenova'nın doğusu, büyük ve orta limanlar; kaba veri ⚠️ "
                            "(docs/design/map-v1.md). core/tools/mapgen.py üretir; elle düzenlenmez.",
             home="VEN", ports=ports, regions=regions, edges=edges, supply=supply, pools=pools)
    p = OUT / f"{name}.json"
    p.write_text(json.dumps(m, ensure_ascii=False, indent=1))
    return m


if __name__ == "__main__":
    m = build()
    for e in m["edges"]:
        print(f'{e["a"]}-{e["b"]}: {e["nm"]} nm, {e["days"]} gün')
