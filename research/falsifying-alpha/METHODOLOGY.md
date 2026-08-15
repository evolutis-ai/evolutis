# Methodology: Nine Traps That Fake a Trading Edge

Every plausible edge in this project first *looked real*. Each was a different way for noise or bias to
masquerade as signal. Naming them turned "why did the live result disagree with the backtest?" into a
checklist. All nine generalize well beyond prediction markets — anywhere you evaluate a strategy from
historical data.

---

# Part I — The inference traps

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

## The through-line (Part I)

All four above are versions of one discipline: **be maximally suspicious of your own positive result, and test the
specific way it could be an artifact before believing it.** In trading, the cost of skipping that step is
paid in real money — which is why the ability to run it is the job, not a footnote to it.

---

# Part II — The measurement traps

Traps 1–4 are about **inference**: the number was right and I read it wrongly. Traps 5–9 are about
**measurement**: the number itself was not the number that mattered. This second class is harder to
see, more expensive, and much less written about — every one below was discovered only after it had
already invalidated a result.

---

## Trap 5 — Obtainability: the good prices had no size behind them

**Symptom.** A paper arm reports a solid, significant edge. The live version of the identical strategy
loses. Fee accounting, latency and slippage models all fail to explain the gap.

**Why it happens.** A paper arm books a trade whenever it *sees* a price; it never checks that anyone
was offering the size it wanted. And the two are coupled in the worst possible direction — an
attractive quote is attractive *because* it is thin. Anything genuinely cheap with real depth behind it
is lifted by someone faster. So the trades that look best are exactly the ones that were not available.

Add one more ordinary ingredient — a fair-value model a few points optimistic — and the arithmetic
turns vicious. Deeply-discounted thin quotes are profitable even against the true probability;
marginally-discounted deep quotes are profitable only against the model's optimism. You can buy only
the second kind, and the blend comes out positive.

**The fix.** Record resting depth at decision time, and treat obtainability as **three** states:
obtainable, not obtainable, and **unknown**. The third is not a rounding detail — depth is missing far
more often than people assume, and letting `unknown` default to either value silently biases every
comparison. Report the split, never the blend.

**Where it bit.** One arm's headline was **+$202.71** at t=+2.90. Split on depth: obtainable
**−$38.74** (−0.0436/trade, t=−2.40, 95% CI entirely below zero); not obtainable **+$241.10**
(+0.1237/trade, t=+7.57). **100% of the apparent profit was unbuyable.** This class of error voided
about a fortnight of prior work, including one result that had passed selection correction *and* both
walk-forward halves *and* independently replicated an earlier finding. **Selection correction and
walk-forward do not protect against a contaminated population.**

---

## Trap 6 — Winner selection: copying the best can be worse than copying at random

**Symptom.** You rank participants by realised performance, follow the top cohort, and underperform
the field — not merely the top cohort's own past, but the *average participant*.

**Why it happens.** Everyone knows ranking on returns mostly ranks luck; that alone would make the
exercise useless, not harmful. It becomes harmful when the noise you rank on and the cost you will pay
share a driver. In a binary market at price p they do:

    outcome variance = p(1-p)          how much luck is available
    fee per share    = rate*p(1-p)     what it costs to trade

Both peak at p = 0.50. Ranking therefore surfaces whoever traded mid-priced contracts, because that is
where the luck was widest — and mid-priced contracts are the most expensive ones. **You select for
cost.** In a zero-skill simulation the selected cohort's out-of-sample return tracks minus its own fee,
exactly, while the selection drags its mean price toward 0.50.

**The fix.** Rank *within* a price bin, never across the book. Then check the average price of the
cohort you selected: if it drifted toward 0.50, you selected the fee, not the skill.

**Where it bit.** On 4,309 real wallets, selected on the first half of their history and measured on the
second: the top 5% lost **5.39pp/share** against the field's **2.92pp**, with mean price 0.538 versus
0.640. The live gap is larger than the fee differential alone — the selected cohort was also trading
worse prices relative to fair — but the *sign* needs no extra ingredient.

---

## Trap 7 — Significance protects against noise, not against bias

**Symptom.** Several strategies in a fleet clear a strict, multiplicity-corrected bar. The fleet as a
whole loses money.

**Why it happens.** A corrected bar genuinely works against luck — in simulation, 97 identically
negative arms produce *zero* qualifiers at any bar. So a fleet where 8 of 97 clear 3.85 is not
reporting luck; it is reporting bias. And bias behaves in the opposite way:

    a NOISY estimate's t wanders around zero, and a bar excludes it
    a BIASED estimate's t GROWS AS sqrt(n) — more data makes it MORE significant

