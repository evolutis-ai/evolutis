# Falsifying Alpha in Crypto Prediction Markets

*A research program that systematically killed its own trading edges — and the reusable methodology that
came out of it.*

**Author:** pgioun@gmail.com

> **The short version:** I built a full data + execution + research stack for short-horizon crypto
> prediction markets and spent six months trying to *falsify* the idea that a small, slow, retail
> participant can extract price alpha there. Roughly **1,050 hypotheses** were tested under
> pre-registration with multiplicity control. Every candidate edge died, and most died the same way —
> **the number being measured was not the number that mattered.** The deliverable isn't a strategy; it's a
> **falsification pipeline** and nine named traps that each make a dead edge look alive. This repo
> reproduces all nine on synthetic data in a few seconds.

---

## Repository layout

```
.
├── README.md                 # this file — the narrative + results
├── METHODOLOGY.md            # the traps in depth, and the real instance behind each
├── requirements.txt          # numpy only
└── exhibits/                 # self-contained, runnable demonstrations
    ├── README.md
    ├── trap1_longshot_tail.py             # the mean lies; the median tells the truth
    ├── trap2_snapshot_sampling.py         # correlated snapshots fake an edge at fake significance
    ├── trap3_maker_adverse_selection.py   # a backtest that assumes fills is fiction
    ├── trap4_overfitting_gap.py           # the best-in-sample parameter set is a mirage
    ├── trap5_obtainable_fills.py          # the good prices had NO SIZE behind them
    ├── trap6_selecting_winners.py         # copying the best performers is WORSE than random
    ├── trap7_significance_vs_bias.py      # a strict bar stops noise, not bias
    ├── trap8_informative_missingness.py   # a high drop rate is fine; a VARYING one is fatal
    └── trap9_metric_decides_the_answer.py # one dataset, four denominators, four answers
```

Run any exhibit with `python exhibits/trapN_*.py` (needs only `numpy`).

## The domain

Binary markets that resolve on a price feed: buy "Up" or "Down" for a fixed 5- or 15-minute window; the
winning share pays \$1, the loser \$0. They *look* like a retail alpha playground — fast feedback, visible
order books, frequent obvious-looking mispricings, spreads wide enough to seem like free money. I treated
that appearance as a hypothesis to break, not a promise.

## Two findings, and the second one is the useful one

**1. The fill is adversely selected.** A fill-or-kill order fills you **on the losers and misses you on the
winners**, because whoever leaves a stale-cheap offer you can lift is disproportionately the party about to
be right. Measured by running the *same* strategy on paper and with real money:

| | Avg price paid | Win rate | Result |
|---|---|---|---|
| Paper | 0.760 | 78% | **+EV** |
| Live (real fills) | 0.785 | 75% | **−EV** |

A **double squeeze** — you pay more *and* win less. Confirmed from the other side too: trades the strategy
*missed* had a **+2.7pp** edge; the ones it *got* had **−3.4pp** (z=+4.37). **Identifying a good trade does
not let you have it.** The counterparty declines exactly when declining is right.

**2. Most of my own results were wrong for measurement reasons, not statistical ones.** This is the part
worth reading. The final, honest, pooled number across everything that traded real money:

```
all live arms, outcome-based (a win counts whether or not it was ever collected)
  3,100 trades   1,183 windows   $3,512 staked
  −6.53% of stake     t = −3.20     95% CI [−0.1067, −0.0257]
```

The entire interval is negative. Meanwhile the paper fleet's headline said otherwise — and the gap between
those two statements is where the nine traps live.

## The graveyard

| Edge | The idea | Cause of death |
|---|---|---|
| Endgame stale-ask sniping | Lift mispriced-cheap offers in the final 2 minutes | Real signal; dies to the fill-race live |
| Order-flow cascade → book lag | A book imbalance leads the market ~2pp; fires *early*, dodging the fill-race | Real & fill-race-immune, but the P&L was **longshot-tail inflated** (Trap 1) |
| Passive making on the cascade | Post a resting bid instead of taking | Adversely selected: filled ~70% of winners vs ~88% of losers (Trap 3) |
| Post-resolution "certain winner" snipe | Buy the decided winner below \$1 in the settlement gap | Book reprices in seconds → a latency race a slow taker loses |
| Early/mid-game mispricing | The cheap side looks underpriced | It's the vig; the headline was a **sampling artifact** (Trap 2) |
| Longshot mispricing | Cheap contracts win more often than they're priced | **+8.0pp in the price, −0.3% in the fills.** Real and not capturable |
| Copying the top wallets | Find persistent winners on-chain and follow them | **Actively harmful** — the top 5% lose more than the field (Trap 6) |
| Below-gate model edge | The model's own edge metric, in the region its filter rejects | Flat in *both* directions; the price there is calibrated to 0.02pp |
| A longer horizon (15m vs 5m) | Maybe the 5m window is just too fast | Indistinguishable from zero; all four price bands flat |
| Cross-venue making (5× the toll) | A bigger fee should mean bigger compensation for liquidity | Adverse selection **+53.9pp**; the subsidy covers **0.4%** of it |
| Multi-outcome / pair / book arbitrage | Mechanical, no forecast required | Overround is smaller than the cost of crossing every leg |
| Imbalance / positioning / cross-venue basis | Classic signals | Efficient, or real but execution-gated (~8% crossable) |

