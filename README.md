# tcosw

Competition prep workspace for IMC Prosperity 4.

This repo is now intended to be the working competition repo, not a notes dump.

## Current state

The starting research base is:

- `prosperity_competition_research.md`
- `prosperity_repo_strategy_mining.md`

Those two documents already answer the broad strategic question. The remaining work is disciplined iteration:

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
- `docs/day0-intake.md` - official Day 0 notes and current tutorial assumptions
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

## Pre-Day-1 status

Completed:

1. Prior-round replay runs locally with `prosperity3bt`.
2. Tutorial logs open in the Prosperity 3 visualizer through `scripts/open_visualizer.py`.
3. Shared runtime covers fixed-fair, dominant-liquidity, basket scaffolding, and conversion cost helpers.
4. Mechanics probes cover order cancellation, position-limit cancellation, and trade-matching mode behavior.
5. Trade decomposition, parameter sweeps, and replay diff tooling are in place.

Current baseline stance from the bundled public data:

- keep round-0 and round-2 baselines simple and evidence-backed
- leave the generic basket module available for experiments, but do not enable it by default until a visual review supports the thresholds on real round data

## Public-round tooling

Start with:

```bash
./scripts/setup_public_tooling.sh
./scripts/run_public_replay.sh --help
./scripts/init_trader_from_template.sh rounds/tutorial/trader.py
./scripts/run_public_replay.sh rounds/tutorial/trader.py 0
./scripts/run_first_practice_backtest.sh
./scripts/run_official_tutorial_backtest.sh
./scripts/run_round2_practice_backtest.sh
./scripts/diff_backtest_trades.py artifacts/sweeps/baseline_runtime.log artifacts/sweeps/bad_resin_runtime.log
./scripts/decompose_backtest_trades.py artifacts/tutorial/replays/round0.log
./scripts/run_mechanics_probes.py
./scripts/open_visualizer.py artifacts/tutorial/replays/round0.log --no-open
```

These helpers are intentionally thin wrappers so the repo can standardize the workflow without locking into one exact public tool implementation.

`prosperity3bt` ships bundled prior-round practice data, so the first replay can run immediately without cloning extra datasets.

For deeper inspection, clone-only research repos live under `external/` locally and are ignored by git.

To sync the exact repo set referenced by the research docs:

```bash
./scripts/sync_research_repos.sh
```
