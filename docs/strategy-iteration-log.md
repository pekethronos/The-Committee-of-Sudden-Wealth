# Strategy Iteration Log

Record every meaningful strategy change here.

Use this log to preserve:

- the exact hypothesis
- the development-window evidence
- any challenge-window evidence
- what changed in code
- what trades were added, removed, or altered

If the sample is tiny, say so explicitly. Do not pretend small-N validation is stronger than it is.

## Entry template

### YYYY-MM-DD - short change label

- Status: `provisional` or `confirmed`
- Area: `market making` / `basket` / `conversion` / `options` / `risk` / `tooling`
- Hypothesis:
- Trigger for the work:
- Development window:
- Challenge window:
- Before:
- After:
- Trade-level changes:
- PnL / trade count deltas:
- Parameter sensitivity note:
- Rejected alternatives:
- Next follow-up:

## Entries

### 2026-03-16 - runtime-backed tutorial scaffold

- Status: `confirmed`
- Area: `tooling`
- Hypothesis: a config-first shared runtime with fixed-fair and dominant-liquidity modules should immediately outperform the placeholder starter trader on bundled round-0 practice data.
- Trigger for the work: repo had only research docs and a placeholder trader path with no reusable runtime.
- Development window: `prosperity3bt` bundled `round 0 day -1`
- Challenge window: not run yet
- Before: original placeholder tutorial trader produced `0` total profit on the bundled tutorial replay.
- After: runtime-backed tutorial trader produced `+3,203` total profit (`KELP +989`, `RAINFOREST_RESIN +2,214`) on the same replay.
- Trade-level changes: switched from a hardcoded placeholder to a shared runtime with fixed-fair resin handling and dominant-liquidity kelp handling; added diff and parameter-sweep tooling around the replay loop.
- PnL / trade count deltas: tutorial replay moved from `0` to `+3,203`; a deliberately bad resin config degraded the same replay to `+819`, validating that config sweeps now propagate into artifacts.
- Parameter sensitivity note: the resin fair-value perturbation was intentionally large and materially degraded results; smaller sweeps should be explored next on stable regions rather than peaks.
- Rejected alternatives: keeping a self-contained one-off trader file separate from the shared runtime.
- Next follow-up: add challenge-window practice runs on additional bundled rounds and extend the runtime with basket and conversion-aware modules when round files support them.

### 2026-03-16 - visualizer-compatible loop and mechanics probes

- Status: `confirmed`
- Area: `tooling`
- Hypothesis: the prep repo should not assume the visualizer or simulator mechanics are working just because the backtester runs; visualizer-compatible logging, explicit mechanics probes, and challenge-window basket checks are required to keep the workflow aligned with the research.
- Trigger for the work: the visualizer failed to parse the repo's initial replay logs, and the first generic round-2 basket implementation lost heavily across the bundled public days.
- Development window: `round 0 day -1`, custom controlled probe datasets, and bundled `round 2 days -1/0/1`
- Challenge window: full bundled `round 2`
- Before: tutorial logs were not visualizer-compatible; no controlled mechanics probes existed; generic round-2 basket execution with component hedging produced `-728,505` over bundled round-2 days.
- After: tutorial logs load in the Prosperity 3 visualizer; controlled probes confirm end-of-iteration cancellation, product-limit cancellation, and `--match-trades` behavior; round-2 baseline trader now stays on the positive fixed-fair plus dominant-liquidity core and produces `+57,018.5` over bundled round-2 days.
- Trade-level changes: added visualizer-format compressed logging, `traderData`-backed runtime persistence, trade decomposition tooling, controlled probe datasets and traders, an explicit visualizer server helper, and a basket engine with a minimum-history gate that remains available for experiments rather than enabled by default.
- PnL / trade count deltas: round-2 no-basket baseline finished at `+57,018.5` with `21,458` submission trades; generic basket variants finished at `-728,505`, `-267,125`, `-77,762`, `-15,654`, and `-14,634` on the same bundled data windows depending on hedging and threshold settings.
- Parameter sensitivity note: basket performance is highly sensitive and remained negative across the bundled challenge window even after stricter thresholds; keep the module experimental until visual inspection on actual round data identifies a repeatable edge.
- Rejected alternatives: assuming `prosperity3bt --vis` implied log compatibility, and defaulting the round-2 practice trader to a generic basket strategy just because basket stat-arb is a recurring archetype.
- Next follow-up: only re-enable basket logic in a default trader after candidate discovery and visual review on the relevant round data support the thresholds.

