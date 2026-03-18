"""Order pricing service -- Python 3.9 branch.

This module is the primary mutation-testing (mutmut) and coverage
(SlipCover / settrace driver) target for the repository.
"""

from typing import Optional, Protocol

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
        """Route an order to a processor.

        No structural pattern matching on this branch -- PEP 634 lands in 3.10,
        so this is an if/elif ladder.
        """
        normalized = channel.removeprefix("channel:").lower()
        if normalized == "retail":
            return "retail_processor"
        if normalized == "wholesale":
            return "wholesale_processor"
        if normalized in ("marketplace", "partner"):
            return "partner_processor"
        return "default_processor"

    def apply_tax(self, total: float, exempt: Optional[bool] = None) -> float:
        if exempt:
            return round(total, 2)
        return round(total * (1.0 + TAX_RATE), 2)
