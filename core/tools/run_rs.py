"""Runs D5b3f-style experiments with the Rust core (same outputs as the Python script); `compare` checks Rust vs Python end to end.

(Original notes in Turkish below.)

D5b3f deneyini Rust çekirdeğiyle koşar (`experiments/d5b3f_entry_diag.py`'nin yerine geçer; aynı çıktı).

Python yalnızca yapılandırmayı kurar (`cfg_of`) ve işleri dağıtır; snapshot üretimi ve koşu `core/target/release/medi`.
Çıktı klasörü ve dosya adları Python betiğiyle aynı (`experiments/out/$DIAG_OUT/AD_SEED.json`); analiz betikleri
değişmeden okur. Rust snapshot'ları Python'unkilerin yanında: `<anahtar>_<k>.rs.json` (+ `.rs.meta.json`).

Kullanım:
  python3 core/tools/run_rs.py 10 VRS-B-R1-O3,F-B-R1-O3        # YEARS, DIAG_OUT, NPROC (varsayılan 4) ortam değişkenleri
  python3 core/tools/run_rs.py compare KURULUM SEED YIL       # Python run() ile Rust çıktısını karşılaştır
Önce: `cargo build --release` (core/).
"""
import json
import math
import os
import pathlib
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "core" / "tools"))
BIN = ROOT / "core" / "target" / "release" / "medi"


def rs_snapshot_path(cfg, k):
    from sim.world5 import snapshot_path
    p = snapshot_path(cfg, k)
    return p.with_name(p.stem + ".rs.json")


def write_cfg(cfg, d: pathlib.Path) -> pathlib.Path:
    from state_io import cfg_json
    p = d / f"cfg_{cfg.seed}_{abs(hash(json.dumps(cfg_json(cfg), sort_keys=True)))}.json"
    p.write_text(json.dumps(cfg_json(cfg)))
    return p


def sh(args):
    r = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(map(str, args))}\n{r.stderr}")
    return r.stdout.strip()


def ensure_snapshots(cfgs, tmp, nproc):
    """Eksik Rust snapshot'larını paralel üretir (kurulum × k)."""
    need = {}
    for cfg in cfgs:
        if cfg.warm_start:
            k = cfg.seed % cfg.warm_n
            p = rs_snapshot_path(cfg, k)
            if not p.exists():
                need[p] = (cfg, k)
    with ThreadPoolExecutor(nproc) as ex:
        for p, out in zip(need, ex.map(lambda it: sh([BIN, "snapshot", write_cfg(it[0], tmp), it[1], it[2]]),
                                       [(c, k, p) for p, (c, k) in need.items()])):
            print("snapshot", p.name, out, flush=True)


def run_jobs(names, seeds, out_dir: pathlib.Path, nproc: int):
    import d5b3f_entry_diag as D
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(n, s) for n in names for s in seeds if not (out_dir / f"{n}_{s}.json").exists()]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        cfgs = {j: D.cfg_of(*j) for j in jobs}
        ensure_snapshots(cfgs.values(), tmp, nproc)

        def one(j):
            cfg = cfgs[j]
            args = [BIN, "run", write_cfg(cfg, tmp), j[0], out_dir / f"{j[0]}_{j[1]}.json"]
            if cfg.warm_start:
                args.append(rs_snapshot_path(cfg, cfg.seed % cfg.warm_n))
            return sh(args)

        with ThreadPoolExecutor(nproc) as ex:
            for res in ex.map(one, jobs):
                print(res, flush=True)


def _norm(x):
    return float(x) if isinstance(x, str) and x in ("inf", "-inf", "nan") else x


def diff(a, b, path="", out=None, limit=20):
    """İki çıktı ağacının farkları (NaN = NaN; "inf" dizgisi = sonsuz; True = 1.0)."""
    out = [] if out is None else out
    a, b = _norm(a), _norm(b)
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a) != list(b):
            out.append((path, "anahtarlar", list(a), list(b)))
        for k in a:
            if k in b:
                diff(a[k], b[k], f"{path}/{k}", out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, "uzunluk", len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diff(x, y, f"{path}/{i}", out, limit)
    elif isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        pass
    elif a != b:
        out.append((path, a, b))
    return out


def compare(name, seed, years):
    """Aynı kurulum ve seed: Python `run()` (DiagWorld) ile Rust `medi run` çıktısı birebir aynı mı."""
    os.environ["YEARS"] = str(years)
    import d5b3f_entry_diag as D
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        D.OUT = tmp / "py"
        D.OUT.mkdir()
        D.run((name, seed))
        cfg = D.cfg_of(name, seed, years=years)
        ensure_snapshots([cfg], tmp, 1)
        args = [BIN, "run", write_cfg(cfg, tmp), name, tmp / "rs.json"]
        if cfg.warm_start:
            args.append(rs_snapshot_path(cfg, cfg.seed % cfg.warm_n))
        sh(args)
        a = json.load(open(D.OUT / f"{name}_{seed}.json"))
        b = json.load(open(tmp / "rs.json"))
    d = diff(a, b)
    print(f"{name} seed {seed} {years} yıl:", "EŞİT" if not d else "FARKLI")
    for x in d:
        print("  ", x)
    return not d


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        sys.exit(0 if compare(sys.argv[2], int(sys.argv[3]), int(sys.argv[4])) else 1)
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    out = ROOT / "experiments" / "out" / os.environ.get("DIAG_OUT", "d5b3f")
    run_jobs(sys.argv[2].split(","), range(int(sys.argv[1])), out, int(os.environ.get("NPROC", 4)))
