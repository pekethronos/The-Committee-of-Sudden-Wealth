# Prosperity Context

## Purpose

This repo is the working preparation and competition workspace for IMC Prosperity 4.

Primary goals before Round 1:

1. Have a reliable local replay and review loop for prior-round public data.
2. Build reusable strategy modules for recurring Prosperity archetypes.
3. Keep evidence, iteration history, and rejected ideas attributable.
4. Be ready to diff Prosperity 4 official rules and data format against prior assumptions on the day they appear.

## Existing research

- `~/tcosw/prosperity_competition_research.md`
- `~/tcosw/prosperity_repo_strategy_mining.md`

These are reference documents, not the operating workflow.

## Open These Next

After loading `CODEX.md`, open only the paths relevant to the task:

- `README.md`
- `docs/strategy-iteration-log.md`
- `docs/trade-candidate-log.md`
- `docs/baseline-snapshots.md`
- `docs/round-open-checklist.md`
- `docs/manual-round-log.md`
- `.agents/skills/prosperity-candidate-discovery/SKILL.md`
- `.agents/skills/prosperity-strategy-iteration/SKILL.md`
- `.agents/skills/prosperity-round-open-checklist/SKILL.md`
- `.agents/skills/prosperity-manual-round-solver/SKILL.md`
- `scripts/setup_public_tooling.sh`
- `scripts/run_public_replay.sh`
- `scripts/run_first_practice_backtest.sh`
- `scripts/diff_backtest_trades.py`
- `scripts/run_parameter_sweep.py`
- `scripts/init_trader_from_template.sh`
- `templates/trader.py`
- `rounds/tutorial/trader.py`

## Repo-local workflow

- Use `$prosperity-round-open-checklist` when official Prosperity materials for a new edition or round become available.
- Use `$prosperity-candidate-discovery` when you want Codex to scan datasets, replay outputs, and logs for promising or suspicious cases before changing strategy code.
- Use `$prosperity-strategy-iteration` when you already have a concrete strategy hypothesis and want code changes plus validation.
- Use `$prosperity-manual-round-solver` when solving or templating manual challenges.

## Principles

- Prefer evidence from official docs and replay outputs over memory and screenshots.
- Keep no-lookahead discipline during idea evaluation.
- Separate candidate discovery from strategy edits.
- Log rejected and uncertain cases so the same weak idea is not rediscovered repeatedly.
- Use challenge-window replays whenever data volume allows; do not trust a single development window.
- Prefer robust threshold regions and simpler logic over a sharper in-sample fit.

## Immediate execution priorities

1. Get prior-round public replay running locally.
2. Create the trader code skeleton with shared helpers and logging discipline.
3. Add a baseline diff workflow for replay outputs.
4. Keep round-opening assumptions explicit so Prosperity 4 changes are caught immediately.

## Standard artifacts

- `docs/strategy-iteration-log.md` records shipped changes.
- `docs/trade-candidate-log.md` records open, rejected, uncertain, and fixed cases.
- `docs/baseline-snapshots.md` records periodic wider-window replay summaries.
- `artifacts/` stores replay outputs, diffs, and visual exports.
- `data/` stores downloaded round files and local copies of public datasets.