## The contribution: nine traps that fake an edge

Every item above first *looked real*. Each was killed by naming and testing a specific trap. **These
generalize far beyond prediction markets** — the exhibits reproduce each one on synthetic data with a known
ground truth.

Traps **1–4 are about inference** — reading a number wrongly. Traps **5–9 are about measurement** — the
number itself being the wrong number. The second class is harder, more expensive, and much less discussed.

| | Trap | The one-line diagnostic |
|---|---|---|
| 1 | Longshot tail | Judge the median, not the mean |
| 2 | Snapshot sampling | One independent observation per outcome |
| 3 | Maker adverse selection | Model the fill as an event; split fill rate by outcome |
| 4 | Overfitting gap | Optimize on train, score out-of-sample, report the gap |
| 5 | **Obtainability** | Record depth at decision time; obtainable / not / **unknown** |
| 6 | **Winner selection** | Rank *within* a price bin; check the selected cohort's mean price |
| 7 | **Significance vs bias** | A biased t grows as √n. Pool the population |
| 8 | **Informative missingness** | Print retention per band of the test variable |
| 9 | **Metric choice** | Correlate the *style* before correlating performance |

See [`exhibits/README.md`](exhibits/README.md) for each one's output and takeaway, and
[`METHODOLOGY.md`](METHODOLOGY.md) for the reasoning and the real instance behind it.

### The single most expensive lesson

**Trap 5.** A paper arm books a trade whenever it *sees* a price; it does not check that anyone was offering
the size. Those are not independent — a quote is attractive *because* it is thin. Splitting one arm's results
on whether the depth was actually there:

```
OBTAINABLE (size existed)    n=1,426   −0.0436/trade   t=−2.40    −$38.74
NOT OBTAINABLE (no size)     n=1,553   +0.1237/trade   t=+7.57   +$241.10
ALL (the headline)           n=2,980   +0.0384/trade   t=+2.90   +$202.71
```

**100% of the apparent profit was in trades that could not have been bought.** This class of error voided
roughly a fortnight of prior results, including one finding that had passed selection correction *and* both
walk-forward halves *and* independently replicated an earlier result — and was still wrong. Selection
correction and walk-forward do not protect you against a contaminated population.

## What actually survives

Three things, none of which is "prediction":

- **Structure** — signals that fire *before* the contested moment. Real, but small and easy to overstate.
- **Subsidy** — liquidity rewards, maker rebates, incentive programs: income paid for *providing liquidity*,
  independent of who you fill. The only mechanism that structurally sidesteps adverse selection, because the
  payoff isn't tied to the outcome. It is a **risk premium for holding inventory**, not a free lunch — and it
  must be sized against the bleed: on one venue the subsidy covered **0.4%** of the measured adverse
  selection.
- **Making, maybe** — a resting order inverts the selection problem: someone else chooses to trade against
  *you*, so you are the party that declines. It is the only idea that attacks the measured cause rather than
  hunting a better forecast. At the time of writing it is under an honest, pre-registered test whose fills are
  determined from the real tape against measured queue depth. The prior is failure.

The unifying lesson: **every durable edge in these markets is "get paid to hold a risk or cost that stops
others from arbitraging it."** These markets are efficient-to-vig at every horizon; the retail-taker edge is
a mirage generated by the traps above.

## What this demonstrates

- Building and operating a full live data + execution + research system solo.
- Reasoning about market microstructure and adverse selection from first principles.
- **Pre-registration with real teeth**: ~30 sealed hypotheses with gates, power calculations and
  multiplicity-corrected bars fixed *before* the data existed — including one whose ambiguity I resolved
  *against myself*, raising its own gate 3.4× rather than take an easier read.
- **The discipline to kill my own best ideas with data before they cost money** — which, in trading, is the
  whole job.

## License

MIT — see [LICENSE](LICENSE). Operational details (keys, infrastructure, live sizing) are intentionally
omitted; all figures come from the research pipeline, and the exhibits use synthetic data only.