The arm with the longest track record and the most impressive t-statistic is, in a biased pipeline,
simply the one that has had the most time to accumulate the bias. No bar can separate them, because a
bar only ever asks "could this be noise?".

**The fix.** Never read a t-statistic as evidence of *validity*. Ask what would have to be biased for
this number to appear, then measure that. And **pool the population**: a significantly negative pool
containing strongly positive members is the signature of bias in the members, not of edge.

**Where it bit.** 8 of 97 paper arms cleared |t| ≥ 3.85 with headline totals to **+$503.97**, while the
pooled paper fleet ran **−1.48% of stake at t=−2.87** over 103,754 trades. The cause was Trap 5. The
high t-statistics measured how long those arms had been wrong. Before pooling, the fleet had been
described as "inflated but positive"; it was not positive at all.

---

## Trap 8 — Informative missingness: a high drop rate is fine, a varying one is fatal

**Symptom.** A join loses rows. You check the fraction lost, judge it tolerable, and proceed. The
result is a clean, strong, entirely fictitious relationship.

**Why it happens.** The *size* of the loss barely matters. What matters is whether the probability of
being lost varies along the variable under test — and worse, whether the outcome affects survival more
strongly at one end of the range. That interaction bends a flat truth into a slope. Nothing about the
artefact is noise, so more data does not dilute it; in simulation the fake t-statistic sharpens from
−12.5 to −53.1 as n grows 16×.

**The fix.** Print **retention per band of the test variable**, always. Flat retention means the drop
is harmless at any size; sloping retention means the surviving sample is biased along the axis of
interest. Then **recover** the missing rows rather than adjusting for them — the mechanism is rarely
known well enough to model.

**Where it bit.** Outcomes were joined from our own trade registries, which contain only markets an arm
actually *traded* — and a rejected deep-edge candidate is precisely the one no arm traded. Retention ran
**91.3%** in the shallowest band of the test variable and **29.0%** in the deepest: a 62-point gradient
along the axis being measured. Re-resolving all 13,207 outcomes from the venue took retention to 100.0%
in every band. **None of Traps 1–7 would have caught this.**

---

## Trap 9 — The metric decides the answer

**Symptom.** "Does past performance predict future performance?" returns a different answer — including
a different *sign* — depending on a denominator you chose without thinking about it.

**Why it happens.** Participants differ in persistent *habits* as well as skill. Two habits dominate:
the price band they trade and how much they stake. Any metric that fails to condition on price inherits
the habit:

    raw $ per market      inherits SIZE and PRICE
    return on notional    inherits PRICE      (dividing by p amplifies the spread across bands)
    margin per share      inherits the FEE    (rate*p*(1-p), a function of the band)
    margin vs cell-mates  inherits nothing

In a zero-skill simulation these give r = +0.42, +0.18, +0.09 and −0.01 respectively — while the price
band itself persists at r = +0.87. The apparent skill persistence *is* the style persistence.

**The fix.** Before correlating performance across time, **correlate the style**. If style persists,
an uncontrolled metric is measuring style. Compare each observation against its cell-mates — others
trading the same instrument in the same price bin — and leave the participant out of its own benchmark,
so it never contributes to the number it is judged against.

**Where it bit.** On 4,309 real wallets the four choices gave **r = −0.480, +0.498, +0.167, +0.091**
while style persisted at **+0.90**. Changing the metric changed the sign, so the question was
unanswerable until it was made specific. The price-controlled figure, +0.091, is closely reproduced by
a simulation containing **no skill at all** — which is the most direct evidence available that the live
number was style.

---

## The through-line, restated

Traps 1–4 say: *be suspicious of your own positive result, and test the specific way it could be an
artefact before believing it.*

Traps 5–9 say something stricter, and it is the lesson that cost the most: **verify that the quantity
you computed is the quantity you meant.** A backtest's number can be wrong in ways that no amount of
statistical rigour applied *to that number* will reveal — because the error is upstream of the
statistics. Depth you never recorded, rows a join silently dropped, a denominator that encodes a habit,
a bias that grows more convincing with every extra observation.

The practical consequence is a short list of questions to ask of any historical result, in this order:
could I have transacted at this price, in this size? Which rows are missing, and is their absence
correlated with what I am measuring? What is this divided by, and what else does that denominator
encode? Is the whole population consistent with the members I like? Only then: is it significant?
