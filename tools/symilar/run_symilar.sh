#!/usr/bin/env bash
# symilar (pylint) runner -- Python 3.13 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# symilar is distributed as part of pylint (4.0.7 on this branch).
echo "[symilar] pylint version:"
pylint --version | head -1

echo
echo "[symilar] 1/2 the deliberate duplicate pair (expect a similarity report)"
symilar --duplicates 8 --ignore-comments --ignore-docstrings \
  src/orderkit/orderkit/services/retail_order_processor.py \
  src/orderkit/orderkit/services/wholesale_order_processor.py || true

echo
echo "[symilar] 2/2 whole services package at a stricter threshold"
symilar --duplicates 4 --ignore-comments --ignore-docstrings --ignore-imports \
  src/orderkit/orderkit/services/*.py || true
