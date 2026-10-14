"""The bridge end to end over a real localhost socket, with a fake action runner."""

import asyncio
import base64
import json
import threading

import pytest

from bambukeypad import faces, icons, macos
from bambukeypad.config import DEFAULT_PORT, port
from bambukeypad.navigator import Nav, Navigator
from bambukeypad.pages import EDIT, HOME, Action, Keys, Menu, all_actions
from bambukeypad.server import Bridge


async def open_bridge():
    ran: list[str] = []
    done = threading.Event()

    def run(action: Action) -> str:
        ran.append(action.label)
        done.set()
        return "fake"

    bridge = Bridge(Navigator(HOME), run)
    server = await bridge.serve(0)
    reader, writer = await asyncio.open_connection("127.0.0.1", server.sockets[0].getsockname()[1])
    return server, reader, writer, ran, done


async def receive(reader) -> dict:
    return json.loads(await asyncio.wait_for(reader.readline(), 2))


def send(writer, message) -> None:
    writer.write((json.dumps(message) + "\n").encode())


def test_client_gets_keys_then_navigates_and_runs_actions():
    async def scenario():
        server, reader, writer, ran, done = await open_bridge()
        first = await receive(reader)
        assert first["type"] == "keys" and len(first["keys"]) == 9
        assert first["keys"][1]["label"] == "Slice"

        send(writer, {"type": "press", "slot": HOME.items.index(EDIT), "layout": first["layout"]})
        second = await receive(reader)
        assert second["layout"] != first["layout"]
        assert second["keys"][0]["label"] == "‹ Back"

        send(writer, {"type": "press", "slot": 1, "layout": first["layout"]})  # stale: ignored
        send(writer, {"type": "press", "slot": 1, "layout": second["layout"]})  # Move
        await asyncio.to_thread(done.wait, 2)
        assert ran == ["Move"]
        writer.close()
        server.close()

    asyncio.run(scenario())


def test_client_sending_non_json_is_dropped():
    async def scenario():
        server, reader, writer, _, _ = await open_bridge()
        await receive(reader)
        writer.write(b"GET / HTTP/1.1\r\n\r\n")
        assert await asyncio.wait_for(reader.read(), 2) == b""  # closed by the bridge
        server.close()

    asyncio.run(scenario())


def test_every_action_step_is_sendable_and_every_icon_exists():
    for action in all_actions():
        assert action.run, action.label
        for step in action.run:
            macos.validate(step)
        assert action.icon in icons.NAMES, action.label


def test_validate_rejects_unsafe_steps():
    with pytest.raises(ValueError):
        macos.validate(Keys("A"))  # uppercase would add an implicit Shift
    with pytest.raises(ValueError):
        macos.validate(Keys("ab"))
    with pytest.raises(ValueError):
        macos.validate(Keys("a", ("hyper",)))
    with pytest.raises(ValueError):
        macos.validate(Menu("File"))


def test_faces_mark_pages_and_nav():
    assert faces.face(EDIT)["label"] == "Edit ›"
    assert faces.face(Nav.BACK)["label"] == "‹ Back"
    assert faces.face(Nav.MORE)["label"] == "More ›"
    assert faces.face(None) == {"label": "", "image": None}
    svg = base64.b64decode(faces.face(HOME.items[0])["image"]).decode()
    assert svg.startswith("<svg") and "{accent}" not in svg


def test_port_precedence(tmp_path):
    cfg = tmp_path / "config.json"
    assert port(cfg, {}) == DEFAULT_PORT
    cfg.write_text('{"port": 50001}')
    assert port(cfg, {}) == 50001
    assert port(cfg, {"BAMBU_KEYPAD_PORT": "50002"}) == 50002
    assert port(cfg, {"BAMBU_KEYPAD_PORT": "nope"}) == 50001
    cfg.write_text('{"port": true}')
    assert port(cfg, {}) == DEFAULT_PORT
