"""Order record model -- Python 3.11 branch.

Version notes
-------------
Adds ``typing.Self`` (PEP 673), ``enum.StrEnum`` and the ``datetime.UTC``
alias, all new in Python 3.11, on top of everything the 3.10 branch uses.
"""

from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from enum import StrEnum
from functools import cache
from itertools import pairwise
from typing import Self, TypeAlias
from zoneinfo import ZoneInfo

PIPELINE_TZ = ZoneInfo("UTC")

DEFAULT_TAGS: dict[str, str] = {"source": "erp", "tier": "standard"}

ExternalRef: TypeAlias = str | int | None


class Channel(StrEnum):
    """enum.StrEnum is new in Python 3.11."""

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
        """PEP 673 ``Self`` return type, new in Python 3.11."""
        return replace(self, discount_pct=pct)

    def stamped(self) -> Self:
        """datetime.UTC is a new alias in Python 3.11."""
        return replace(self, placed_on=datetime.now(UTC).date())


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
    }
