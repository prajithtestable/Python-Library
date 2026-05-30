"""Marker module -- the ToolIntegrationMarker.cs analogue.

Its only job is to exist inside a project that depends on both the application
and the test project, guaranteeing the tools project resolves last.
"""

PROJECT_TYPE = "PyPI Library / Package Distribution"
SCENARIO = "1 - Monolithic"
MODULE_STYLE = "flat (single module)"
PYTHON_TARGET = "3.13"
HATCHLING_VERSION = "1.32.0"
TOOL_COUNT = 15
