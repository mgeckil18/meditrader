"""Ship-loss and voyage-tempo analysis for M-series runs (M1, M2).

Usage (repo root): OUT=m2 python3 core/tools/an_loss.py NAME   # reads experiments/out/$OUT/NAME_{0..5}.json
"""
import json, heapq, collections, statistics as st, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
PFX=sys.argv[1] if len(sys.argv)>1 else 'M2'
import os; OUT=os.environ.get('OUT','m1')
M=json.load(open(ROOT / 'core/maps/east-med-v1.json'))
tier={p['id']:p.get('tier','') for p in M['ports']}
reg={r['id']:r for r in M['regions']}
adj=collections.defaultdict(list)
for e in M['edges']:
    adj[e['a']].append((e['b'],e['days'],e['regions'])); adj[e['b']].append((e['a'],e['days'],e['regions']))
def route(a,b):
    D={a:(0,[])};pq=[(0,a,[])];seen=set()
    while pq:
        d,u,path=heapq.heappop(pq)
        if u in seen: continue
        seen.add(u)
        if u==b: return d,path
        for v,dd,rr in adj[u]:
            if v not in seen: heapq.heappush(pq,(d+dd,v,path+[rr]))
R={}
def info(a,b):
    if (a,b) not in R: R[(a,b)]=route(a,b)
    return R[(a,b)]
rows=[];prizes=[];lost_total=0;ships=[];scr=0;lscr=0;fleet=[]
for s in range(6):
    d=json.load(open(ROOT / f'experiments/out/{OUT}/{PFX}_{s}.json'))
    t0=d['t0']
    prizes.append((d.get('prizes',0),d.get('prizes_sold',0)))
    for x in d['dep_log']:
        day,a,b,lost,cause,mon=x[:6]; loaded=x[6] if len(x)>6 else True; age=x[7] if len(x)>7 else -1
        pdays=x[8] if len(x)>8 else -1; sdays=x[9] if len(x)>9 else None
        if day<t0: continue
        days,path=info(a,b)
        regs=sorted({r for leg in path for r in leg})
        rows.append(dict(pdays=pdays,sdays=sdays,loaded=loaded,age=age,s=s,a=a,b=b,lost=lost,cause=cause,mon=mon,days=days,legs=len(path),regs=regs,win=mon in (11,12,1,2,3)))
    for x in d['ship_log']: scr+=x[7]; lscr+=x[8]
    fleet.append(st.mean(d['fleet'][-120:] if len(d['fleet'])>120 else d['fleet']))
    ships.append(d['ships_lost'])
N=len(rows); L=sum(r['lost'] for r in rows)
yrs=10
print(f"kalkış (yüklü+balast) {N}, kayıp {L} ({L/N:.2%}); ships_lost toplam {sum(ships)}; filo ort {st.mean(fleet):.0f}")
print(f"filo-yılı başına sefer {N/(st.mean(fleet)*6*yrs):.1f}; yıllık kayıp {sum(ships)/(st.mean(fleet)*6*yrs):.1%}")
print("ganimet (çıkan, satılan):",[sum(x[0] for x in prizes),sum(x[1] for x in prizes)])
print(f"hurda (ömür) {scr:.0f}, bağlama-hurda {lscr:.0f}  -> 6 seed toplam")
c=collections.Counter(r['cause'] for r in rows if r['lost']); print("neden", {k:f"{v} ({v/L:.0%})" for k,v in c.items()})
def tab(key,label):
    g=collections.defaultdict(lambda:[0,0,collections.Counter()])
    for r in rows:
        k=key(r); g[k][0]+=1; g[k][1]+=r['lost']
        if r['lost']: g[k][2][r['cause']]+=1
    print(f"\n== {label}")
    for k in sorted(g,key=lambda k:str(k)):
        n,l,cc=g[k]; print(f"{str(k):28s} sefer {n:6d} ({n/N:5.1%})  kayıp {l:5d} ({l/n:5.2%})  korsan {cc['corsair']/max(l,1):4.0%}  kayıp payı {l/L:5.1%}")
tab(lambda r:'yüklü' if r['loaded'] else 'balast','yük')
tab(lambda r:'?' if r['age']<0 else '<1y' if r['age']<365 else '1-2y' if r['age']<730 else '2-4y' if r['age']<1460 else '4y+','gemi yaşı')
tab(lambda r:r['legs'],'bacak sayısı')
tab(lambda r:'<3g' if r['days']<3 else '3-6g' if r['days']<6 else '6-10g' if r['days']<10 else '10g+','süre (gün)')
tab(lambda r:'kış' if r['win'] else 'yaz','mevsim (kış=Kas-Mar)')
tab(lambda r:tier[r['a']]+'→'+tier[r['b']],'liman kademesi')
g=collections.defaultdict(lambda:[0,0])
for r in rows:
    for x in r['regs']: g[x][0]+=1; g[x][1]+=r['lost']
print("\n== bölge (rotası bölgeden geçen seferler)")
for k,(n,l) in sorted(g.items()): print(f"{k:4s} corsair0 {reg[k]['corsair']:.3f} kışx{reg[k]['winter_mult']}  sefer {n:6d}  kayıp {l/n:5.2%}")
rt=collections.Counter((r['a'],r['b']) for r in rows); rl=collections.Counter((r['a'],r['b']) for r in rows if r['lost'])
print("\n== en çok kayıp veren 12 rota")
for k,v in rl.most_common(12):
    days,path=info(*k); print(f"{k[0]}-{k[1]} {days:4.1f}g {len(path)} bacak  sefer {rt[k]:5d}  kayıp {v} ({v/rt[k]:.1%})")
print("\n== en sık 10 rota")
for k,v in rt.most_common(10):
    days,path=info(*k); print(f"{k[0]}-{k[1]} {days:4.1f}g {len(path)} bacak  sefer {v:5d} ({v/N:.1%})  kayıp {rl[k]/v:.1%}")
sea=sum(r['days'] for r in rows); fy=st.mean(fleet)*6*yrs
print(f"\nort. sefer süresi {sea/N:.1f}g; gemi-yılı başına denizde gün (taban süre) {sea/fy:.0f}")
print("yaş dağılımı (son an):", [round(x,1) for x in sorted(json.load(open(ROOT / f'experiments/out/{OUT}/{PFX}_0.json'))['ship_ages'])[::17]])

P=[r for r in rows if r['pdays']>=0]
if P:
    import statistics as st2
    def q(v,f): v=sorted(v); return v[int(f*(len(v)-1))]
    for lab,sel in [('hepsi',P),('yüklü',[r for r in P if r['loaded']]),('balast',[r for r in P if not r['loaded']])]:
        v=[r['pdays'] for r in sel]
        if v: print(f"limanda gün ({lab}): ort {st2.mean(v):.1f}  medyan {q(v,.5)}  p90 {q(v,.9)}")
    sd=sum(r['sdays'] for r in P); pd_=sum(r['pdays'] for r in P)
    print(f"zaman payı: denizde {sd/(sd+pd_):.0%}, limanda {pd_/(sd+pd_):.0%}; gemi-yılı başına denizde gün (gerçek) {sum(r['sdays'] for r in rows if r['sdays'])/fy:.0f}")
