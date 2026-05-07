"""Unit tests for the order pricing service.

Primary coverage target for SlipCover, the sys.settrace driver and
diff-cover, and the test suite whose strength mutmut measures.
"""

import pytest

from orderkit.services.order_service import OrderService
from orderkit.services.retail_order_processor import process_retail_order
from orderkit.services.wholesale_order_processor import process_wholesale_order


@pytest.fixture()
def service():
    return OrderService()


def test_calculate_total_applies_discount(service):
    assert service.calculate_total(2, 100.0, 10.0) == 180.0


def test_calculate_total_without_discount(service):
    assert service.calculate_total(3, 10.0) == 30.0


def test_calculate_total_rejects_zero_quantity(service):
    with pytest.raises(ValueError):
        service.calculate_total(0, 10.0, 0.0)


def test_calculate_total_rejects_negative_quantity(service):
    with pytest.raises(ValueError):
        service.calculate_total(-1, 10.0, 0.0)


@pytest.mark.parametrize(
    ("total", "expected"),
    [(49.99, False), (50.0, True), (100.0, True), (0.0, False)],
)
def test_free_shipping_threshold(service, total, expected):
    assert service.is_eligible_for_free_shipping(total) is expected


@pytest.mark.parametrize(
    ("channel", "expected"),
    [
        ("retail", "retail_processor"),
        ("channel:retail", "retail_processor"),
        ("wholesale", "wholesale_processor"),
        ("marketplace", "partner_processor"),
        ("partner", "partner_processor"),
        ("unknown", "default_processor"),
    ],
)
def test_resolve_processor(service, channel, expected):
    assert service.resolve_processor(channel) == expected


def test_retail_and_wholesale_agree_on_price():
    """The two processors are deliberate duplicates -- symilar fixture."""
    retail = process_retail_order(4, 25.0, 10.0)
    wholesale = process_wholesale_order(4, 25.0, 10.0)
    assert retail == wholesale


def test_processor_rejects_out_of_range_discount():
    with pytest.raises(ValueError):
        process_retail_order(1, 10.0, 99.0)
