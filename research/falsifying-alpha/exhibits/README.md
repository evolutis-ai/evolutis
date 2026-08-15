# Exhibits — reproduce each trap in a few seconds

Each script is self-contained (only `numpy`), uses synthetic data with a **known ground truth**, and prints
the naive (wrong) conclusion next to the correct one. Together they demonstrate the nine ways a dead
strategy looks alive.

```bash
pip install -r ../requirements.txt
python trap1_longshot_tail.py
python trap2_snapshot_sampling.py
python trap3_maker_adverse_selection.py
python trap4_overfitting_gap.py
python trap5_obtainable_fills.py
python trap6_selecting_winners.py
python trap7_significance_vs_bias.py
python trap8_informative_missingness.py
python trap9_metric_decides_the_answer.py
```

The random seeds are fixed, so your output should match the numbers below.

Traps 1–4 are about **inference** — reading a number wrongly. Traps 5–9 are about **measurement** — the
number itself being the wrong number, which is the harder and more expensive class. Every one of 5–9 was
discovered the hard way, after it had already invalidated a result.

---

### `trap1_longshot_tail.py` — the mean lies; the median tells the truth
A strategy with a **true negative edge** on cheap, heavy-tailed payoffs.
```
TRUE edge (N=2,000,000):  mean=-0.0175   median=-0.1438   win%=15.8
At n=300, over 2,000 independent runs:
  sample MEAN   > 0 in  19.4% of runs   <-- the tail fakes a positive edge
  sample MEDIAN > 0 in   0.0% of runs   <-- the median is not fooled
```
**Takeaway:** for heavy-tailed P&L, a positive small-sample mean is not evidence. Judge the median; demand
large N.

---

### `trap2_snapshot_sampling.py` — correlated snapshots fake an edge at fake significance
Identical data, evaluated two ways.
```
POOLED snapshots      : WR=0.475  edge=+0.275  n=311035  (+306.8 SE)   <-- fake strong POSITIVE edge
ONE entry per market  : WR=0.184  edge=-0.016  n=4000    ( -2.5 SE)    <-- the TRUTH: negative
```
**Takeaway:** collapse to one independent observation per outcome before computing an edge *or* its
significance.

---

### `trap3_maker_adverse_selection.py` — a backtest that assumes fills is fiction
Resting a passive bid; naive vs observable fills.
```
NAIVE (assume fill)  : WR=0.50  EV/bet=+0.0536   <-- looks profitable
OBSERVABLE fills     : WR=0.30  EV/bet=-0.1470   <-- the truth
fill rate on WINNERS = 41%   vs   LOSERS = 95%   <-- adverse selection
```
**Takeaway:** model the fill as an event and split the fill rate by outcome; a passive backtest that assumes
fills is not a backtest.

---

### `trap4_overfitting_gap.py` — the best-in-sample parameter set is a mirage
A grid of 400 combos, *every one with true edge 0*.
```
best IN-SAMPLE combo      : mean = +0.116   <-- looks like a strong edge (pure selection)
that combo OUT-OF-SAMPLE  : mean = +0.036   <-- the truth: ~0
OVERFITTING GAP           : +0.080
OOS significance of winner: +0.8 SE  (indistinguishable from zero)
```
**Takeaway:** searching many combos manufactures a positive in-sample optimum from noise; optimize on train,
score on held-out data, and report the in-sample-vs-OOS gap. The bigger the grid, the bigger the mirage.

---

### `trap5_obtainable_fills.py` — the good prices had NO SIZE behind them
Trap 3 is about a fill that *happens* being adversely selected. This is worse: a fill that is **recorded but
was never available.** A quote is attractive *because* it is thin — anything genuinely cheap with real depth
gets lifted by someone faster. Add a fair-value model that is a few points optimistic and the headline goes
positive while the buyable half loses.
```
ALL TRADED (headline)    n=50454  mean=+0.0173  t= +8.95   <-- what a paper arm reports
OBTAINABLE               n=25185  mean=-0.0070  t= -2.56   <-- what you could actually buy
NOT obtainable           n=25269  mean=+0.0416  t=+15.17   <-- where the 'edge' lives
mean TRUE edge, obtainable = -0.0084     NOT obtainable = +0.0422
```
**Takeaway:** record resting depth at decision time and treat obtainability as **three** states —
obtainable, not obtainable, and *unknown*. Never let unknown default to either; report the split, not the
blend. Live instance: a **+$202.71** paper result became **−$38.74** on the fills that had real size behind
them, with 100% of the profit in the unobtainable bucket.

---

