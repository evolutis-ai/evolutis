"""Trap 4 — the overfitting gap: the best-in-sample parameter set is a mirage of multiple testing.

You sweep a grid of G parameter combinations and keep the best one. But if the true edge is ~0 (an efficient
market), the BEST in-sample mean is positive *purely by selection* — you picked the luckiest of G noisy
estimates. Out-of-sample, that same combo reverts to its true ~0 edge. The gap between the in-sample optimum
and the out-of-sample result IS the overfitting, and it grows with the size of the grid you searched.

This is the exact pattern from a real cascade parameter sweep: in-sample tail-robust optimum +0.034, pooled
walk-forward out-of-sample +0.011 (statistical zero), with the chosen params jumping around fold to fold.

Lesson: never trust an in-sample optimum. Optimize on train, score on held-out data — a real edge survives,
a mirage collapses. Report the in-sample-vs-OOS gap explicitly.
Run: python trap4_overfitting_gap.py
"""
import numpy as np

rng = np.random.default_rng(3)

G = 400            # parameter combos in the grid
N = 600            # trades per combo per period
SIGMA = 1.0        # per-trade noise
TRUE_EDGE = 0.0    # efficient market: NOT ONE combo has a real edge

# in-sample and INDEPENDENT out-of-sample returns for every combo; all with true edge 0
IS = rng.normal(TRUE_EDGE, SIGMA, (G, N))
OOS = rng.normal(TRUE_EDGE, SIGMA, (G, N))

is_mean = IS.mean(1)
best = int(is_mean.argmax())                       # pick the best IN-SAMPLE combo
oos_mean = OOS[best].mean()
oos_se = OOS[best].std() / np.sqrt(N)

print(f"grid of {G} parameter combos, every one with TRUE edge = {TRUE_EDGE}")
print(f"best IN-SAMPLE combo      : mean = {is_mean[best]:+.3f}   <-- looks like a strong edge (pure selection)")
print(f"that combo OUT-OF-SAMPLE  : mean = {oos_mean:+.3f}   <-- the truth: ~0")
print(f"OVERFITTING GAP           : {is_mean[best] - oos_mean:+.3f}")
print(f"OOS significance of winner: {oos_mean / oos_se:+.1f} SE  (indistinguishable from zero)")
print("\n=> Searching G combos manufactures a positive in-sample optimum from noise. Only the out-of-sample")
print("   score is real. The bigger the grid, the bigger the mirage.")
