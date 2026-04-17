"""Public exception hierarchy.

A distributable library must give its callers something stable to catch. Every
error this package raises derives from :class:`OrderKitError`, so downstream
code can catch one base class and never see a bare ``ValueError`` leak out of
an internal helper.

This module is part of the public API and is covered by the compatibility
policy in the README. 3.9-compatible syntax; identical on every branch.
"""


class OrderKitError(Exception):
    """Base class for every error raised by orderkit."""


class ValidationError(OrderKitError, ValueError):
    """A caller supplied a value outside its documented domain.

    Derives from :class:`ValueError` as well, so callers written against the
    pre-1.0 API that caught ``ValueError`` keep working.
    """

    def __init__(self, message, field=None, value=None):
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self):
        base = super().__str__()
        if self.field is None:
            return base
        return "{0} (field={1!r}, value={2!r})".format(base, self.field, self.value)


class PricingError(OrderKitError):
    """Pricing could not be completed for a record."""

    def __init__(self, message, order_id=None):
        super().__init__(message)
        self.order_id = order_id


class ConfigurationError(OrderKitError):
    """The supplied configuration document is malformed."""


class UnsupportedChannelError(ValidationError):
    """The requested sales channel has no registered processor."""


__all__ = [
    "OrderKitError",
    "ValidationError",
    "PricingError",
    "ConfigurationError",
    "UnsupportedChannelError",
]
