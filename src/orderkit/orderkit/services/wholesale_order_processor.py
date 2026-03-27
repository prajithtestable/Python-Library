"""Wholesale order processing strategy.

DUPLICATION FIXTURE
-------------------
This module is deliberately near-identical to
``retail_order_processor.py``. The pair is the copy/paste target for
symilar (pylint) and mirrors the ``RetailOrderProcessor`` /
``WholesaleOrderProcessor`` pair in the C# reference repository.

It is written in Python 3.9-compatible syntax and kept byte-comparable on
every branch so duplication results are directly comparable across the
version matrix.
"""

TAX_RATE = 0.08
HANDLING_FEE = 0.95
MIN_QUANTITY = 1
MAX_DISCOUNT_PCT = 40.0


def validate_order(quantity, unit_price, discount_pct):
    """Reject structurally invalid orders before pricing."""
    if quantity < MIN_QUANTITY:
        raise ValueError("quantity must be positive")
    if unit_price < 0:
        raise ValueError("unit_price must not be negative")
    if discount_pct < 0 or discount_pct > MAX_DISCOUNT_PCT:
        raise ValueError("discount_pct out of range")
    return True


def process_wholesale_order(quantity, unit_price, discount_pct=0.0):
    """Price a single wholesale order line."""
    validate_order(quantity, unit_price, discount_pct)
    subtotal = quantity * unit_price
    discount = subtotal * (discount_pct / 100.0)
    total = subtotal - discount
    tax = total * TAX_RATE
    total = total + tax
    total = total + HANDLING_FEE
    return round(total, 2)
