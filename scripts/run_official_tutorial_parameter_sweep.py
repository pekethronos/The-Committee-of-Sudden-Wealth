#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the official tutorial bundle repeatedly with config overrides."
    )
    parser.add_argument(
        "algorithm",
        type=Path,
        help="Path to the trader file to replay against the official tutorial data.",
    )
    parser.add_argument(
        "--config-json",
        action="append",
        required=True,
        help="Inline JSON override for TCOSW_TRADER_CONFIG.",
    )
    parser.add_argument("--label", action="append", help="Optional label matching each --config-json.")
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/official_tutorial/sweeps"))
    args = parser.parse_args()

    labels = args.label or []
    if labels and len(labels) != len(args.config_json):
        raise SystemExit("--label count must match --config-json count")

    root_dir = Path(__file__).resolve().parents[1]
    data_src = root_dir / "data" / "TUTORIAL_ROUND_1"
    if not data_src.exists():
        raise SystemExit(f"Official tutorial data not found at {data_src}")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_round_dir = Path(tmp_dir) / "round0"
        os.symlink(data_src, tmp_round_dir)

        for idx, override in enumerate(args.config_json):
            label = labels[idx] if idx < len(labels) else f"run_{idx:02d}"
            env = os.environ.copy()
            env["TCOSW_TRADER_CONFIG"] = json.dumps(json.loads(override), separators=(",", ":"))
            out_file = args.out_dir / f"{label}.log"
            cmd = [
                str(root_dir / ".venv" / "bin" / "python"),
                str(root_dir / "scripts" / "run_backtest_with_limit_overrides.py"),
                "--limit",
                "EMERALDS=80",
                "--limit",
                "TOMATOES=80",
                "--",
                str(args.algorithm.resolve()),
                "0",
                "--data",
                tmp_dir,
                "--merge-pnl",
                "--out",
                str(out_file),
                "--no-progress",
            ]
            print(f"Running {label}: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, env=env)


if __name__ == "__main__":
    main()
