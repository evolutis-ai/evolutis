# Falsifying Alpha in Crypto Prediction Markets

*A research program that systematically killed its own trading edges — and the reusable methodology that
came out of it.*

**Author:** pgioun@gmail.com

> **The short version:** I built a full data + execution + research stack for short-horizon crypto
> prediction markets and spent six weeks trying to *falsify* the idea that a small, slow, retail participant
> can extract price alpha there. Every candidate edge died, and they all died to the same thing — **adverse
> selection in the fill** (the winner's curse). The deliverable isn't a strategy; it's a **falsification
> pipeline** and four named statistical traps that each make a dead edge look alive. This repo reproduces
> all four on synthetic data in a few seconds.

---

## Repository layout

```
.
├── README.md                 # this file — the narrative + results
├── METHODOLOGY.md            # the three traps in depth
├── requirements.txt          # numpy only
└── exhibits/                 # self-contained, runnable demonstrations
    ├── README.md
    ├── trap1_longshot_tail.py           # the mean lies; the median tells the truth
    ├── trap2_snapshot_sampling.py       # correlated snapshots fake an edge at fake significance
    ├── trap3_maker_adverse_selection.py # a backtest that assumes fills is fiction
    └── trap4_overfitting_gap.py         # the best-in-sample parameter set is a mirage
```

Run any exhibit with `python exhibits/trapN_*.py` (needs only `numpy`).

## The domain

Binary markets that resolve on a price feed: buy "Up" or "Down" for a fixed 5- or 15-minute window; the
winning share pays \$1, the loser \$0. They *look* like a retail alpha playground — fast feedback, visible
order books, frequent obvious-looking mispricings, spreads wide enough to seem like free money. I treated
that appearance as a hypothesis to break, not a promise.

## The central finding: the fill is adversely selected

Taker fills suffer the winner's curse. A fill-or-kill order fills you **on the losers and misses you on the
winners**, because whoever leaves a stale-cheap offer you can lift is disproportionately the party about to
be right. Measured by running the *same* strategy on paper and with real money:

| | Avg price paid | Win rate | Result |
|---|---|---|---|
| Paper | 0.760 | 78% | **+EV** |
| Live (real fills) | 0.785 | 75% | **−EV** |

A **double squeeze** — you pay more *and* win less — silently flips a backtested edge into a realized loss.

## The graveyard

| Edge | The idea | Cause of death |
|---|---|---|
| Endgame stale-ask sniping | Lift mispriced-cheap offers in the final 2 minutes | Real signal; dies to the fill-race live |
| Order-flow cascade → book lag | An order-book imbalance leads the market book ~2pp; fires *early*, dodging the fill-race | Real & fill-race-immune, but the P&L was **longshot-tail inflated** (Trap 1) |
| Passive making on the cascade | Post a resting bid instead of taking | Adversely selected: filled ~70% of winners vs ~88% of losers (Trap 3) |
| Post-resolution "certain winner" snipe | Buy the decided winner below \$1 in the settlement gap | Book reprices in seconds → a latency race a slow taker loses |
| Early/mid-game mispricing | The cheap side looks underpriced | It's the vig; the headline signal was a **sampling artifact** (Trap 2) |
| Imbalance / positioning / cross-venue basis | Classic signals | Efficient, or real but execution-gated (~8% crossable) |

## The contribution: four traps that fake an edge

Every item above first *looked real*. Each was killed by naming and testing a specific trap. **These
generalize far beyond prediction markets** — the exhibits reproduce each one on synthetic data.

### Trap 1 — the longshot tail *(judge the median, not the mean)*
Heavy-tailed P&L: a true-**negative**-edge strategy still shows a positive small-sample mean a large fraction
of the time, carried by rare big wins. `exhibits/trap1_longshot_tail.py`:
```
TRUE edge (N=2,000,000):  mean=-0.0175   median=-0.1438   win%=15.8
At n=300, over 2,000 runs:  MEAN>0 in 19.4% of runs;  MEDIAN>0 in 0.0% of runs
```

### Trap 2 — snapshot sampling *(de-duplicate shared outcomes)*
Pooling correlated per-snapshot observations inflates n *and* biases the estimate toward winners.
`exhibits/trap2_snapshot_sampling.py`:
```
POOLED snapshots      : WR=0.475  edge=+0.275  n=311035  (+306.8 SE)   <-- fake strong POSITIVE edge
ONE entry per market  : WR=0.184  edge=-0.016  n=4000    ( -2.5 SE)    <-- the TRUTH: negative
```
This is the exact mechanism behind a real study that showed **+7% per bet over 333k snapshots** and became
**−10% per bet at −12σ** once de-duplicated to one entry per market.

### Trap 3 — maker-fill adverse selection *(model fills as events)*
A resting bid fills only when the price comes to you — i.e. when you're losing. `exhibits/trap3_maker_adverse_selection.py`:
```
NAIVE (assume fill)  : WR=0.50  EV/bet=+0.0536   <-- looks profitable
OBSERVABLE fills     : WR=0.30  EV/bet=-0.1470   <-- the truth
fill rate on WINNERS = 41%   vs   LOSERS = 95%   <-- adverse selection
```

### Trap 4 — the overfitting gap *(optimize on train, score out-of-sample)*
Sweeping a grid and keeping the best combo manufactures a positive optimum from noise; only the out-of-sample
score is real. `exhibits/trap4_overfitting_gap.py` (400 combos, *every one with true edge 0*):
```
best IN-SAMPLE combo      : mean = +0.116   <-- looks like a strong edge (pure selection)
that combo OUT-OF-SAMPLE  : mean = +0.036   <-- the truth: ~0  (+0.8 SE)
```
Same shape as a real walk-forward cascade sweep: in-sample optimum +0.034 → pooled out-of-sample +0.011
(statistical zero), chosen params flipping fold to fold. The in-sample optimum was the mirage.

## What actually survives

Two things, neither of which is "prediction":

- **Structure** — signals that fire *before* the contested moment (the order-flow cascade). Real, but small
  and easy to overstate (Trap 1).
- **Subsidy** — liquidity rewards, maker rebates, incentive programs: income paid for *providing liquidity*,
  independent of who you fill. The only thing that structurally sidesteps adverse selection — because the
  payoff isn't tied to the outcome. It is a **risk premium for holding inventory**, not a free lunch.

The unifying lesson: **every durable edge in these markets is "get paid to hold a risk or cost that stops
others from arbitraging it."** These markets are efficient-to-vig at every horizon; the retail-taker edge is
a mirage generated by the four traps above.

## What this demonstrates

- Building and operating a full live data + execution + research system solo.
- Reasoning about market microstructure and adverse selection from first principles.
- **The discipline to kill my own best ideas with data before they cost money** — which, in trading, is the
  whole job.

## License

MIT — see [LICENSE](LICENSE). Operational details (keys, infrastructure, live sizing) are intentionally
omitted; all figures come from the research pipeline, and the exhibits use synthetic data.
