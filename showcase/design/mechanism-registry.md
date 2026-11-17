# Mechanism registry

Every mechanism in the simulation records **where it came from** and **how settled it is**, so that any of it can be re-examined later. This is a curated English selection. The full registry (Turkish, ~140 rows, including removed and diagnostic-only mechanisms) is [`docs/design/mechanism-registry.md`](../../docs/design/mechanism-registry.md).

**Origin**
- **F**: Furkan's idea or decision (the designer).
- **C**: proposed or designed by Claude (AI assistant).
- **L**: adapted from the literature (source given).

Most rows are mixed. "F idea, C design" means Furkan decided *what* and Claude proposed *how* (formula, bounds, coefficients).

**Status**
- **Decided**: explicitly approved by Furkan; numbered decision K-xxx in [`docs/decisions.md`](../../docs/decisions.md).
- **Supported**: worked in an experiment and was not objected to. Never treated as final; it will be re-examined.
- **Experimental**: in one experiment only, or behind a flag that is off by default.
- **Proxy**: a temporary value or form, flagged for replacement by a historical or emergent one.

**Code**: Python oracle `sim/` (frozen) and Rust `core/medi-core/src/` (where ported). The Rust core carries everything in the current base setup plus all M-series mechanisms.

## Markets and prices

| Mechanism | Origin | Experiment | Status | Code |
|---|---|---|---|---|
| Urban demand pool (elasticity, budget) | C; L (King-Davenant; Stone) | D1 | Supported | `sim/model.py`, `market.rs` |
| Different elasticities by good; subsistence floor | F | D1, D4 | Decided | `sim/multigood.py` |
| Storer: fundamentalist, harvest news, median "usual price", carry | C; L (Williams & Wright; Deaton & Laroque) | D1f, D1g | Supported | `sim/model.py`, `market.rs` |
| Institutional wholesale call market (*kapan*), one clearing price a day | C proposal; F decision rule | D5a | Decided (K-013) | `sim/world5.py` `_kapan`, `world/kapan.rs` |
| Competitive retail: price cuts and rises must have a competitive cost | F | D5a2 | Decided (K-016) | `world/kapan.rs` |
| Logit customer shares with 30-day inertia | C; L (McFadden; Anderson, de Palma & Thisse) | D5a2 | Supported (β = 12 is a proxy) | `world/kapan.rs` |
| Lerner margin μ = 1/(ε − 1) | C; L (Lerner 1934) | D5a2 | Supported | `world/kapan.rs` |
| Dust lot: cargo under 1 unit is written off | C (diagnosis) | D5b2 | Bug fix (Zeno artifact) | `world/trade.rs` |

## Demand and production

| Mechanism | Origin | Experiment | Status | Code |
|---|---|---|---|---|
| Linear Expenditure System + CES (two-stage budgeting) | C; L (Stone; Deaton & Muellbauer) | D4 | Supported | `sim/multigood.py` |
| Urban income classes (rich / middle / poor) | F idea; C design | D4b | Decided | `sim/multigood.py`, `world/kapan.rs` |
| Cloth split into coarse and fine | F | D4b, D4c | Decided | map data |
| Production chains, shared raw materials, producer pools | F idea; C design (Leontief recipes) | D4c | Decided | `sim/production.py`, `world/kapan.rs` |
| Wages and the Labrousse multiplier | C; L (Labrousse) | D4c | Experimental | `sim/production.py`, `world/kapan.rs` |

## Merchants, information and expectations

