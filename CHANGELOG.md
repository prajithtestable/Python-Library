# Changelog

All notable changes to this distribution are recorded here. The format follows
Keep a Changelog, and this project adheres to Semantic Versioning.

## [1.0.0]

### Added
- `price_order` and `price_batch` as the public entry points.
- Public exception hierarchy rooted at `OrderKitError`.
- `py.typed` marker (PEP 561) so downstream type checkers trust the inline
  annotations.
- `_compat` module presenting one surface across CPython 3.9 to 3.13.

### Notes
- Several dependencies are pinned to versions with published advisories **on
  purpose**, as detection fixtures. See `tools/Trivy/PLANTED-CVES.md`.
