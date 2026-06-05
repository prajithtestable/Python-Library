#!/usr/bin/env bash
# mutmut runner -- Python 3.12 branch.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# mutmut 3.7.0 reads its configuration from setup.cfg [mutmut].
# Verified against the CLI: with no source_paths it aborts with
# "Could not figure out where the code to mutate is."
echo "[mutmut] configuration in use:"
sed -n '/\[mutmut\]/,/^$/p' setup.cfg

echo
echo "[mutmut] 1/3 run mutation testing over the services package"
mutmut run || true

echo
echo "[mutmut] 2/3 results summary"
mutmut results || true

echo
echo "[mutmut] 3/3 surviving mutants indicate weak assertions in the suite"
mutmut browse --help >/dev/null 2>&1 && echo "        (run 'mutmut browse' for the interactive view)"
