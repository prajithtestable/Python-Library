"""Feature tests for the Python 3.12 branch.

Every assertion below exercises a capability that does not exist on
Python 3.11. This file is the executable proof that the branch is
genuinely version-locked rather than merely version-labelled.
"""

def test_pep695_type_alias():
    """PEP 695, new in 3.12 -- SyntaxError on 3.11."""
    from orderkit.models.order_record import ExternalRef

    assert ExternalRef.__value__ is not None


def test_pep695_generic_class():
    """PEP 695 class type parameters."""
    from orderkit.models.order_record import RecordBuffer

    buffer = RecordBuffer()
    buffer.add("a").add("b")
    assert len(buffer) == 2
    assert buffer.drain() == ["a", "b"]


def test_itertools_batched():
    """itertools.batched, new in 3.12."""
    from itertools import batched

    assert list(batched([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]


def test_pep701_fstring_quote_reuse():
    """PEP 701, new in 3.12 -- SyntaxError on 3.11."""
    data = {"tier": "standard"}
    assert f"{data["tier"]}" == "standard"


def test_override_decorator():
    """PEP 698, new in 3.12."""
    from orderkit.services.order_service import TaxExemptOrderService

    assert TaxExemptOrderService().apply_tax(100.0) == 100.0
