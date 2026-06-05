#!/usr/bin/env bash
# Opengrep runner -- Python 3.10 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Opengrep is a standalone binary, not a PyPI package -- there is no version
# to pin in pyproject.toml. Install it before running:
#   curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
if ! command -v opengrep >/dev/null 2>&1; then
  echo "[Opengrep] binary not found on PATH -- see the install note above." >&2
  exit 127
fi

echo "[Opengrep] version:"
opengrep --version

echo
echo "[Opengrep] 1/2 custom rules against the planted SAST fixture"
opengrep scan --config tools/Opengrep/rules/ \
  --text \
  src/orderkit/orderkit/analysis/sast_fixture.py || true

echo
echo "[Opengrep] 2/2 custom rules across the whole package"
opengrep scan --config tools/Opengrep/rules/ --text src/orderkit/orderkit || true
