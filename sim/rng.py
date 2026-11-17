"""Seeded per-subsystem PRNG streams (adding a draw in one subsystem never shifts another's sequence).

(Original notes in Turkish below.)

Seed'li, alt sisteme özel PRNG akışları (bkz. docs/design/determinism.md).

Her alt sistem kendi akışını adıyla ister. Bir alt sisteme yeni bir zar atışı
eklemek diğerlerinin sayı dizisini kaydırmaz.
"""
import zlib

import numpy as np


class RngStreams:
    def __init__(self, seed: int):
        self.seed = seed
        self._streams: dict[str, np.random.Generator] = {}

    def get(self, name: str) -> np.random.Generator:
        if name not in self._streams:
            # crc32 Python'un hash()'inden farklı olarak çalıştırmalar arasında sabittir.
            ss = np.random.SeedSequence([self.seed, zlib.crc32(name.encode())])
            self._streams[name] = np.random.default_rng(ss)
        return self._streams[name]
