#!/usr/bin/env python3
# TODO(data-platform): unify CLI output formatting across tool runners.
"""astroid static inference pass -- Python 3.13 branch.

astroid 4.3.0 is pinned on this branch. The 3.x and 4.x series differ, which
is one of the more meaningful cross-branch differences in this repository:
py3.9 gets astroid 3.3.11 and every other branch gets 4.3.0.

This script walks the services package, builds an astroid AST for each module
and reports what astroid can infer statically: function signatures, inferred
return types, class hierarchies and unresolvable names.
"""

import sys
from pathlib import Path

import astroid
from astroid import nodes

# Import node classes from astroid.nodes rather than the astroid root: the
# root re-exports are deprecated in astroid 4 and slated for removal in 5,
# while astroid.nodes works on both the 3.x and 4.x series this matrix pins.

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGETS = [
    REPO_ROOT / "src/orderkit/orderkit/services",
    REPO_ROOT / "src/orderkit/orderkit/analysis/call_graph_sample.py",
]


def iter_python_files(paths):
    for path in paths:
        if path.is_dir():
            yield from sorted(path.glob("*.py"))
        elif path.exists():
            yield path


def describe_function(node):
    args = [arg.name for arg in node.args.args]
    try:
        # astroid 4 made `caller` a required positional argument;
        # passing it explicitly works on both 3.x and 4.x.
        inferred = {type(value).__name__ for value in node.infer_call_result(None)}
    except (astroid.AstroidError, StopIteration, AttributeError, TypeError):
        inferred = {"<uninferable>"}
    return f"    def {node.name}({', '.join(args)}) -> {'|'.join(sorted(inferred))}"


def main() -> int:
    print(f"[astroid] version {astroid.__version__}")
    print(f"[astroid] python  {sys.version.split()[0]}")
    print()

    total_functions = 0
    total_classes = 0
    uninferable = 0

    for path in iter_python_files(TARGETS):
        rel = path.relative_to(REPO_ROOT)
        try:
            module = astroid.parse(path.read_text(encoding="utf-8"), module_name=path.stem)
        except astroid.AstroidSyntaxError as exc:
            print(f"[astroid] SYNTAX ERROR in {rel}: {exc}")
            continue

        print(f"  {rel}")
        for node in module.body:
            if isinstance(node, nodes.FunctionDef):
                total_functions += 1
                line = describe_function(node)
                if "<uninferable>" in line:
                    uninferable += 1
                print(line)
            elif isinstance(node, nodes.ClassDef):
                total_classes += 1
                bases = [base.as_string() for base in node.bases]
                suffix = f" <- {', '.join(bases)}" if bases else ""
                print(f"    class {node.name}{suffix}")
                for child in node.body:
                    if isinstance(child, nodes.FunctionDef):
                        total_functions += 1
                        line = describe_function(child)
                        if "<uninferable>" in line:
                            uninferable += 1
                        print("    " + line.strip())
        print()

    print("[astroid] summary")
    print(f"  classes inferred      : {total_classes}")
    print(f"  functions inspected   : {total_functions}")
    print(f"  uninferable returns   : {uninferable}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
