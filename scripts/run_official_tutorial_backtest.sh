#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_SRC="${ROOT_DIR}/data/TUTORIAL_ROUND_1"
OUTPUT_DIR="${ROOT_DIR}/artifacts/official_tutorial/replays"
OUTPUT_FILE="${OUTPUT_DIR}/round0.log"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

if [[ ! -d "${DATA_SRC}" ]]; then
  echo "Official tutorial data not found at ${DATA_SRC}" >&2
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"
ln -s "${DATA_SRC}" "${TMP_DIR}/round0"

"${ROOT_DIR}/.venv/bin/python" "${ROOT_DIR}/scripts/run_backtest_with_limit_overrides.py" \
  --limit EMERALDS=80 \
  --limit TOMATOES=80 \
  -- \
  "${ROOT_DIR}/rounds/tutorial_round_1/trader.py" \
  0 \
  --data "${TMP_DIR}" \
  --merge-pnl \
  --out "${OUTPUT_FILE}"

echo "Official tutorial replay written to ${OUTPUT_FILE}"
