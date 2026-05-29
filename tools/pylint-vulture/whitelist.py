"""Vulture whitelist.

Names referenced only by frameworks, and therefore invisible to static
analysis. Listing them here keeps vulture's real findings -- the planted dead
code in analysis/dead_code.py -- from being buried under framework noise.

This file is never imported at runtime.
"""

# ruff: noqa
# pylint: disable=all


class _AirflowOperatorAttributes:
    template_fields = None
    execute = None
    log = None


class _PytestHooks:
    conftest = None
