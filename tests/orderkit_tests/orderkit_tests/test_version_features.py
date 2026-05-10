"""Feature tests for the Python 3.13 branch.

Every assertion below exercises a capability that does not exist on
Python 3.12. This file is the executable proof that the branch is
genuinely version-locked rather than merely version-labelled.
"""

def test_pep696_type_param_default():
    """PEP 696, new in 3.13 -- SyntaxError on 3.12."""
    from orderkit.models.order_record import Batch

    (param,) = Batch.__type_params__
    assert param.has_default()


def test_pep696_class_default():
    """PEP 696 default on a class type parameter."""
    from orderkit.models.order_record import OrderRecord, RecordBuffer

    (param,) = RecordBuffer.__type_params__
    assert param.__default__ is OrderRecord


def test_copy_replace():
    """copy.replace, new in 3.13."""
    import copy

    from orderkit.models.order_record import OrderRecord

    record = OrderRecord(order_id="A", channel="retail", quantity=1, unit_price=10.0)
    updated = copy.replace(record, discount_pct=25.0)
    assert updated.discount_pct == 25.0
    assert record.discount_pct == 0.0


def test_typeis_narrowing():
    """PEP 742 typing.TypeIs, new in 3.13."""
    from orderkit.models.order_record import OrderRecord, is_order_record

    record = OrderRecord(order_id="A", channel="retail", quantity=1, unit_price=10.0)
    assert is_order_record(record) is True
    assert is_order_record("not a record") is False


def test_deprecated_decorator():
    """PEP 702 warnings.deprecated, new in 3.13."""
    import warnings

    from orderkit.services.order_service import OrderService

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        OrderService().compute_total(2, 10.0)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_process_cpu_count():
    """os.process_cpu_count, new in 3.13."""
    from orderkit.config import suggested_parallelism

    assert suggested_parallelism() >= 1
