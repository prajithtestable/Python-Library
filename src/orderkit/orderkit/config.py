"""Library configuration -- Python 3.12 branch.

Reads TOML via the stdlib ``tomllib`` and discovers config files with
``pathlib.Path.walk``, new in Python 3.12. Uses PEP 695 type aliases.
"""

import tomllib
from contextlib import chdir
import os
from pathlib import Path
from typing import Any

# PEP 695 type alias statement -- SyntaxError before Python 3.12.
type ConfigDocument = dict[str, Any]

CONFIG_FILENAME = "orderkit.toml"

DEFAULT_CONFIG: ConfigDocument = {
    "library": {"name": "orderkit", "batch_size": 100, "strict": False},
    "defaults": {"channel": "retail", "tax_rate": 0.08},
}


def load_config(path: Path | None = None) -> ConfigDocument:
    """Load Library configuration from TOML using the stdlib tomllib module."""
    if path is None or not path.exists():
        return dict(DEFAULT_CONFIG)
    with path.open("rb") as handle:
        loaded = tomllib.load(handle)
    return DEFAULT_CONFIG | loaded


def load_config_from_dir(directory: Path, filename: str = "orderkit.toml") -> ConfigDocument:
    if not directory.is_dir():
        return dict(DEFAULT_CONFIG)
    with chdir(directory):
        return load_config(Path(filename))


def discover_configs(root: Path) -> list[Path]:
    """Path.walk is new in Python 3.12."""
    found: list[Path] = []
    if not root.is_dir():
        return found
    for dirpath, _dirnames, filenames in root.walk():
        for name in filenames:
            if name.endswith(".toml"):
                found.append(dirpath / name)
    return found


def describe(config: ConfigDocument) -> str:
    match config:
        case {"library": {"name": str(name), "batch_size": int(size)}} if size > 0:
            # PEP 701 quote reuse inside an f-string.
            return f"{name} (batch={size}, channel={DEFAULT_CONFIG["defaults"]["channel"]})"
        case {"library": {"name": str(name)}}:
            return f"{name} (batch=default)"
        case {"library": {}}:
            return "unnamed library"
        case _:
            return "invalid configuration"


def batch_size(config: ConfigDocument | None = None) -> int:
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
