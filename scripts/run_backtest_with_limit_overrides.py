#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from prosperity3bt.__main__ import main
from prosperity3bt.data import LIMITS


def main_wrapper() -> None:
    parser = argparse.ArgumentParser(
        description="Run prosperity3bt after patching product limit overrides."
    )
    parser.add_argument(
        "--limit",
        action="append",
        default=[],
        help="Override of the form PRODUCT=LIMIT. May be repeated.",
    )
    parser.add_argument("prosperity_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    prosperity_args = args.prosperity_args
    if prosperity_args and prosperity_args[0] == "--":
        prosperity_args = prosperity_args[1:]
    if not prosperity_args:
        raise SystemExit("No prosperity3bt arguments provided")

    for override in args.limit:
        product, raw_limit = override.split("=", 1)
        LIMITS[product] = int(raw_limit)

    sys.argv = ["prosperity3bt", *prosperity_args]
    main()


if __name__ == "__main__":
    main_wrapper()