### `trap6_selecting_winners.py` — selecting on past performance can be WORSE than not selecting
Ranking traders on returns mostly ranks luck — that part is well known. The damaging part is that it is
*actively harmful* when the noise you rank on and the cost you pay share a driver. In a binary market both
are `p(1-p)`, maximal at p=0.50, so ranking walks the selection into the most expensive band. Every agent
below has **zero skill**.
```
cohort            n       track      FUTURE   mean px their fee
top 5%          200     +0.1510     -0.0154     0.646    0.0160
top 10%         400     +0.1248     -0.0154     0.661    0.0157
top 25%        1000     +0.0864     -0.0138     0.705    0.0145
everyone       4000     -0.0115     -0.0129     0.724    0.0140

top 5% out of sample MINUS everyone = -0.0025/share  <-- copying the best is WORSE
```
Note `FUTURE` tracks `-fee` in every row — zero skill, confirmed — while the selection drags mean price
0.724 → 0.646, toward 0.50.
**Takeaway:** rank *within* a price bin, never across the book, and check the average price of the cohort you
selected. If it drifted toward 0.50, you selected the fee. Live: the top 5% of 4,309 real wallets lost
**5.39pp/share** out of sample against the field's **2.92pp**.

---

### `trap7_significance_vs_bias.py` — significance protects against noise, not bias
Part 1 confirms a corrected bar *works* against luck: 97 identically-negative arms, and none clears any bar.
Which is why a real fleet showing 8 of 97 over 3.85 is reporting **bias**, not luck — and bias runs the other
way, because its t-statistic grows as `sqrt(n)`.
```
PART 1  97 arms x 6800 trades, all true edge -0.015   best t=+0.62   t>=1.96: 0  t>=3.85: 0

PART 2  one arm, true edge -0.015, plus a constant +0.050 accounting bias
          trades         mean          t  verdict at 3.85
            1100      +0.0362      +1.77                -
            6800      +0.0332      +3.99           PASSES
           30000      +0.0288      +7.37           PASSES

PART 3  arms clearing 3.85: 7 of 97      POOLED mean=-0.0061  (true -0.0150)
```
**Takeaway:** the longest-running arm looks the best and is the most wrong, because it has had the most time
to accumulate the bias. Never read a t-statistic as evidence of *validity* — ask what would have to be biased
for this number to appear, then measure that. Then pool: a significantly negative pool containing strongly
positive members is the signature of bias in the members.

---

### `trap8_informative_missingness.py` — a high drop rate is fine, a VARYING one is fatal
Joins lose rows. The instinct is to check *how many* were lost. What matters is whether the chance of being
lost **varies along the variable under test**. Truth below is exactly flat.
```
band              total    kept  retention  kept WR
x < -0.05         27195   14575      53.6%    0.811
[-0.05,-0.02)      5556    4628      83.3%    0.765
[-0.02, 0)         3617    3307      91.4%    0.746
[0, 0.02)          3632    3536      97.4%    0.742
retention spread: 44 percentage points   <-- INFORMATIVE

FULL population (the truth)  slope=-0.0155  t=  -0.46
SURVIVORS of the join        slope=-0.5950  t= -14.13   <-- a large effect from nothing

more data only sharpens it:  n=40k t=-12.54   n=160k t=-27.33   n=640k t=-53.14
```
**Takeaway:** print retention per band of the test variable, always. If it slopes, the sample is biased along
the axis of interest — and **recover** the missing rows rather than adjusting for them. Live: retention ran
**91.3% → 29.0%** across the test axis, because outcomes were joined from our own trade registries and the
untraded rows were exactly the ones being tested.

---

### `trap9_metric_decides_the_answer.py` — "does skill persist?" has four different answers
Same data, zero skill, four denominators. The participants differ only in two persistent *habits* — the price
band they trade and what they stake — and any metric that fails to condition on price inherits the habit.
```
metric, h1 vs h2                  r          t
raw $ per market            +0.4186     +25.24
return on notional          +0.1806     +10.05
margin per share            +0.0932      +5.12
margin vs cell-mates        -0.0069      -0.38   <-- price-controlled, leave-one-out

price style itself          +0.8712     +97.16   <-- THE CONFOUNDER
```
**Takeaway:** before correlating performance across time, correlate the **style**. If style persists, an
uncontrolled metric is measuring style. Compare against cell-mates in the same price bin, with the
participant left out of its own benchmark. Live, the same four choices gave **−0.480, +0.498, +0.167, +0.091**
with style persisting at **+0.90** — the metric changed the *sign*, so the question was unanswerable until it
was made specific. And note `margin per share` reproduces the live **+0.091** here with **no skill in the data
at all.**

---

See [`../METHODOLOGY.md`](../METHODOLOGY.md) for the reasoning and the real-world instance behind each trap.
