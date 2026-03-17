---
name: prosperity-live-submission-review
description: Review downloaded Prosperity submission logs, reconstruct the hidden evaluation path where possible, and turn the result into concrete strategy evidence. Use when a Prosperity upload has finished and the user has downloaded the resulting log/json/python bundle.
---

# Prosperity Live Submission Review

Use this skill after a real Prosperity upload returns logs.

## Core Workflow

1. Capture the bundle.
- Identify the downloaded folder and the submission id or numeric label.
- Read:
  - `/Users/sb/tcosw/README.md`
  - `/Users/sb/tcosw/CODEX.md`
  - `/Users/sb/tcosw/docs/day0-intake.md` when working in the tutorial phase
  - `/Users/sb/tcosw/docs/strategy-iteration-log.md`
  - `/Users/sb/tcosw/docs/baseline-snapshots.md`

2. Normalize the evidence.
- Treat the downloaded `.log` file as the primary source of truth.
- Use:
  - `/Users/sb/tcosw/scripts/analyze_submission_log.py`
  - `/Users/sb/tcosw/scripts/extract_submission_round_data.py`
- Save normalized artifacts under `/Users/sb/tcosw/artifacts/submissions/<id>/`.

3. Compare against local assumptions.
- Check whether the hidden evaluation path differs from the public sample data or replay bundle.
- Quantify:
  - product-level estimated contribution
  - make versus take behavior
  - maximum inventory used
  - repeated good and bad live-side trade patterns

4. Decide whether a patch is justified.
- Prefer the smallest change supported by repeated live evidence.
- Do not overreact to one hidden run if the patch obviously damages the public challenge window.
- If the hidden logs expose a simulator mismatch, say so explicitly.

5. Hand off correctly.
- If the result is only diagnostic, stop with the review.
- If a strategy patch is justified, switch to `$prosperity-strategy-iteration`.
- If the result should change how future live runs are reviewed, update the relevant repo-local skill.

## Output Standard

Return:

- the reported submission result
- the hidden-versus-public mismatch summary
- product-level contribution estimate
- make versus take summary
- the exact upload recommendation
- whether the result justifies another code change now

## References

- For the live-review checklist, read:
  - `/Users/sb/tcosw/.agents/skills/prosperity-live-submission-review/references/workflow.md`
