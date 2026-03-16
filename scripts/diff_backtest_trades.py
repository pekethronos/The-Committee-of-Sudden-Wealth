#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from tcosw.analysis.backtest_logs import diff_trades, parse_backtest_log


def main() -> None:
    parser = argparse.ArgumentParser(description="Diff two prosperity3bt output logs.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("--timestamp-tolerance", type=int, default=0)
    parser.add_argument("--show-details", action="store_true")
    parser.add_argument("--show-unchanged", action="store_true")
    args = parser.parse_args()

    baseline = parse_backtest_log(args.baseline)
    current = parse_backtest_log(args.current)
    diff = diff_trades(
        baseline.trades,
        current.trades,
        timestamp_tolerance=args.timestamp_tolerance,
    )
    payload = {
        "baseline_total_pnl": baseline.total_pnl,
        "current_total_pnl": current.total_pnl,
        "delta_total_pnl": current.total_pnl - baseline.total_pnl,
        "added_count": len(diff["added"]),
        "removed_count": len(diff["removed"]),
        "unchanged_count": len(diff["unchanged"]),
    }
    if args.show_details:
        payload["added"] = diff["added"]
        payload["removed"] = diff["removed"]
    if args.show_unchanged:
        payload["unchanged"] = diff["unchanged"]
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
