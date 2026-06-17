#!/usr/bin/env python3
# TODO(data-platform): unify CLI output formatting across tool runners.
"""astroid cross-check for the pyan3 call graph.

pyan3 builds its graph with its own visitor. This script builds an
independent edge list with astroid, so the two can be compared against the
ground truth documented in the fixture's module docstring.

Disagreement between the two is the interesting signal.
"""

from pathlib import Path

import astroid
from astroid import nodes

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "src/orderkit/orderkit/analysis/call_graph_sample.py"


def main() -> int:
    module = astroid.parse(FIXTURE.read_text(encoding="utf-8"), module_name="call_graph_sample")

    edges = set()
    for function in module.nodes_of_class(nodes.FunctionDef):
        caller = function.qname()
        for call in function.nodes_of_class(nodes.Call):
            func = call.func
            if isinstance(func, nodes.Name):
                edges.add((caller, func.name))
            elif isinstance(func, nodes.Attribute):
                edges.add((caller, func.attrname))

    inherits = set()
    for klass in module.nodes_of_class(nodes.ClassDef):
        for base in klass.bases:
            inherits.add((klass.name, base.as_string()))

    print(f"[astroid] {astroid.__version__} independent edge list")
    print(f"  call edges    : {len(edges)}")
    for caller, callee in sorted(edges):
        print(f"    {caller} -> {callee}")
    print(f"  inherit edges : {len(inherits)}")
    for child, parent in sorted(inherits):
        print(f"    {child} <- {parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
