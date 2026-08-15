"""Trap 8 — informative missingness: a high drop rate is fine, a VARYING one is fatal.

You join two sources — decisions to outcomes, quotes to resolutions, orders to fills — and some rows
do not match. The instinct is to check how many were lost and, if the fraction is tolerable, proceed.
That instinct is backwards. The size of the loss barely matters; what matters is whether the
probability of being lost **varies along the variable you are testing.**

Here the truth is flat: there is no relationship anywhere. But rows survive the join more often at one
end of the range than the other, AND the outcome affects survival more strongly where retention is
worst. The observed relationship acquires a large slope that does not exist — and it does not wash out
with more data, because nothing about it is noise. More data measures the artefact more precisely.

The diagnostic is one table: retention by band of the test variable. If it is flat, the drop is
harmless at any size. If it slopes, the surviving sample is biased along the axis of interest and the
result is uninterpretable until you recover the missing rows.

Lesson: never report a joined result without printing retention per band. And RECOVER the rows rather
than adjusting for them — the mechanism is rarely known well enough to model.
Run: python trap8_informative_missingness.py
"""
import numpy as np

rng = np.random.default_rng(8)

TRUE_EFFECT = 0.0          # ground truth: FLAT. no relationship between x and y, anywhere.
BASE_WR = 0.75


def sample(n):
    """Returns x, y, kept. The truth is flat; only the JOIN is selective."""
    x = rng.uniform(-0.20, 0.02, n)              # test variable, e.g. a model's claimed edge
    won = rng.random(n) < BASE_WR                # outcome, independent of x by construction
    y = np.where(won, 1.0, 0.0) - BASE_WR + TRUE_EFFECT * x

    # ⛔ Retention falls as x falls. In the live instance outcomes were joined from our own trade
    # registries, which only contain markets an arm actually TRADED — and a rejected deep-edge
    # candidate is exactly the one no arm traded.
    base = np.clip(0.95 + 3.0 * x, 0.05, 0.98)
    # ⛔ AND the outcome matters MORE where retention is worst: a losing row at the sparse end is
    # likelier still to vanish. This interaction is what bends a flat truth into a slope.
    loser_factor = np.clip(0.45 + 3.0 * (x + 0.20), 0.45, 1.0)
    p_keep = base * np.where(won, 1.0, loser_factor)
    return x, y, rng.random(n) < p_keep


def slope(xx, yy):
    b, a = np.polyfit(xx, yy, 1)
    resid = yy - (b * xx + a)
    se = np.sqrt((resid ** 2).sum() / (len(xx) - 2) / ((xx - xx.mean()) ** 2).sum())
    return b, b / se


N = 40000
x, y, kept = sample(N)

BANDS = [("x < -0.05", -9.0, -0.05), ("[-0.05,-0.02)", -0.05, -0.02),
         ("[-0.02, 0)", -0.02, 0.0), ("[0, 0.02)", 0.0, 0.02)]

print("%d rows; the TRUE effect of x on y is exactly %.1f — flat everywhere\n" % (N, TRUE_EFFECT))
print("  RETENTION BY BAND — the one table that catches this")
print("  %-16s %9s %9s %10s %10s" % ("band", "total", "kept", "retention", "kept WR"))
for lab, lo, hi in BANDS:
    m = (x >= lo) & (x < hi)
    k = m & kept
    print("  %-16s %9d %9d %9.1f%% %10.3f"
          % (lab, m.sum(), k.sum(), 100 * kept[m].mean(), (y[k] + BASE_WR).mean()))
rates = [kept[(x >= lo) & (x < hi)].mean() for _l, lo, hi in BANDS]
spread = max(rates) - min(rates)
print("  retention spread across bands: %.0f percentage points   <-- %s"
      % (100 * spread, "INFORMATIVE: the sample is biased along the test axis"
         if spread > 0.15 else "harmless"))
print("  (note the kept win-rate also drifts, which is the interaction doing the damage)")

b_all, t_all = slope(x, y)
b_obs, t_obs = slope(x[kept], y[kept])
print("\n  %-28s slope=%+.4f  t=%+7.2f   n=%d" % ("FULL population (the truth)", b_all, t_all, N))
print("  %-28s slope=%+.4f  t=%+7.2f   n=%d   <-- a large effect from nothing"
      % ("SURVIVORS of the join", b_obs, t_obs, kept.sum()))
print("  %-28s %.1f%% of rows" % ("dropped", 100 * (1 - kept.mean())))

print("\n  more data does NOT help — it only sharpens the artefact:")
for n in (40000, 160000, 640000):
    xx, yy, kk = sample(n)
    b, t = slope(xx[kk], yy[kk])
    print("     n=%-7d  slope=%+.4f  t=%+7.2f" % (n, b, t))

print("\n=> Live instance: outcomes joined from our own registries retained 91.3% of rows in the")
print("   shallowest band and 29.0% in the deepest — a 62-point gradient along the very axis under")
print("   test. Recovering all 13,207 outcomes from the venue lifted retention to 100.0% in every")
print("   band. None of the other checks in this repo would have caught it.")
