#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRADER_PATH="${ROOT_DIR}/rounds/tutorial/trader.py"
OUT_DIR="${ROOT_DIR}/artifacts/tutorial/replays"
OUT_FILE="${OUT_DIR}/round0.log"

mkdir -p "${OUT_DIR}"

if [[ ! -f "${TRADER_PATH}" ]]; then
  "${ROOT_DIR}/scripts/init_trader_from_template.sh" "${TRADER_PATH}"
fi

"${ROOT_DIR}/scripts/run_public_replay.sh" "${TRADER_PATH}" 0 --out "${OUT_FILE}"
echo "Wrote ${OUT_FILE}"
