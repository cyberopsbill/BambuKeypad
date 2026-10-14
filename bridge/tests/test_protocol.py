import json

import pytest

from bambukeypad import protocol


def test_encode_is_one_utf8_json_line():
    data = protocol.encode({"type": "keys", "layout": 1, "keys": [{"label": "‹ Back", "image": None}]})
    assert data.endswith(b"\n") and data.count(b"\n") == 1
    assert json.loads(data)["keys"][0]["label"] == "‹ Back"


def test_decode_round_trips():
    assert protocol.decode(b'{"type":"press","slot":3,"layout":12}\n') == {"type": "press", "slot": 3, "layout": 12}


@pytest.mark.parametrize("line", [b"GET / HTTP/1.1\r\n", b"[1,2]\n", b'"text"\n', b"\xff\xfe\n"])
def test_decode_rejects_anything_but_an_object(line):
    with pytest.raises(protocol.ProtocolError):
        protocol.decode(line)


def test_press_accepts_well_formed():
    assert protocol.press({"type": "press", "slot": 0, "layout": 7}) == (0, 7)


@pytest.mark.parametrize("message", [
    {"type": "keys", "slot": 0, "layout": 1},
    {"type": "press", "slot": "0", "layout": 1},
    {"type": "press", "slot": 0},
    {"type": "press", "slot": True, "layout": 1},
    {"type": "press", "slot": 1.0, "layout": 1},
])
def test_press_rejects_malformed(message):
    assert protocol.press(message) is None
