"""Order pricing service -- Python 3.13 branch.

Adds PEP 702 ``warnings.deprecated`` and PEP 696 type-parameter defaults on
generic methods. Both are unavailable on Python 3.12.
"""

from typing import Protocol, Self, assert_never, override
from warnings import deprecated

from orderkit.models.order_record import Channel, OrderRecord

FREE_SHIPPING_THRESHOLD = 75.0
TAX_RATE = 0.08

type PricingResult = dict[str, float]


class OrderServiceProtocol(Protocol):
    """Structural contract for order pricing."""

    def calculate_total(
        self, quantity: int, unit_price: float, discount_pct: float
    ) -> float:
        ...

    def is_eligible_for_free_shipping(self, order_total: float) -> bool:
        ...


class OrderService:
    """Reference implementation of :class:`OrderServiceProtocol`."""

    def __init__(self, tax_rate: float = TAX_RATE) -> None:
        self.tax_rate = tax_rate

    def with_tax_rate(self, tax_rate: float) -> Self:
        return type(self)(tax_rate=tax_rate)

    def calculate_total(
        self, quantity: int, unit_price: float, discount_pct: float = 0.0
    ) -> float:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        subtotal = quantity * unit_price
        discount = subtotal * (discount_pct / 100.0)
        return round(subtotal - discount, 2)

    @deprecated("Use calculate_total(); removed after the 2026.2 pipeline release.")
    def compute_total(self, quantity: int, unit_price: float) -> float:
        """PEP 702 warnings.deprecated is new in Python 3.13."""
        return self.calculate_total(quantity, unit_price, 0.0)

    def is_eligible_for_free_shipping(self, order_total: float) -> bool:
        return order_total >= FREE_SHIPPING_THRESHOLD

    def resolve_processor(self, channel: str) -> str:
        normalized = channel.removeprefix("channel:").lower()
        match normalized:
            case Channel.RETAIL:
                return "retail_processor"
            case Channel.WHOLESALE:
                return "wholesale_processor"
            case Channel.MARKETPLACE | Channel.PARTNER:
                return "partner_processor"
            case _:
                return "default_processor"

    def describe_channel(self, channel: Channel) -> str:
        match channel:
            case Channel.RETAIL:
                return "direct-to-consumer"
            case Channel.WHOLESALE:
                return "bulk contract"
            case Channel.MARKETPLACE:
                return "third-party marketplace"
            case Channel.PARTNER:
                return "reseller partner"
            case _:
                assert_never(channel)

    def classify_order(self, payload: dict[str, object]) -> str:
        match payload:
            case {"channel": "wholesale", "quantity": int(qty)} if qty >= 100:
                return "bulk-wholesale"
            case {"channel": "wholesale"}:
                return "wholesale"
            case {"channel": str(channel), "quantity": int(qty)} if qty == 1:
                return f"single-{channel}"
            case {"channel": str(channel)}:
                return channel
            case _:
                return "unknown"

    def apply_tax(self, total: float, exempt: bool | None = None) -> float:
        if exempt:
            return round(total, 2)
        return round(total * (1.0 + self.tax_rate), 2)

    def summarise[T = OrderRecord](self, records: list[T]) -> dict[str, int]:
        """PEP 696 type-parameter default on a method -- 3.13+ only."""
        return {"count": len(records)}


@deprecated("Superseded by TaxExemptOrderService; scheduled for removal in 2026.3.")
class LegacyOrderService(OrderService):
    """Class-level PEP 702 deprecation, new in Python 3.13."""


class TaxExemptOrderService(OrderService):
    """Wholesale variant."""

    @override
    def apply_tax(self, total: float, exempt: bool | None = None) -> float:
        return round(total, 2)

    @override
    def is_eligible_for_free_shipping(self, order_total: float) -> bool:
        return True
