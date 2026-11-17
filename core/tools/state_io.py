"""Canonical state dump and day trace of the Python D5World, for bit-level comparison with the Rust core.

(Original notes in Turkish below.)

Python D5World durumunun kanonik dökümü ve gün izi (Rust çekirdeğiyle bit düzeyinde karşılaştırma için).

Biçim Rust'ın `medi-core/src/world/{mod,types}.rs` yapılarının serde biçimidir (Rust aynısını okur ve yazar):
  - liman ve mal adları dizgi ("VEN", "WHT"); pazar anahtarlı sözlükler pazar sırasına göre yoğun listeler
  - liman anahtarlı sözlükler {"VEN": ...}; demet → liste; küme → sıralı liste
  - tüccar kimliği tam sayı ("m12" → 12; "public" → 0; "pend3" → −4)
  - inf / nan → "inf" / "nan"
  - Python'da sonradan eklenen öznitelikler (getattr varsayılanlı) yoksa varsayılanla yazılır
Her nesnede bilinmeyen bir öznitelik görülürse döküm durur: Python'a yeni durum eklendiyse Rust'a da eklenmeli.

Özet (digest): ağaç, tip etiketli bayt dizisine çevrilip SHA-1 alınır (sözlük anahtarları sıralı; int ve float aynı
float64 bitleriyle). Üst düzey alan başına bir özet; `merchants`, `markets`, `gone` eleman başına.

Kullanım:
  python3 core/tools/state_io.py dump  SETUP SEED OUT.json               # başlangıç durumu (snapshot sonrası)
  python3 core/tools/state_io.py trace SETUP SEED DAYS OUT.jsonl [GÜNLER] # gün sonu özetleri (+ GÜNLER'de tam döküm)
  python3 core/tools/state_io.py cfg   SETUP SEED OUT.json [YIL]           # yapılandırma (Rust soğuk başlangıç / koşucu)
  python3 core/tools/state_io.py snap  SETUP K OUT.json                    # Python snapshot'ının (pkl) dökümü
SETUP "AD@cold" = snapshot ön koşusunun yapılandırması (soğuk başlangıç; seed olduğu gibi kullanılır).
"""
import dataclasses
import hashlib
import json
import math
import os
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from sim.world5 import CLASS_TEMPLATE, CONSUMER_CATS, GOODS5, REGIONS, M5, D5World  # noqa: E402

GOODS = list(GOODS5)
MARKET_CFG = ("good", "harvest_month", "continuous_supply", "yield_sigma", "elasticity", "spoilage_per_day",
              "farm_spoilage_per_day", "interdealer", "harvest_news_weight", "external_wholesale", "yield_overrides")


def fl(x):
    x = float(x)
    if math.isfinite(x):
        return x
    return "nan" if math.isnan(x) else ("inf" if x > 0 else "-inf")


def num(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, int):
        return x
    if hasattr(x, "dtype"):
        x = x.item()
        if isinstance(x, int):
            return x
    return fl(x)


def opt(x, f=num):
    return None if x is None else f(x)


def mid(s):
    if s == "public":
        return 0
    if s.startswith("pend"):
        return -1 - int(s[4:])
    assert s.startswith("m"), s
    return int(s[1:])


def gstr(g):
    return g if g else None


def load(v):
    o, d, g, q, day, m = v
    return [o, d, g, num(q), day, mid(m)]


def loads_map(d):
    out = {}
    for k, v in d.items():
        assert isinstance(k, int), k
        out[str(k)] = load(v)
    return out


def rng_state(streams):
    out = {}
    for name, g in streams._streams.items():
        s = g.bit_generator.state
        out[name] = dict(state=str(s["state"]["state"]), inc=str(s["state"]["inc"]),
                         has_uint32=int(s["has_uint32"]), uinteger=int(s["uinteger"]))
    return dict(seed=int(streams.seed), streams=out)


