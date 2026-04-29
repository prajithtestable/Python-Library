"""Public API and packaging contract tests.

For a distributable library the contract IS the deliverable, so these tests
assert on the surface a consumer sees: what is importable from the top-level
namespace, what ``__all__`` promises, that the exception hierarchy is catchable
from one base class, and that the PEP 561 marker is present.

They are the coverage surface SlipCover, the settrace driver and mutmut
measure, alongside test_order_service.py.
"""

import pathlib

import pytest

import orderkit
from orderkit import (
    OrderKitError,
    UnsupportedChannelError,
    ValidationError,
    price_batch,
    price_order,
    supported_channels,
)


def test_version_is_exposed():
    assert orderkit.__version__ == "1.0.0"


def test_all_is_declared_and_complete():
    assert "__all__" in dir(orderkit)
    for name in orderkit.__all__:
        assert hasattr(orderkit, name), f"__all__ promises {name} but it is missing"


def test_public_names_are_importable_from_the_top_level():
    for name in ("price_order", "price_batch", "OrderRecord", "ValidationError"):
        assert name in orderkit.__all__


def test_py_typed_marker_ships_with_the_package():
    """PEP 561: without this file type checkers ignore the inline annotations."""
    marker = pathlib.Path(orderkit.__file__).parent / "py.typed"
    assert marker.is_file()


def test_price_order_retail():
    assert price_order(2, 100.0, 10.0, "retail") > 0


def test_price_order_wholesale_matches_retail():
    """The two processors are deliberate duplicates -- symilar fixture."""
    assert price_order(4, 25.0, 10.0, "retail") == price_order(4, 25.0, 10.0, "wholesale")


@pytest.mark.parametrize(
    ("quantity", "unit_price", "discount"),
    [(0, 10.0, 0.0), (-1, 10.0, 0.0), (1, -5.0, 0.0), (1, 10.0, 99.0), (1, 10.0, -1.0)],
)
def test_price_order_rejects_bad_input(quantity, unit_price, discount):
    with pytest.raises(ValidationError):
        price_order(quantity, unit_price, discount)


def test_validation_error_carries_field_and_value():
    with pytest.raises(ValidationError) as info:
        price_order(0, 10.0)
    assert info.value.field == "quantity"
    assert info.value.value == 0


def test_unknown_channel_raises():
    with pytest.raises(UnsupportedChannelError):
        price_order(1, 10.0, 0.0, "carrier-pigeon")


def test_every_public_error_is_catchable_as_one_base_class():
    for call in (
        lambda: price_order(0, 10.0),
        lambda: price_order(1, 10.0, 0.0, "nope"),
    ):
        with pytest.raises(OrderKitError):
            call()


def test_validation_error_is_also_a_value_error():
    """Back-compatibility: callers written against the pre-1.0 API caught ValueError."""
    with pytest.raises(ValueError):
        price_order(0, 10.0)


def test_supported_channels_is_a_stable_tuple():
    channels = supported_channels()
    assert isinstance(channels, tuple)
    assert "retail" in channels and "wholesale" in channels


def test_price_batch_returns_priced_and_failures():
    rows = [
        {"order_id": "A", "channel": "retail", "quantity": 2, "unit_price": 10.0},
        {"order_id": "B", "channel": "wholesale", "quantity": 3, "unit_price": 5.0},
    ]
    result = price_batch(rows)
    assert len(result["priced"]) == 2
    assert result["failures"] == []


def test_price_batch_collects_failures_without_raising():
    rows = [
        {"order_id": "A", "channel": "retail", "quantity": 2, "unit_price": 10.0},
        {"order_id": "B", "channel": "retail", "quantity": 0, "unit_price": 10.0},
    ]
    result = price_batch(rows)
    assert len(result["priced"]) == 1
    assert len(result["failures"]) == 1


def test_compat_surface_is_uniform_across_branches():
    """Every branch must expose the same shim names, however they are built."""
    from orderkit import _compat

    for name in (
        "PY_VERSION", "UTC", "StrEnumBase", "load_toml",
        "CONFIG_FORMAT", "batched", "deprecated", "capability_report",
    ):
        assert hasattr(_compat, name), f"_compat is missing {name}"


def test_compat_batched_behaves_the_same_everywhere():
    from orderkit import _compat

    assert _compat.batched([1, 2, 3, 4, 5], 2) == [(1, 2), (3, 4), (5,)]
    with pytest.raises(ValueError):
        _compat.batched([1], 0)


def test_capability_report_matches_the_branch():
    from orderkit import _compat

    report = _compat.capability_report()
    major, minor = _compat.PY_VERSION
    assert report["tomllib"] is (minor >= 11)
    assert report["itertools.batched"] is (minor >= 12)
    assert report["warnings.deprecated"] is (minor >= 13)
    assert report["config_format"] == ("toml" if minor >= 11 else "json")
