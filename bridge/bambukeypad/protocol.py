"""Messages between the bridge and the Logi plugin. docs/protocol.md is the
specification; plugin/src/protocol.ts is the other side."""

from __future__ import annotations

import json


class ProtocolError(ValueError):
    """A line that isn't a JSON object. The bridge drops the client that sent it."""


def encode(message: dict) -> bytes:
    return (json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def keys_message(layout: int, keys: list[dict]) -> dict:
    return {"type": "keys", "layout": layout, "keys": keys}


def decode(line: bytes) -> dict:
    try:
        message = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtocolError(f"not JSON: {error}") from None
    if not isinstance(message, dict):
        raise ProtocolError("not a JSON object")
    return message


def press(message: dict) -> tuple[int, int] | None:
    """(slot, layout) for a well-formed press message, otherwise None."""
    slot, layout = message.get("slot"), message.get("layout")
    if message.get("type") != "press" or type(slot) is not int or type(layout) is not int:
        return None
    return slot, layout
