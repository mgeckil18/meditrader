# Literature map

Each experiment is read against the literature: either it **reproduces a known result** (evidence the model is wired correctly), or it uses a **known method**. Results specific to this model are marked as such. Full table with more rows (Turkish): [`docs/research/simulation/13-literature-map.md`](../../docs/research/simulation/13-literature-map.md). There, ⚠️ marks citations recalled from memory and not yet checked against the source.

## Results reproduced

| Experiment | What appeared | Known result | Source |
|---|---|---|---|
| D2 · [01](../experiments/01-instant-information.md) | Price gap settles at transport cost; no opportunities with instant information | Law of one price, spatial price equilibrium; Grossman-Stiglitz paradox | Samuelson (1952) *AER* 42; Takayama & Judge (1971); Grossman & Stiglitz (1980) *AER* 70(3) |
| D3 · [02](../experiments/02-information-delay.md) | Information worth +11-23 pts/yr; reverting expectations damp herding | Economics of information; regressive expectations | Stigler (1961) *JPE* 69(3); Nerlove (1958) |
| D3 · [02](../experiments/02-information-delay.md) | Stale signals → simultaneous arrivals → price collapse | Cobweb | Kaldor (1934); Ezekiel (1938) *QJE* 52(2) |
| D3b · [03](../experiments/03-entry-speed.md) | Slow entry = rent; free entry = bond + risk; herd entry = cycle | Barriers to entry; normal profit; hog cycle | Bain (1956); Stigler (1968); Hanau (1928) |
| D4 | Linear Expenditure System + CES won; Labrousse effect appeared | LES; CES; Slutsky decomposition; Labrousse crises | Stone (1954) *EJ* 64; Arrow, Chenery, Minhas & Solow (1961); Labrousse |
| D4b · [04](../experiments/04-cloth-artifact.md) | In shortage, goods flow from poor to rich | Entitlement approach | Sen (1981) |
| D4c | Recipes, producer pools, wage stages | Input-output; putting-out system | Leontief (1936) *REStat* 18 |
| D5a | Institutional call market replaced four ad-hoc fixes | Market microstructure: call auction | O'Hara (1995) |
| D5b | Rival information prevents collapse; depth of thinking decides who earns | Heterogeneous agents; El Farol; level-k | Brock & Hommes (1998); Arthur (1994); Nagel (1995); Camerer, Ho & Chong (2004) |
| D5a2 | Retail margin at its theoretical value | Logit differentiated competition; Lerner index | Anderson, de Palma & Thisse (1992); Lerner (1934) |
| D5b3 | Entering cohort overestimates returns | Optimizer's curse; excess entry | Smith & Winkler (2006); Camerer & Lovallo (1999) *AER* 89 |
| D5b3g | Common entry/exit threshold → oscillation | Divergent cobweb; missing hysteresis band | Ezekiel (1938); Dixit (1989) |
| M2 · [05](../experiments/05-port-time.md) | Port time drives voyage tempo | Port time dominates pre-industrial shipping productivity | Jones (1998) |

## Methods used

| Method | Where | Source |
|---|---|---|
| Pattern-oriented modelling: choose structures by how many observed patterns they reproduce at once; tune last | Whole experiment programme | Grimm et al. (2005); Fagiolo et al. (2007) on stylized facts |
| Credibility weighting of a merchant's own record vs the public record | Entry/exit beliefs (D5b3h) | Bühlmann (1967); Bühlmann & Straub (1970) |
| Warm-up / burn-in with snapshots chosen by a rule fixed in advance | All runs since D5b3g | Standard simulation practice (Law & Kelton) |
| Marginal value theorem as a departure rule | Port time (M2) | Charnov (1976) |
| Shrinkage of noisy estimates toward a prior | Proposed fix for wandering cargo (M2) | Smith & Winkler (2006) |

## Results specific to this model
- The Zeno artifact: proportional sharing in the call market never empties a cargo ([D5b2](../../docs/experiments/D5b2.md)).
- The cloth seasonality artifact ([04](../experiments/04-cloth-artifact.md)).
- The size of the value of information (+11 to +23 points a year) and of survivorship bias under herd entry (12-22% seen vs 1-2% actual).
- Fresher information did not reduce reroutes in the multi-port world; it made real gaps more visible ([M2 · I1](../../docs/experiments/M2.md)).
- Storers have no capital entry or exit, and most of them are broke in every variant ([05](../experiments/05-port-time.md)).
