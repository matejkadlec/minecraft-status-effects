#!/usr/bin/env bash
# Unified test runner for project Python validation / test scripts.
#
# Usage:
#   ./run_tests.sh                # discover and run all known test scripts
#   ./run_tests.sh scripts/validate_effects.py other_test.py
#   ./run_tests.sh --help         # show help
#
# Discovery rules (when no explicit files are passed):
#   1. scripts/validate_effects.py (explicitly included if present)
#   2. scripts/test_*.py           (pytest-like prefix pattern)
#   3. scripts/*_test.py           (alternate suffix pattern)
# Duplicate paths are de-duplicated in listed order.
# To add new tests later, just drop a file following one of the patterns above
# or pass it explicitly as an argument.
#
# Exit status: 0 if all tests pass, 1 otherwise.

set -euo pipefail

# Colors (fallback to plain if not a TTY)
if [ -t 1 ]; then
  GREEN='\033[32m'; RED='\033[31m'; YELLOW='\033[33m'; BOLD='\033[1m'; RESET='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; BOLD=''; RESET=''
fi

show_help() {
  grep '^#' "$0" | sed 's/^# \{0,1\}//'
}

if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then
  show_help
  exit 0
fi

# Activate venv if present and not already active
if [ -d "venv" ] && [ -f "venv/bin/activate" ] && [ -z "${VIRTUAL_ENV:-}" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

# Build test list
declare -a TESTS
if [ "$#" -gt 0 ]; then
  for t in "$@"; do
    if [ ! -f "$t" ]; then
      echo -e "${RED}Missing test file:${RESET} $t" >&2
      exit 1
    fi
    TESTS+=("$t")
  done
else
  shopt -s nullglob
  if [ -f scripts/validate_effects.py ]; then TESTS+=(scripts/validate_effects.py); fi
  for f in scripts/test_*.py; do TESTS+=("$f"); done
  for f in scripts/*_test.py; do TESTS+=("$f"); done
  shopt -u nullglob
fi

# De-duplicate while preserving order
declare -A SEEN
declare -a UNIQUE
for f in "${TESTS[@]}"; do
  if [[ -z ${SEEN[$f]:-} ]]; then
    SEEN[$f]=1
    UNIQUE+=("$f")
  fi
done
TESTS=("${UNIQUE[@]}")

if [ ${#TESTS[@]} -eq 0 ]; then
  echo -e "${YELLOW}No test scripts discovered.${RESET}" >&2
  exit 0
fi

echo -e "${BOLD}Discovered ${#TESTS[@]} test script(s):${RESET}"
for t in "${TESTS[@]}"; do echo "  - $t"; done
echo

failures=0
for t in "${TESTS[@]}"; do
  echo -e "${BOLD}>>> Running:${RESET} $t"
  if python "$t"; then
    echo -e "${GREEN}PASS:${RESET} $t"
  else
    echo -e "${RED}FAIL:${RESET} $t"
    failures=$((failures+1))
  fi
  echo
done

if [ $failures -eq 0 ]; then
  echo -e "${GREEN}All tests passed (${#TESTS[@]}).${RESET}"
  exit 0
else
  echo -e "${RED}$failures test(s) failed.${RESET}" >&2
  exit 1
fi
