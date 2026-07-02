# Python Library — Monolithic (py3.13)

`orderkit`, a distributable PyPI library, for the **py3.13** branch, targeting
**CPython 3.13** (verified against 3.13.7).

## Project type

- **Language:** Python
- **Scenario:** 1 - Monolithic
- **Project type:** PyPI Library / Package Distribution
- **Module:** flat (single module)
- **Python:** 3.13
- **Build backend:** hatchling 1.32.0
- **Distribution:** `orderkit` 1.0.0, typed (PEP 561)

## Branches

`main` carries only the repository title. Every version branch holds the full
project:

- `py3.13` ← you are here
- `py3.9`
- `py3.10`
- `py3.11`
- `py3.12`

This branch does not run on Python 3.12. That is verified, not claimed — see *Version locking* below.

## Supported tools

- Ruff
- complexipy
- symilar (pylint)
- Opengrep
- Trivy
- SlipCover
- mutmut
- diff-cover
- astroid
- astroid + SlipCover
- Opengrep (taint mode)
- sys.settrace driver (stdlib)
- pyan3 + astroid
- pylint + vulture
- dulwich

## Build

```bash
uv venv --python 3.13
uv pip install -e src/orderkit -e tests/orderkit_tests -e tools/orderkit_tools
python tools/tool_integration.py --verify
```

This project type has **no runtime framework at all** — the library depends on
nothing but the standard library plus its planted fixture pins. What differs by
branch is the *build and publish toolchain*: hatchling, build, twine and
setuptools. See *Dependency pins that differ by branch*.

Fast check (compile only, no install):

```bash
python3.13 -m compileall -q src tests tools
```

## Run

There is no process to start — the deliverable is a distribution. "Running"
this project means building and validating the artefacts:

```bash
cd src/orderkit
python -m build                 # produces dist/orderkit-1.0.0-py3-none-any.whl and .tar.gz
twine check dist/*              # validates the metadata the index will render
```

Inspect what actually shipped, including the PEP 561 marker:

```bash
python -c "import zipfile,glob; print(zipfile.ZipFile(glob.glob('dist/*.whl')[0]).namelist())"
```

Use the library:

```python
from orderkit import price_order, price_batch, ValidationError

total = price_order(quantity=4, unit_price=25.0, discount_pct=10, channel="retail")

try:
    price_order(quantity=0, unit_price=25.0)
except ValidationError as exc:
    print(exc.field, exc.value)     # -> quantity 0
```

Every public name is re-exported from the top level and listed in
`orderkit.__all__`; anything reached through a private submodule is not covered
by the compatibility policy.

## Test

```bash
pytest tests/orderkit_tests
```

## Workspace projects

| Project | Path | Role |
|---------|------|------|
| `orderkit` | `src/orderkit/` | The distributable library (public API, compat shims, services, models) |
| `orderkit-tests` | `tests/orderkit_tests/` | pytest suite (SlipCover, mutmut, diff-cover target) |
| `orderkit-tools` | `tools/orderkit_tools/` | Tool integration (depends on library + tests) |

Three linked projects mirroring `CSharpWebApi` / `CSharpWebApi.Tests` /
`CSharpWebApi.Tools`. The tools project depends on both of the others, so it
always resolves last. The workspace root `pyproject.toml` declares all three
under `[tool.uv.workspace]` and holds the shared tool configuration — the
`Directory.Build.props` plus `.sln` analogue.

```
Python-Library/
├── pyproject.toml                 workspace root — Directory.Build.props / .sln
├── setup.cfg                      [mutmut] — mutmut 3.x does not read pyproject.toml
├── .python-version                pins the interpreter — the global.json analogue
├── src/orderkit/orderkit/
│   ├── analysis/                  deliberate fixtures — see analysis/README.md
│   ├── models/                    dataclass models
│   ├── services/                  business logic (mutation + coverage target)
│   ├── __init__.py                public re-exports + __all__
│   ├── _compat.py                 interpreter shims, 3.9 → 3.13
│   ├── api.py                     the stable public facade
│   ├── config.py                  optional user configuration
│   ├── exceptions.py              public exception hierarchy
│   ├── pricing.py                 batch pricing engine
│   └── py.typed                   PEP 561 marker
├── tests/orderkit_tests/
└── tools/
    ├── orderkit_tools/       tool integration project
    └── tool_integration.py        the ToolIntegration.targets analogue
```

