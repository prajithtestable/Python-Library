"""Order record model -- Python 3.12 branch.

Version notes
-------------
Uses PEP 695 type-parameter syntax (``type X = ...``, ``class C[T]``,
``def f[T]()``), which is a hard SyntaxError on Python 3.11. Also exercises
``itertools.batched`` and the ``calendar.Month`` enum, both new in 3.12.
"""

import calendar
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from enum import StrEnum
from functools import cache
from itertools import batched, pairwise
from typing import Self
from zoneinfo import ZoneInfo

PIPELINE_TZ = ZoneInfo("UTC")

DEFAULT_TAGS: dict[str, str] = {"source": "erp", "tier": "standard"}

# PEP 695 type alias statement -- SyntaxError before Python 3.12.
type ExternalRef = str | int | None
type Batch[T] = tuple[T, ...]

# calendar.Month is new in Python 3.12.
FISCAL_YEAR_START = calendar.Month.FEBRUARY


class Channel(StrEnum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    MARKETPLACE = "marketplace"
    PARTNER = "partner"


@dataclass(slots=True, kw_only=True)
class OrderRecord:
    """A single order row flowing through the ETL pipeline."""

    order_id: str
    channel: str
    quantity: int
    unit_price: float
    discount_pct: float = 0.0
    placed_on: date | None = None
    external_ref: ExternalRef = None
    tags: list[str] = field(default_factory=list)

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

    def normalized_channel(self) -> str:
        return self.channel.removeprefix("channel:").removesuffix("/v1").lower()

    def merged_tags(self, overrides: dict[str, str]) -> dict[str, str]:
        return DEFAULT_TAGS | overrides

    def quantity_bits(self) -> int:
        return self.quantity.bit_count()

    def with_discount(self, pct: float) -> Self:
        return replace(self, discount_pct=pct)

    def stamped(self) -> Self:
        return replace(self, placed_on=datetime.now(UTC).date())

    def summary(self) -> str:
        """PEP 701 -- quote reuse inside an f-string, SyntaxError before 3.12."""
        return f"{self.order_id}: {DEFAULT_TAGS["tier"]} / {self.normalized_channel()}"


class RecordBuffer[T]:
    """PEP 695 generic class syntax -- SyntaxError before Python 3.12."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def add(self, item: T) -> Self:
        self._items.append(item)
        return self

    def drain(self) -> list[T]:
        items, self._items = self._items, []
        return items

    def __len__(self) -> int:
        return len(self._items)


def batched_payloads[T](items: list[T], size: int) -> list[Batch[T]]:
    """PEP 695 generic function syntax plus itertools.batched (both 3.12+)."""
    if size <= 0:
        raise ValueError("size must be positive")
    return list(batched(items, size))


@cache
def channel_weight(channel: str) -> int:
    return len(channel) % 7


def price_deltas(prices: list[float]) -> list[float]:
    return [later - earlier for earlier, later in pairwise(prices)]


def zip_records(ids: list[str], totals: list[float]) -> list[tuple[str, float]]:
    return list(zip(ids, totals, strict=True))


def to_payload(record: OrderRecord) -> dict[str, object]:
    return {
        "order_id": record.order_id,
        "channel": record.normalized_channel(),
        "quantity": record.quantity,
        "unit_price": record.unit_price,
        "subtotal": record.subtotal,
        "weight": channel_weight(record.channel),
        "quantity_bits": record.quantity_bits(),
        "summary": record.summary(),
    }
