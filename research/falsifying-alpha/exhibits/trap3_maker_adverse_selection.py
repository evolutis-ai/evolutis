"""Trap 3 — maker-fill adverse selection: a backtest that ASSUMES fills is fiction.

You rest a passive bid at price P on the "up" side. It only fills if the market trades DOWN to P — but the
market trading down to P is exactly when "up" is losing. So your fills are disproportionately LOSERS. A
naive maker backtest that assumes every bid fills shows +EV; the observable-fill version (fill iff the price
actually reached P) shows -EV, with a fill rate far higher on losers than on winners.

Lesson: model the fill as an observable event, and split the fill rate by outcome. A passive backtest that
assumes fills is not a backtest.
Run: python trap3_maker_adverse_selection.py
"""
import numpy as np

rng = np.random.default_rng(2)

N = 20000
START = 0.50
P = 0.45                 # your resting bid on "up", just below mid
STEPS = 30

walk = rng.normal(0, 0.03, (N, STEPS)).cumsum(1)
path = np.clip(START + walk, 0.01, 0.99)
final = path[:, -1]
up_won = final > START                 # market resolves "up" if it finishes above the open
filled = path.min(1) <= P              # your resting bid fills iff the price dipped to P at some point

# NAIVE: assume every bid fills, hold to resolution
naive_ev = np.where(up_won, 1 - P, -P).mean()
# OBSERVABLE: only the bids that actually filled
f = filled
obs_ev = np.where(up_won[f], 1 - P, -P).mean()

print("resting bid at P=%.2f on 'up' (market opens at %.2f)" % (P, START))
print("NAIVE (assume fill)  : n=%-6d  WR=%.2f  EV/bet=%+.4f   <-- looks profitable"
      % (N, up_won.mean(), naive_ev))
print("OBSERVABLE fills     : n=%-6d  fill%%=%2.0f  WR=%.2f  EV/bet=%+.4f   <-- the truth: unprofitable"
      % (f.sum(), f.mean() * 100, up_won[f].mean(), obs_ev))
print("fill rate on WINNERS = %2.0f%%   vs   LOSERS = %2.0f%%   <-- adverse selection"
      % (filled[up_won].mean() * 100, filled[~up_won].mean() * 100))
print("\n=> The fill is not free: you fill losers far more than winners. Assuming fills flips the sign of the EV.")
