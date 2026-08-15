"""Trap 1 — the longshot tail: for heavy-tailed P&L the small-sample MEAN lies; the MEDIAN tells the truth.

A strategy buys cheap ("longshot") outcomes. The market is efficient-to-vig, so the true edge is slightly
NEGATIVE (the cheap side wins a little less often than it's priced — the favorite-longshot bias, which is
the vig, not an edge). Yet because wins are rare and large, a modest sample's MEAN is positive a large
fraction of the time — carried by a few lucky hits — while the MEDIAN trade loses and the large-sample mean
reveals the truth.

Lesson: for heavy-tailed payoffs, judge the median (and demand large N), not the small-sample mean.
Run: python trap1_longshot_tail.py
"""
import numpy as np

rng = np.random.default_rng(0)


def pnl(n):
    ask = rng.uniform(0.05, 0.30, n)      # you buy the cheap side at its ask (price paid = implied prob)
    true_p = ask * 0.90                    # it actually WINS less than priced -> genuine negative edge
    win = rng.random(n) < true_p
    return np.where(win, 1 - ask, -ask)    # +(1-ask) on a win, -ask on a loss


big = pnl(2_000_000)
print("TRUE edge (N=2,000,000):  mean=%+.4f   median=%+.4f   win%%=%.1f"
      % (big.mean(), np.median(big), (big > 0).mean() * 100))

mus = np.array([pnl(300).mean() for _ in range(2000)])
meds = np.array([np.median(pnl(300)) for _ in range(2000)])
print("\nAt n=300, over 2,000 independent runs of a TRUE-negative-edge strategy:")
print("  sample MEAN   > 0 in %5.1f%% of runs   <-- the tail fakes a positive edge" % ((mus > 0).mean() * 100))
print("  sample MEDIAN > 0 in %5.1f%% of runs   <-- the median is not fooled" % ((meds > 0).mean() * 100))
print("\n=> A positive small-sample mean is not evidence of edge here. Judge the median; demand large N.")
