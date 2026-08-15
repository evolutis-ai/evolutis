"""Trap 5 — obtainability: the good prices had NO SIZE behind them.

Trap 3 showed that a fill which HAPPENS is adversely selected. This is the earlier, more brutal
failure: a trade that is recorded but **could never have happened at all**, because nobody was
offering the size you wanted at that price.

A paper arm books a trade whenever it SEES a price. It does not check that anyone was offering size.
And the two are not independent — an attractive quote is attractive *because* it is thin: a genuinely
cheap offer with real depth behind it gets lifted by someone faster than you. So the trades that look
best are precisely the ones you could not have had.

Add one more realistic ingredient — a model whose fair value is a few points optimistic — and the
arithmetic turns vicious. The thin, deeply-discounted quotes are so cheap they are profitable *even
against the true probability*, while the deep, marginally-discounted ones are only profitable against
the model's optimism. You can buy only the second kind. The headline averages a real loss with an
impossible profit and comes out positive.

Lesson: record resting depth at decision time and treat obtainability as THREE states — obtainable,
not obtainable, and UNKNOWN. Never let unknown default to either; report the split, not the blend.
Run: python trap5_obtainable_fills.py
"""
import numpy as np

rng = np.random.default_rng(5)

N = 60000
SIZE = 5.0                  # shares we want — e.g. a venue minimum
P_TRUE = 0.75               # the contract's real probability of paying
P_MODEL = 0.81              # our model is 6pp optimistic — inside the 5-7pp bias measured live

# The market quotes near the TRUE value, with noise.
ask = np.clip(P_TRUE + rng.normal(0, 0.06, N), 0.02, 0.98)

# Our entry filter: take it if the model says there is edge. This is what every arm does.
enter = (P_MODEL - ask) > 0
edge_model = P_MODEL - ask               # the edge we BELIEVE we have
edge_true = P_TRUE - ask                 # the edge we ACTUALLY have

# ⛔ THE COUPLING: depth is thin exactly where the discount is generous, because a genuinely cheap
# offer with real size behind it is lifted by someone faster. Deep books sit at fair or worse.
depth = rng.gamma(shape=2.0, scale=9.0 * np.exp(-edge_model / 0.07))

won = rng.random(N) < P_TRUE              # the outcome does not care what we believed
pnl = np.where(won, 1.0 - ask, -ask)

traded = enter
obtainable = traded & (depth >= SIZE)
missed = traded & (depth < SIZE)

def block(label, mask, tag):
    n = int(mask.sum())
    m = pnl[mask].mean()
    t = m / (pnl[mask].std(ddof=1) / np.sqrt(n))
    print("  %-24s n=%-6d mean=%+.4f  t=%+6.2f  total=%+9.2f   %s"
          % (label, n, m, t, pnl[mask].sum(), tag))

print("%d quotes; true fair %.2f; our model believes %.2f; we need %.0f shares"
      % (N, P_TRUE, P_MODEL, SIZE))
print("entry filter: buy when (model fair - ask) > 0     traded %d of %d\n"
      % (traded.sum(), N))
block("ALL TRADED (headline)", traded, "<-- what a paper arm reports")
block("OBTAINABLE", obtainable, "<-- what you could actually buy")
block("NOT obtainable", missed, "<-- where the 'edge' lives")

print("\n  mean TRUE edge, obtainable     = %+.4f   <-- negative: only the model's optimism made it look good"
      % edge_true[obtainable].mean())
print("  mean TRUE edge, NOT obtainable = %+.4f   <-- the real bargains were the thin ones"
      % edge_true[missed].mean())
print("  obtainable share of traded     = %.1f%%" % (obtainable.sum() / traded.sum() * 100))

print("\n=> The headline is a blend of a real loss and an impossible profit, and the blend is POSITIVE.")
print("   Splitting on depth moves the entire apparent edge into trades nobody was offering size for.")
print("   In the live instance this turned a +$202.71 paper result into -$38.74 on the fills that had")
print("   real size behind them — 100% of the profit sat in the unobtainable bucket.")
