# Experiments

The economy is built by experiment, not by tuning. Each experiment asks one structural question ("does information delay keep opportunities alive?"), swaps candidate mechanisms from the literature into one *slot* of the model, and compares them on fixed criteria. Parameters stay at literature or default values. Calibration is left for the end, when the structure is settled.

Full log (Turkish, every attempt including failed ones): [`docs/process/experiment-log.md`](../../docs/process/experiment-log.md). Reports: [`docs/experiments/`](../../docs/experiments/).

## Method

**Slots, not whole models.** Most academic models cover one part of the system: usually a single central market, without geography or information delay. So the simulation is split into slots (price formation, merchant decision rule, expectations, information spread, storage, entry and exit), and each experiment races candidates in one slot while the others stay fixed at the current best.

**Criteria, in order:**

| Group | Example |
|---|---|
| Stability | no price explosions, money and goods ledger balanced every day, same seed gives the same run |
| Historical patterns (qualitative) | convex price response to bad harvests, post-harvest cheapness, lasting but bounded price gaps between ports |
| Game-critical | how long opportunities last, how many there are, how readable volatility is, what an exploit bot earns |
| Cost | run time, code complexity |

**Phenomenon or artifact?** When an unexpected dynamic appears, it is classified before anything is changed. It is kept if it is a real economic phenomenon: realistic micro-behaviour, historically plausible size, not leaning on an artificial bound, readable by a player. Pork cycles, cobwebs, herding and survivorship bias are wanted. An artifact is found in the code and fixed.

**Attribution.** When a known result appears (law of one price, entry eliminating rents, Grossman-Stiglitz), it is written as "reproduces the known result X (source)". "We found" is used only for findings specific to this model, such as an engine artifact.

**Measurement without the agents' biases.** Agents decide on survivor statistics, like real merchants. Our measurements come from the ledger at system level, including those who went bankrupt.

## Selected experiments

| # | Question | Result | Engine |
|---|---|---|---|
| [01](01-instant-information.md) | Does trade between two ports close price gaps, and do opportunities survive? | Reproduces the law of one price. With instant information, competent NPCs leave no opportunities: a greedy player bot earns 2.5-3.6% a year. | Python |
| [02](02-information-delay.md) | Does realistic information delay keep opportunities alive? | Opportunity days rise from 0.3% to 20-40%. Better information is worth +11 to +23 points of return a year. | Python |
| [03](03-entry-speed.md) | Does free entry tied to the bond rate produce "bond + risk premium" returns? | Yes, at moderate entry speed (sector return 6-11%). Entry speed sets the rent; survivor statistics overstate returns. | Python |
| [04](04-cloth-artifact.md) | Is a seasonal swing in cloth demand a real income effect? | No. One ablation showed it was an engine artifact; fixed, the swing fell from 2.38 to 1.03. | Python |
| [05](05-port-time.md) | Why do ships sail 3x more than historical ships? | Costs shrank the fleet but did not change behaviour. Port time and mixed cargo moved the tempo toward history: still 2x too fast. | Rust |

The first four ran on the Python reference engine; the fifth on the Rust core, which reproduces the Python engine bit for bit before any new mechanism is switched on ([engineering](../engineering/determinism-and-rust-port.md)).

## Two engine bugs worth knowing about

- **Zeno artifact (D5b2).** In some runs, 15-25 merchants sat for years in one port "selling" pepper. Diagnosis: the wholesale market shares sales in proportion to remaining cargo, so remaining cargo shrank geometrically and never reached zero. Merchants held 0.0001-0.7 units and never left the selling state. Fix: under one unit, the remainder is written off (`dust_lot`, logged in the ledger). An earlier report's "thin market trap" turned out to be entirely this bug. [Report](../../docs/experiments/D5b2.md) (Turkish).
- **Sale-agreement leftovers (M2, MK).** A lot closed at the dust threshold while a tiny agreement with a storer was still open. The next lot used the old market's storer index and the run crashed. Fix: remaining contracted goods are delivered when a lot closes; departures and lot switches with an open agreement are now assertions. [Report](../../docs/experiments/M2.md) (Turkish).

## Reproducing

Every page lists the command that produces its numbers. The figures here are built from those outputs:

```
python3 experiments/d2_two_ports.py        # ~3 min
python3 experiments/d3_information.py      # ~4 min
python3 experiments/d3b_entry_exit.py      # ~12 min
python3 experiments/d4b_classes.py         # ~1 min
bash core/tools/run_m.sh PF                # Rust; also MX, MW (~10 min each)
python3 showcase/experiments/make_figures.py
```
