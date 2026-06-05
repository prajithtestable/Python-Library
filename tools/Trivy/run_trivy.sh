#!/usr/bin/env bash
# Trivy runner -- Python 3.10 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Trivy is a standalone Go binary, not a PyPI package.
#   https://trivy.dev/latest/getting-started/installation/
if ! command -v trivy >/dev/null 2>&1; then
  echo "[Trivy] binary not found on PATH -- see the install note above." >&2
  exit 127
fi

echo "[Trivy] version:"
trivy --version | head -1

echo
echo "[Trivy] 1/2 filesystem scan of declared dependencies"
echo "        (expect findings -- see tools/Trivy/PLANTED-CVES.md)"
trivy fs --config tools/Trivy/trivy.yaml . || true

echo
echo "[Trivy] 2/2 secret scan of the planted SAST fixture"
trivy fs --scanners secret src/orderkit/orderkit/analysis/ || true
