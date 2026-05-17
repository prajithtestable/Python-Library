"""Lint fixture -- deliberate style and correctness violations.

Target for Ruff and for pylint (via the pylint + vulture pairing).
Mirrors ``Analysis/LintViolations.cs`` in the C# reference repository.

Every violation below is intentional. Do not "fix" this file.
Expected findings include: non-PEP8 module/class/function naming, an unused
import, an unused local, a mutable default argument, a bare except, a
comparison to None with ==, a lambda bound to a name, and shadowing of a
builtin.
"""

# ruff: noqa
# pylint: disable=all

import os  # unused import
import sys  # unused import


class calculator:  # invalid-name: class should be CapWords
    """Badly named class with badly named methods."""

    def addNumbers(self, a, b):  # invalid-name: should be snake_case
        temp = 0  # unused local variable
        return a + b

    def Divide(self, a, b):  # invalid-name
        try:
            return a / b
        except:  # bare-except
            return None

    def collect(self, items=[]):  # dangerous-default-value: mutable default
        items.append(1)
        return items


def CheckValue(value):  # invalid-name
    if value == None:  # singleton-comparison: should be 'is None'
        return False
    if value != True:  # singleton-comparison
        return True
    return False


# lambda assigned to a name instead of using def
double = lambda x: x * 2

# shadowing a builtin
list = [1, 2, 3]
type = "order"


def unusedHelper(a, b, c, d, e, f, g, h):  # too-many-arguments, invalid-name
    """Never called anywhere in the codebase."""
    result = a + b + c + d + e + f + g + h
    unused_total = result * 2  # unused local
    return result


def inconsistent_returns(flag):
    """Some paths return a value, others fall through implicitly."""
    if flag:
        return "yes"
    # implicit None return on the else path
