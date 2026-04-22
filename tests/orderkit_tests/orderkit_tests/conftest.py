"""Pytest configuration.

Adds the application package to sys.path so the suite runs without an
editable install, which keeps the tool runners in tools/ independent of how
the workspace was provisioned.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "orderkit"))
