# Risk model

> Status: physical risk per leg (R1), corsair pressure, ship loss, ballast risk and the ship market are implemented in the Rust core. Agents' risk learning (R2-R3), insurance (R4) and the investor premium (R5) are design only.
> Source (Turkish): [`docs/design/risk-model.md`](../../docs/design/risk-model.md); history: [maritime risk](../../docs/research/history/maritime-risk-16c.md), [ship life and piracy](../../docs/research/history/ship-life-piracy-16c.md)

## Three layers of risk

| Layer | What | Insurable | Diversifiable by ship shares (*carati*) |
|---|---|---|---|
| Physical: nature | Storm, sinking | Yes | Mostly (ship-specific) |
| Physical: corsairs | Capture | Yes | Partly: corsair pressure hits a whole region (common shock) |
| Commercial | Low price at arrival, crowding, wrong decisions on stale information | No | The ship-specific part yes; the market-wide part (everyone chasing the same signal) no |

**Losses from bad information are part of commercial risk; no separate term is needed.** An investor sees outcomes and cannot tell bad luck from a bad estimate. Measured from realised voyage outcomes, commercial risk already contains information errors. Adding an "information risk" term would count them twice. Under parameter uncertainty a Bayesian investor faces predictive variance (Kandel & Stambaugh 1996; Barberis 2000).

## Physical hazard (world side, implemented)

Hazard per **leg** of the route, not per day:

```
h_leg(t) = 1 − (1 − d_leg(month)) · (1 − c_region(t) · v)
```

- `d_leg(month)`: natural hazard by region and month. The winter effect is regional: bora in the Adriatic, small in the Levant.
- `c_region(t)`: **corsair pressure**, a world variable. It follows a log-AR(1) process with rare jumps around a persistent level. Its form was chosen by Claude and is to be calibrated on historical premium jumps (Ceccarelli 2007).
- `v`: vulnerability of the ship; 1 for now. Later it depends on ship type, flag and convoy.
- Multi-leg routes combine the probabilities. Outcomes: sinking or capture, each losing ship and cargo. Captured ships are resold as prizes. Empty (ballast) voyages carry risk too.

**Calibrated to patterns, not parameters:** about 2-4% loss per voyage, 1-15% spread of insurance premiums between regions, corsairs at least half of losses. At 2-4 voyages a year, that is roughly 4-12% of the fleet lost per year. With war years included, the upper end (10-13%) is better supported. [Experiment 05](../experiments/05-port-time.md) shows why the model still loses more: per-voyage risk is right, but ships make too many voyages.

## Agents' estimate of risk (design)
Merchants, investors and insurers do not know the true probabilities; they learn from loss news that reaches the port with a delay.
- Per-leg loss frequency as a Beta-Binomial estimate with forgetting.
- Pulled toward the sea-wide average by credibility weighting (Bühlmann): a rarely sailed leg stays near the average.
- Commercial risk: mean and variance of voyage returns from the public record, last 12 months.

## Insurance and the investor's premium (design)
- **Insurers:** in the Genoa 1564-72 ledger, a closed group of merchants insured each other (Iodice 2023).
- **Premium** = insurer's expected loss + its own risk premium. The risk premium uses the same Arrow-Pratt rule (γ · w · σ²), so the loading comes from how diversified the insurer is; no separate parameter is needed.
- A merchant insures when the premium is below their certainty equivalent of the loss.
- **Investor's required excess return** ≈ γ · w · σ²_eff. Here σ²_eff counts the voyages per year, common and ship-specific variance (the latter divided by the number of ships N the investor spreads over), and uninsured physical loss. `w` and `N` are to come from Venetian *carati* records. Until then they are flagged temporary proxies.