| Mechanism | Origin | Experiment | Status | Code |
|---|---|---|---|---|
| Greedy core decision rule | C (D2 race) | D2 | Supported | `world/trade.rs` |
| Information carried by ship + harbour rumour | F idea; C design | D3 | Decided | `world/info.rs` |
| Lognormal belief + reversion to the usual price | F (lognormal); C (reversion, median) | D3 | Supported | `world/trade.rs` |
| Free entry/exit tied to the bond rate | F frame; C mechanism | D3b | Decided (direction Y10b) | `world/entry.rs` |
| Merchant diversity: depth of thinking, imitation, overconfidence, wealth-dependent risk | F idea; C design; L (Camerer, Ho & Chong; Odean; Arrow-Pratt; Roy) | D5b | Decided (K-014); coefficients are proxies | `world/info.rs`, `world/trade.rs` |
| Rumour "X loaded Z for Y" | F | D5b | Decided (K-014) | `world/info.rs` |
| Price current: a port's public price sheet updated by ship news | C; L (McCusker & Gravesteijn 1991) | D5b3 | Experimental | `world/info.rs` |
| Credibility weighting of own record (Bühlmann-Straub, k from data) | L (Bühlmann & Straub 1970); C | D5b3h | Supported | `world/entry.rs` |
| Ships relay every price they know (`info_relay`); couriers between neighbours (`courier_every`) | F direction; C design | M2 · I1 | Experimental | `world/info.rs` |

## Finance and entry

| Mechanism | Origin | Experiment | Status | Code |
|---|---|---|---|---|
| *Colleganza*: port investors fund merchants short of cash | F; C design; L (González de Lara) | D5b3 | Experimental | `sim/world5.py` (not ported) |
| Term debt from the port pool, leverage cap 1 | F | D5b3c | Experimental | `world/finance.rs` |
| Voyage-based lender pricing | F idea; C mechanics; L (Diamond 1984) | D5b3d | Experimental | `world/finance.rs` |
| Snapshot warm start chosen by a fixed rule | F idea; C rule | D5b3g | Experimental | `world/snapshot.rs` |
| Public record of total capital returns, bankrupts and leavers included | F; C | D5b3g | Experimental | `world/entry.rs` |
| Real-options band on entry/exit | C; L (Dixit 1989) | D5b3g | **Proxy** (to be replaced by an emergent mechanism) | `world/entry.rs` |

## Sea, ships and ports

| Mechanism | Origin | Experiment | Status | Code |
|---|---|---|---|---|
| Hazard per leg and region, seasonal | F idea (K-030); L (Ceccarelli 2007) | D5b3i | Experimental | `world/ships.rs` |
| Corsair pressure: log-AR(1) + jumps per region | C; L (premium jumps, Ceccarelli 2007) | D5b3i | Experimental; form chosen by Claude | `world/ships.rs` |
| Ship market: ageing, sinking, second-hand call market, shipyard, foreign ships | F (K-032); C design; L (Tobin's q; Dixit hysteresis) | D5b3j | Experimental | `world/ships.rs` |
| Data-driven map (`core/maps/*.json`) | F (K-035); C design | M0, M1 | Experimental; data are proxies | `map.rs` |
| Duration-dependent leg hazard; ballast risk; corsair prizes | F asked for the fix; C form | M1.4 | Supported | `world/ships.rs`, `world/trade.rs` |
| Handling speed by port tier (`handling`) | F direction; C design | M2.1 | Experimental; levels are proxies | `world/trade.rs`, `world/kapan.rs` |
| Departure by marginal value theorem (`fill_decision`) | C; L (Charnov 1976) | M2.1 | Experimental | `world/trade.rs` |
| Cargo spoilage on board (`cargo_spoil`) | F | CS | Experimental; values are rough proxies | `world/trade.rs` |
| Ship cost package (`port_costs`): harbour dues, customs on entry, crew, wear | F | PC, PF | Experimental; levels within historical ranges | `world/trade.rs`, `world/info.rs` |
| Mixed cargo (`mixed`): hold split into lots by destination | F (K-040) | MX | Experimental | `world/trade.rs`, `world/types.rs` |
| Route commitment (`commit`); merging lots of the same good | C (MX diagnosis) | MX-v3, v4 | Bug fix in nature | `world/info.rs`, `world/trade.rs` |
| Weighing rate for valuable goods (`weigh_rate`) | F (pepper example); C levels | MW | Experimental; levels are proxies | `world/trade.rs` |
| Sale agreement with storers (`sale_contract`) | F | MK | Experimental | `world/trade.rs` |
