#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class BookRow:
    day: int
    timestamp: int
    product: str
    best_bid: int | None
    best_ask: int | None
    bid_levels: tuple[tuple[int, int], ...]
    ask_levels: tuple[tuple[int, int], ...]
    largest_bid_price: int | None
    largest_bid_size: int
    largest_ask_price: int | None
    largest_ask_size: int
    wall_mid: float | None
    mid_price: float
    pnl: float


def parse_levels(row: dict[str, str], side: str) -> tuple[tuple[int, int], ...]:
    levels: list[tuple[int, int]] = []
    for idx in range(1, 4):
        price_key = f"{side}_price_{idx}"
        volume_key = f"{side}_volume_{idx}"
        if not row.get(price_key) or not row.get(volume_key):
            continue
        levels.append((int(row[price_key]), abs(int(row[volume_key]))))
    return tuple(levels)


def pick_largest_level(levels: tuple[tuple[int, int], ...], is_bid: bool) -> tuple[int | None, int]:
    if not levels:
        return None, 0
    return max(levels, key=lambda item: (item[1], item[0] if is_bid else -item[0]))


def parse_activities_log(payload: str) -> dict[tuple[str, int], BookRow]:
    rows: dict[tuple[str, int], BookRow] = {}
    reader = csv.DictReader(payload.splitlines(), delimiter=";")
    for row in reader:
        bid = int(row["bid_price_1"]) if row["bid_price_1"] else None
        ask = int(row["ask_price_1"]) if row["ask_price_1"] else None
        bid_levels = parse_levels(row, "bid")
        ask_levels = parse_levels(row, "ask")
        largest_bid_price, largest_bid_size = pick_largest_level(bid_levels, is_bid=True)
        largest_ask_price, largest_ask_size = pick_largest_level(ask_levels, is_bid=False)
        wall_mid = None
        if (
            largest_bid_price is not None
            and largest_ask_price is not None
            and largest_bid_size >= 15
            and largest_ask_size >= 15
        ):
            wall_mid = (largest_bid_price + largest_ask_price) / 2.0
        rows[(row["product"], int(row["timestamp"]))] = BookRow(
            day=int(row["day"]),
            timestamp=int(row["timestamp"]),
            product=row["product"],
            best_bid=bid,
            best_ask=ask,
            bid_levels=bid_levels,
            ask_levels=ask_levels,
            largest_bid_price=largest_bid_price,
            largest_bid_size=largest_bid_size,
            largest_ask_price=largest_ask_price,
            largest_ask_size=largest_ask_size,
            wall_mid=wall_mid,
            mid_price=float(row["mid_price"]),
            pnl=float(row["profit_and_loss"]),
        )
    return rows


def classify_trade(
    trade: dict[str, Any],
    book_rows: dict[tuple[str, int], BookRow],
) -> str:
    key = (trade["symbol"], int(trade["timestamp"]))
    book = book_rows.get(key)
    if book is None:
        return "unknown"

    price = float(trade["price"])
    if trade["buyer"] == "SUBMISSION":
        if book.best_ask is not None and price >= book.best_ask:
            return "take"
        if book.best_ask is not None and price < book.best_ask:
            return "make"
        return "unknown"

    if trade["seller"] == "SUBMISSION":
        if book.best_bid is not None and price <= book.best_bid:
            return "take"
        if book.best_bid is not None and price > book.best_bid:
            return "make"
        return "unknown"

    return "market"


