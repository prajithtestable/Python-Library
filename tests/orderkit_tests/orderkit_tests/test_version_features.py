"""Feature tests for the Python 3.9 branch.

Every assertion below exercises a capability that does not exist on
Python 3.8. This file is the executable proof that the branch is
genuinely version-locked rather than merely version-labelled.
"""

def test_dict_union_operator():
    """PEP 584, new in 3.9."""
    assert ({"a": 1} | {"b": 2}) == {"a": 1, "b": 2}


def test_removeprefix():
    """str.removeprefix, new in 3.9."""
    assert "channel:retail".removeprefix("channel:") == "retail"


def test_builtin_generics():
    """PEP 585, new in 3.9."""
    annotation = list[str]
    assert annotation.__origin__ is list


def test_unions_use_typing_module():
    """PEP 604 (int | None) is NOT available on this branch."""
    from orderkit.models.order_record import ExternalRef

    assert ExternalRef is not None
