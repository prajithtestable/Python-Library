#!/usr/bin/env bash
# diff-cover runner -- Python 3.9 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

if [ ! -f coverage.xml ]; then
  echo "[diff-cover] coverage.xml missing -- generating it via SlipCover first."
  bash tools/SlipCover/run_slipcover.sh
fi

echo "[diff-cover] version:"
diff-cover --version

echo
echo "[diff-cover] 1/2 coverage of lines changed against main"
diff-cover coverage.xml \
  --compare-branch main \
  --src-roots src/orderkit/orderkit \
  --show-uncovered \
  --fail-under 80 || true

echo
echo "[diff-cover] 2/2 HTML report"
diff-cover coverage.xml \
  --compare-branch main \
  --src-roots src/orderkit/orderkit \
  --format "html:diff-cover-report.html" || true