### 2026-03-16 - official Day 0 tutorial intake and baseline

- Status: `confirmed`
- Area: `tooling`
- Hypothesis: the fastest correct Day 0 move is to ingest the official tutorial files exactly as provided, patch only the tooling breakage needed to replay them locally, and ship the simplest baseline that matches the two tutorial archetypes.
- Trigger for the work: official Day 0 materials arrived with a new wiki, `EMERALDS` and `TOMATOES` tutorial files, and confirmed tutorial limits.
- Development window: official tutorial `round 0 days -2/-1` from `data/TUTORIAL_ROUND_1/`
- Challenge window: same official tutorial bundle; no additional official round data yet
- Before: repo had no runner for the official tutorial folder, no recorded Day 0 intake, and the public backtester crashed on the new product names because its built-in limit table did not include `EMERALDS` or `TOMATOES`.
- After: repo now has a Day 0 intake note, a limit-override backtest wrapper, an official tutorial replay script, and a tutorial-round baseline trader using `EMERALDS` fixed fair plus `TOMATOES` dominant-liquidity; the official tutorial baseline replay produced `+8,022` over the two provided days.
- Trade-level changes: added `scripts/run_backtest_with_limit_overrides.py`, `scripts/run_official_tutorial_backtest.sh`, and `rounds/tutorial_round_1/trader.py`; patched the baseline to use the official `80` position limits from the wiki.
- PnL / trade count deltas: official tutorial replay finished `EMERALDS +1,464`, `TOMATOES +6,558`, total `+8,022`, with `1,945` submission trades.
- Parameter sensitivity note: `EMERALDS` is stable enough to keep fixed fair at `10,000`; `TOMATOES` mean shifts across the two tutorial days, so keep it on a book-driven fair until visual review identifies something stronger.
- Rejected alternatives: hardcoding a single fair for `TOMATOES`, renaming official files to match prior Prosperity product names, or editing the installed backtester package directly.
- Next follow-up: run candidate discovery on `TOMATOES` using the official tutorial log and only then decide whether any extra tomato-specific logic is worth adding.

### 2026-03-16 - official tutorial tomato quote and take refinement

- Status: `confirmed`
- Area: `market making`
- Hypothesis: `TOMATOES` should stay on the dominant-liquidity archetype from the research, but the baseline was likely over-taking and over-clearing relative to the official tutorial order-book behavior.
- Trigger for the work: Day 0 candidate discovery on the official tutorial replay showed the baseline `TOMATOES` logic was profitable but left obvious room to widen quotes, suppress weak taker fills, and reduce unnecessary inventory clearing.
- Development window: official tutorial `round 0 days -2/-1` from `data/TUTORIAL_ROUND_1/`
- Challenge window: same official two-day tutorial bundle; no broader official Prosperity 4 window exists yet
- Before: tutorial upload baseline used `quote_width 1`, `quote_clip 3`, `min_take_edge 1`, `clear_threshold 10` and finished at `+8,022` total (`EMERALDS +1,464`, `TOMATOES +6,558`).
- After: current upload candidate keeps `EMERALDS` unchanged and sets `TOMATOES` to `quote_width 6`, `quote_clip 5`, `min_take_edge 3`, `clear_threshold 99`, `clear_clip 5`, `skew_per_unit 0.04`, `min_wall_size 6`; replay finished at `+17,408.5` total (`EMERALDS +1,464.0`, `TOMATOES +15,944.5`).
- Trade-level changes: the winning path came from the same dominant-liquidity engine, not a new strategy family; wider `TOMATOES` quotes captured more spread, raising `min_take_edge` removed weak tomato taker trades entirely on the observed bundle, and effectively disabling tomato clearing helped because the replay never pushed inventory anywhere near the `80` limit.
- PnL / trade count deltas: total official tutorial PnL improved by `+9,386.5`; `TOMATOES` PnL improved by `+9,386.5`; final replay used `1,218` submission trades, down from `1,945`; the best no-clearing candidate stayed at a maximum observed absolute tomato position of `43`, well below the `80` limit.
- Parameter sensitivity note: `TOMATOES` showed a broad profitable region around `quote_width 6` with stricter take thresholds and much looser clearing. Widths `7` and `8` degraded, while `quote_clip 5` and `6` tied at the top. `min_take_edge 3` and `4` also tied on the observed bundle, so keep the slightly simpler `3`.
- Rejected alternatives: adding a new tomato-specific predictive model, changing the `EMERALDS` core, or enabling more aggressive tomato clearing just because prior-round research says clearing often matters near position limits.
- Next follow-up: use this file as the tutorial upload candidate and wait for Round 1 materials before adding any new strategy family.

