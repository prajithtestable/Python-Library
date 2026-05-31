#!/usr/bin/env python3
# TODO(data-platform): unify CLI output formatting across tool runners.
"""Stdlib-only coverage driver -- Python 3.12 branch.

A deliberately minimal line-coverage recorder built on sys.settrace and
nothing else. It exists as the CONTROL in this repository: whatever SlipCover
reports, this establishes what the standard library alone can measure, and
how much slower it is doing so.

Reports lines executed per file, plus wall-clock overhead versus an untraced
run of the same suite.
"""

import sys
import time
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE = (REPO_ROOT / "src" / "orderkit" / "orderkit").resolve()
TESTS = REPO_ROOT / "tests" / "orderkit_tests"

executed = defaultdict(set)


def tracer(frame, event, arg):
    """Local trace function. Records every line event inside the package."""
    if event == "line":
        filename = frame.f_code.co_filename
        if filename.startswith(str(PACKAGE)):
            executed[filename].add(frame.f_lineno)
    return tracer


TRIPLE_DOUBLE = chr(34) * 3
TRIPLE_SINGLE = chr(39) * 3


def countable_lines(path):
    """Crude executable-line count: non-blank, non-comment, non-docstring-ish."""
    total = 0
    in_docstring = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        quotes = line.count(TRIPLE_DOUBLE) + line.count(TRIPLE_SINGLE)
        if quotes % 2 == 1:
            in_docstring = not in_docstring
            continue
        if in_docstring or not line or line.startswith("#"):
            continue
        total += 1
    return total


def run_suite():
    import pytest

    return pytest.main([str(TESTS), "-q", "--no-header", "-p", "no:cacheprovider"])


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT / "src" / "orderkit"))

    print(f"[settrace] python {sys.version.split()[0]}")
    print("[settrace] baseline run (untraced)")
    start = time.perf_counter()
    run_suite()
    baseline = time.perf_counter() - start

    print()
    print("[settrace] traced run")
    start = time.perf_counter()
    sys.settrace(tracer)
    try:
        run_suite()
    finally:
        sys.settrace(None)
    traced = time.perf_counter() - start

    print()
    print("[settrace] per-file line coverage")
    grand_hit = 0
    grand_total = 0
    for path in sorted(PACKAGE.rglob("*.py")):
        if "analysis" in path.parts:
            continue
        hit = len(executed.get(str(path), set()))
        total = countable_lines(path)
        if not total:
            continue
        grand_hit += hit
        grand_total += total
        pct = 100.0 * hit / total
        print(f"  {path.relative_to(REPO_ROOT)!s:<62} {hit:>4}/{total:<4} {pct:5.1f}%")

    print()
    if grand_total:
        print(f"  TOTAL {grand_hit}/{grand_total} = {100.0 * grand_hit / grand_total:.1f}%")
    print(f"  untraced : {baseline:.3f}s")
    print(f"  traced   : {traced:.3f}s")
    if baseline > 0:
        print(f"  overhead : {traced / baseline:.2f}x")
    print()
    print("  Compare against tools/SlipCover/run_slipcover.sh on the same suite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
