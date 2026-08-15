# Exhibits — reproduce each trap in a few seconds

Each script is self-contained (only `numpy`), uses synthetic data with a **known ground truth**, and prints
the naive (wrong) conclusion next to the correct one. Together they demonstrate the three ways a dead
strategy looks alive.

```bash
pip install -r ../requirements.txt
python trap1_longshot_tail.py
python trap2_snapshot_sampling.py
python trap3_maker_adverse_selection.py
python trap4_overfitting_gap.py
```

The random seeds are fixed, so your output should match the numbers below.

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

See [`../METHODOLOGY.md`](../METHODOLOGY.md) for the reasoning and the real-world instance behind each trap.
