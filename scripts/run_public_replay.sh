#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -d "${ROOT_DIR}/.venv" ]]; then
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.venv/bin/activate"
fi

if ! command -v prosperity3bt >/dev/null 2>&1; then
  echo "prosperity3bt is not installed. Run ./scripts/setup_public_tooling.sh first." >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "Usage: ./scripts/run_public_replay.sh <prosperity3bt args...>" >&2
  echo "Example: ./scripts/run_public_replay.sh rounds/tutorial/trader.py 0" >&2
  exit 1
fi

exec prosperity3bt "$@"
