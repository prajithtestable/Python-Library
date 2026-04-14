"""Interpreter compatibility shims -- Python 3.13 branch.

Same surface as every other branch, and on 3.13 every shim collapses: this is
the only branch where nothing is backfilled. ``warnings.deprecated`` (PEP 702)
is native here, and PEP 696 type-parameter defaults are available.
"""

import sys
import tomllib
from datetime import UTC
from enum import StrEnum
from itertools import batched as _batched
from typing import ReadOnly, Self, TypedDict, TypeIs
from warnings import deprecated as _deprecated

PY_VERSION = sys.version_info[:2]

type ExternalRef = str | int | None
type MaybeStr = str | None

StrEnumBase = StrEnum


class CapabilityRecord(TypedDict):
    """``typing.ReadOnly`` for TypedDict items is new in Python 3.13 (PEP 705)."""

    name: ReadOnly[str]
    native: bool


def load_toml(handle):
    """``tomllib`` is in the standard library from 3.11 (PEP 680)."""
    return tomllib.load(handle)


CONFIG_FORMAT = "toml"


class CapabilityProbe:
    """Fluent probe. ``check`` returns ``Self`` (PEP 673)."""

    def __init__(self) -> None:
        self.checked: list[str] = []

    def check(self, name: str) -> Self:
        self.checked.append(name)
        return self

    def result(self) -> dict[str, str]:
        return {name: describe_capability(name) for name in self.checked}


# PEP 696 type-parameter defaults -- SyntaxError before Python 3.13.
type Batch[T = str] = tuple[T, ...]


class TypedProbe[T = str](CapabilityProbe):
    """PEP 696 default on a class type parameter -- 3.13+ only."""

    def __init__(self, tag: T) -> None:
        super().__init__()
        self.tag = tag


def batched[T = str](iterable: list[T], size: int) -> list[Batch[T]]:
    """PEP 696 default on a generic function -- SyntaxError before 3.13."""
    if size <= 0:
        raise ValueError("size must be positive")
    return list(_batched(iterable, size))


#: ``warnings.deprecated`` is native from 3.13; the shim is the real decorator.
deprecated = _deprecated


def is_capability_record(value: object) -> TypeIs[dict]:
    """``typing.TypeIs`` is new in Python 3.13 (PEP 742)."""
    return isinstance(value, dict)


def describe_capability(name: str) -> str:
    match name:
        case (
            "tomllib"
            | "StrEnum"
            | "datetime.UTC"
            | "typing.Self"
            | "itertools.batched"
            | "PEP 695"
            | "PEP 696"
            | "warnings.deprecated"
        ):
            return "native"
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
    """On this branch every capability is native -- nothing is backfilled."""
    return {
        "tomllib": True,
        "StrEnum": True,
        "itertools.batched": True,
        "warnings.deprecated": True,
        "datetime.UTC": True,
        "config_format": CONFIG_FORMAT,
        "python": f"{PY_VERSION[0]}.{PY_VERSION[1]} ({describe_capability("PEP 696")})",
        "utc": str(UTC),
    }


__all__ = [
    "PY_VERSION",
    "UTC",
    "ExternalRef",
    "MaybeStr",
    "Batch",
    "CapabilityRecord",
    "StrEnumBase",
    "load_toml",
    "CONFIG_FORMAT",
    "batched",
    "deprecated",
    "CapabilityProbe",
    "TypedProbe",
    "describe_capability",
    "collect_errors",
    "is_capability_record",
    "capability_report",
]
