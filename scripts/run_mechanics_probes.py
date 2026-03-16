#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from tcosw.analysis.backtest_logs import classify_submission_trades, parse_backtest_log


def run_backtest(name: str, trader: Path, day: str, extra_args: list[str] | None = None) -> Path:
    output = ROOT_DIR / "artifacts" / "probes" / f"{name}.log"
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(ROOT_DIR / ".venv" / "bin" / "prosperity3bt"),
        str(trader),
        day,
        "--data",
        str(ROOT_DIR / "data" / "probes"),
        "--out",
        str(output),
        "--no-progress",
    ]
    if extra_args:
        cmd.extend(extra_args)
    subprocess.run(cmd, check=True)
    return output


def main() -> None:
    probe_results: dict[str, object] = {}

    lifetime_log = run_backtest("order_lifetime", ROOT_DIR / "rounds" / "probes" / "order_lifetime_probe.py", "0-0")
    lifetime_summary = parse_backtest_log(lifetime_log)
    lifetime_trades = classify_submission_trades(lifetime_summary)
    probe_results["order_lifetime"] = {
        "submission_trade_count": len(lifetime_trades),
        "expected": "0 trades if unfilled orders cancel at end-of-iteration",
        "pass": len(lifetime_trades) == 0,
    }

    limit_log = run_backtest("limit", ROOT_DIR / "rounds" / "probes" / "limit_probe.py", "0-2")
    limit_raw = limit_log.read_text(encoding="utf-8")
    limit_summary = parse_backtest_log(limit_log)
    limit_trades = classify_submission_trades(limit_summary)
    probe_results["position_limit"] = {
        "submission_trade_count": len(limit_trades),
        "sandbox_flagged": "exceeded limit" in limit_raw,
        "expected": "0 trades and sandbox warning when total long quantity breaches the product limit",
        "pass": len(limit_trades) == 0 and "exceeded limit" in limit_raw,
    }

    match_all_log = run_backtest(
        "match_trades_all",
        ROOT_DIR / "rounds" / "probes" / "match_trade_probe.py",
        "0-1",
        extra_args=["--match-trades", "all"],
    )
    match_worse_log = run_backtest(
        "match_trades_worse",
        ROOT_DIR / "rounds" / "probes" / "match_trade_probe.py",
        "0-1",
        extra_args=["--match-trades", "worse"],
    )
    match_none_log = run_backtest(
        "match_trades_none",
        ROOT_DIR / "rounds" / "probes" / "match_trade_probe.py",
        "0-1",
        extra_args=["--match-trades", "none"],
    )

    all_trades = classify_submission_trades(parse_backtest_log(match_all_log))
    worse_trades = classify_submission_trades(parse_backtest_log(match_worse_log))
    none_trades = classify_submission_trades(parse_backtest_log(match_none_log))
    probe_results["match_trades"] = {
        "all_count": len(all_trades),
        "worse_count": len(worse_trades),
        "none_count": len(none_trades),
        "expected": "`all` fills on equal-price market trades, `worse` and `none` do not",
        "pass": len(all_trades) == 1 and len(worse_trades) == 0 and len(none_trades) == 0,
    }

    print(json.dumps(probe_results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
