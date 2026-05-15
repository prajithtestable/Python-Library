"""Call-graph fixture -- a deliberately layered call chain.

Target for the pyan3 + astroid pairing, which builds a static call graph.
The chain below is deep enough to distinguish a real interprocedural graph
from a shallow one, and includes the three edge kinds pyan3 distinguishes:
defines, uses and inherits.

Ground-truth call graph
-----------------------
    ingest
      -> _read_source
           -> _decode_row
                -> _coerce_number
      -> _validate_rows
           -> _coerce_number
      -> Normalizer.run
           -> Normalizer._strip
           -> Normalizer._retag
                -> _coerce_number
    StrictNormalizer inherits Normalizer and overrides _retag.

Nothing here is called by the pipeline.
"""

# ruff: noqa
# pylint: disable=all


def _coerce_number(raw):
    """Leaf function. Reached from three distinct callers."""
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _decode_row(line):
    parts = line.split(",")
    return {
        "order_id": parts[0] if parts else "",
        "quantity": _coerce_number(parts[1] if len(parts) > 1 else 0),
    }


def _read_source(lines):
    return [_decode_row(line) for line in lines]


def _validate_rows(rows):
    valid = []
    for row in rows:
        if _coerce_number(row.get("quantity")) > 0:
            valid.append(row)
    return valid


class Normalizer:
    """Base normalizer. Two private helpers, one public entry point."""

    prefix = "channel:"

    def _strip(self, value):
        return value.replace(self.prefix, "")

    def _retag(self, row):
        row["weight"] = _coerce_number(row.get("quantity")) * 1.0
        return row

    def run(self, rows):
        output = []
        for row in rows:
            row["order_id"] = self._strip(str(row.get("order_id", "")))
            output.append(self._retag(row))
        return output


class StrictNormalizer(Normalizer):
    """Inherits Normalizer and overrides one method -- an 'inherits' edge."""

    def _retag(self, row):
        row = super()._retag(row)
        row["strict"] = True
        return row


def ingest(lines, strict=False):
    """Top of the call graph."""
    rows = _read_source(lines)
    rows = _validate_rows(rows)
    normalizer = StrictNormalizer() if strict else Normalizer()
    return normalizer.run(rows)
