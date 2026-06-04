#!/usr/bin/env bash
# Ruff runner -- Python 3.11 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "[Ruff] version:"
ruff --version

echo
echo "[Ruff] 1/3 lint of real source (fixtures excluded, expect clean)"
ruff check --config tools/Ruff/ruff.toml \
  --exclude "src/orderkit/orderkit/analysis" \
  src/orderkit/orderkit || true

echo
echo "[Ruff] 2/3 lint of the planted fixture (expect findings)"
# --ignore-noqa defeats the file-level '# ruff: noqa' the fixture carries.
ruff check --config tools/Ruff/ruff.toml --ignore-noqa \
  --output-format concise \
  src/orderkit/orderkit/analysis/lint_violations.py || true

echo
echo "[Ruff] 3/3 format check"
ruff format --check --config tools/Ruff/ruff.toml src/orderkit/orderkit || true
