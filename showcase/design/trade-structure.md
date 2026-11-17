# Trade structure

> Status: direction decided (port hierarchy first, then the full map). M0 and M1 are done; M2 is in progress.
> Source (Turkish): [`docs/design/trade-structure.md`](../../docs/design/trade-structure.md); history: [port hierarchy](../../docs/research/history/port-hierarchy-16c.md), [shipping scale](../../docs/research/history/shipping-scale-16c.md)

## What sets profitability, and what doesn't

Five things obviously matter: ship life, voyage frequency, cost of trade, return per voyage and ship loss. They are not of the same kind:
- **Exogenous** (physical, technological): ship life, loss hazard, time in port, time at sea. **Taken from history.**
- **Endogenous** (emerge in the model): voyage frequency, return per voyage, profitability. These are **validation targets, not tuning knobs.**

**The level of profit is set by entry.** With free entry, returns fall to the cost of capital plus a risk premium ([experiment 03](../experiments/03-entry-speed.md)). In one run, 28% annual ship loss still left returns at the hurdle: the risk moved into freight rates and price gaps. The five dimensions decide other things: the size of price gaps and freight, fleet size, turnover, volatility, and who wins. For profitability to look historical, the entry side must be historical too: interest, risk attitudes, barriers (capital, connections, state convoy auctions (*muda*), nobility).

**Design consequence:** a long route cannot stay more profitable on its own; others enter and close the gap. Late-game profit has to come from rents behind barriers: a large capital threshold, reputation, credit, consuls, news networks, *muda* access. The player earns more by winning the right to enter, not by discovering the route.

## What a shipment is

Cargo size, duration, and kind of goods. Around it: buying, selling, loading and unloading, risk management. Three corrections to the naive picture:
1. **Capacity is not always binding.** Bulk grain fills the hold; pepper ties up capital first. Historically, spare space was filled with mixed cargo and other merchants' goods, and filling a ship took time.
2. **Risk does not follow from duration alone.** Valuable cargo attracts corsairs; perishables lose value; the same route's risk changes year to year.
3. **Duration = finding cargo + loading + waiting for wind + sea + quarantine/customs + unloading and finding buyers.** The early engine modelled only the sea. This is why its ships sailed 3-5 times more often than historical ones ([experiment 05](../experiments/05-port-time.md)).

**Principle:** variety comes from each option having a different trade-off, not from the number of options. Each dimension is added as its own step and measured.

## Ports have three properties

| Property | Content |
|---|---|
| Physical harbour | Largest ship that can berth (or needs lighters), loading speed, lighterage cost |
| Market | Population and classes, hinterland production, consumption. Full market (kapan, shops, storers) for large and medium ports; a light market for small ones |
| Institutions | Customs, staple rights (Gulf of Venice), quarantine, privileges |

"Large / medium / small" summarises the three. Alexandria (large market, poor harbour) and Split (small town, transit hub after 1592) can only be represented this way.

## Roadmap

| Step | Content | Status |
|---|---|---|
| M0 | Map read from data (`core/maps/*.json`); the default reproduces the old 6-port world exactly | Done |
| M1 | Full map v1: the Mediterranean east of Genoa, 20 large and medium ports, rough data (flagged proxies); 9 goods | Done |
| M2 | Time in port, port physical properties, mixed cargo, ship types | In progress ([experiment 05](../experiments/05-port-time.md)) |
| M3 | Small ports region by region; light market | Planned |
| M4 | Freight and orders: cargo on other people's ships, storers' orders | Planned |
| M5 | Black Sea; caravan borders as external supply and demand | Planned |
| M6 | Institutions and historical events: staple, quarantine, Chios 1566, Cyprus 1571, Split 1592, Livorno 1593 | Planned |