### 2026-03-16 - tutorial teammate algo integration and upload-safe rewrite

- Status: `confirmed`
- Area: `market making`
- Hypothesis: a stronger tutorial candidate might already exist in teammate work, but the winning logic still needs to respect the research constraints and be converted into a true single-file Prosperity upload.
- Trigger for the work: teammate commit `57a3e06` added `algo.py`, and the previous recommended upload file turned out to be invalid for real submission because it imported repo-local modules.
- Development window: official tutorial `round 0 days -2/-1` from `data/TUTORIAL_ROUND_1/`
- Challenge window: same official two-day tutorial bundle; no broader official Prosperity 4 window exists yet
- Before: repo-recommended upload file was not packaging-safe and the best verified valid strategy in repo produced `+17,408.5`.
- After: `rounds/tutorial_round_1/trader.py` is now a true standalone upload file using only `datamodel` plus standard library imports, and it integrates the better teammate logic with `traderData` persistence for tomato EMA state; replay finished at `+31,797.0` total (`EMERALDS +14,945.0`, `TOMATOES +16,852.0`).
- Trade-level changes: `EMERALDS` moved from conservative clipped quoting to a full-capacity fixed-fair take / clear / make loop; `TOMATOES` moved from dominant-liquidity quoting to EMA-plus-mean-reversion market making with adverse-volume filtering and inventory skew. The standalone rewrite preserved the teammate logic’s PnL exactly while removing the upload packaging failure mode.
- PnL / trade count deltas: total official tutorial PnL improved by `+14,388.5` versus the prior repo candidate and by `+23,775.0` versus the first official baseline; final replay used `1,995` submission trades; max observed absolute position stayed at `30` in `EMERALDS` and `26` in `TOMATOES`, both well below the official `80` limit.
- Parameter sensitivity note: the teammate strategy already sat on a strong region without further tuning. The material edge came from the strategy family change on the tutorial products, not from another local threshold sweep.
- Rejected alternatives: keeping the invalid repo-import upload file, uploading the teammate file unchanged with its `prosperity3bt.datamodel` dependency, or rewrapping the teammate logic back into repo-local shared modules for the upload path.
- Next follow-up: upload `rounds/tutorial_round_1/trader.py` only, and treat any future live-round submission as invalid until it passes the standalone single-file check.

### 2026-03-17 - live tutorial review and asymmetric tomato taking

