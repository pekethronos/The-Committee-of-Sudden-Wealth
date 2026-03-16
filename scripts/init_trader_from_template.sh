#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: ./scripts/init_trader_from_template.sh <target-path>" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_PATH="$1"
TARGET_DIR="$(cd "$(dirname "${TARGET_PATH}")" && pwd)"

if [[ -e "${TARGET_PATH}" ]]; then
  echo "Refusing to overwrite existing file: ${TARGET_PATH}" >&2
  exit 1
fi

cp "${ROOT_DIR}/templates/trader.py" "${TARGET_PATH}"
if [[ ! -e "${TARGET_DIR}/datamodel.py" ]]; then
  cp "${ROOT_DIR}/templates/datamodel.py" "${TARGET_DIR}/datamodel.py"
fi
echo "Created ${TARGET_PATH} from templates/trader.py"
