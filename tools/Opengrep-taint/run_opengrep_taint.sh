#!/usr/bin/env bash
# Opengrep (taint mode) runner -- Python 3.13 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if ! command -v opengrep >/dev/null 2>&1; then
  echo "[Opengrep-taint] binary not found on PATH." >&2
  exit 127
fi

echo "[Opengrep-taint] interprocedural dataflow rules"
echo "  ground truth: FLOW 1-4 are real; FLOW 5 is sanitized via shlex.quote"
echo "  and reporting it counts as a false positive."
echo

opengrep scan --config tools/Opengrep-taint/taint-rules.yaml \
  --text \
  src/orderkit/orderkit/analysis/taint_fixture.py || true
