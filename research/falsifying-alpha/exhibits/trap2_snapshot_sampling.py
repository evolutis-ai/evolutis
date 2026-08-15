"""Trap 2 — snapshot sampling: pooling correlated observations inflates n AND biases the estimate.

You study a cheap-side entry by pooling every order-book SNAPSHOT you recorded. But a single market
contributes MANY snapshots that share ONE outcome, and the snapshot COUNT is correlated with the outcome
(a market destined to win lingers "cheap but climbing," generating more cheap-band snapshots than a market
destined to lose). Pooling therefore weights winners more heavily -> a fake positive edge, at a fake-high
significance driven by the inflated n. One independent entry per market recovers the truth.

This is the exact mechanism by which a real study showed "+7% per bet over 333k snapshots" that became
"-10% per bet at -12 sigma" once de-duplicated to one entry per market.

Lesson: de-duplicate shared outcomes (one observation per independent event) before trusting an edge.
Run: python trap2_snapshot_sampling.py
"""
import numpy as np

rng = np.random.default_rng(1)

N = 4000                 # independent markets
ASK = 0.20               # price you pay for the cheap side
TRUE_WR = 0.18           # per-market truth: it wins 18% < 20% priced -> a genuine NEGATIVE edge

win = rng.random(N) < TRUE_WR
# outcome-correlated snapshot counts: eventual winners linger cheap-but-climbing => more snapshots
snaps = np.where(win, rng.poisson(200, N), rng.poisson(50, N)).clip(1)

# NAIVE pooled estimate — every snapshot counted (each market weighted by its snapshot count)
pooled_wr = (win * snaps).sum() / snaps.sum()
pooled_n = int(snaps.sum())
pooled_se = np.sqrt(pooled_wr * (1 - pooled_wr) / pooled_n)

# HONEST estimate — one independent entry per market
per_wr = win.mean()
per_se = np.sqrt(per_wr * (1 - per_wr) / N)

print("price paid (ask)      : %.2f" % ASK)
print("POOLED snapshots      : WR=%.3f  edge=%+.3f  n=%-8d (%+.1f SE)   <-- looks like a STRONG positive edge"
      % (pooled_wr, pooled_wr - ASK, pooled_n, (pooled_wr - ASK) / pooled_se))
print("ONE entry per market  : WR=%.3f  edge=%+.3f  n=%-8d (%+.1f SE)   <-- the TRUTH: negative"
      % (per_wr, per_wr - ASK, N, (per_wr - ASK) / per_se))
print("\n=> Same data, opposite verdict. The pooled 'significance' is an artifact of counting correlated "
      "snapshots. De-duplicate to one observation per independent outcome.")
