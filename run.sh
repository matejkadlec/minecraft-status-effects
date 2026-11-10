#!/usr/bin/env bash
# Runs the website without having to activate the virtual environment.
#
#   ./run.sh                 development server with auto-reload on http://localhost:8000
#   ./run.sh --port 8080     any option of `python -m status_effects` (--host, --port, --workers, ...)
#   ./run.sh prod            production mode: no reload, 2 workers, trusts proxy headers, binds 127.0.0.1
#   ./run.sh test            all tests (pytest + the JavaScript tests when Node.js is installed)
#   ./run.sh lint            ruff on the Python code and the effect writing rules on data/effects.json
#
# The first run creates ./venv and installs the project into it; later runs reinstall only when
# pyproject.toml changes.
set -euo pipefail
cd "$(dirname "$0")"

VENV=venv
PYTHON="$VENV/bin/python"
STAMP="$VENV/.installed"

if [[ ! -x "$PYTHON" ]]; then
  echo "Creating the virtual environment in ./$VENV ..."
  python3 -m venv "$VENV"
fi
if [[ ! -f "$STAMP" || pyproject.toml -nt "$STAMP" ]]; then
  echo "Installing dependencies ..."
  "$PYTHON" -m pip install --quiet --upgrade pip
  "$PYTHON" -m pip install --quiet -e ".[dev]"
  touch "$STAMP"
fi

case "${1:-}" in
  test)
    shift
    "$PYTHON" -m pytest "$@"
    if command -v node >/dev/null 2>&1; then
      node --test "tests/js/*.test.mjs"
    else
      echo "Node.js not found, skipping the JavaScript tests."
    fi
    ;;
  lint)
    "$VENV/bin/ruff" check src tests
    "$PYTHON" tests/effect_rules.py data/effects.json
    ;;
  prod)
    shift
    exec "$PYTHON" -m status_effects --host 127.0.0.1 --workers 2 --proxy-headers "$@"
    ;;
  *)
    exec "$PYTHON" -m status_effects --reload "$@"
    ;;
esac