- Status: `confirmed`
- Area: `market making`
- Hypothesis: the hidden tutorial evaluator differs materially from the public sample day, so the safest improvement is a small change supported by the real submission log rather than another broad local overfit.
- Trigger for the work: live submission `576` returned about `+2,434.6`, far below the local two-day tutorial replay expectation, and the downloaded hidden logs showed a different order-book path from the public `day -1` file.
- Development window: hidden live submission `data/576/576.log`
- Challenge window: official public tutorial bundle `data/TUTORIAL_ROUND_1/`
- Before: standalone upload candidate used symmetric tomato taker thresholds with `TOMATOES_BUY_TAKE_WIDTH = 1` and `TOMATOES_SELL_TAKE_WIDTH = 1`.
- After: current upload candidate keeps tomato buy-taking at width `1` but raises tomato sell-taking to width `3`.
- Trade-level changes: hidden-log analysis showed tomato maker fills had positive edge while tomato buy-takes had positive short-horizon follow-through, but tomato sell-takes had negative short-horizon follow-through. Tightening only the tomato sell side preserves the live-supported asymmetry without disturbing the profitable maker engine.
- PnL / trade count deltas: the hidden reconstructed replay improved from `+147` to `+195` on the same extracted hidden day path, while the public tutorial bundle moved from `+31,797` to `+31,558`, a modest giveback that preserves the high-performing public baseline.
- Parameter sensitivity note: raising the tomato sell take width from `1` to `2`, `3`, and `99` all helped on the reconstructed hidden day. Width `3` was chosen because it captured most of the hidden improvement while keeping the public-bundle degradation slightly smaller than fully disabling tomato sell-takes.
- Rejected alternatives: trusting the public tutorial sample as if it matched the live evaluator, disabling all tomato taking, or changing the fixed-fair `EMERALDS` engine despite positive live contribution.
- Next follow-up: use the new standalone trader for the next upload and keep `data/576/576.log` as the reference live-evidence bundle for tutorial-round review.

### 2026-03-17 - repeated live review from submission 1462

- Status: `confirmed`
- Area: `market making`
- Hypothesis: a second downloaded hidden-run bundle on the same evaluator path should tell us whether the previous tomato sell-taker patch was a real gain or just reconstructed-backtest noise.
- Trigger for the work: submission `1462` returned another hidden-run result after the tomato sell-taker patch was uploaded.
- Development window: hidden live submission bundles `data/576/576.log` and `data/1462/1462.log`
- Challenge window: official public tutorial bundle `data/TUTORIAL_ROUND_1/`
- Before: submission `576` finished at `+2,434.578125`.
- After: submission `1462` finished at `+2,436.296875`.
- Trade-level changes: repeated hidden-log analysis confirmed the same hidden order-book path as `576` and the same broad product contribution split (`EMERALDS` about `+1,050`, `TOMATOES` about `+1,385`). Additional candidate changes tested after `1462` included asymmetric tomato reversion and more aggressive tomato buy-taking; neither produced a robust enough improvement to justify shipping.
- PnL / trade count deltas: `1462` improved the reported hidden result by only `+1.71875` versus `576`, which is not enough to credit the live patch with confidence; hidden reconstructed sweeps favored the current buy-take setting and rejected more aggressive tomato buying.
- Parameter sensitivity note: repeated hidden evidence was stable enough to reject several tempting changes, but not strong enough to justify another strategy patch beyond the current file.
- Rejected alternatives: asymmetric tomato reversion betas, wider tomato buy-taking, and looser tomato adverse-volume gating.
- Next follow-up: keep the current standalone trader as the upload candidate until a new real submission bundle produces a materially different hidden signal.

### 2026-03-17 - tutorial tomato feature refactor and gated mode promotion

