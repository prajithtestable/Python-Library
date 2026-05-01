"""Feature tests for the Python 3.10 branch.

Every assertion below exercises a capability that does not exist on
Python 3.9. This file is the executable proof that the branch is
genuinely version-locked rather than merely version-labelled.
"""

def test_match_statement():
    """PEP 634, new in 3.10 -- SyntaxError on 3.9."""
    def classify(value):
        match value:
            case 0:
                return "zero"
            case int():
                return "int"
            case _:
                return "other"

    assert classify(0) == "zero"
    assert classify(7) == "int"
    assert classify("x") == "other"


def test_pep604_union():
    """PEP 604, new in 3.10."""
    annotation = int | None
    assert type(None) in annotation.__args__


def test_zip_strict():
    """PEP 618, new in 3.10."""
    import pytest

    with pytest.raises(ValueError):
        list(zip([1, 2], [1], strict=True))


def test_bit_count():
    """int.bit_count, new in 3.10."""
    assert (7).bit_count() == 3
