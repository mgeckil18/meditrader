"""Price spikes (monthly kapan price / reference). Usage: python3 core/tools/an_px.py OUTDIR A,B,...

(Original notes in Turkish below.)

Fiyat sıçramaları (px_log: aylık kapan fiyatı / referans). Kullanım: python3 core/tools/an_px.py OUTDIR AD1,AD2"""
import json, sys, math, collections
out, names = sys.argv[1], sys.argv[2].split(',')
M = json.load(open('core/maps/east-med-v1.json'))
tier = {p['id']: p['tier'] for p in M['ports']}
def q(v, f):
    v = sorted(v); return v[int(f * (len(v) - 1))] if v else float('nan')
res = {}
for n in names:
    by = collections.defaultdict(list)
    for s in range(6):
        d = json.load(open(f'experiments/out/{out}/{n}_{s}.json'))
        keys = d['market_keys']
        for row in d['px_log']:
            for mi, x in enumerate(row):
                if not isinstance(x, (int, float)) or math.isnan(x): continue
                p, g = keys[mi]
                by[g].append(x); by[(g, tier[p])].append(x); by['HEPSİ'].append(x)
    res[n] = by
goods = ['WHT', 'BRL', 'OIL', 'WIN', 'CLC', 'CLF', 'PEP', 'WOL', 'ALM']
print('fiyat / referans: medyan | p99 | en yüksek | >3× payı   (pazar-ay)')
for g in goods + ['HEPSİ']:
    line = f'{g:6s}'
    for n in names:
        v = res[n].get(g, [])
        if not v: line += f' | {n}: —'; continue
        line += f' | {n}: {q(v,.5):5.2f} {q(v,.99):6.2f} {max(v):7.1f} {sum(1 for x in v if x > 3)/len(v):5.1%}'
    print(line)
print('\nbiber ve ince kumaş, liman kademesine göre (p99 / en yüksek)')
for g in ['PEP', 'CLF', 'WIN']:
    for t in ['büyük', 'orta']:
        line = f'{g} {t:6s}'
        for n in names:
            v = res[n].get((g, t), [])
            line += f' | {n}: {q(v,.99):6.2f} {max(v) if v else float("nan"):7.1f}'
        print(line)
