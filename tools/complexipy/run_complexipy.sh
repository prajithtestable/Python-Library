#!/usr/bin/env bash
# complexipy runner -- Python 3.10 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "[complexipy] version:"
complexipy --version || true

echo
echo "[complexipy] 1/2 whole package, sorted by descending complexity"
complexipy src/orderkit/orderkit --sort desc || true

echo
echo "[complexipy] 2/2 threshold run against the planted fixture"
# -mx sets the maximum cognitive complexity allowed per function.
# grade_shipment() in complexity_sample.py is built to exceed it.
complexipy src/orderkit/orderkit/analysis/complexity_sample.py -mx 15 --failed || true
