#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXTERNAL_DIR="${ROOT_DIR}/external"

mkdir -p "${EXTERNAL_DIR}"

REPOS=(
  "imc-prosperity-3-timo|https://github.com/TimoDiehm/imc-prosperity-3"
  "imc-prosperity-2-linear-utility|https://github.com/ericcccsliu/imc-prosperity-2"
  "imc-prosperity-3-chris|https://github.com/chrispyroberts/imc-prosperity-3"
  "imc-prosperity-3-carter|https://github.com/CarterT27/imc-prosperity-3"
  "imc-prosperity-2023-stanford|https://github.com/ShubhamAnandJain/IMC-Prosperity-2023-Stanford-Cardinal"
  "imc-prosperity-3-backtester|https://github.com/jmerle/imc-prosperity-3-backtester"
  "imc-prosperity-3-visualizer|https://github.com/jmerle/imc-prosperity-3-visualizer"
  "imc-prosperity-3-submitter|https://github.com/jmerle/imc-prosperity-3-submitter"
  "imc-prosperity-2-submitter|https://github.com/jmerle/imc-prosperity-2-submitter"
  "imc-prosperity-2-jmerle|https://github.com/jmerle/imc-prosperity-2"
  "imc-prosperity-2-backtester|https://github.com/jmerle/imc-prosperity-2-backtester"
  "imc-prosperity-2-manual|https://github.com/gabsens/IMC-Prosperity-2-Manual"
)

for entry in "${REPOS[@]}"; do
  name="${entry%%|*}"
  url="${entry##*|}"
  target="${EXTERNAL_DIR}/${name}"

  if [[ -d "${target}/.git" ]]; then
    echo "Updating ${name}"
    git -C "${target}" fetch --all --tags --prune
    continue
  fi

  echo "Cloning ${name}"
  git clone "${url}" "${target}"
done

echo "Research repos available in ${EXTERNAL_DIR}"
