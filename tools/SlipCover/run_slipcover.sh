#!/usr/bin/env bash
# SlipCover runner -- Python 3.10 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "[SlipCover] version:"
python -m slipcover --version

echo
echo "[SlipCover] 1/2 branch coverage -> XML (consumed by diff-cover)"
python -m slipcover --branch \
  --source src/orderkit/orderkit \
  --xml --out coverage.xml \
  -m pytest tests/orderkit_tests || true

echo
echo "[SlipCover] 2/2 branch coverage -> JSON (consumed by astroid + SlipCover)"
python -m slipcover --branch \
  --source src/orderkit/orderkit \
  --json --pretty-print --out coverage.json \
  -m pytest tests/orderkit_tests || true

echo
echo "[SlipCover] wrote coverage.xml and coverage.json to the repository root"
