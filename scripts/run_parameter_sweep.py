#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run prosperity3bt repeatedly with config overrides.")
    parser.add_argument("algorithm", type=Path)
    parser.add_argument("days", nargs="+")
    parser.add_argument("--config-json", action="append", required=True, help="Inline JSON override for TCOSW_TRADER_CONFIG.")
    parser.add_argument("--label", action="append", help="Optional label matching each --config-json.")
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/sweeps"))
    args = parser.parse_args()

    labels = args.label or []
    if labels and len(labels) != len(args.config_json):
        raise SystemExit("--label count must match --config-json count")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    for idx, override in enumerate(args.config_json):
        label = labels[idx] if idx < len(labels) else f"run_{idx:02d}"
        env = os.environ.copy()
        env["TCOSW_TRADER_CONFIG"] = json.dumps(json.loads(override), separators=(",", ":"))
        out_file = args.out_dir / f"{label}.log"
        cmd = [
            str(Path("scripts/run_public_replay.sh")),
            str(args.algorithm),
            *args.days,
            "--out",
            str(out_file),
            "--no-progress",
        ]
        print(f"Running {label}: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, env=env)


if __name__ == "__main__":
    main()
