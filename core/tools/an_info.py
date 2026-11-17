"""Information-system diagnostics (reroute log, voyage metrics). Usage: python3 core/tools/an_info.py OUTDIR A,B,...

(Original notes in Turkish below.)

Bilgi sistemi teşhisi (I0/I1): yön değiştirme kaydı (rr_log) ve sefer ölçütleri.
Kullanım: python3 core/tools/an_info.py OUTDIR AD1,AD2,...   (experiments/out/OUTDIR/AD_s.json, s=0..5)"""
import json, sys, statistics as st
out, names = sys.argv[1], sys.argv[2].split(',')
def q(v, f):
    v = sorted(v); return v[int(f * (len(v) - 1))] if v else float('nan')
print(f"{'':26s}" + ''.join(f"{n:>14s}" for n in names))
R = {}
for n in names:
    rr, dep_l, short, pd, sy, fleet, ret = [], 0, 0, [], 0, [], []
    for s in range(6):
        d = json.load(open(f'experiments/out/{out}/{n}_{s}.json'))
        t0 = d['t0']
        rr += [x for x in d.get('rr_log', []) if x[0] >= t0]
        for x in d['dep_log']:
            if x[0] < t0 or len(x) < 10: continue
            if x[6]:
                dep_l += 1
                if 0 <= x[8] <= 1: short += 1
                elif x[8] >= 2: pd.append(x[8])
        fleet.append(st.mean(d['fleet'][-120:])); ret.append(d['agg'])
    fy = st.mean(fleet) * 6 * 10
    found = [x[12] / x[7] for x in rr if x[7] > 0]          # varışta bulunan / beklenen (ham)
    vs_here = [x[12] / (x[4]) for x in rr if x[4] > 0]       # varışta bulunan / bıraktığı limanın fiyatı (ham)
    R[n] = [
        ('yön değiştirme / gemi-yılı', len(rr) / fy),
        ('yüklü kalkışta ≤1 gün payı', short / max(dep_l, 1)),
        ('gerçek uğrak: limanda medyan', q(pd, .5)),
        ('yüklü sefer / gemi-yılı', dep_l / fy),
        ('bulunan/beklenen medyan', q(found, .5)),
        ('bulunan/beklenen p25', q(found, .25)),
        ('bulunan < beklenen payı', sum(1 for f in found if f < 1) / max(len(found), 1)),
        ('bulunan/bırakılan medyan', q(vs_here, .5)),
        ('hedef bilgisinin yaşı medyan', q([x[10] for x in rr], .5)),
        ('hedef bilgisinin yaşı p90', q([x[10] for x in rr], .9)),
        ('bırakılan limanda kendi etki', q([x[5] for x in rr], .5)),
        ('hedefte beklenen etki', q([x[8] for x in rr], .5)),
        ('agg (getiri)', st.mean(ret)),
        ('filo', st.mean(fleet)),
    ]
for i, (lab, _) in enumerate(R[names[0]]):
    print(f"{lab:26s}" + ''.join(f"{R[n][i][1]:14.3f}" for n in names))