def fields_of(o, extra=(), ignore=()):
    """Dataclass alanları + bilinen sonradan eklenen öznitelikler; bilinmeyen öznitelik → hata."""
    names = [f.name for f in dataclasses.fields(o)]
    known = set(names) | set(extra) | set(ignore)
    unknown = set(o.__dict__) - known
    assert not unknown, f"{type(o).__name__}: Rust'ta karşılığı olmayan öznitelik {sorted(unknown)}"
    return names


SHOP_DYN = dict(marks=list, stocked_out=lambda: False, unmet_frac=lambda: 0.0, peak_paid=lambda: 0.0,
                broke_months=lambda: 0)


def shop(s):
    out = {}
    for n in fields_of(s, extra=SHOP_DYN, ignore=("trapped",)):
        v = getattr(s, n)
        out[n] = v if isinstance(v, str) else num(v)
    for n, dflt in SHOP_DYN.items():
        v = getattr(s, n, None)
        v = dflt() if v is None else v
        out[n] = [num(x) for x in v] if n == "marks" else num(v)
    return out


def storer(s):
    out = {}
    for n in fields_of(s):
        v = getattr(s, n)
        if n == "season_history":
            out[n] = [num(x) for x in v]
        else:
            out[n] = v if isinstance(v, str) else num(v)
    return out


def rural(r):
    return {n: num(getattr(r, n)) for n in fields_of(r)}


def market(mk):
    c = dataclasses.asdict(mk.cfg)
    return dict(cfg={k: c[k] for k in MARKET_CFG}, day=mk.day, date=mk.date.isoformat(),
                harvest_day=getattr(mk, "harvest_day", None), harvest_ratio=opt(getattr(mk, "harvest_ratio", None)),
                rng=rng_state(mk.rng), rural=rural(mk.rural), shops=[shop(s) for s in mk.shops],
                storers=[storer(s) for s in mk.storers])


def pool(pl):
    fields_of(pl, extra=("reservation",))
    return dict(good=pl.good, recipe=dict(inputs=[[g, num(q)] for g, q in pl.recipe.inputs.items()],
                                          labor=num(pl.recipe.labor)),
                capacity=num(pl.capacity), cash=num(pl.cash), util=num(pl.util), output=num(pl.output),
                inputs=[[g, num(q)] for g, q in pl.inputs.items()], input_days=num(pl.input_days),
                margin_target=num(pl.margin_target), util_speed=num(pl.util_speed),
                util_hist=[num(x) for x in pl.util_hist], divs=num(pl.divs),
                reservation=num(getattr(pl, "reservation", 0.0)))


def dense(info: dict, keys):
    """(liman, mal) → (değer, gün) sözlüğü → pazar sırasına göre yoğun liste."""
    return [None if k not in info else [num(info[k][0]), info[k][1]] for k in keys]


M5_DYN = ("voy", "voy_overhead", "packet", "packet_hnews", "packet_harbor", "carried", "debt_pd")
M5_IGNORE = ("colleg", "network", "net_count", "house", "colleg_score")


