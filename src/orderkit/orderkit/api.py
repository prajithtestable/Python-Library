"""The stable public API surface.

Everything a consumer of this distribution is meant to touch is re-exported
here and, in turn, from ``orderkit/__init__.py``. Anything not named in
``__all__`` is private and may change without a major version bump.

Keeping the facade in its own module rather than in ``__init__.py`` means the
package's import graph stays acyclic and inspectable: ``__init__`` imports
``api``, ``api`` imports the implementation modules, and no implementation
module imports either. Static call-graph tools should be able to follow that.

3.9-compatible syntax; identical on every branch. The version-specific work
lives in ``_compat.py``.
"""

from orderkit._compat import PY_VERSION, batched, load_toml
from orderkit.exceptions import (
    ConfigurationError,
    OrderKitError,
    PricingError,
    UnsupportedChannelError,
    ValidationError,
)
from orderkit.models.order_record import OrderRecord, to_payload
from orderkit.pricing import BatchPricer
from orderkit.services.order_service import OrderService
from orderkit.services.retail_order_processor import process_retail_order
from orderkit.services.wholesale_order_processor import process_wholesale_order


def price_order(quantity, unit_price, discount_pct=0.0, channel="retail"):
    """Price a single order line.

    The one-call entry point most consumers use.

    :param quantity: units ordered; must be positive.
    :param unit_price: price per unit; must not be negative.
    :param discount_pct: percentage discount, 0 to 40 inclusive.
    :param channel: ``retail``, ``wholesale``, ``marketplace`` or ``partner``.
    :returns: the total including tax and handling, rounded to 2 places.
    :raises ValidationError: if any argument is outside its domain.
    :raises UnsupportedChannelError: if the channel has no processor.
    """
    if quantity is None or quantity <= 0:
        raise ValidationError("quantity must be positive", "quantity", quantity)
    if unit_price is None or unit_price < 0:
        raise ValidationError("unit_price must not be negative", "unit_price", unit_price)
    if discount_pct is None or discount_pct < 0 or discount_pct > 40.0:
        raise ValidationError(
            "discount_pct must be between 0 and 40", "discount_pct", discount_pct
        )

    service = OrderService()
    target = service.resolve_processor(channel)
    if target == "default_processor":
        raise UnsupportedChannelError(
            "no processor registered for this channel", "channel", channel
        )

    try:
        if target == "wholesale_processor":
            return process_wholesale_order(quantity, unit_price, discount_pct)
        return process_retail_order(quantity, unit_price, discount_pct)
    except ValueError as exc:
        raise PricingError(str(exc)) from exc


def price_batch(rows, batch_size=50, fail_fast=False):
    """Price many order rows at once.

    :param rows: an iterable of mappings with ``order_id``, ``channel``,
        ``quantity``, ``unit_price`` and optionally ``discount_pct``.
    :returns: a mapping with ``priced`` and ``failures`` lists.
    """
    pricer = BatchPricer()
    records = list(pricer.records_from(rows))
    return pricer.price_batch(records, batch_size=batch_size, fail_fast=fail_fast)


def supported_channels():
    """The channels this release knows how to route."""
    return ("retail", "wholesale", "marketplace", "partner")


__all__ = [
    # Entry points
    "price_order",
    "price_batch",
    "supported_channels",
    # Types
    "OrderRecord",
    "OrderService",
    "BatchPricer",
    "to_payload",
    # Exceptions
    "OrderKitError",
    "ValidationError",
    "PricingError",
    "ConfigurationError",
    "UnsupportedChannelError",
    # Compatibility helpers, exported because downstream code that supports the
    # same interpreter range finds them useful.
    "PY_VERSION",
    "batched",
    "load_toml",
]
