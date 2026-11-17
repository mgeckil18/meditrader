# Information model

> Status: the expectation part (lognormal belief + reversion) is implemented and was the best of five candidates in [experiment 02](../experiments/02-information-delay.md). Display modes are design only.
> Source (Turkish): [`docs/design/information-model.md`](../../docs/design/information-model.md)

**Principle:** information travels physically and goes stale. This is the core of the design. The player and every NPC use the same data.

## A price is a distribution, not a number

"Wheat is 3 lire in Edirne" heard a week ago is shown as a band around 3, not as 3.

- **Lognormal, not normal:** prices are positive and move proportionally. A doubling is far more likely than a fall to zero, so the band grows a longer upper tail with age. That tail is the risk of scarcity.
- **Uncertainty grows with age:**

  ```
  σ(age) = sqrt( σ_source² + v_good · age )
  ```

  - `σ_source`: how unreliable the source is (own eyes ≈ 0; harbour rumour high).
  - `v_good`: volatility of the good (grain at harvest time high; salt low).
  - The square root of age is random-walk growth.
- **Old information reverts to the usual price.** As the news ages, the belief's centre drifts toward the merchant's own long-run median ("normal price"). The median is robust to outlier years.

## Combining two reports

Precision-weighted averaging (the simplest Kalman update):

```
w = 1/σ²     μ = (w1·μ1 + w2·μ2)/(w1 + w2)     σ² = 1/(w1 + w2)
```

Fresh, reliable reports dominate; two reports that agree narrow the band. One caveat is kept in the design: two old reports of the same price never beat one fresh report, because they share the same past random walk and are not independent.

## What the experiments showed

| Setup | Opportunity days | Value of information |
|---|---|---|
| Instant information | 0.3% | ~0 |
| Ship news, last observation | 20-25% | +12 to +19 pts/yr |
| Rumour, lognormal + reversion (adopted) | 30-40% | +11 to +23 pts/yr |

The adopted rule also damped herding best (arrival irregularity 0.91 → 0.73, bankruptcies 0.5 → 0.1 a year). [Experiment 02](../experiments/02-information-delay.md).

Later steps added more channels, each behind a flag: rumours of who loaded what for where ([D5b](../../docs/experiments/D5b.md): this decided whether the world collapsed into herding); a port's public price current; ships carrying every price they know; couriers between neighbouring ports ([M2 · I1](../../docs/experiments/M2.md)). One finding from I1, specific to this model: fresher information did *not* reduce reroutes. Reroutes chased real price gaps, which fresher news made more visible.

## Display (design)

| Mode | What the player sees |
|---|---|
| Easy | Shaded band + "probably 2.6-3.5 lire" + age of the news |
| Normal | Shaded band + age |
| Hard | Raw report only: "3 lire, 7 days ago, from a caravan driver" |

```
Edirne   · wheat   ░▒▓█▓▒░░      ~3.0 lire  (7 days, caravan driver)
Istanbul · wheat       ▒█▒       ~3.4 lire  (1 day, own eyes)
```

Hiding the band makes the game harder without changing any mechanic: a clean difficulty dial.

**Readability risk:** a band for every port and every good is noise. Show only the goods and ports the player follows; details on demand.
