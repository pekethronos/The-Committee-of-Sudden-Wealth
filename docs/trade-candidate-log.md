# Trade Candidate Log

Use this file to preserve cases that should survive beyond the current turn.

Record:

- open valid targets not yet implemented
- rejected or visually misleading setups
- uncertain cases waiting for more examples
- cases later fixed by a strategy change

## Entry template

### candidate-id

- Status: `open` / `rejected` / `uncertain` / `fixed`
- Pattern tags:
- Round / product:
- Window:
- Why it looked interesting:
- What weakens the case:
- Max favorable:
- Max adverse:
- Related files:
- Related iteration:
- Notes:

## Entries

### tutorial-tomatoes-hybrid-wall-mid

- Status: `rejected`
- Pattern tags: `tutorial`, `tomatoes`, `wall-mid`, `large-level`, `fair-estimation`
- Round / product: `tutorial_round_1 / TOMATOES`
- Window: official tutorial `days -2/-1`, reconstructed hidden days from `576` and `1462`
- Why it looked interesting: top public Prosperity evidence repeatedly favored dominant-liquidity / wall-mid fair estimation, and the old tutorial trader really was treating all large displayed levels as generic adverse selection.
- What weakens the case: the actual hidden tutorial bundles had zero large-level tomato taker fills, and defaulting to the `hybrid` wall-mid path degraded both the official replay (`+31,508` vs `+31,558`) and the reconstructed `576` hidden replay (`+146` vs `+195`).
- Max favorable: `+50` worse than baseline on the public tutorial bundle, with lower tomato take quantity but no compensating hidden gain.
- Max adverse: `-49` on the reconstructed `576` hidden replay relative to the current candidate gate.
- Related files: `rounds/tutorial_round_1/trader.py`, `scripts/analyze_submission_log.py`
- Related iteration: `2026-03-17 - tutorial tomato feature refactor and gated mode promotion`
- Notes: keep the wall-mid and large-level helpers in the file for future replay work, but do not promote `hybrid` again without new live evidence that large tomato walls are actually tradable.

### tutorial-tomatoes-nearby-constant-sweep

- Status: `rejected`
- Pattern tags: `tutorial`, `tomatoes`, `execution`, `take-width`, `maker-edge`, `ema`
- Round / product: `tutorial_round_1 / TOMATOES`
- Window: official tutorial `days -2/-1`, reconstructed hidden days from `576` and `1462`
- Why it looked interesting: the active tutorial trader was clearly better than the old `+31,797` public winner on hidden reconstruction, but it still felt plausible that one more narrow tomato constant change could beat the current hidden plateaus without rewriting the strategy.
- What weakens the case: repeated sweeps around the current settings kept selecting the same active constants. Nearby alternatives improved one window at best, then regressed on either the public tutorial bundle or the second reconstructed hidden bundle.
- Max favorable: the strongest alternatives only tied the current `+195` reconstructed `576` result or landed slightly below it, while still giving back public or `1462` performance.
- Max adverse: lower skew, weaker reversion, or more aggressive buy-taking collapsed hidden tomato PnL quickly; examples included reconstructed `1462` falling to `+97` with `skew 0.10` and reconstructed `576` falling to `+13` to `+28` with `buy width 2`.
- Related files: `rounds/tutorial_round_1/trader.py`, `artifacts/sweeps/2026-03-17-hidden576`, `artifacts/sweeps/2026-03-17-hidden576-fair`, `artifacts/sweeps/2026-03-17-hidden1462`, `artifacts/sweeps/2026-03-17-public-check`
- Related iteration: `2026-03-17 - final tutorial tomato constant sweep`
- Notes: keep the active constants as the tutorial final. Do not re-open this exact local search space unless a future live bundle shows a different hidden tomato trade mix.
