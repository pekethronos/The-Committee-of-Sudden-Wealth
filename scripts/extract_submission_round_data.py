#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PRICE_HEADER = [
    "day",
    "timestamp",
    "product",
    "bid_price_1",
    "bid_volume_1",
    "bid_price_2",
    "bid_volume_2",
    "bid_price_3",
    "bid_volume_3",
    "ask_price_1",
    "ask_volume_1",
    "ask_price_2",
    "ask_volume_2",
    "ask_price_3",
    "ask_volume_3",
    "mid_price",
    "profit_and_loss",
]

TRADE_HEADER = ["timestamp", "buyer", "seller", "symbol", "currency", "price", "quantity"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconstruct price/trade CSVs from a downloaded submission log.")
    parser.add_argument("submission_log", type=Path, help="Path to the downloaded .log JSON file.")
    parser.add_argument("out_dir", type=Path, help="Output directory that will receive round0/*.csv files.")
    parser.add_argument("--round", type=int, default=0)
    parser.add_argument("--day", type=int, default=-1)
    args = parser.parse_args()

    payload = json.loads(args.submission_log.read_text())
    round_dir = args.out_dir / f"round{args.round}"
    round_dir.mkdir(parents=True, exist_ok=True)

    price_path = round_dir / f"prices_round_{args.round}_day_{args.day}.csv"
    trade_path = round_dir / f"trades_round_{args.round}_day_{args.day}.csv"

    activities_reader = csv.DictReader(payload["activitiesLog"].splitlines(), delimiter=";")
    with price_path.open("w", newline="") as price_file:
        writer = csv.DictWriter(price_file, delimiter=";", fieldnames=PRICE_HEADER)
        writer.writeheader()
        for row in activities_reader:
            writer.writerow({key: row.get(key, "") for key in PRICE_HEADER})

    seen_market_trades: set[tuple[int, str, str, str, str, float, int]] = set()
    with trade_path.open("w", newline="") as trade_file:
        writer = csv.DictWriter(trade_file, delimiter=";", fieldnames=TRADE_HEADER)
        writer.writeheader()
        for entry in payload.get("logs", []):
            state = json.loads(entry["lambdaLog"])[0]
            market_trades = state[5]
            for trade in market_trades:
                row = {
                    "timestamp": int(trade[5]),
                    "buyer": trade[3],
                    "seller": trade[4],
                    "symbol": trade[0],
                    "currency": "XIRECS",
                    "price": float(trade[1]),
                    "quantity": int(trade[2]),
                }
                key = (
                    row["timestamp"],
                    row["buyer"],
                    row["seller"],
                    row["symbol"],
                    row["currency"],
                    row["price"],
                    row["quantity"],
                )
                if key in seen_market_trades:
                    continue
                seen_market_trades.add(key)
                writer.writerow(row)

    print(json.dumps({"prices": str(price_path), "trades": str(trade_path)}, indent=2))


if __name__ == "__main__":
    main()