## Tool entry points

```bash
python tools/tool_integration.py            # print the wiring banner
python tools/tool_integration.py --verify   # assert every tool is wired
python tools/tool_integration.py --run Ruff # run one tool
```

| Tool | Folder | Connection |
|------|--------|------------|
| Ruff | `tools/Ruff/` | pinned 0.16.2 -> tools/Ruff/ruff.toml + analysis/lint_violations.py |
| complexipy | `tools/complexipy/` | pinned 7.0.1 -> analysis/complexity_sample.py |
| symilar (pylint) | `tools/symilar/` | ships with pylint 4.0.7 -> services/{retail,wholesale}_order_processor.py |
| Opengrep | `tools/Opengrep/` | standalone binary -> tools/Opengrep/rules/ + analysis/sast_fixture.py |
| Trivy | `tools/Trivy/` | standalone binary -> src/orderkit/pyproject.toml planted CVE pins |
| SlipCover | `tools/SlipCover/` | pinned 1.0.18 -> coverage.xml + coverage.json |
| mutmut | `tools/mutmut/` | pinned 3.7.0 -> setup.cfg [mutmut] source_paths=services/ |
| diff-cover | `tools/diff-cover/` | pinned 10.5.0 -> consumes SlipCover coverage.xml |
| astroid | `tools/astroid/` | pinned 4.3.0 -> static inference over services/ |
| astroid + SlipCover | `tools/astroid-SlipCover/` | joins astroid function inventory with SlipCover coverage.json |
| Opengrep (taint mode) | `tools/Opengrep-taint/` | taint mode -> analysis/taint_fixture.py, 4 flows + 1 sanitized control |
| sys.settrace driver (stdlib) | `tools/settrace-driver/` | stdlib only -> coverage control baseline vs SlipCover |
| pyan3 + astroid | `tools/pyan3-astroid/` | pyan3 2.6.2 + astroid -> analysis/call_graph_sample.py |
| pylint + vulture | `tools/pylint-vulture/` | pylint 4.0.7 + vulture 2.16 -> lint_violations.py, dead_code.py |
| dulwich | `tools/dulwich/` | pinned 1.2.12 -> repository history mining (replaces pydriller) |

Every tool folder contains a `trigger.yaml` manifest in the same shape as the
C# repository's manifests, plus a runner script. `Opengrep` and `Trivy` are
standalone binaries rather than PyPI packages, so they carry an install note
instead of a pin.

## What Python 3.13 contributes

- PEP 696 type parameter defaults -- type X[T = str] = ..., class C[T = int]  (syntax)
- PEP 702 warnings.deprecated
- PEP 705 typing.ReadOnly for TypedDict
- PEP 742 typing.TypeIs
- copy.replace()
- glob.translate
- os.process_cpu_count()
- random.Random.binomialvariate

`tests/orderkit_tests/orderkit_tests/test_version_features.py` asserts
each of these at runtime, so the branch's version-locking is executable rather
than documented.

## Version locking

The whole matrix was verified by compiling and importing every branch with
every interpreter from 3.9 to 3.13. The result is strictly triangular: branch
N works on interpreters ≥ N and fails on every interpreter below it.

Two mechanisms produce the lock:

- **Parse-time** — syntax that is a hard `SyntaxError` on the previous version
  (`match` on 3.9, `except*` on 3.10, PEP 695 on 3.11, PEP 696 on 3.12).
- **Import-time** — standard-library surface that does not exist yet, so the
  module compiles but raises `ImportError` (`typing.Self`, `enum.StrEnum` and
  `datetime.UTC` on 3.10; `typing.override` on 3.11; `typing.TypeIs` and
  `warnings.deprecated` on 3.12).

Reproduce it:

```bash
python3.12 -m compileall -q src   # expect SyntaxError on this branch
python3.13 -m compileall -q src      # expect success
```

## Fixtures

Nothing in `src/orderkit/orderkit/analysis/` is imported by the library.
Each module plants defects for a specific tool — see
[`analysis/README.md`](src/orderkit/orderkit/analysis/README.md) for the
full ground-truth table, including the **false-positive control** in
`taint_fixture.py`.