def merchant(m: M5, keys):
    fields_of(m, extra=M5_DYN, ignore=M5_IGNORE)
    assert m.colleg is None and not m.house and not m.network, "taşınmayan dal"
    heard = [x for x in m.heard if isinstance(x, int)]
    hh = [x[1] for x in m.heard if isinstance(x, tuple) and x[0] == "h"]
    hn = [x[1] for x in m.heard if isinstance(x, tuple) and x[0] == "hn"]
    assert len(heard) + len(hh) + len(hn) == len(m.heard)
    voy = getattr(m, "voy", None)
    pk = getattr(m, "packet", None)
    return dict(
        id=mid(m.id), cash=num(m.cash), capacity=num(m.capacity), is_player=m.is_player, informed=m.informed,
        state=m.state, loc=m.loc, dest=gstr(m.dest), arrive_day=m.arrive_day, good=gstr(m.good), qty=num(m.qty),
        cost_basis=num(m.cost_basis),
        plan=None if m.plan is None else [m.plan[0], m.plan[1], num(m.plan[2]), num(m.plan[3])],
        wait=m.wait, risk_aversion=num(m.risk_aversion),
        obs=[[num(m.obs[k][0]), m.obs[k][1]] for k in keys], hist=[[num(x) for x in m.hist[k]] for k in keys],
        heard=sorted(heard), heard_h=sorted(hh), heard_hn=sorted(hn), born_day=m.born_day,
        start_capital=num(m.start_capital), divs=num(m.divs), marks=[num(x) for x in m.marks], level=m.level,
        imitation=num(m.imitation), overconf=num(m.overconf), p_hear=num(m.p_hear), dara=m.dara,
        known_loads=loads_map(m.known_loads), w_fund=num(m.w_fund), hnews=dense(m.hnews, keys),
        seen_buys=[[mid(b[0]), b[1], b[2], num(b[3]), b[4]] for b in m.seen_buys], reservation=num(m.reservation),
        harbor=dense(m.harbor, keys), home=m.home,
        record=[[x[0], num(x[1]), num(x[2]), num(x[3]), x[4]] for x in m.record],
        debt=None if m.debt is None else [num(m.debt[0]), m.debt[1], num(m.debt[2]), m.debt[3], num(m.debt[4])],
        debt_lost=m.debt_lost, broke=m.broke, emarks=[num(x) for x in m.emarks], retire=m.retire, v0=num(m.v0),
        t0=m.t0, ship=m.ship, on_order=m.on_order, exit_ship=num(m.exit_ship),
        voy=None if voy is None else [voy[0], voy[1], num(voy[2]), num(voy[3]), num(voy[4]), num(voy[5]), voy[6],
                                      voy[7], voy[8]],
        voy_overhead=num(getattr(m, "voy_overhead", 0)),
        packet=None if pk is None else [pk[0], pk[1], [[g, num(v)] for g, v in pk[2].items()]],
        packet_hnews=dense(getattr(m, "packet_hnews", {}), keys),
        packet_harbor=dense(getattr(m, "packet_harbor", {}), keys),
        carried=loads_map(getattr(m, "carried", {})), debt_pd=opt(getattr(m, "debt_pd", None)),
    )


WORLD_DONE = {
    "cfg", "rng", "ledger", "day", "date", "port_list", "good_list", "markets", "pools", "income_ref", "local_cons",
    "demand_L", "cls", "normal_wage", "wage_yday", "n_init", "_corsair_x", "_corsair_z", "corsair", "dep_log",
    "kapan_price", "kapan_quote", "kapan_bid", "kapan_traded", "kapan_today", "kapan_volume", "shop_exits",
    "shop_entries", "pool_investments", "current", "current_hist", "pool", "pending", "ship_list", "ship_px",
    "yard_next", "ship_log", "ships_lost", "_ship_buyers", "candidates", "_track_known", "trailing_median", "voy_log",
    "pop_roi", "entry_log", "_next", "entries", "exits", "bankruptcies", "reroutes", "debt_bankruptcies",
    "commissions", "ruin_days", "agg_hist", "public_agg", "_prev_val", "_gone_seen", "t0_day", "start_date",
    "pub_log", "cred_k", "cred_log", "_public_voy", "_public_route", "_last_voyage", "news", "loads", "harbor_news",
    "hnews_board", "port_buys", "_load_id", "_news_id", "departures", "flows", "loan_log", "fin_log", "loan_el",
    "route_stats", "lender_book", "lender_calib", "rationed", "merchants", "gone", "log",
}
# Taşınmayan dallar, sabit kalibrasyon ara ürünleri, teşhis alt sınıfı (DiagWorld) ve günlük geçici önbellekler
WORLD_IGNORE = {
    "days", "legs", "colleg_n", "colleg_in", "colleg_out", "colleg_ann", "colleg_contracts", "colleg_requests",
    "colleg_budget", "colleg_track", "colleg_routes", "colleg_share_now", "required_fleet", "spinup_fleet",
    "entry_pool", "pool_target", "supply", "bid_snap", "n_houses", "farm_sold", "_waiting_cache", "_committed_cache",
    "elog", "slog", "xlog", "born", "_sig", "_in_entry",
}