def summarize_positions(log_entries: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    max_abs: dict[str, int] = defaultdict(int)
    final_pos: dict[str, int] = {}
    for entry in log_entries:
        state = json.loads(entry["lambdaLog"])[0]
        positions = state[6]
        for product, quantity in positions.items():
            qty = int(quantity)
            max_abs[product] = max(max_abs[product], abs(qty))
            final_pos[product] = qty
    return {
        product: {"max_abs_position": max_abs[product], "final_position": final_pos.get(product, 0)}
        for product in sorted(set(max_abs) | set(final_pos))
    }


def classify_tomato_trade_bucket(trade: dict[str, Any], mode: str, book: BookRow) -> str:
    if mode == "make":
        return "maker"

    levels = book.ask_levels if trade["buyer"] == "SUBMISSION" else book.bid_levels
    level_bucket = "small"
    price = int(trade["price"])
    for level_price, level_size in levels:
        if level_price != price:
            continue
        if level_size >= 15:
            level_bucket = "large"
        break

    side_prefix = "buy" if trade["buyer"] == "SUBMISSION" else "sell"
    return f"{side_prefix}_take_{level_bucket}"


def summarize_tomato_trade_buckets(
    trade_history: list[dict[str, Any]],
    book_rows: dict[tuple[str, int], BookRow],
) -> dict[str, dict[str, float | int | None]]:
    buckets: dict[str, dict[str, float | int | None]] = defaultdict(
        lambda: {
            "trade_count": 0,
            "quantity": 0,
            "signed_cashflow": 0.0,
            "raw_mid_distance_sum": 0.0,
            "wall_mid_distance_sum": 0.0,
            "wall_mid_samples": 0,
        }
    )

    for trade in trade_history:
        if trade["symbol"] != "TOMATOES":
            continue
        if trade["buyer"] != "SUBMISSION" and trade["seller"] != "SUBMISSION":
            continue

        key = (trade["symbol"], int(trade["timestamp"]))
        book = book_rows.get(key)
        if book is None:
            continue

        mode = classify_trade(trade, book_rows)
        bucket_name = classify_tomato_trade_bucket(trade, mode, book)
        quantity = int(trade["quantity"])
        price = float(trade["price"])
        side = "BUY" if trade["buyer"] == "SUBMISSION" else "SELL"
        cashflow = -price * quantity if side == "BUY" else price * quantity

        bucket = buckets[bucket_name]
        bucket["trade_count"] += 1
        bucket["quantity"] += quantity
        bucket["signed_cashflow"] += cashflow
        bucket["raw_mid_distance_sum"] += abs(price - book.mid_price)
        if book.wall_mid is not None:
            bucket["wall_mid_distance_sum"] += abs(price - book.wall_mid)
            bucket["wall_mid_samples"] += 1

    ordered_names = (
        "buy_take_small",
        "buy_take_large",
        "sell_take_small",
        "sell_take_large",
        "maker",
    )
    summary: dict[str, dict[str, float | int | None]] = {}
    for name in ordered_names:
        bucket = buckets[name]
        trade_count = int(bucket["trade_count"])
        wall_mid_samples = int(bucket["wall_mid_samples"])
        summary[name] = {
            "trade_count": trade_count,
            "quantity": int(bucket["quantity"]),
            "signed_cashflow": float(bucket["signed_cashflow"]),
            "avg_abs_raw_mid_distance": (
                float(bucket["raw_mid_distance_sum"]) / trade_count if trade_count else None
            ),
            "avg_abs_wall_mid_distance": (
                float(bucket["wall_mid_distance_sum"]) / wall_mid_samples if wall_mid_samples else None
            ),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a Prosperity submission log JSON file.")
    parser.add_argument("submission_log", type=Path, help="Path to the downloaded .log JSON file.")
    parser.add_argument(
        "--compare-prices",
        type=Path,
        help="Optional public prices CSV to compare against the activities log.",
    )
    args = parser.parse_args()

    payload = json.loads(args.submission_log.read_text())
    activities = parse_activities_log(payload["activitiesLog"])
    log_entries = payload.get("logs", [])
    trade_history = payload.get("tradeHistory", [])

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

    for trade in trade_history:
        if trade["buyer"] != "SUBMISSION" and trade["seller"] != "SUBMISSION":
            continue

        product = trade["symbol"]
        quantity = int(trade["quantity"])
        price = float(trade["price"])
        mode = classify_trade(trade, activities)
        side = "BUY" if trade["buyer"] == "SUBMISSION" else "SELL"
        cashflow = -price * quantity if side == "BUY" else price * quantity

        row = by_product[product]
        row["trade_count"] += 1
        row[f"{side.lower()}_qty"] += quantity
        row[f"{mode}_qty"] += quantity
        row["signed_cashflow"] += cashflow

        mode_row = by_mode[mode]
        mode_row["trade_count"] += 1
        mode_row["quantity"] += quantity
        mode_row["signed_cashflow"] += cashflow

    position_summary = summarize_positions(log_entries)
    final_marks: dict[str, float] = {}
    final_row_pnl: dict[str, float] = {}
    latest_timestamp: dict[str, int] = {}
    for (product, timestamp), row in activities.items():
        if timestamp >= latest_timestamp.get(product, -1):
            latest_timestamp[product] = timestamp
            final_marks[product] = row.mid_price
            final_row_pnl[product] = row.pnl

    product_estimated_pnl: dict[str, float] = {}
    for product, row in by_product.items():
        position = position_summary.get(product, {}).get("final_position", 0)
        final_mid = final_marks.get(product, 0.0)
        product_estimated_pnl[product] = float(row["signed_cashflow"]) + position * final_mid

    comparison: dict[str, Any] | None = None
    if args.compare_prices is not None:
        reference_rows = parse_activities_log(args.compare_prices.read_text())
        mismatch_count = 0
        checked_count = 0
        examples: list[dict[str, Any]] = []
        for key, live_row in activities.items():
            ref_row = reference_rows.get(key)
            if ref_row is None:
                continue
            checked_count += 1
            if (
                live_row.best_bid != ref_row.best_bid
                or live_row.best_ask != ref_row.best_ask
                or abs(live_row.mid_price - ref_row.mid_price) > 1e-9
            ):
                mismatch_count += 1
                if len(examples) < 5:
                    examples.append(
                        {
                            "product": live_row.product,
                            "timestamp": live_row.timestamp,
                            "live_best_bid": live_row.best_bid,
                            "ref_best_bid": ref_row.best_bid,
                            "live_best_ask": live_row.best_ask,
                            "ref_best_ask": ref_row.best_ask,
                            "live_mid": live_row.mid_price,
                            "ref_mid": ref_row.mid_price,
                        }
                    )
        comparison = {
            "reference_prices": str(args.compare_prices),
            "checked_rows": checked_count,
            "mismatch_rows": mismatch_count,
            "examples": examples,
        }

    final_profit = sum(final_row_pnl.values())
    summary = {
        "submission_log": str(args.submission_log),
        "reported_final_profit": final_profit,
        "submission_trade_count": sum(int(row["trade_count"]) for row in by_product.values()),
        "by_product": dict(sorted(by_product.items())),
        "by_mode": dict(sorted(by_mode.items())),
        "estimated_product_pnl": dict(sorted(product_estimated_pnl.items())),
        "position_summary": position_summary,
        "tomatoes_trade_buckets": summarize_tomato_trade_buckets(trade_history, activities),
        "reference_comparison": comparison,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
