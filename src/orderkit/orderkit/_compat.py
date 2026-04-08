"""Interpreter compatibility shims -- Python 3.11 branch.

Same surface as every other branch. From 3.11 onward ``tomllib``,
``enum.StrEnum``, ``typing.Self`` and ``datetime.UTC`` are native, so those
four shims collapse into direct re-exports. ``itertools.batched`` and
``warnings.deprecated`` are still backfilled.
"""

import sys
import tomllib
from datetime import UTC
from enum import StrEnum
from typing import Self, TypeAlias

PY_VERSION = sys.version_info[:2]

ExternalRef: TypeAlias = str | int | None
MaybeStr: TypeAlias = str | None

#: ``enum.StrEnum`` is native from 3.11, so the shim is the real thing.
StrEnumBase = StrEnum


def load_toml(handle):
    """``tomllib`` is in the standard library from 3.11 (PEP 680)."""
    return tomllib.load(handle)


CONFIG_FORMAT = "toml"


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


class CapabilityProbe:
    """Small helper whose fluent methods return ``Self`` (PEP 673, 3.11+)."""

    def __init__(self) -> None:
        self.checked: list[str] = []

    def check(self, name: str) -> Self:
        self.checked.append(name)
        return self

    def result(self) -> dict[str, str]:
        return {name: describe_capability(name) for name in self.checked}


def describe_capability(name: str) -> str:
    match name:
        case "tomllib" | "StrEnum" | "datetime.UTC" | "typing.Self":
            return "native"
        case "itertools.batched":
            return "backfilled (native in 3.12)"
        case "warnings.deprecated":
            return "backfilled (native in 3.13)"
        case _:
            return "unknown"


def collect_errors(values: list[int]) -> list[str]:
    """Aggregate validation problems with PEP 654 exception groups (3.11+).

    ``except*`` is a hard SyntaxError on Python 3.10 and earlier.
    """
    problems: list[Exception] = [
        ValueError(f"negative: {value}") for value in values if value < 0
    ]
    if not problems:
        return []

    collected: list[str] = []
    try:
        raise ExceptionGroup("validation", problems)
    except* ValueError as group:
        collected.extend(str(error) for error in group.exceptions)
    return collected


def capability_report() -> dict[str, object]:
    """Which shims are native on this interpreter and which are backfilled."""
    return {
        "tomllib": True,
        "StrEnum": True,
        "itertools.batched": False,
        "warnings.deprecated": False,
        "datetime.UTC": True,
        "config_format": CONFIG_FORMAT,
        "python": f"{PY_VERSION[0]}.{PY_VERSION[1]}",
        "utc": str(UTC),
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
    "CapabilityProbe",
    "describe_capability",
    "collect_errors",
    "capability_report",
]