def by_market(d, keys, f=num):
    return [opt(d.get(k), f) for k in keys]


def port_map(d, f):
    return {p: f(v) for p, v in d.items() if p is not None}


def export(w: D5World) -> dict:
    unknown = set(w.__dict__) - WORLD_DONE - WORLD_IGNORE
    assert not unknown, f"D5World: Rust'ta karşılığı olmayan öznitelik {sorted(unknown)}"
    assert not getattr(w, "_ship_buyers", []), "_ship_buyers gün sonunda boş olmalı"
    keys = list(w.markets)
    L = w.ledger

    def route(r):
        return None if r is None else list(r)

    return dict(
        cfg=cfg_json(w.cfg),
        rng=rng_state(w.rng),
        ledger=dict(money_in={k: num(v) for k, v in L.money_in.items()},
                    money_out={k: num(v) for k, v in L.money_out.items()},
                    goods_in={f"{g}|{n}": num(v) for (g, n), v in L.goods_in.items()},
                    goods_out={f"{g}|{n}": num(v) for (g, n), v in L.goods_out.items()},
                    money_start=num(L._money_start), goods_start={g: num(v) for g, v in L._goods_start.items()}),
        day=w.day, date=w.date.isoformat(), port_list=list(w.port_list), good_list=list(w.good_list),
        market_keys=[list(k) for k in keys], markets=[market(w.markets[k]) for k in keys],
        pools=[[list(k), pool(pl)] for k, pl in w.pools.items()],
        income_ref=port_map(w.income_ref, lambda d: [num(d[k]) for k in CLASS_TEMPLATE]),
        local_cons=port_map(w.local_cons, lambda d: [num(d[g]) for g in GOODS]),
        demand_L=port_map(w.demand_L, lambda d: [num(d[g]) for g in GOODS]),
        cls=port_map(w.cls, lambda ks: [dict(name=k["name"], a=[num(k["a"]["WHT"]), num(k["a"]["BRL"])],
                                             gamma=[num(k["gamma"][c]) for c in CONSUMER_CATS],
                                             beta=[num(k["beta"][c]) for c in CONSUMER_CATS]) for k in ks]),
        normal_wage=port_map(w.normal_wage, num), wage_yday=port_map(w.wage_yday, num), n_init=w.n_init,
        _corsair_x=[num(w._corsair_x[r]) for r in REGIONS], _corsair_z=num(w._corsair_z),
        corsair=[num(w.corsair[r]) for r in REGIONS],
        dep_log=[[x[0], x[1], x[2], bool(x[3]), x[4], x[5]] for x in w.dep_log],
        kapan_price=by_market(w.kapan_price, keys), kapan_quote=by_market(w.kapan_quote, keys),
        kapan_bid=by_market(w.kapan_bid, keys), kapan_traded=by_market(w.kapan_traded, keys, bool),
        kapan_today=by_market(w.kapan_today, keys), kapan_volume=by_market(w.kapan_volume, keys),
        shop_exits=w.shop_exits, shop_entries=w.shop_entries, pool_investments=w.pool_investments,
        current=port_map(w.current, lambda d: [[num(d[k][0]), d[k][1]] for k in keys]),
        current_hist=port_map(w.current_hist, lambda d: [[num(x) for x in d[k]] for k in keys]),
        pool=port_map(w.pool, num),
        pending=[[x[0], x[1], route(x[2]), x[3]] for x in w.pending],
        ship_list=[dict(built=x["built"], owner=x["owner"], day=x["day"]) for x in w.ship_list],
        ship_px=num(w.ship_px), yard_next=num(float(w.yard_next)),
        ship_log=[[num(v) for v in x] for x in w.ship_log],
        ships_lost=w.ships_lost, _ship_buyers=[],
        candidates=[[c[0], num(c[1]), c[2], c[3]] for c in getattr(w, "candidates", [])],
        _track_known=w._track_known, trailing_median=num(w.trailing_median),
        voy_log=[[x[0], x[1], x[2], x[3], x[4], num(x[5]), num(x[6]), num(x[7]), num(x[8]), x[9], x[10], num(x[11])]
                 for x in w.voy_log],
        pop_roi=None if w.pop_roi is None else [num(x) for x in w.pop_roi],
        entry_log=[[x[0], x[1], num(x[2]), x[3], num(x[4])] for x in w.entry_log],
        _next=w._next, entries=w.entries, exits=w.exits, bankruptcies=w.bankruptcies, reroutes=w.reroutes,
        debt_bankruptcies=w.debt_bankruptcies, commissions=num(w.commissions), ruin_days=list(w.ruin_days),
        agg_hist=[num(x) for x in w.agg_hist], public_agg=opt(w.public_agg),
        _prev_val={str(mid(k)): num(v) for k, v in w._prev_val.items()}, _gone_seen=w._gone_seen,
        t0_day=w.t0_day, start_date=w.start_date.isoformat(),
        pub_log=[[x[0], opt(x[1]), num(x[2])] for x in getattr(w, "pub_log", [])],
        cred_k=opt(getattr(w, "cred_k", None)),
        cred_log=[[x[0], num(x[1]), num(x[2]), num(x[3]), x[4], opt(x[5])] for x in getattr(w, "cred_log", [])],
        _public_voy=num(getattr(w, "_public_voy", 0.0)), _public_route=route(getattr(w, "_public_route", None)),
        _last_voyage=[num(x) for x in getattr(w, "_last_voyage", (0.0, 0.0))],
        news=port_map(w.news, lambda ns: [[n[0], n[1], n[2], [[g, num(v)] for g, v in n[3].items()]] for n in ns]),
        loads=port_map(w.loads, loads_map),
        harbor_news=port_map(w.harbor_news, lambda ns: [[n[0], dense(n[1], keys)] for n in ns]),
        hnews_board=port_map(w.hnews_board, lambda ns: [[n[0], dense(n[1], keys)] for n in ns]),
        port_buys=port_map(w.port_buys, lambda bs: [[mid(b[0]), b[1], b[2], num(b[3]), b[4]] for b in bs]),
        _load_id=w._load_id, _news_id=w._news_id,
        departures=[[x[0], x[1], x[2], x[3], num(x[4]), x[5]] for x in w.departures],
        flows=[[list(k), num(v)] for k, v in w.flows.items()],
        loan_log=[[x[0], x[1], num(x[2]), x[3], num(x[4]), num(x[5]), x[6], bool(x[7]), bool(x[8]), opt(x[9])]
                  for x in w.loan_log],
        fin_log=[[x[0], x[1], num(x[2]), x[3], x[4], num(x[5])] for x in w.fin_log],
        loan_el=port_map(w.loan_el, num), loan_el_all=opt(w.loan_el.get(None)),
        route_stats=[[list(k), [v[0], num(v[1]), num(v[2]), num(v[3]), num(v[4])]] for k, v in w.route_stats.items()],
        lender_book={p: [[x[0], x[1], x[2], num(x[3]), mid(x[4])] for x in w.lender_book.get(p, [])]
                     for p in w.port_list},
        lender_calib=port_map(w.lender_calib, num), rationed=w.rationed,
        n_npc=list(w.log["n_npc"]),
        merchants=[merchant(m, keys) for m in w.merchants],
        gone=[[merchant(m, keys), d, num(c)] for m, d, c in w.gone],
    )


