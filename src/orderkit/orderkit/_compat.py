"""Interpreter compatibility shims -- Python 3.10 branch.

Same surface as every other branch. On 3.10, PEP 604 unions and PEP 634
pattern matching are available, but ``tomllib``, ``enum.StrEnum``,
``itertools.batched`` and ``warnings.deprecated`` are still backfilled here.
"""

import json
import sys
from datetime import timezone
from enum import Enum
from typing import TypeAlias

PY_VERSION = sys.version_info[:2]

UTC = timezone.utc

# PEP 604 unions plus PEP 613 explicit aliases, both new in 3.10.
ExternalRef: TypeAlias = str | int | None
MaybeStr: TypeAlias = str | None


class StrEnumBase(str, Enum):
    """Stand-in for ``enum.StrEnum``, which arrives in Python 3.11."""

    def __str__(self) -> str:
        return str(self.value)


def load_toml(handle):
    """``tomllib`` lands in 3.11 (PEP 680); this branch reads JSON."""
    return json.load(handle)


CONFIG_FORMAT = "json"


def batched(iterable, size: int) -> list[tuple]:
    """Stand-in for ``itertools.batched``, which arrives in Python 3.12."""
    if size <= 0:
        raise ValueError("size must be positive")
    items = list(iterable)
    return [tuple(items[index : index + size]) for index in range(0, len(items), size)]


def deprecated(message: str):
    """Stand-in for ``warnings.deprecated`` (PEP 702), which arrives in 3.13."""

    def decorate(obj):
        obj.__deprecated__ = message
        obj.__doc__ = f"{obj.__doc__ or ''}\n\nDeprecated: {message}"
        return obj

    return decorate


def describe_capability(name: str) -> str:
    """Report how one capability is provided, using PEP 634 pattern matching."""
    match name:
        case "tomllib" | "StrEnum":
            return "backfilled (native in 3.11)"
        case "itertools.batched":
            return "backfilled (native in 3.12)"
        case "warnings.deprecated":
            return "backfilled (native in 3.13)"
        case "match":
            return "native"
        case _:
            return "unknown"


def capability_report() -> dict[str, object]:
    """Which shims are native on this interpreter and which are backfilled."""
    return {
        "tomllib": False,
        "StrEnum": False,
        "itertools.batched": False,
        "warnings.deprecated": False,
        "datetime.UTC": False,
        "config_format": CONFIG_FORMAT,
        "python": f"{PY_VERSION[0]}.{PY_VERSION[1]}",
    }


__all__ = [
    "PY_VERSION",
    "UTC",
    "ExternalRef",
    "MaybeStr",
    "StrEnumBase",
    "load_toml",
    "CONFIG_FORMAT",
    "batched",
    "deprecated",
    "describe_capability",
    "capability_report",
]
