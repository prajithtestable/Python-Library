#!/usr/bin/env python3
"""Tool integration entry point -- the ToolIntegration.targets analogue.

In the C# reference repository, tools/ToolIntegration.targets is imported by
CSharpWebApi.Tools.csproj and prints one high-importance MSBuild message per
wired tool, so that a single build proves every tool is connected. This module
is the direct equivalent.

    python tools/tool_integration.py            # print the wiring banner
    python tools/tool_integration.py --list     # machine-readable tool list
    python tools/tool_integration.py --verify   # check every runner exists
    python tools/tool_integration.py --run RUFF # run one tool's runner
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
PYTHON_TARGET = "3.13"
HATCHLING_VERSION = "1.32.0"

# (directory, human label, how the tool is wired into this repository)
TOOL_WIRING = [
    ("Ruff", "Ruff", "pinned 0.16.2 -> tools/Ruff/ruff.toml + analysis/lint_violations.py"),
    ("complexipy", "complexipy", "pinned 7.0.1 -> analysis/complexity_sample.py"),
    ("symilar", "symilar (pylint)", "ships with pylint 4.0.7 -> services/{retail,wholesale}_order_processor.py"),
    ("Opengrep", "Opengrep", "standalone binary -> tools/Opengrep/rules/ + analysis/sast_fixture.py"),
    ("Trivy", "Trivy", "standalone binary -> src/orderkit/pyproject.toml planted CVE pins"),
    ("SlipCover", "SlipCover", "pinned 1.0.18 -> coverage.xml + coverage.json"),
    ("mutmut", "mutmut", "pinned 3.7.0 -> setup.cfg [mutmut] source_paths=services/"),
    ("diff-cover", "diff-cover", "pinned 10.5.0 -> consumes SlipCover coverage.xml"),
    ("astroid", "astroid", "pinned 4.3.0 -> static inference over services/"),
    ("astroid-SlipCover", "astroid + SlipCover", "joins astroid function inventory with SlipCover coverage.json"),
    ("Opengrep-taint", "Opengrep (taint mode)", "taint mode -> analysis/taint_fixture.py, 4 flows + 1 sanitized control"),
    ("settrace-driver", "sys.settrace driver (stdlib)", "stdlib only -> coverage control baseline vs SlipCover"),
    ("pyan3-astroid", "pyan3 + astroid", "pyan3 2.6.2 + astroid -> analysis/call_graph_sample.py"),
    ("pylint-vulture", "pylint + vulture", "pylint 4.0.7 + vulture 2.16 -> lint_violations.py, dead_code.py"),
    ("dulwich", "dulwich", "pinned 1.2.12 -> repository history mining (replaces pydriller)"),
]


def banner() -> int:
    print(f"=== Tool integration for Python {PYTHON_TARGET} "
          f"(hatchling {HATCHLING_VERSION}) ===")
    for directory, label, wiring in TOOL_WIRING:
        print(f"[{label}] {wiring}")
    print(f"=== {len(TOOL_WIRING)} tools wired ===")
    return 0


def list_tools() -> int:
    for directory, label, _wiring in TOOL_WIRING:
        print(f"{directory}\t{label}")
    return 0


def verify() -> int:
    problems = []
    for directory, label, _wiring in TOOL_WIRING:
        folder = TOOLS_DIR / directory
        if not folder.is_dir():
            problems.append(f"{label}: missing folder tools/{directory}")
            continue
        if not (folder / "trigger.yaml").is_file():
            problems.append(f"{label}: missing tools/{directory}/trigger.yaml")
        runners = list(folder.glob("run_*.sh")) + list(folder.glob("run_*.py"))
        if not runners:
            problems.append(f"{label}: no runner script in tools/{directory}")

    if problems:
        print("FAILED")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"OK -- all {len(TOOL_WIRING)} tools have a folder, a manifest and a runner.")
    return 0


def run(name: str) -> int:
    matches = [d for d, _l, _w in TOOL_WIRING if d.lower() == name.lower()]
    if not matches:
        print(f"unknown tool: {name}", file=sys.stderr)
        print("known tools: " + ", ".join(d for d, _l, _w in TOOL_WIRING), file=sys.stderr)
        return 2
    folder = TOOLS_DIR / matches[0]
    runners = sorted(folder.glob("run_*.sh")) + sorted(folder.glob("run_*.py"))
    runner = runners[0]
    command = (
        ["bash", str(runner)] if runner.suffix == ".sh" else [sys.executable, str(runner)]
    )
    return subprocess.call(command, cwd=REPO_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="machine-readable tool list")
    parser.add_argument("--verify", action="store_true", help="check wiring completeness")
    parser.add_argument("--run", metavar="TOOL", help="run a single tool's runner")
    args = parser.parse_args()

    if args.list:
        return list_tools()
    if args.verify:
        return verify()
    if args.run:
        return run(args.run)
    return banner()


if __name__ == "__main__":
    raise SystemExit(main())