- Status: `confirmed`
- Area: `market making`
- Hypothesis: the tomato review was directionally right about fair estimation, large-level handling, and passive quote sizing, but only a replay-gated refactor should be allowed to replace the current upload candidate.
- Trigger for the work: an external review argued that `TOMATOES` was anchored to the wrong signal, skipped the wrong large levels, and quoted too much residual capacity; repo review confirmed those as valid hypotheses but not as already-proven fixes on the hidden evaluator.
- Development window: official tutorial `round 0 days -2/-1` from `data/TUTORIAL_ROUND_1/`
- Challenge window: reconstructed hidden days from `data/576/576.log` and `data/1462/1462.log`, plus direct hidden-log analysis of the downloaded submission bundles
- Before: current upload candidate used one tomato path only: EMA-plus-reversion fair, blanket skipping of large taker levels, and full residual-capacity passive quoting; official tutorial replay finished at `+31,558.0`, reconstructed hidden replays finished at `+195` on `576` and `+221` on `1462`.
- After: `rounds/tutorial_round_1/trader.py` now keeps an exact `baseline` mode plus new tomato helpers for book features, fair estimation, large-level classification, and inventory-based quote caps. Validation rejected `hybrid` as the default (`+31,508` public, `+146` reconstructed `576`) and promoted the refactored `ema_reversion` path instead (`+31,559` public, `+195` reconstructed `576`, `+221` reconstructed `1462`).
- Trade-level changes: large tomato levels are no longer blanket-skipped in the experimental path; they now feed a wall-mid candidate and require extra taker edge. Passive tomato quotes now cap only the inventory-increasing side more aggressively as inventory grows. Hidden log analysis on `576` and `1462` also showed zero large-level tomato taker fills on the actual live path, which is why the `hybrid` wall-mid default failed to earn its way in.
- PnL / trade count deltas: promoted candidate improved official tutorial replay by `+1.0` (`+31,559.0` vs `+31,558.0`) while reducing total submission trades from `1,995` to `1,930`; reconstructed hidden replays stayed flat at `+195` on `576` and `+221` on `1462`, meeting the non-regression gate.
- Parameter sensitivity note: the fair-estimator refactor was useful, but the actual winner was not the originally planned `hybrid` default. Current data supports keeping `ema_reversion` as the hardcoded upload path while preserving `baseline`, `dominant_liquidity`, and `hybrid` only as replay concepts outside the submitted file.
- Rejected alternatives: defaulting the upload file to `hybrid`, switching to pure dominant-liquidity fair without a gate, and promoting a candidate that missed the reconstructed-hidden threshold just because it looked more aligned with prior public writeups.
- Next follow-up: keep the refactored `ema_reversion` default as the tutorial upload candidate, avoid adding local-config toggles to the upload file, and revisit `hybrid` only if a future live bundle actually contains large-level tomato taker opportunities.

### 2026-03-17 - final tutorial tomato constant sweep

- Status: `confirmed`
- Area: `market making`
- Hypothesis: after the repeated hidden tutorial bundles, there might still be a better tomato execution variant hiding in a narrow constant change rather than a broader fair-model rewrite.
- Trigger for the work: submission `1989` produced literally the same hidden PnL as `1462`, so the refactor was clearly not an algorithm improvement and the active candidate still needed a last evidence-based search before being treated as final.
- Development window: official tutorial `round 0 days -2/-1` from `data/TUTORIAL_ROUND_1/`
- Challenge window: reconstructed hidden days from `data/576/576.log` and `data/1462/1462.log`
- Before: active upload candidate used `TOMATOES_BUY_TAKE_WIDTH = 1`, `TOMATOES_SELL_TAKE_WIDTH = 3`, `TOMATOES_MIN_EDGE = 2`, `TOMATOES_SKEW_FACTOR = 0.15`, `TOMATOES_EMA_WINDOW = 10`, `TOMATOES_REVERSION_BETA = -0.25`; replay finished at `+31,559.0` on the official tutorial bundle, `+195` on reconstructed `576`, and `+221` on reconstructed `1462`.
- After: no new code was promoted. The same active candidate remains the final tutorial upload recommendation because every nearby tomato variant tested lost on at least one required window.
- Trade-level changes: none promoted. Hidden tomato review still showed the same shape as earlier: positive maker contribution, usable buy-taking, weaker sell-taking than the public sample, and zero large-level tomato taker fills on the actual hidden path.
- PnL / trade count deltas: tested variants included buy-take widths `0/1/2`, sell-take widths `2/3/4`, maker edge `1/2/3`, skew `0.10/0.15/0.20`, EMA windows `6/10/14`, and reversion betas `-0.10/-0.25/-0.40`. The best reconstructed `576` result stayed at `+195` and the best reconstructed `1462` result stayed at `+221`, both with the current settings; public alternatives such as `sell width 4`, `edge 1`, and `buy width 0` all regressed to `+31,477` to `+31,528`.
- Parameter sensitivity note: the active tomato settings sit on a small but stable plateau across the only hidden windows available. The hidden evidence was especially intolerant of lower skew and weaker reversion settings, while public-only improvements remained the same overfit trap as before.
- Rejected alternatives: looser tomato buy-taking, tighter maker edge, sell width `4`, lower skew, shorter EMA windows, and weaker reversion.
- Next follow-up: treat the current `rounds/tutorial_round_1/trader.py` as final for the tutorial phase and stop iterating it unless a new live bundle produces a materially different hidden path.
