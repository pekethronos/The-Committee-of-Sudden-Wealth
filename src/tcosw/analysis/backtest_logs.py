from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ParsedTrade:
    timestamp: int
    buyer: str
    seller: str
    symbol: str
    price: int
    quantity: int

    @property
    def side(self) -> str:
        return "BUY" if self.quantity > 0 else "SELL"


@dataclass(frozen=True, slots=True)
class BacktestSummary:
    product_pnl: dict[str, float]
    total_pnl: float
    trades: list[ParsedTrade]


def parse_backtest_log(path: str | Path) -> BacktestSummary:
    raw = Path(path).read_text(encoding="utf-8")
    activities_marker = "\n\n\nActivities log:\n"
    trades_marker = "\n\n\n\n\nTrade History:\n"
    activities_start = raw.index(activities_marker) + len(activities_marker)
    trades_start = raw.index(trades_marker)
    activities_blob = raw[activities_start:trades_start].strip()
    trades_blob = raw[trades_start + len(trades_marker) :].strip()

    lines = [line for line in activities_blob.splitlines() if line.strip()]
    rows = [line.split(";") for line in lines[1:]]
    last_timestamp = int(rows[-1][1])
    product_pnl = {
        row[2]: float(row[-1])
        for row in rows
        if int(row[1]) == last_timestamp
    }

    cleaned_trades = re.sub(r",(\s*[}\]])", r"\1", trades_blob)
    trade_rows = json.loads(cleaned_trades)
    trades = [
        ParsedTrade(
            timestamp=int(row["timestamp"]),
            buyer=row["buyer"],
            seller=row["seller"],
            symbol=row["symbol"],
            price=int(row["price"]),
            quantity=int(row["quantity"]),
        )
        for row in trade_rows
    ]
    return BacktestSummary(
        product_pnl=product_pnl,
        total_pnl=sum(product_pnl.values()),
        trades=trades,
    )


def diff_trades(
    baseline: list[ParsedTrade],
    current: list[ParsedTrade],
    timestamp_tolerance: int = 0,
) -> dict[str, list[dict[str, int | str]]]:
    remaining = current[:]
    added: list[dict[str, int | str]] = []
    removed: list[dict[str, int | str]] = []
    unchanged: list[dict[str, int | str]] = []

    for base in baseline:
        match_idx = _find_trade_match(base, remaining, timestamp_tolerance)
        if match_idx is None:
            removed.append(_trade_key(base))
            continue
        current_trade = remaining.pop(match_idx)
        unchanged.append(_trade_key(current_trade))

    added.extend(_trade_key(trade) for trade in remaining)
    return {
        "added": added,
        "removed": removed,
        "unchanged": unchanged,
    }


def _find_trade_match(
    target: ParsedTrade,
    candidates: list[ParsedTrade],
    timestamp_tolerance: int,
) -> int | None:
    for idx, candidate in enumerate(candidates):
        if (
            candidate.symbol == target.symbol
            and candidate.price == target.price
            and candidate.quantity == target.quantity
            and abs(candidate.timestamp - target.timestamp) <= timestamp_tolerance
        ):
            return idx
    return None


def _trade_key(trade: ParsedTrade) -> dict[str, int | str]:
    return {
        "timestamp": trade.timestamp,
        "symbol": trade.symbol,
        "price": trade.price,
        "quantity": trade.quantity,
        "side": trade.side,
    }
