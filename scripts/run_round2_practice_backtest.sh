#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${ROOT_DIR}/artifacts/round2/replays"
OUTPUT_FILE="${OUTPUT_DIR}/round2.log"

mkdir -p "${OUTPUT_DIR}"

"${ROOT_DIR}/scripts/run_public_replay.sh" "${ROOT_DIR}/rounds/round2/trader.py" 2 --merge-pnl --out "${OUTPUT_FILE}"

echo "Round 2 replay written to ${OUTPUT_FILE}"
