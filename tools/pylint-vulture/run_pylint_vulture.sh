#!/usr/bin/env bash
# pylint + vulture runner -- Python 3.12 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "[pylint] version:"
pylint --version | head -1

echo
echo "[pylint] 1/3 real source (fixtures excluded, expect a high score)"
pylint --rcfile tools/pylint-vulture/.pylintrc \
  --ignore-paths "^src/orderkit/orderkit/analysis/.*$" \
  src/orderkit/orderkit || true

echo
echo "[pylint] 2/3 planted lint fixture (expect findings)"
# The fixture carries a file-level 'pylint: disable=all', so the runner
# re-enables everything explicitly.
pylint --rcfile tools/pylint-vulture/.pylintrc \
  --enable=all \
  src/orderkit/orderkit/analysis/lint_violations.py || true

echo
echo "[vulture] 3/3 dead-code detection (expect findings in dead_code.py)"
vulture src/orderkit/orderkit tools/pylint-vulture/whitelist.py \
  --min-confidence 60 \
  --sort-by-size || true
