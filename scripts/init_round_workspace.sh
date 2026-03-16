#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: ./scripts/init_round_workspace.sh <round-name>" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROUND_NAME="$1"
ROUND_DIR="${ROOT_DIR}/artifacts/${ROUND_NAME}"

mkdir -p "${ROUND_DIR}/replays" "${ROUND_DIR}/diffs" "${ROUND_DIR}/notes"

echo "Created:"
echo "  ${ROUND_DIR}/replays"
echo "  ${ROUND_DIR}/diffs"
echo "  ${ROUND_DIR}/notes"
