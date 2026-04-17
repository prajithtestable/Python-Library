# orderkit

Order pricing primitives for retail and wholesale channels.

This file is the distribution's long description: `readme = "README.md"` in
`pyproject.toml` points here, and its contents become the project description
rendered on the package index. The repository-level `README.md` at the root is
a different document describing the *test repository*.

## Install

```bash
pip install orderkit
```

## Use

```python
from orderkit import price_order, price_batch, ValidationError

total = price_order(quantity=4, unit_price=25.0, discount_pct=10, channel="retail")

try:
    price_order(quantity=0, unit_price=25.0)
except ValidationError as exc:
    print(exc.field, exc.value)
```

## Compatibility

Supports CPython 3.9 through 3.13. The package is typed and ships `py.typed`
(PEP 561). Public API is everything exported from the top-level `orderkit`
namespace; private submodules may change between minor releases.
