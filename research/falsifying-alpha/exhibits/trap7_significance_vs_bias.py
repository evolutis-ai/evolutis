"""Trap 7 — significance protects you against NOISE, not against BIAS.

A strict significance bar is the standard defence against having searched too much. It works: raising
the bar from 1.96 to a multiplicity-corrected 3.85 really does stop lucky arms from qualifying. This
exhibit starts by confirming that — 97 identically-negative arms, and at n=1,100 not one of them
clears any bar.

Which is exactly why a fleet where **8 of 97 arms DO clear 3.85** is not telling you about luck. It
is telling you about bias. And bias behaves in the opposite way to noise:

    a NOISY estimate's t-statistic wanders around zero, and a bar excludes it
    a BIASED estimate's t-statistic GROWS AS sqrt(n), so more data makes it MORE significant

So the arm with the longest track record and the most impressive t is, in a biased pipeline, simply
the arm that has had the most time to accumulate the bias. Significance cannot distinguish the two,
because significance only ever asks "could this be noise?".

Two diagnostics do work: pool the whole population (a significantly negative pool means any
positive member is measurement, not edge), and compare each arm against a reference that shares its
bias rather than against zero.

Lesson: never read a t-statistic as evidence of validity. Ask what would have to be biased for this
number to appear, then measure that. Then pool.
Run: python trap7_significance_vs_bias.py
"""
import numpy as np

rng = np.random.default_rng(7)

N_ARMS = 97
TRUE_EDGE = -0.015        # every arm is identically, mildly negative
SD = 0.68                 # per-trade sd, as measured on real fills
BARS = (1.96, 3.00, 3.85)

print("PART 1 — a strict bar DOES hold against pure noise")
print("=" * 78)
for trades in (1100, 6800):
    pnl = rng.normal(TRUE_EDGE, SD, (N_ARMS, trades))
    t = pnl.mean(1) / (pnl.std(1, ddof=1) / np.sqrt(trades))
    counts = "  ".join("t>=%.2f: %d" % (b, int((t >= b).sum())) for b in BARS)
    print("  %d arms x %-5d trades, all true edge %+.3f   best t=%+.2f   %s"
          % (N_ARMS, trades, TRUE_EDGE, t.max(), counts))
print("\n  => luck alone does not clear a corrected bar. So when a real fleet shows 8 of 97 arms")
print("     over 3.85, the explanation is not chance.\n")

print("PART 2 — the same bar is powerless against a small bias, and MORE DATA MAKES IT WORSE")
print("=" * 78)
BIAS = 0.05               # a modest upward accounting bias, e.g. booking unobtainable fills
print("  one arm, true edge %+.3f, plus a constant accounting bias of %+.3f" % (TRUE_EDGE, BIAS))
print("  %10s %12s %10s %12s" % ("trades", "mean", "t", "verdict at 3.85"))
for trades in (100, 500, 1100, 6800, 30000):
    pnl = rng.normal(TRUE_EDGE + BIAS, SD, trades)
    t = pnl.mean() / (pnl.std(ddof=1) / np.sqrt(trades))
    print("  %10d %+12.4f %+10.2f %12s"
          % (trades, pnl.mean(), t, "PASSES" if t >= 3.85 else "-"))
print("\n  => the bias is fixed; only the certainty grows. The longest-running arm looks the best,")
print("     and it is the most wrong. No bar can fix this, because nothing here is noise.\n")

print("PART 3 — the diagnostic that does survive: POOL THE POPULATION")
print("=" * 78)
# a heterogeneous fleet: most arms mildly biased, a handful heavily biased, all truly negative
heavy = rng.random(N_ARMS) < 0.10
bias = np.where(heavy, rng.normal(0.11, 0.02, N_ARMS), rng.normal(0.004, 0.004, N_ARMS))
trades = rng.integers(200, 7000, N_ARMS)
means, ts, tot, stake = [], [], 0.0, 0
for i in range(N_ARMS):
    pnl = rng.normal(TRUE_EDGE + bias[i], SD, trades[i])
    means.append(pnl.mean())
    ts.append(pnl.mean() / (pnl.std(ddof=1) / np.sqrt(trades[i])))
    tot += pnl.sum()
    stake += trades[i]
means, ts = np.array(means), np.array(ts)
print("  fleet of %d arms, %d total trades; EVERY arm's true edge is %+.3f"
      % (N_ARMS, stake, TRUE_EDGE))
print("  arms clearing 3.85 : %d        best arm: mean=%+.4f t=%+.2f"
      % (int((ts >= 3.85).sum()), means.max(), ts.max()))
print("  POOLED             : mean=%+.4f  (true %+.4f)   <-- the honest estimate"
      % (tot / stake, TRUE_EDGE))
print("  => pooling recovers the NEGATIVE sign even though 7 arms cleared 3.85. It is dragged")
print("     upward by the heavy-bias arms (-0.0061 against a true -0.0150), so it understates the")
print("     damage — but it gets the sign right, and the sign is what settles the question.")
print("     A significantly negative pool containing strongly positive members is the signature")
print("     of bias in the members, not of edge.")

print("\n=> Live instance: 8 of 97 paper arms cleared |t| >= 3.85 with totals up to +$503.97, while")
print("   the pooled paper fleet ran -1.48% of stake at t=-2.87 over 103,754 trades. Part 1 rules")
print("   out luck; the cause was bias — those arms were booking fills that had no size behind them")
print("   (see trap5). Their high t-statistics were a measure of how long they had been wrong.")
