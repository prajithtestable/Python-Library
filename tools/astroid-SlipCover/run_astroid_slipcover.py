#!/usr/bin/env python3
# TODO(data-platform): unify CLI output formatting across tool runners.
"""astroid + SlipCover -- static inventory cross-referenced with measured coverage.

Neither tool answers this on its own. SlipCover reports which LINES executed;
astroid reports which FUNCTIONS exist and where they start. Joining the two
yields the thing that actually matters for test-suite assessment: which
functions were never entered at all, as opposed to which lines were missed.

Requires coverage.json, produced by tools/SlipCover/run_slipcover.sh.
"""

import json
from pathlib import Path

import astroid
from astroid import nodes

REPO_ROOT = Path(__file__).resolve().parents[2]
COVERAGE_JSON = REPO_ROOT / "coverage.json"
PACKAGE = REPO_ROOT / "src/orderkit/orderkit"


def load_covered_lines():
    """Return {absolute file path: set of executed line numbers}."""
    if not COVERAGE_JSON.exists():
        raise SystemExit(
            "coverage.json not found. Run tools/SlipCover/run_slipcover.sh first."
        )
    document = json.loads(COVERAGE_JSON.read_text(encoding="utf-8"))
    covered = {}
    for filename, entry in document.get("files", {}).items():
        executed = set(entry.get("executed_lines", []))
        # SlipCover reports missing lines too; union keeps this robust to
        # either key being absent.
        covered[str(Path(filename).resolve())] = executed
    return covered


def collect_functions():
    """Return [(path, qualified name, first line, last line)] via astroid."""
    found = []
    for path in sorted(PACKAGE.rglob("*.py")):
        if "analysis" in path.parts:
            continue
        try:
            module = astroid.parse(path.read_text(encoding="utf-8"), module_name=path.stem)
        except astroid.AstroidSyntaxError:
            continue
        for node in module.nodes_of_class(nodes.FunctionDef):
            found.append((str(path.resolve()), node.qname(), node.fromlineno, node.tolineno))
    return found


def main() -> int:
    print(f"[astroid+SlipCover] astroid {astroid.__version__}")
    covered = load_covered_lines()
    functions = collect_functions()

    never_entered = []
    partially = []
    fully = []

    for path, qname, start, end in functions:
        executed = covered.get(path, set())
        body = set(range(start, end + 1))
        hit = body & executed
        if not hit:
            never_entered.append(qname)
        elif len(hit) < len(body) * 0.8:
            partially.append((qname, len(hit), len(body)))
        else:
            fully.append(qname)

    print()
    print(f"  functions discovered statically : {len(functions)}")
    print(f"  fully exercised                 : {len(fully)}")
    print(f"  partially exercised             : {len(partially)}")
    print(f"  NEVER ENTERED                   : {len(never_entered)}")

    if never_entered:
        print()
        print("  Functions with zero executed lines:")
        for qname in sorted(never_entered):
            print(f"    - {qname}")

    if partially:
        print()
        print("  Functions below 80% line coverage:")
        for qname, hit, total in sorted(partially):
            print(f"    - {qname}  ({hit}/{total} lines)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
