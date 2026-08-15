# Methodology: Three Traps That Fake a Trading Edge

Every plausible edge in this project first *looked real*. Each was a different way for noise or bias to
masquerade as signal. Naming them turned "why did the live result disagree with the backtest?" into a
checklist. All three generalize well beyond prediction markets — anywhere you evaluate a strategy from
historical data.

---

## Trap 1 — The longshot tail

**Symptom.** A strategy that buys cheap, high-payoff outcomes shows an attractive *mean* return.

**Why it fools you.** The P&L is heavy-tailed: most trades lose a small amount, a few win big. A modest
sample's mean is dominated by whether a couple of longshots happened to hit — so it's a high-variance,
easily-positive estimator even when the true edge is negative.

**The test.** Report the **median** alongside the mean, and re-estimate the mean at very large N. If the
median is negative and the large-N mean converges negative, the positive small-sample mean was tail noise.

**Reproduction** (`exhibits/trap1_longshot_tail.py`): a strategy with a *genuine negative* edge shows a
positive sample mean in ~19% of 300-trade runs, while the sample median is positive in **0%** of runs.

**Real instance.** A cascade strategy reporting "+10% per bet" had a **median P&L of −1× stake**; the mean
was a handful of ~50× longshot wins.

---

## Trap 2 — Snapshot sampling

**Symptom.** A signal looks strong *and* highly significant across a huge number of observations.

**Why it fools you.** The observations aren't independent. One market (one outcome) contributes many
order-book snapshots, and the number of snapshots is **correlated with the outcome** — a market destined to
win lingers "cheap but climbing," generating more cheap-band snapshots than one destined to lose. Pooling
snapshots therefore (a) inflates the sample size, making the standard error fictitiously tiny, and
(b) weights winners more heavily, biasing the estimate upward.

**The test.** Collapse to **one independent observation per event** (per market/outcome) under a fixed entry
rule, and compute significance on *that* count.

**Reproduction** (`exhibits/trap2_snapshot_sampling.py`): identical data yields
`WR 0.475, +307σ` pooled vs `WR 0.184, −2.5σ` per-market — a full sign flip.

**Real instance.** A cheap-side signal measured **+7% per bet over 333k snapshots**; de-duplicated to one
entry per market it was **−10% per bet at −12σ**.

---

## Trap 3 — Maker-fill adverse selection

**Symptom.** A passive/market-making backtest that assumes your resting orders fill shows positive EV.

**Why it fools you.** A resting bid fills only when the price trades down to it — which is precisely when
your position is going against you. Your fills are therefore adversely selected: you fill losers far more
often than winners. Assuming fills discards exactly the information that kills the strategy.

**The test.** Model the fill as an **observable event** (a bid at P fills iff the market's offer actually
reached P), and split the realized fill rate **by outcome** (winners vs losers). A large gap is adverse
selection.

**Reproduction** (`exhibits/trap3_maker_adverse_selection.py`): assume-fill EV `+0.054` vs observable-fill
EV `−0.147`, with fill rate **41% on winners vs 95% on losers**.

**Real instance.** An observable-fill backtest of resting bids showed fills on ~70% of eventual winners vs
~88% of losers — no edge over simply taking, and adversely selected.

---

## Trap 4 — The overfitting gap

**Symptom.** You sweep a grid of parameters and the best combination looks great.

**Why it fools you.** If the true edge is ~0, the *maximum* in-sample result over G combinations is positive
purely by selection — you kept the luckiest of many noisy estimates. Out-of-sample, that same combo reverts
to its true ~0 edge. The gap between the in-sample optimum and the out-of-sample score is the overfitting,
and it grows with the size of the grid you searched.

**The test.** **Walk-forward:** optimize on a train window, score on a held-out forward window, and roll.
Report the in-sample optimum next to the pooled out-of-sample result, and check whether the chosen
parameters are *stable* across folds (a wandering optimum is noise). Use a tail-robust objective (Trap 1) so
you're not selecting on a longshot fluke either.

**Reproduction** (`exhibits/trap4_overfitting_gap.py`): a grid of 400 combos, *every one with true edge 0*,
yields a best-in-sample mean of `+0.116` that collapses to `+0.036` (+0.8 SE, ~0) out-of-sample.

**Real instance.** A walk-forward tail-robust sweep of the cascade parameter space: in-sample optimum
`+0.034`, pooled out-of-sample `+0.011` (~+0.5 SE, statistical zero), with the chosen parameters flipping
between folds (`both`↔`up`, `tleft` 60↔180). No stable, out-of-sample edge existed to tune toward — the
in-sample optimum was the mirage.

## The through-line

All four are versions of one discipline: **be maximally suspicious of your own positive result, and test the
specific way it could be an artifact before believing it.** In trading, the cost of skipping that step is
paid in real money — which is why the ability to run it is the job, not a footnote to it.
