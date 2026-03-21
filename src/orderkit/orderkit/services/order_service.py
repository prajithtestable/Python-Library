"""Order pricing service -- Python 3.10 branch.

``resolve_processor`` uses PEP 634 structural pattern matching. ``match`` /
``case`` is a hard SyntaxError on Python 3.9, which is what makes this branch
genuinely version-locked.
"""

from typing import Protocol

FREE_SHIPPING_THRESHOLD = 75.0
TAX_RATE = 0.08


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

    def calculate_total(
        self, quantity: int, unit_price: float, discount_pct: float = 0.0
    ) -> float:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        subtotal = quantity * unit_price
        discount = subtotal * (discount_pct / 100.0)
        return round(subtotal - discount, 2)

    def is_eligible_for_free_shipping(self, order_total: float) -> bool:
        return order_total >= FREE_SHIPPING_THRESHOLD

    def resolve_processor(self, channel: str) -> str:
        """Route an order to a processor using PEP 634 pattern matching."""
        normalized = channel.removeprefix("channel:").lower()
        match normalized:
            case "retail":
                return "retail_processor"
            case "wholesale":
                return "wholesale_processor"
            case "marketplace" | "partner":
                return "partner_processor"
            case _:
                return "default_processor"

    def classify_order(self, payload: dict[str, object]) -> str:
        """Mapping patterns with capture and guard, also PEP 634."""
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
        return round(total * (1.0 + TAX_RATE), 2)
