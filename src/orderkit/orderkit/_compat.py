"""Interpreter compatibility shims -- Python 3.12 branch.

Same surface as every other branch. From 3.12 ``itertools.batched`` is native
and PEP 695 type-parameter syntax replaces ``typing.TypeAlias``. Only
``warnings.deprecated`` is still backfilled.
"""

import sys
import tomllib
from datetime import UTC
from enum import StrEnum
from itertools import batched as _batched
from typing import Self

PY_VERSION = sys.version_info[:2]

# PEP 695 type alias statements -- SyntaxError before Python 3.12.
type ExternalRef = str | int | None
type MaybeStr = str | None
type Batch[T] = tuple[T, ...]

StrEnumBase = StrEnum


def load_toml(handle):
    """``tomllib`` is in the standard library from 3.11 (PEP 680)."""
    return tomllib.load(handle)


CONFIG_FORMAT = "toml"


def batched[T](iterable: list[T], size: int) -> list[Batch[T]]:
    """``itertools.batched`` is native from 3.12; this just adapts the return type.

    Declared with PEP 695 generic-function syntax, a SyntaxError before 3.12.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    return list(_batched(iterable, size))


def deprecated(message: str):
    """Stand-in for ``warnings.deprecated`` (PEP 702), which arrives in 3.13."""

    def decorate(obj):
        obj.__deprecated__ = message
        obj.__doc__ = f"{obj.__doc__ or ''}\n\nDeprecated: {message}"
        return obj

    return decorate


class CapabilityProbe:
    """Fluent probe. ``check`` returns ``Self`` (PEP 673)."""

    def __init__(self) -> None:
        self.checked: list[str] = []

    def check(self, name: str) -> Self:
        self.checked.append(name)
        return self

    def result(self) -> dict[str, str]:
        return {name: describe_capability(name) for name in self.checked}


class TypedProbe[T](CapabilityProbe):
    """PEP 695 generic class syntax -- SyntaxError before Python 3.12."""

    def __init__(self, tag: T) -> None:
        super().__init__()
        self.tag = tag


def describe_capability(name: str) -> str:
    match name:
        case "tomllib" | "StrEnum" | "datetime.UTC" | "typing.Self":
            return "native"
        case "itertools.batched" | "PEP 695":
            return "native"
        case "warnings.deprecated":
            return "backfilled (native in 3.13)"
        case _:
            return "unknown"


def collect_errors(values: list[int]) -> list[str]:
    """Aggregate validation problems with PEP 654 exception groups."""
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
        "itertools.batched": True,
        "warnings.deprecated": False,
        "datetime.UTC": True,
        "config_format": CONFIG_FORMAT,
        # PEP 701 quote reuse inside an f-string, 3.12+.
        "python": f"{PY_VERSION[0]}.{PY_VERSION[1]} ({describe_capability("PEP 695")})",
        "utc": str(UTC),
    }


__all__ = [
    "PY_VERSION",
    "UTC",
    "ExternalRef",
    "MaybeStr",
    "Batch",
    "StrEnumBase",
    "load_toml",
    "CONFIG_FORMAT",
    "batched",
    "deprecated",
    "CapabilityProbe",
    "TypedProbe",
    "describe_capability",
    "collect_errors",
    "capability_report",
]
