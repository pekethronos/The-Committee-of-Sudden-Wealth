#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from tcosw.analysis.backtest_logs import classify_submission_trades, parse_backtest_log


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize submission-side backtest trades by product and take/make mode."
    )
    parser.add_argument("logfile", type=Path)
    args = parser.parse_args()

    summary = parse_backtest_log(args.logfile)
    classified = classify_submission_trades(summary)

    by_product: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "trade_count": 0,
            "buy_qty": 0,
            "sell_qty": 0,
            "make_qty": 0,
            "take_qty": 0,
            "unknown_qty": 0,
            "signed_cashflow": 0.0,
        }
    )
    by_mode: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"trade_count": 0, "quantity": 0, "signed_cashflow": 0.0}
    )

    for trade in classified:
        product_row = by_product[trade.product]
        product_row["trade_count"] += 1
        if trade.side == "BUY":
            product_row["buy_qty"] += trade.quantity
        else:
            product_row["sell_qty"] += trade.quantity
        product_row[f"{trade.mode}_qty"] += trade.quantity
        product_row["signed_cashflow"] += trade.cashflow

        mode_row = by_mode[trade.mode]
        mode_row["trade_count"] += 1
        mode_row["quantity"] += trade.quantity
        mode_row["signed_cashflow"] += trade.cashflow

    payload = {
        "total_pnl": summary.total_pnl,
        "product_pnl": summary.product_pnl,
        "submission_trade_count": len(classified),
        "by_product": dict(sorted(by_product.items())),
        "by_mode": dict(sorted(by_mode.items())),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