`services/retail_order_processor.py` and `services/wholesale_order_processor.py`
are deliberate near-duplicates. That is the symilar fixture, mirroring the
`RetailOrderProcessor` / `WholesaleOrderProcessor` pair in the C# repository.

## Planted vulnerable dependencies

`src/orderkit/pyproject.toml` pins five dependencies to versions with
published advisories, so Trivy has something real to find:

| Package | Version | Confirmed advisories |
|---------|---------|----------------------|
| `requests` | `2.31.0` | PYSEC-2026-1873, PYSEC-2026-1872, PYSEC-2026-2275 |
| `Jinja2` | `3.1.3` | PYSEC-2026-1471, PYSEC-2026-1472, PYSEC-2026-1474, PYSEC-2026-1475 |
| `urllib3` | `2.0.6` | PYSEC-2023-212, PYSEC-2026-141, PYSEC-2026-1995 |
| `cryptography` | `42.0.0` | PYSEC-2024-225, PYSEC-2026-1284, PYSEC-2026-1285 |
| `paramiko` | `2.4.1` | CVE-2018-1000805, PYSEC-2022-166 |

All confirmed against the live PyPI Advisory Database. Full rationale in
[`tools/Trivy/PLANTED-CVES.md`](tools/Trivy/PLANTED-CVES.md).

## Dependency pins that differ by branch

| Package | py3.9 | py3.10 – py3.13 |
|---------|-------|-----------------|
| `hatchling` (build backend) | 1.27.0 | 1.32.0 |
| `build` | 1.4.4 | 1.5.0 |
| `twine` | 6.2.0 | **7.0.0** |
| `setuptools` | 82.0.1 | 84.0.0 |
| `pylint` (ships `symilar`) | 3.3.9 | 4.0.7 |
| `astroid` | 3.3.11 | 4.3.0 |
| `pyan3` | 1.2.0 | 2.6.2 |
| `dulwich` | 0.24.10 | 1.2.12 |
| `mutmut` | 3.3.1 | 3.7.0 |
| `diff-cover` | 10.0.0 | 10.5.0 |
| `pytest` | 8.4.2 | 9.1.1 |

**This repository has no runtime framework to split**, which is the fourth
distinct pattern in the family. The library's only runtime dependencies are the
planted fixture pins; everything else it needs is in the standard library. What
splits instead is the **build toolchain**, including `twine` across a major
version boundary.

That is why `_compat.py` exists and carries so much of this repository's
version-specific weight. A library that claims 3.9–3.13 support has to present
one surface across all of them, so every branch exports the same shim names
with whatever implementation its interpreter allows:

| Capability | py3.9 | py3.10 | py3.11 | py3.12 | py3.13 |
|---|---|---|---|---|---|
| `tomllib` | backfilled | backfilled | native | native | native |
| `enum.StrEnum` | backfilled | backfilled | native | native | native |
| `itertools.batched` | backfilled | backfilled | backfilled | native | native |
| `warnings.deprecated` | backfilled | backfilled | backfilled | backfilled | native |
| config format | json | json | toml | toml | toml |

`py3.13` is the only branch where nothing is backfilled. `test_public_api.py`
asserts this table at runtime via `capability_report()`.

Compare with the siblings: Airflow splits on one package, Celery on none,
Typer/Click on both.

`ruff`, `complexipy`, `slipcover`, `vulture` and `packaging` resolve
identically on all five interpreters.

## Relationship to the sibling repositories

The `models/`, `services/` and `analysis/` layers are deliberately held
constant across the Python-Repos family. Holding the domain and the planted
fixtures fixed means a difference in tool output between repositories is
attributable to the **project type**, not to the code the tool happened to be
pointed at.

What changes here is that the framework layer is replaced by a *packaging*
layer: `api.py` (the stable facade), `exceptions.py` (the public error
hierarchy), `_compat.py` (interpreter shims), `py.typed`, the distribution
`README.md`, `CHANGELOG.md`, `LICENSE`, and a `pyproject.toml` carrying real
Trove classifiers, URLs and extras.

The taint fixture is also the hardest of the four here. A library does not
control its callers, so **every public function parameter is a taint source** —
there is no argv, no request and no broker message to anchor on. An engine that
only recognises `sys.argv`, `os.environ` or a web request object will miss
three of the four planted flows.
