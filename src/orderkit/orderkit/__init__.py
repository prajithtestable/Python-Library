"""orderkit -- order pricing primitives for retail and wholesale channels.

A distributable library. Everything importable from this top-level namespace
is public and covered by the compatibility policy; anything reached through a
private submodule is not.

Scenario: 1 - Monolithic
Module:   flat (single module)
Branch:   py3.11  (targets CPython 3.11, verified against 3.11.13)
"""

from orderkit.api import (
    BatchPricer,
    ConfigurationError,
    OrderKitError,
    OrderRecord,
    OrderService,
    PricingError,
    UnsupportedChannelError,
    ValidationError,
    batched,
    load_toml,
    price_batch,
    price_order,
    supported_channels,
    to_payload,
)

__version__ = "1.0.0"
PYTHON_TARGET = "3.11"
HATCHLING_VERSION = "1.32.0"

#: The public surface. Anything absent from this list is private.
__all__ = [
    "__version__",
    "price_order",
    "price_batch",
    "supported_channels",
    "OrderRecord",
    "OrderService",
    "BatchPricer",
    "to_payload",
    "OrderKitError",
    "ValidationError",
    "PricingError",
    "ConfigurationError",
    "UnsupportedChannelError",
    "batched",
    "load_toml",
]
