"""Generates NumPy/Python fixtures for the Rust numeric and RNG tests (core/fixtures/*.json). Usage: python3 core/tools/make_fixtures.py

(Original notes in Turkish below.)

Rust çekirdeğinin sayısal ve RNG testleri için NumPy/Python'dan fikstür üretir (core/fixtures/*.json).

Kullanım: python3 core/tools/make_fixtures.py
"""
import json
import math
import pathlib
import random
import zlib

import numpy as np

OUT = pathlib.Path(__file__).resolve().parents[1] / "fixtures"
OUT.mkdir(exist_ok=True)


def f(x):
    return x.hex() if isinstance(x, float) else x


def rng_fixture():
    cases = []
    for seed in (0, 1, 7, 1000, 1002, 123456, 4_000_123):
        for name in ("voyage", "market", "entry_exit", "merchants_init"):
            g = np.random.default_rng(np.random.SeedSequence([seed, zlib.crc32(name.encode())]))
            st = g.bit_generator.state["state"]
            draws = []
            for i in range(400):
                k = i % 11
                if k == 0:
                    draws.append(["random", [], f(float(g.random()))])
                elif k == 1:
                    draws.append(["normal", [0.0, 0.25], f(float(g.normal(0, 0.25)))])
                elif k == 2:
                    draws.append(["standard_normal", [], f(float(g.standard_normal()))])
                elif k == 3:
                    draws.append(["uniform", [0.5, 1.5], f(float(g.uniform(0.5, 1.5)))])
                elif k == 4:
                    hi = [3, 6, 31, 61, 5476][i % 5]
                    draws.append(["integers", [0, hi], int(g.integers(hi))])
                elif k == 5:
                    lam = [0.3, 2.5, 9.99, 10.0, 37.2, 400.0][i % 6]
                    draws.append(["poisson", [lam], int(g.poisson(lam))])
                elif k == 6:
                    a, b = [(2, 5), (2, 2)][i % 2]
                    draws.append(["beta", [a, b], f(float(g.beta(a, b)))])
                elif k == 7:
                    n = [1, 2, 9, 45, 180][i % 5]
                    draws.append(["permutation", [n], [int(v) for v in g.permutation(n)]])
                elif k == 8:
                    draws.append(["integers", [30, 61], int(g.integers(30, 60 + 1))])
                elif k == 9:
                    draws.append(["standard_exponential", [], f(float(g.standard_exponential()))])
                else:
                    draws.append(["random", [], f(float(g.random()))])
            end = g.bit_generator.state
            cases.append(dict(seed=seed, name=name, crc=zlib.crc32(name.encode()), init_state=str(st["state"]),
                              init_inc=str(st["inc"]), draws=draws, end_state=str(end["state"]["state"]),
                              end_has=end["has_uint32"], end_u=end["uinteger"]))
    json.dump(cases, open(OUT / "rng.json", "w"))


def math_fixture():
    r = random.Random(5)
    sums, means, stds, medians, rounds, mods, fdivs = [], [], [], [], [], [], []
    for n in list(range(0, 20)) + [31, 64, 127, 128, 129, 200, 300, 777]:
        for _ in range(3):
            v = [r.uniform(-1e3, 1e5) * (10 ** r.randint(-8, 3)) for _ in range(n)]
            sums.append([[f(x) for x in v], f(float(sum(v)))])
            if n:
                means.append([[f(x) for x in v], f(float(np.mean(v)))])
                stds.append([[f(x) for x in v], f(float(np.std(v)))])
                medians.append([[f(x) for x in v], f(float(np.median(v)))])
    for _ in range(3000):
        x = r.uniform(-1e6, 1e6) if r.random() < 0.7 else r.randint(-1000, 1000) + 0.5
        rounds.append([f(x), round(x)])
        a, b = r.uniform(-1e3, 1e3), r.choice([365.0, -7.5, 240000.0, 3.0])
        mods.append([f(a), f(b), f(a % b)])
        fdivs.append([f(a * 1e3), f(b), f((a * 1e3) // b)])
    json.dump(dict(sums=sums, means=means, stds=stds, medians=medians, rounds=rounds, mods=mods, fdivs=fdivs),
              open(OUT / "math.json", "w"))


if __name__ == "__main__":
    rng_fixture()
    math_fixture()
    print("ok", list(OUT.iterdir()))
