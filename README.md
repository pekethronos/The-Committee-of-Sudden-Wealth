# tcosw

Competition prep workspace for IMC Prosperity 4.

This repo is now intended to be the working competition repo, not a notes dump.

## Current state

The starting research base is:

- `prosperity_competition_research.md`
- `prosperity_repo_strategy_mining.md`

Those two documents already answer the broad strategic question. The remaining work is execution:

- build a fast replay and review loop
- implement reusable strategy modules for recurring Prosperity archetypes
- keep evidence and iteration notes in one place
- be ready to diff official Prosperity 4 materials the day they drop

## Repo layout

- `CODEX.md` - repo handoff and operating context
- `.agents/skills/` - repo-local Prosperity workflow skills
- `docs/strategy-iteration-log.md` - shipped strategy changes and validation notes
- `docs/trade-candidate-log.md` - open, rejected, uncertain, and fixed candidate cases
- `docs/baseline-snapshots.md` - periodic replay snapshots to detect drift
- `docs/round-open-checklist.md` - Day 1 / new-round checklist
- `docs/manual-round-log.md` - manual-round work log and solved patterns
- `scripts/` - lightweight workflow helpers
- `templates/trader.py` - minimal Prosperity trader starting point
- `rounds/` - round-local traders and support shims
- `data/` - local datasets, downloaded round inputs, sqlite snapshots, and sample files
- `artifacts/` - replay outputs, visualizer exports, and diff artifacts

## Operating workflow

1. Use `$prosperity-round-open-checklist` when official Prosperity 4 materials or a new round opens.
2. Use `$prosperity-candidate-discovery` to scan round data for missed trades, suspicious triggers, and repeated failure patterns.
3. Use `$prosperity-strategy-iteration` to patch the trader, replay the change, and log the before/after evidence.
4. Use `$prosperity-manual-round-solver` only when the manual challenge is live or when building reusable templates for it.

## Immediate priorities

Before Prosperity 4 starts:

1. Verify the prior-round replay toolchain works locally.
2. Build a trader code skeleton with shared execution and risk helpers.
3. Implement the recurring modules first:
   - fixed-fair market making with inventory clearing
   - dominant-liquidity fair estimation
   - basket premium arbitrage
   - conversion-cost accounting scaffold
4. Keep all iteration evidence in the logs under `docs/`.

## Public-round tooling

Start with:

```bash
./scripts/setup_public_tooling.sh
./scripts/run_public_replay.sh --help
./scripts/init_trader_from_template.sh rounds/tutorial/trader.py
./scripts/run_public_replay.sh rounds/tutorial/trader.py 0
./scripts/run_first_practice_backtest.sh
./scripts/diff_backtest_trades.py artifacts/sweeps/baseline_runtime.log artifacts/sweeps/bad_resin_runtime.log
```

These helpers are intentionally thin wrappers so the repo can standardize the workflow without locking into one exact public tool implementation.

`prosperity3bt` ships bundled prior-round practice data, so the first replay can run immediately without cloning extra datasets.

For deeper inspection, clone-only research repos live under `external/` locally and are ignored by git.

To sync the exact repo set referenced by the research docs:

```bash
./scripts/sync_research_repos.sh
```
