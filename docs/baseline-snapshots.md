# Baseline Snapshots

Use this file for wider-window replay summaries so cumulative drift is visible.

## Snapshot template

### YYYY-MM-DD

- Commit / branch:
- Dataset:
- Window:
- Trade count:
- Realized PnL:
- Win rate:
- Max drawdown:
- Notes:

## Snapshots

### 2026-03-16

- Commit / branch: `uncommitted scaffold on main`
- Dataset: `prosperity3bt` bundled resources
- Window: `round 0 day -1`
- Trade count: tutorial artifact generated; use `scripts/diff_backtest_trades.py --show-unchanged` for exact count
- Realized PnL: `+3,203`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: first end-to-end local replay for the repo using the shared runtime scaffold in `rounds/tutorial/trader.py`

### 2026-03-16

- Commit / branch: `post-probe pre-commit state on main`
- Dataset: `prosperity3bt` bundled resources
- Window: `round 2 days -1/0/1`
- Trade count: `21,458` submission trades
- Realized PnL: `+57,018.5`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: round-2 baseline uses only the positive fixed-fair and dominant-liquidity core; generic basket variants were left out of the default trader after challenge-window sweeps stayed negative on the bundled public data

### 2026-03-16

- Commit / branch: `post-Day-0 intake pre-commit state on main`
- Dataset: official tutorial bundle in `data/TUTORIAL_ROUND_1/`
- Window: `round 0 days -2/-1`
- Trade count: `1,945` submission trades
- Realized PnL: `+8,022`
- Win rate: not yet summarized
- Max drawdown: not yet summarized
- Notes: first official Prosperity 4 tutorial baseline; local replay uses product-limit overrides because the public backtester does not yet know the `EMERALDS` and `TOMATOES` names
