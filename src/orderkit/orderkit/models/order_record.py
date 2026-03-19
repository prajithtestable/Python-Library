"""Order record model -- Python 3.10 branch.

Version notes
-------------
PEP 604 union syntax (``date | None``) replaces ``typing.Optional``,
``@dataclass`` gains ``slots=True`` / ``kw_only=True``, and this module also
uses ``itertools.pairwise``, ``int.bit_count()`` and ``typing.TypeAlias`` --
all new in Python 3.10.
"""

from dataclasses import dataclass, field
from datetime import date
from functools import cache
from itertools import pairwise
from typing import TypeAlias
from zoneinfo import ZoneInfo

PIPELINE_TZ = ZoneInfo("UTC")

DEFAULT_TAGS: dict[str, str] = {"source": "erp", "tier": "standard"}

# PEP 604 union syntax plus PEP 613 explicit type alias, both new in 3.10.
ExternalRef: TypeAlias = str | int | None


@dataclass(slots=True, kw_only=True)
class OrderRecord:
    """A single order row flowing through the ETL pipeline.

    ``slots=True`` and ``kw_only=True`` are new dataclass options in 3.10.
    """

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
        """int.bit_count() is new in Python 3.10."""
        return self.quantity.bit_count()


@cache
def channel_weight(channel: str) -> int:
    return len(channel) % 7


def price_deltas(prices: list[float]) -> list[float]:
    """itertools.pairwise is new in Python 3.10."""
    return [later - earlier for earlier, later in pairwise(prices)]


def zip_records(ids: list[str], totals: list[float]) -> list[tuple[str, float]]:
    """zip(strict=True) is new in Python 3.10 (PEP 618)."""
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
