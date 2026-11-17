# Optimizer's curse

**Literature.** If you choose the best of several noisy estimates, the chosen one is on average overestimated, even if each estimate is unbiased (Smith & Winkler 2006; related: the winner's curse, Capen, Clapp & Campbell 1971).

**Mechanism in the model.** Merchants compare many ports and goods on noisy, stale estimates and pick the best.

**What appeared.**
- In the entry experiments (D5b3), the public estimate of the best opportunity ran at 200-900% a year, while realised returns were around −1%. Part of the gap was a measurement bug: the annualisation ignored selling time. The rest was the curse. Entry beliefs were changed to the public record of realised returns plus a discounted voyage estimate. [D5b3](../../docs/experiments/D5b3.md) (Turkish).
- In the first version of mixed cargo (M2, MX-v2), lots kept in the hold "for a better port" found a median of only 0.57 of the expected price at the target, and wandered between ports. [Experiment 05](../experiments/05-port-time.md). The proposed fix is the one Smith & Winkler suggest: shrink each estimate toward the local price by its uncertainty, not a hand-set threshold.

**Player text.**
> You hear of ten opportunities and pick the brightest. But the one that looks brightest is usually the one most exaggerated. Experienced investors discount every bright rumour a little and look at what others actually earned.
