"""Library configuration -- Python 3.9 branch.

``tomllib`` arrives in the standard library in Python 3.11 (PEP 680), so this
branch reads its configuration from JSON instead.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

CONFIG_FILENAME = "orderkit.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "library": {"name": "orderkit", "batch_size": 100, "strict": False},
    "defaults": {"channel": "retail", "tax_rate": 0.08},
}


def load_config(path: Optional[Path] = None) -> dict[str, Any]:
    """Load Library configuration, falling back to the built-in defaults."""
    if path is None or not path.exists():
        return dict(DEFAULT_CONFIG)
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    # PEP 584 dict union, new in 3.9.
    return DEFAULT_CONFIG | loaded


def batch_size(config: Optional[dict[str, Any]] = None) -> int:
    resolved = config if config is not None else DEFAULT_CONFIG
    return int(resolved.get("library", {}).get("batch_size", 100))


# ---------------------------------------------------------------- CLI wiring

def config_path() -> Path:
    """Where the library looks for optional user configuration."""
    override = os.environ.get("ORDERKIT_CONFIG")
    if override:
        return Path(override)
    return Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "orderkit" / CONFIG_FILENAME


def default_channel() -> str:
    """The channel used when a caller does not supply one."""
    return DEFAULT_CONFIG["defaults"]["channel"]


def strict_mode() -> bool:
    """Whether the library should raise rather than collect batch failures."""
    if os.environ.get("ORDERKIT_STRICT"):
        return True
    return bool(DEFAULT_CONFIG["library"]["strict"])
