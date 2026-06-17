#!/usr/bin/env bash
# pyan3 + astroid runner -- Python 3.11 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

OUT="tools/pyan3-astroid/out"
mkdir -p "$OUT"

echo "[pyan3] building the static call graph for the fixture"
echo "        ground truth is documented in the fixture's module docstring."
pyan3 src/orderkit/orderkit/analysis/call_graph_sample.py \
  --uses --defines --colored --grouped \
  --dot --file "$OUT/call_graph.dot" || true

echo
echo "[pyan3] plain-text graph for diffing"
pyan3 src/orderkit/orderkit/analysis/call_graph_sample.py \
  --uses --defines --text --file "$OUT/call_graph.txt" || true

echo
echo "[pyan3] whole services package"
pyan3 src/orderkit/orderkit/services/*.py \
  --uses --defines --colored --grouped \
  --dot --file "$OUT/services_graph.dot" || true

echo
echo "[astroid] independent inference pass for cross-checking pyan3's edges"
python tools/pyan3-astroid/cross_check_astroid.py

echo
echo "[pyan3-astroid] wrote graphs to $OUT"
