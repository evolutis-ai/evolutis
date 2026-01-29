# Evolutis

**Autonomous crypto trading system powered by evolutionary reinforcement learning.**

Evolutis uses a population of PPO (Proximal Policy Optimization) agents that evolve across generations through a genetic algorithm. The best-performing agents are selected, mutated, and recombined to produce increasingly effective trading strategies across 9 cryptocurrency pairs.

---

## How It Works

### Evolutionary Training Pipeline

1. **Population Initialization** — A diverse population of RL agents is spawned, each with randomized hyperparameters and trading rules
2. **Training** — Each agent is trained via PPO on historical 1-minute OHLCV data across 9 crypto pairs (BTC, ETH, BNB, ADA, XRP, DOGE, DOT, LTC, LINK)
3. **Evaluation** — Agents are backtested on held-out data; portfolio performance, risk metrics, and consistency are measured
4. **Selection & Evolution** — Top performers are selected. Their hyperparameters and trading rules are crossed over and mutated to create the next generation
5. **Repeat** — The cycle continues for 15+ generations, progressively improving agent quality

### Trading Architecture

- **Environment**: Custom Gymnasium environment simulating multi-asset portfolio management with realistic transaction fees, slippage, and position sizing constraints
- **Observation Space**: OHLCV data enriched with technical indicators (SMA, RSI, EMA) across multiple timeframes (10, 20, 50, 100, 1000 periods)
- **Action Space**: 303 discrete actions per cryptocurrency — granular sell/hold/buy decisions with 150 position-sizing steps
- **Trading Rules**: Each agent evolves its own set of trading filters (RSI thresholds, SMA crossovers, BTC correlation stops, trailing stops, profit-taking rules)

### Execution Modes

| Mode | Description |
|------|-------------|
| **Backtest** | Simulate on historical data with full metrics |
| **Paper Trading** | Real-time market data, simulated execution |
| **Testnet Trading** | Real orders on Binance Testnet |
| **Ensemble Voting** | Multiple agents vote on trades (majority, weighted, conservative, median strategies) |

---

## Results

### 365-Day Backtest — All Top Performers

![All Agents Comparison](results/backtests/all_agents_365d_comparison.png)

### Performance Summary

![Summary Table](results/backtests/summary_table.png)

All 6 top-performing agents achieved positive returns over the 365-day backtest period (Jan 2025 — Jan 2026), with the best agent returning **+134.5%**.

### Individual Agent Performance

<details>
<summary>Agent 21 (Gen 8) — Best Performer (+134.5%)</summary>

![Agent 21](results/backtests/agent_21_gen_8_365d.png)
</details>

<details>
<summary>Agent 12 (Gen 12) — +86.4%</summary>

![Agent 12](results/backtests/agent_12_gen_12_365d.png)
</details>

<details>
<summary>Agent 4 (Gen 7) — +48.3%</summary>

![Agent 4](results/backtests/agent_4_gen_7_365d.png)
</details>

<details>
<summary>Agent 8 (Gen 5) — +46.5%</summary>

![Agent 8](results/backtests/agent_8_gen_5_365d.png)
</details>

<details>
<summary>Agent 34 (Gen 14) — +44.8%</summary>

![Agent 34](results/backtests/agent_34_gen_14_365d.png)
</details>

<details>
<summary>Agent 6 (Gen 12) — +17.3%</summary>

![Agent 6](results/backtests/agent_6_gen_12_365d.png)
</details>

---

## Tech Stack

- **RL Framework**: Stable-Baselines3 (PPO)
- **Environment**: Gymnasium (custom multi-asset trading env)
- **Data**: Binance API via ccxt (1-minute OHLCV candles)
- **Indicators**: ta (Technical Analysis library)
- **Evolution**: Custom genetic algorithm for hyperparameter and trading rule optimization

---

## Disclaimer

This project is for educational and research purposes only. Past backtest performance does not guarantee future results. Cryptocurrency trading involves substantial risk of loss. Do not trade with money you cannot afford to lose.

---

## License

MIT
