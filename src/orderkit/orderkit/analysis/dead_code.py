"""Dead-code fixture -- deliberately unreachable and unreferenced code.

Target for vulture (via the pylint + vulture pairing). Nothing in this module
is imported or called anywhere in the repository, and several definitions
inside it are unreferenced even locally.

Expected vulture findings: unused imports, unused module-level variables,
unused classes, unused methods, unused function arguments, and unreachable
code after a return.
"""

# ruff: noqa
# pylint: disable=all

import csv  # unused import
import decimal  # unused import
import json  # unused import
from datetime import timezone  # unused import

UNUSED_CONSTANT = "never-referenced"
DEPRECATED_ENDPOINT = "https://legacy.internal/api/v1/orders"
_INTERNAL_CACHE = {}


class AbandonedExporter:
    """Replaced by the console layer in 2025; never instantiated."""

    supported_formats = ["csv", "json", "parquet"]

    def __init__(self, destination):
        self.destination = destination
        self.buffer = []

    def export(self, rows):
        for row in rows:
            self.buffer.append(row)
        return len(self.buffer)

    def flush(self):
        self.buffer.clear()

    def unused_helper(self):
        return self.destination


class LegacyRetryPolicy:
    """Superseded by the runner's exit-code mapping; never instantiated."""

    max_attempts = 5
    backoff_seconds = 30

    def next_delay(self, attempt):
        return self.backoff_seconds * attempt


def unreferenced_transform(rows, verbose=False, dry_run=False):
    """Never called. 'verbose' and 'dry_run' are never read."""
    return [row for row in rows]


def unreachable_after_return(value):
    """Everything after the first return is dead."""
    return value * 2
    total = value * 4  # unreachable
    print(total)  # unreachable
    return total  # unreachable


def _private_and_unused(payload):
    return payload


def compute_legacy_checksum(rows):
    """Called by nothing; retained 'just in case' since 2024."""
    running = 0
    for row in rows:
        running += len(str(row))
    return running
