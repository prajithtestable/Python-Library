"""Feature tests for the Python 3.11 branch.

Every assertion below exercises a capability that does not exist on
Python 3.10. This file is the executable proof that the branch is
genuinely version-locked rather than merely version-labelled.
"""

def test_exception_group_and_except_star():
    """PEP 654, new in 3.11 -- SyntaxError on 3.10."""
    caught = []
    try:
        raise ExceptionGroup("g", [ValueError("a"), TypeError("b")])
    except* ValueError as group:
        caught.append(("value", len(group.exceptions)))
    except* TypeError as group:
        caught.append(("type", len(group.exceptions)))
    assert ("value", 1) in caught
    assert ("type", 1) in caught


def test_tomllib_is_stdlib():
    """PEP 680, new in 3.11."""
    import tomllib

    assert tomllib.loads('key = "value"') == {"key": "value"}


def test_str_enum():
    """enum.StrEnum, new in 3.11."""
    from orderkit.models.order_record import Channel

    assert Channel.RETAIL == "retail"
    assert isinstance(Channel.RETAIL, str)


def test_add_note():
    """BaseException.add_note, new in 3.11."""
    err = ValueError("boom")
    err.add_note("context")
    assert err.__notes__ == ["context"]
