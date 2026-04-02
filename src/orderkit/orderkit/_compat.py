"""Interpreter compatibility shims -- Python 3.9 branch.

A distribution that claims to support 3.9 through 3.13 has to present one
surface to its callers regardless of which interpreter they are on. That is
what this module is for: every name below exists on every branch, but the
implementation is whatever the branch's Python can actually do.

On 3.9 none of ``tomllib``, ``enum.StrEnum``, ``itertools.batched`` or
``warnings.deprecated`` exist, so all four are provided by hand here.
"""

import json
import sys
from datetime import timezone
from enum import Enum
from typing import Optional, Union

#: The running interpreter, as a two-tuple.
PY_VERSION = sys.version_info[:2]

#: ``datetime.UTC`` is added in 3.11; before that the alias is spelled out.
UTC = timezone.utc

#: PEP 604 (``str | None``) is 3.10+, so aliases use ``typing`` here.
ExternalRef = Union[str, int, None]
MaybeStr = Optional[str]


class StrEnumBase(str, Enum):
    """Stand-in for ``enum.StrEnum``, which arrives in Python 3.11.

    This is the documented pre-3.11 recipe: inherit from both ``str`` and
    ``Enum`` so members compare equal to their values.
    """

    def __str__(self):
        return str(self.value)


def load_toml(handle):
    """Parse a configuration document from an open binary handle.

    ``tomllib`` lands in the standard library in 3.11 (PEP 680). This branch
    ships its configuration as JSON instead, which is why
    :data:`CONFIG_FORMAT` differs across the matrix.
    """
    return json.load(handle)


CONFIG_FORMAT = "json"


def batched(iterable, size):
    """Stand-in for ``itertools.batched``, which arrives in Python 3.12."""
    if size <= 0:
        raise ValueError("size must be positive")
    items = list(iterable)
    return [tuple(items[index : index + size]) for index in range(0, len(items), size)]


def deprecated(message):
    """Stand-in for ``warnings.deprecated`` (PEP 702), which arrives in 3.13.

    Records the notice on the object and in its docstring. The real decorator
    also emits a runtime ``DeprecationWarning``; this shim deliberately does
    not, because doing so reliably on 3.9 requires wrapping every call site.
    """

    def decorate(obj):
        obj.__deprecated__ = message
        obj.__doc__ = "{0}\n\nDeprecated: {1}".format(obj.__doc__ or "", message)
        return obj

    return decorate


def capability_report():
    """Which shims are native on this interpreter and which are backfilled."""
    return {
        "tomllib": False,
        "StrEnum": False,
        "itertools.batched": False,
        "warnings.deprecated": False,
        "datetime.UTC": False,
        "config_format": CONFIG_FORMAT,
        "python": "{0}.{1}".format(*PY_VERSION),
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
    "capability_report",
]
