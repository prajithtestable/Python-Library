"""Order record model -- Python 3.9 branch.

Version notes
-------------
This branch predates PEP 604, so unions are spelled with ``typing.Optional``
and ``typing.Union``.  It does exercise features that are new in 3.9:
PEP 585 builtin generics, the PEP 584 dict union operator, ``functools.cache``,
``str.removeprefix`` / ``str.removesuffix`` and ``zoneinfo``.
"""

from dataclasses import dataclass, field
from datetime import date
from functools import cache
from typing import Optional, Union
from zoneinfo import ZoneInfo

# zoneinfo is new in Python 3.9 (PEP 615).
PIPELINE_TZ = ZoneInfo("UTC")

# PEP 585: builtin generics in annotations, new in Python 3.9.
DEFAULT_TAGS: dict[str, str] = {"source": "erp", "tier": "standard"}

# PEP 604 (str | int | None) is not available on 3.9.
ExternalRef = Union[str, int, None]


@dataclass
class OrderRecord:
    """A single order row flowing through the ETL pipeline."""

    order_id: str
    channel: str
    quantity: int
    unit_price: float
    discount_pct: float = 0.0
    placed_on: Optional[date] = None
    external_ref: ExternalRef = None
    tags: list[str] = field(default_factory=list)

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

    def normalized_channel(self) -> str:
        """str.removeprefix / str.removesuffix are new in Python 3.9."""
        return self.channel.removeprefix("channel:").removesuffix("/v1").lower()

    def merged_tags(self, overrides: dict[str, str]) -> dict[str, str]:
        """PEP 584 dict union operator, new in Python 3.9."""
        return DEFAULT_TAGS | overrides


@cache
def channel_weight(channel: str) -> int:
    """functools.cache is new in Python 3.9."""
    return len(channel) % 7


def to_payload(record: OrderRecord) -> dict[str, object]:
    return {
        "order_id": record.order_id,
        "channel": record.normalized_channel(),
        "quantity": record.quantity,
        "unit_price": record.unit_price,
        "subtotal": record.subtotal,
        "weight": channel_weight(record.channel),
    }
