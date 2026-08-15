"""Trap 6 — selecting on past performance can be WORSE than not selecting at all.

Everyone knows that ranking traders on past returns mostly ranks luck. The subtler and more damaging
result is that the ranking is not merely uninformative — it is **actively harmful**, whenever the
noise you rank on and the cost you will pay share a common driver.

In a binary market they do. For a contract at price p:

    outcome variance = p(1-p)         <- how much luck is available
    fee per share    = rate*p(1-p)    <- what it costs to trade

Both peak at p = 0.50. So ranking participants on realised performance preferentially surfaces
whoever traded mid-priced contracts, because that is where the luck was widest — and mid-priced
contracts are also the most expensive to trade. **You select for cost.**

Below, every participant has ZERO skill and is priced fairly, so out of sample each one earns exactly
minus its own fee. Ranking drags the selected cohort's average price toward 0.50, so the "best"
traders are simply the ones paying the most. Copying them beats copying nobody — downward.

Lesson: rank WITHIN a price bin, never across the book. And before copying anyone, check the average
price of the cohort you selected: if it drifted toward 0.50, you selected the fee, not the skill.
Run: python trap6_selecting_winners.py
"""
import numpy as np

rng = np.random.default_rng(6)

N_AGENTS = 4000
RANK_BETS = 30           # short, noisy track record — what you actually get to rank on
MEASURE_BETS = 1000      # long out-of-sample period, so the measurement itself is precise
FEE_RATE = 0.07          # the venue's coefficient: fee per share = rate * p * (1-p)

# Every agent has a price STYLE — the band it habitually trades — and NO skill whatsoever.
style = rng.uniform(0.50, 0.95, N_AGENTS)


def play(p, n):
    """n fairly-priced bets at price p. Zero gross edge, so the only drift is the fee."""
    won = rng.random((len(p), n)) < p[:, None]
    gross = np.where(won, 1 - p[:, None], -p[:, None])
    return gross - (FEE_RATE * p * (1 - p))[:, None]


track = play(style, RANK_BETS).mean(1)        # rank on this
future = play(style, MEASURE_BETS).mean(1)    # measure on this
order = np.argsort(-track)

print("%d agents, ZERO skill, all fairly priced; fee/share = %.2f*p*(1-p)"
      % (N_AGENTS, FEE_RATE))
print("ranked on %d bets, measured on %d further bets (strictly out of sample)\n"
      % (RANK_BETS, MEASURE_BETS))
print("  %-11s %7s %11s %11s %9s %9s" % ("cohort", "n", "track", "FUTURE", "mean px", "their fee"))
for frac, label in ((0.05, "top 5%"), (0.10, "top 10%"), (0.25, "top 25%"), (1.00, "everyone")):
    k = max(10, int(N_AGENTS * frac))
    s = order[:k]
    px = style[s].mean()
    print("  %-11s %7d %+11.4f %+11.4f %9.3f %9.4f"
          % (label, k, track[s].mean(), future[s].mean(), px, FEE_RATE * px * (1 - px)))

top = order[:max(10, N_AGENTS // 20)]
gap = future[top].mean() - future.mean()
print("\n  top 5%% out of sample MINUS everyone = %+.4f/share  <-- %s"
      % (gap, "copying the best is WORSE than copying at random"
         if gap < 0 else "copying the best is better"))
print("  and note FUTURE tracks -fee almost exactly in every row: that is zero skill, confirmed.")
print("  the selection moved mean price %.3f -> %.3f, i.e. toward 0.50 where the fee peaks."
      % (style.mean(), style[top].mean()))

print("\n=> With no skill anywhere, the 'best' cohort is just the most expensive one. Ranking walked")
print("   the selection toward p=0.50, where luck is widest and the fee is largest.")
print("   Live, on 4,309 real wallets ranked the same way, the top 5% lost 5.39pp/share out of")
print("   sample against the field's 2.92pp. ⚠️ That live gap is LARGER than the fee differential")
print("   alone, so the fee explains the DIRECTION and part of the size — the selected cohort was")
print("   also trading worse prices relative to fair. The sign, though, needs no extra ingredient.")
