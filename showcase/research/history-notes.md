# History notes

The model's exogenous inputs (voyage times, loss rates, costs, consumption) come from history; its endogenous outputs (voyage frequency, returns, fleet size) are checked against it. These notes summarise what the engine currently relies on.

**Source flags** (from the Turkish research files): 🔎 = taken from a search summary or a secondary review, not yet read in the original; ⚠️ = Claude's estimate or unverified. All values below are drafts that steer the engine, not final calibration.

## Starting point: around 1560
- The Venetian state galley convoys (*muda*) ran continuously in 1315-1533; by 1560 most lines had closed and round-hulled sailing ships had taken over ([overview](../../docs/research/history/mediterranean-16c-overview.md)). So the player starts by renting cargo space on private sailing ships; *muda* is atmosphere, or a mechanic only with an earlier start date.
- Turning points to seed the event inventory: Chios 1566, Cyprus and Lepanto 1571, the Ottoman-Spanish truce of 1581, Split as a transit hub from 1592, Livorno 1593 (roadmap step M6).

## Ships and voyages ([shipping scale](../../docs/research/history/shipping-scale-16c.md))
| Finding | Source |
|---|---|
| A Ragusan ship could make two or three voyages a year | Braudel 🔎 |
| *Santa Maria Maddalena* log: 1579, two Apulia → Naples grain voyages of about a month each; 1581, Sicily → Genoa in 72 and 63 days | *Business History* 66(3) 🔎 |
| Most of a voyage was spent in port: buying, selling, loading, waiting | Braudel 🔎; Gluzman 2021 🔎 |
| Venice-Levant round trip usually 7.5-10 months including idle time in port | Gluzman 2021 🔎 |

**Inference** ⚠️: about 2-4 voyages a year for a large ship on a long route. The early model made 3-5 times more. The gap was time in port, not sea time.

## Losses and insurance ([maritime risk](../../docs/research/history/maritime-risk-16c.md), [ship life and piracy](../../docs/research/history/ship-life-piracy-16c.md))
| Finding | Source |
|---|---|
| Distance was not the main driver of premiums; risk concentrated on coasts, harbours and corsair zones | Ceccarelli 2007 |
| Piracy and war made up at least half the premium; an unarmed ship paid about twice a galley's rate | Ceccarelli 2007 |
| Premiums jumped with news: Barcelona → Messina 1461 went 3.5% → 10-12% → 4% within two weeks | Ceccarelli 2007 |
| Genoa 1564-72: 757 policies; insurers a closed group of merchants insuring each other | Iodice 2023 ⚠️ |
| Venice 1592-1609: about 37 sinkings or captures a year in notarial records | Tenenti 1959, via Braudel |
| "Century of corsairs" 1580-1680, with an explosion in 1580-1620; "no merchants, no corsairs" | Fontenay; Braudel 🔎 |
| Ship life around 10 years; annual fleet loss 10-13% including war years | Gluzman 🔎 |

**Inference** ⚠️: per-voyage loss of 2-4% at 2-4 voyages a year means losing 4-12% of the fleet a year, at the upper end in the late century. Peace-time premiums (1-2.5% per voyage) include natural hazard, not only corsairs.

## Consumption ([consumer profiles](../../docs/research/history/consumer-profiles-16c.md))
Five class templates and six city tables (around 1560) built on historical consumption baskets and welfare ratios (Phelps Brown & Hopkins 1956; Allen 2001). They feed the Linear Expenditure System parameters of urban demand ([experiment 04](../experiments/04-cloth-artifact.md)).

## Ports ([port hierarchy](../../docs/research/history/port-hierarchy-16c.md))
Port type is not one dimension: a port has a physical harbour, a market and institutions. Alexandria was a large market with a poor harbour. Split was a small town that became a transit hub. This is why the engine models ports with three properties ([trade structure](../design/trade-structure.md)). Populations and production per port have no single source; the 20-port map uses rough values flagged as temporary proxies.

## Not found yet
Venetian premium series 1590-1610 (Tenenti 1985); captures per year by year; Ragusan voyage durations (Tadić); historical weighing capacity at the scales of the Fondaco or Cairo (needed to replace the temporary weighing-rate proxy of experiment 05).
