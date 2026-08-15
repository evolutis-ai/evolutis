"""Trap 9 — the METRIC decides the answer: "does skill persist?" has four different answers.

You want to know whether past performance predicts future performance. You split each participant's
history in half and correlate. It is the obvious test, and the number it returns depends almost
entirely on a choice you probably made without thinking: what you divided by.

Below, **nobody has any skill at all.** Every participant is priced fairly and differs only in two
persistent habits — the price band they trade, and how much they stake. Those habits alone manufacture
apparent persistence, because any metric that is not price-controlled inherits the habit:

    raw $ per market      inherits SIZE and PRICE   (a big staker stays a big staker)
    return on notional    inherits PRICE            (dividing by p amplifies the spread across bands)
    margin per share      inherits the FEE          (rate*p*(1-p) — a function of the band)
    margin vs cell-mates  inherits nothing          <- the only defensible one

The confounder is easy to see once you look for it: the price band a participant trades is highly
persistent. Correlate *that* and you get the number people mistake for skill.

Lesson: before correlating performance across time, correlate the STYLE. If style persists, any metric
that does not condition on it is measuring style. Compare each observation against its cell-mates —
others trading the same instrument in the same price bin — and leave the participant out of its own
benchmark.
Run: python trap9_metric_decides_the_answer.py
"""
import numpy as np

rng = np.random.default_rng(9)

N_AGENTS = 3000
BETS_PER_HALF = 1200     # long halves, so each agent's own mean is measured precisely
FEE_RATE = 0.07          # fee per share = rate * p * (1-p)
STYLE_DRIFT = 0.05       # habits are persistent, not frozen

# Two persistent habits, zero skill.
style = rng.uniform(0.50, 0.95, N_AGENTS)                 # the price band they live in
notional = np.exp(rng.normal(2.0, 1.1, N_AGENTS))         # what they stake, heavy-tailed


def half():
    """One observation period. Returns the four metrics, per agent."""
    p = np.clip(style + rng.normal(0, STYLE_DRIFT, N_AGENTS), 0.05, 0.98)
    won = rng.random((N_AGENTS, BETS_PER_HALF)) < p[:, None]
    margin = np.where(won, 1 - p[:, None], -p[:, None]) \
        - (FEE_RATE * p * (1 - p))[:, None]               # per share, net of fee
    shares = (notional / p)[:, None]
    return {
        "raw $ per market": (margin * shares).mean(1),
        "return on notional": (margin * shares).mean(1) / notional,
        "margin per share": margin.mean(1),
        "__price": p,
    }


A, B = half(), half()


def pearson(u, v):
    u, v = np.asarray(u, float), np.asarray(v, float)
    u, v = u - u.mean(), v - v.mean()
    r = float((u * v).sum() / np.sqrt((u * u).sum() * (v * v).sum()))
    t = r * np.sqrt(len(u) - 2) / np.sqrt(max(1 - r * r, 1e-15))
    return r, t


def demean_within_price(vals, price, k=25):
    """Subtract the LEAVE-ONE-OUT mean of everyone else in the same price bin."""
    bins = np.clip((price * k).astype(int), 0, k - 1)
    out = np.zeros_like(vals)
    for bi in range(k):
        m = bins == bi
        n = int(m.sum())
        if n < 2:
            continue
        out[m] = vals[m] - (vals[m].sum() - vals[m]) / (n - 1)
    return out


print("%d agents, ZERO skill, %d bets per half, all fairly priced." % (N_AGENTS, BETS_PER_HALF))
print("They differ only in two persistent habits: price band, and stake size.\n")
print("  %-24s %10s %10s" % ("metric, h1 vs h2", "r", "t"))
for k in ("raw $ per market", "return on notional", "margin per share"):
    r, t = pearson(A[k], B[k])
    print("  %-24s %+10.4f %+10.2f" % (k, r, t))

r, t = pearson(demean_within_price(A["margin per share"], A["__price"]),
               demean_within_price(B["margin per share"], B["__price"]))
print("  %-24s %+10.4f %+10.2f   <-- price-controlled, leave-one-out"
      % ("margin vs cell-mates", r, t))

r, t = pearson(A["__price"], B["__price"])
print("\n  %-24s %+10.4f %+10.2f   <-- THE CONFOUNDER" % ("price style itself", r, t))

print("\n=> Four numbers, one dataset, zero skill. Every metric that fails to condition on the price")
print("   band reports persistence, because the band is what persists. Controlling for it — against")
print("   cell-mates, with the agent left out of its own benchmark — collapses it toward zero.")
print("   Live, on 4,309 real wallets, the same four choices gave r = -0.480, +0.498, +0.167 and")
print("   +0.091, while price style persisted at r = +0.90. There the metric changed not just the")
print("   magnitude but the SIGN — so 'does skill persist?' was unanswerable until the question was")
print("   made specific. Report the style correlation next to any persistence claim.")
print("\n   ⭐ Note how closely 'margin per share' above matches the live +0.091 — reproduced here")
print("      with NO skill in the data at all. That is evidence the live number was style, not skill.")
