#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
python -m pip install prosperity3bt

echo "Installed prosperity3bt into ${VENV_DIR}"
echo "Next:"
echo "  source ${VENV_DIR}/bin/activate"
echo "  ${ROOT_DIR}/scripts/run_public_replay.sh --help"
