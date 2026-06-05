# Planted vulnerable dependencies

**These pins are deliberate. Do not "fix" them.**

`src/orderkit/pyproject.toml` pins five dependencies to versions with
published security advisories, so that Trivy has real findings to report. A
Trivy run that reports nothing against this repository is failing, not
passing.

This mirrors the C# reference repository, which pinned
`System.Data.SqlClient 4.8.6` as NuGet-Audit bait.

## The planted pins

| Package | Pinned version | Confirmed advisories |
|---------|----------------|----------------------|
| `requests` | `2.31.0` | PYSEC-2026-1873, PYSEC-2026-1872, PYSEC-2026-2275 |
| `Jinja2` | `3.1.3` | PYSEC-2026-1471, PYSEC-2026-1472, PYSEC-2026-1474, PYSEC-2026-1475 |
| `urllib3` | `2.0.6` | PYSEC-2023-212, PYSEC-2026-141, PYSEC-2026-1995 |
| `cryptography` | `42.0.0` | PYSEC-2024-225, PYSEC-2026-1284, PYSEC-2026-1285 |
| `paramiko` | `2.4.1` | CVE-2018-1000805, PYSEC-2022-166 |

Every advisory ID above was confirmed against the live PyPI Advisory Database
with `pip-audit` at the time this repository was generated. They were not
recalled from memory.

## Why these five

All five are dependencies a real library would plausibly carry:
`requests` for optional HTTP helpers, `paramiko` for an SFTP extra, `Jinja2`
for report rendering, `cryptography` as a transitive security dependency and `urllib3`
beneath `requests`. A scanner cannot dismiss them as obviously synthetic.

They are also pinned to *recent* versions rather than ancient ones. An
eight-year-old pin is trivially detectable and would not distinguish a good
scanner from a weak one; these sit close enough to current that the scanner
has to actually consult its advisory database.

## Verifying independently

```bash
pip-audit -r <(python - <<'PY'
print("requests==2.31.0")
print("Jinja2==3.1.3")
print("urllib3==2.0.6")
print("cryptography==42.0.0")
print("paramiko==2.4.1")
PY
) --no-deps
```

## Branch note

These pins are identical on all five version branches. Only
This distribution has no runtime framework, so the planted pins above are
essentially its entire dependency list -- which makes Trivy's job here purely
about the fixture. The build toolchain (`hatchling` 1.32.0 on
py3.10) is what differs across branches, and it is a build-time requirement
rather than a runtime dependency, so it does not appear in a `pip install`
dependency scan.
