"""Money and goods accounting: money is integer, totals change only through named sources and sinks; checked every tick.

(Original notes in Turkish below.)

Para ve mal muhasebesi (spec §6.11, desen P10).

Para tamsayı (soldo). Sistemdeki toplam para sadece adı konmuş musluk ve
yutaklardan değişebilir; her tick doğrulanır.
"""
from collections import defaultdict


class LedgerError(AssertionError):
    pass


class Ledger:
    def __init__(self):
        self.money_in = defaultdict(int)     # musluk adı -> toplam soldo
        self.money_out = defaultdict(int)    # yutak adı -> toplam soldo
        self.goods_in = defaultdict(float)   # (mal, kaynak) -> miktar
        self.goods_out = defaultdict(float)
        self._money_start = None
        self._goods_start = {}

    def start(self, money_total: int, goods_totals: dict[str, float]):
        self._money_start = money_total
        self._goods_start = dict(goods_totals)

    def money_source(self, name: str, amount: int):
        self.money_in[name] += amount

    def money_sink(self, name: str, amount: int):
        self.money_out[name] += amount

    def goods_source(self, good: str, name: str, qty: float):
        self.goods_in[(good, name)] += qty

    def goods_sink(self, good: str, name: str, qty: float):
        self.goods_out[(good, name)] += qty

    def check(self, money_total: int, goods_totals: dict[str, float]):
        expected = self._money_start + sum(self.money_in.values()) - sum(self.money_out.values())
        if money_total != expected:
            raise LedgerError(f"para tutarsız: {money_total} != {expected}")
        for good, total in goods_totals.items():
            exp = (self._goods_start.get(good, 0.0)
                   + sum(v for (g, _), v in self.goods_in.items() if g == good)
                   - sum(v for (g, _), v in self.goods_out.items() if g == good))
            if abs(total - exp) > 1e-6 * max(1.0, abs(exp)):
                raise LedgerError(f"{good} tutarsız: {total} != {exp}")