# --- özet -------------------------------------------------------------------------------------------------
def _ser(v, buf: bytearray):
    if v is None:
        buf += b"N"
    elif v is True:
        buf += b"T"
    elif v is False:
        buf += b"F"
    elif isinstance(v, (int, float)):
        buf += b"D" + struct.pack("<d", float(v))
    elif isinstance(v, str):
        if v in ("inf", "-inf", "nan"):
            buf += b"D" + struct.pack("<d", float(v))
        else:
            b = v.encode()
            buf += b"S" + struct.pack("<I", len(b)) + b
    elif isinstance(v, list):
        buf += b"L" + struct.pack("<I", len(v))
        for x in v:
            _ser(x, buf)
    elif isinstance(v, dict):
        buf += b"M" + struct.pack("<I", len(v))
        for k in sorted(v):
            b = k.encode()
            buf += struct.pack("<I", len(b)) + b
            _ser(v[k], buf)
    else:
        raise TypeError(type(v))


def _h(v):
    b = bytearray()
    _ser(v, b)
    return hashlib.sha1(b).hexdigest()[:16]


def digest(tree: dict) -> dict:
    out = {}
    for k in sorted(tree):
        if k in ("n_npc", "cfg"):
            continue
        v = tree[k]
        if k in ("merchants", "markets", "gone"):
            for i, x in enumerate(v):
                out[f"{k}/{i}"] = _h(x)
            out[f"{k}/len"] = str(len(v))
        else:
            out[k] = _h(v)
    return out


