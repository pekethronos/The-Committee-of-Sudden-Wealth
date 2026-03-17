#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path


def apply_overrides(source: str, overrides: dict[str, str]) -> str:
    updated = source
    for key, value in overrides.items():
        pattern = rf"^{re.escape(key)}\s*=.*$"
        replacement = f"{key} = {value}"
        updated, count = re.subn(pattern, replacement, updated, flags=re.MULTILINE)
        if count != 1:
            raise SystemExit(f"did not find exactly one assignment for {key}")
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest standalone tutorial trader variants by overriding constants.")
    parser.add_argument("algorithm", type=Path)
    parser.add_argument("dataset", type=Path, help="Directory containing round0/*.csv")
    parser.add_argument("--label", action="append", required=True)
    parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        required=True,
        help="Override group in NAME=VALUE,NAME=VALUE format. One per --label.",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    if len(args.label) != len(args.overrides):
        raise SystemExit("--label count must match --set count")

    root_dir = Path(__file__).resolve().parents[1]
    source = args.algorithm.read_text()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for label, raw_override in zip(args.label, args.overrides):
        overrides: dict[str, str] = {}
        for item in raw_override.split(","):
            key, value = item.split("=", 1)
            overrides[key.strip()] = value.strip()

        updated = apply_overrides(source, overrides)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_algorithm = Path(tmp_dir) / "trader.py"
            datamodel_src = args.algorithm.parent / "datamodel.py"
            if datamodel_src.exists():
                (Path(tmp_dir) / "datamodel.py").write_text(datamodel_src.read_text())
            tmp_algorithm.write_text(updated)
            out_file = args.out_dir / f"{label}.log"
            cmd = [
                str(root_dir / ".venv" / "bin" / "python"),
                str(root_dir / "scripts" / "run_backtest_with_limit_overrides.py"),
                "--limit",
                "EMERALDS=80",
                "--limit",
                "TOMATOES=80",
                "--",
                str(tmp_algorithm),
                "0",
                "--data",
                str(args.dataset),
                "--merge-pnl",
                "--out",
                str(out_file),
                "--no-progress",
            ]
            print(f"Running {label}: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
