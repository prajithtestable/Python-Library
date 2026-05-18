# Analysis fixtures

Deliberately flawed code. **Nothing in this package is imported by the
pipeline** — every module exists purely to give one or more analysis tools
something to detect, so that a tool reporting nothing here is demonstrably
failing rather than demonstrably clean.

This mirrors `src/CSharpWebApi/Analysis/` in the C# reference repository.

| File | Primary target tool | What is planted |
|------|--------------------|-----------------|
| `complexity_sample.py` | complexipy | Deep nesting, long branch ladders, loops with `break`/`continue`. Version-flavoured: the 3.10+ branches add `match`, 3.11+ adds `except*`, 3.12+ adds PEP 695 generics. |
| `lint_violations.py` | Ruff, pylint | Non-PEP8 naming, unused imports and locals, mutable default argument, bare `except`, `== None`, lambda binding, builtin shadowing, inconsistent returns. |
| `sast_fixture.py` | Opengrep (rule mode) | Single-expression weaknesses: SQL injection, command injection, `eval`/`exec`, `pickle.loads`, `yaml.load`, hardcoded credentials, MD5, `verify=False`, insecure temp files. |
| `taint_fixture.py` | Opengrep (taint mode) | Five annotated multi-hop source→sink dataflows (sources are Celery task payloads), including one **sanitized control flow** that must NOT be reported. |
| `dead_code.py` | vulture | Unused imports, constants, classes, methods, arguments, and code after `return`. |
| `call_graph_sample.py` | pyan3 + astroid | A layered call chain with documented ground-truth edges, including one `inherits` edge via `super()`. |

## Why the fixtures are split this way

`sast_fixture.py` and `taint_fixture.py` are deliberately separate. The first
is catchable by single-file pattern matching; the second requires
interprocedural dataflow. Keeping them apart makes it possible to tell
whether Opengrep's taint mode is actually adding detection capability over
its default rule mode, rather than both modes simply re-finding the same
obvious `eval`.

`taint_fixture.py` FLOW 5 is a **false-positive control**: the tainted value
passes through `shlex.quote` before reaching the sink. A tool that reports
FLOW 5 is over-reporting.

## Suppressions

Each fixture carries `# ruff: noqa` and `# pylint: disable=all` at the top,
and this directory has its own `.editorconfig`. This is intentional and
mirrors the scoped `.editorconfig` in the C# repo's `Analysis/` folder: the
fixtures must not break an ordinary lint run of the real source tree. The
tool runners in `tools/` deliberately re-enable the rules when scanning this
directory — see each tool's `trigger.yaml`.