def make_cfg(setup: str, seed: int, years: int = 1):
    """`AD@cold`: snapshot ön koşusunun yapılandırması (`build_snapshot`: soğuk başlangıç, spin-up yok)."""
    import d5b3f_entry_diag as D
    name, _, mode = setup.partition("@")
    cfg = D.cfg_of(name, seed, years=years)
    if mode == "cold":
        cfg = dataclasses.replace(cfg, warm_start=False, seed=seed, years=cfg.warm_years, spinup_years=0.0)
    return cfg


def make_world(setup: str, seed: int, years: int = 1):
    return D5World(make_cfg(setup, seed, years))


def cfg_json(cfg) -> dict:
    return json.loads(json.dumps(dataclasses.asdict(cfg), default=list))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dump":
        w = make_world(sys.argv[2], int(sys.argv[3]))
        json.dump(export(w), open(sys.argv[4], "w"))
    elif cmd == "trace":
        setup, seed, days, outp = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        full_at = {int(x) for x in sys.argv[6].split(",")} if len(sys.argv) > 6 else set()
        w = make_world(setup, seed, years=max(1, days // 365 + 1))
        with open(outp, "w") as f:
            tree = export(w)
            f.write(json.dumps(dict(day=w.day, digest=digest(tree))) + "\n")
            if 0 in full_at:
                json.dump(tree, open(f"{outp}.day0.json", "w"))
            frm = int(os.environ.get("TRACE_FROM", 0))        # bu günden önce özet yazılmaz (hızlı ilerleme)
            for i in range(days):
                w.step()
                if i + 1 < frm and i + 1 not in full_at:
                    continue
                tree = export(w)
                f.write(json.dumps(dict(day=w.day, digest=digest(tree))) + "\n")
                if i + 1 in full_at:
                    json.dump(tree, open(f"{outp}.day{i + 1}.json", "w"))
    elif cmd == "cfg":                     # cfg SETUP SEED OUT.json [YIL]
        years = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        json.dump(cfg_json(make_cfg(sys.argv[2], int(sys.argv[3]), years)), open(sys.argv[4], "w"))
    elif cmd == "snap":                    # snap SETUP K OUT.json: Python snapshot'ının (pkl) dökümü
        import pickle
        from sim.world5 import snapshot_path
        cfg = make_cfg(sys.argv[2], 0)
        w = pickle.load(open(snapshot_path(cfg, int(sys.argv[3])), "rb"))
        json.dump(export(w), open(sys.argv[4], "w"))
    else:
        raise SystemExit(__doc__)
