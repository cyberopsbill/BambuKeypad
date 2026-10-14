"""Settings shared with the plugin, which reads the same file (plugin/src/protocol.ts)."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_PORT = 47833
CONFIG_PATH = Path.home() / "Library" / "Application Support" / "BambuKeypad" / "config.json"
LOG_PATH = Path.home() / "Library" / "Logs" / "BambuKeypad-bridge.log"


def port(path: Path = CONFIG_PATH, environ: dict[str, str] | None = None) -> int:
    """BAMBU_KEYPAD_PORT, else the config file's "port", else the default.

    The environment variable only reaches the bridge, so set the port in the
    config file when both sides need to move.
    """
    environ = os.environ if environ is None else environ
    for candidate in (environ.get("BAMBU_KEYPAD_PORT"), _from_file(path)):
        try:
            value = int(candidate) if candidate is not None else None
        except (TypeError, ValueError):
            value = None
        if value is not None and 0 < value < 65536:
            return value
    return DEFAULT_PORT


def _from_file(path: Path):
    try:
        value = json.loads(path.read_text("utf-8")).get("port")
    except (OSError, ValueError, AttributeError):
        return None
    return value if isinstance(value, int) and not isinstance(value, bool) else None
