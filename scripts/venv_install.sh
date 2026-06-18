#!/usr/bin/env bash
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

choose_python() {
  for cmd in python python3 python3.14 python3.13 python3.12 python3.11 python3.10; do
    if command -v "$cmd" >/dev/null 2>&1; then
      printf '%s\n' "$cmd"
      return 0
    fi
  done
  return 1
}

PYTHON_BIN=$(choose_python) || {
  printf 'ERROR: Could not find a Python interpreter.\n' >&2
  exit 1
}

printf 'Using Python: %s\n' "$PYTHON_BIN"
"$PYTHON_BIN" -m venv "$VENV_DIR"

if [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
elif [ -x "$VENV_DIR/bin/python" ]; then
  VENV_PYTHON="$VENV_DIR/bin/python"
else
  printf 'ERROR: Could not locate the virtual environment python executable.\n' >&2
  exit 1
fi

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r "$REQUIREMENTS_FILE"

printf 'Virtual environment ready: %s\n' "$VENV_DIR"
printf 'Interpreter: %s\n' "$VENV_PYTHON"
