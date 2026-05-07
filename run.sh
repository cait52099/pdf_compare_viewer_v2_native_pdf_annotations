#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Missing virtual environment: $ROOT_DIR/.venv"
  echo "This copy is expected to run from the bundled Python 3.12 virtual environment."
  echo "If .venv is missing, recreate it with a Python 3.12 interpreter before installing dependencies."
  exit 1
fi

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

exec "$VENV_PYTHON" "$ROOT_DIR/starter/main.py"
