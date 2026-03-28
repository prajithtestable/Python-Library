"""Library configuration -- Python 3.10 branch.

``tomllib`` is still 3.11+, so configuration is JSON here. The loader uses
PEP 634 pattern matching to validate the parsed document.
"""

import json
import os
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "orderkit.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "library": {"name": "orderkit", "batch_size": 100, "strict": False},
    "defaults": {"channel": "retail", "tax_rate": 0.08},
}


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load Library configuration, falling back to the built-in defaults."""
    if path is None or not path.exists():
        return dict(DEFAULT_CONFIG)
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    return DEFAULT_CONFIG | loaded


def describe(config: dict[str, Any]) -> str:
    """Validate the config shape with structural pattern matching (3.10+)."""
    match config:
        case {"library": {"name": str(name), "batch_size": int(size)}} if size > 0:
            return f"{name} (batch={size})"
        case {"library": {"name": str(name)}}:
            return f"{name} (batch=default)"
        case {"library": {}}:
            return "unnamed library"
        case _:
            return "invalid configuration"


def batch_size(config: dict[str, Any] | None = None) -> int:
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
