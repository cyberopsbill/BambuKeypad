"""The keystroke gate: telling Bambu Studio's tabs apart and refusing unsafe keys.

The texts are trimmed from Accessibility snapshots of Bambu Studio 02.09.01.70.
"""

import pytest

from bambukeypad import macos
from bambukeypad.pages import HOME, Action, Keys, Menu, all_actions
from bambukeypad.studio import UNKNOWN, Studio, Tab, bare, classify, refusal

PREPARE = ["Printer", "Nozzle", "Diameter", "Flow", "Project Filaments", "Filament",
           "Add Mixed Filament", "Process", "Advanced", "top_end_cap_v4"]
DEVICE = ["Camera", "Printing Progress", "0.2mm layer, 2 walls, 8% infill", "2h8min35s",
          "Layer: 1/110", "Printing", "Control", "Bed", "Extruder"]
CALIBRATION = ["Flow Dynamics Calibration", "Wiki", "About this calibration", "SCHUBOX"]

PLATER = Studio(front=True, tab=Tab.PLATER, typing=False)
TYPING = Studio(front=True, tab=Tab.PLATER, typing=True)


def test_tabs_are_told_apart_by_their_texts():
    assert classify(True, PREPARE, "AXWindow") == PLATER
    assert classify(True, DEVICE, "AXWindow").tab is Tab.DEVICE
    assert classify(True, CALIBRATION, "AXWindow").tab is Tab.OTHER
    assert classify(True, [], None).tab is Tab.OTHER  # Project with no info shows no texts


def test_a_tab_needs_every_marker():
    assert classify(True, ["Printer", "Process"], None).tab is Tab.OTHER  # e.g. a dialog
    assert classify(True, ["Camera"], None).tab is Tab.OTHER


def test_text_field_focus_is_typing():
    assert classify(True, PREPARE, "AXTextField").typing
    assert not classify(True, PREPARE, "AXWindow").typing


@pytest.mark.parametrize("key", [Keys("a"), Keys("f"), Keys("m"), Keys("z"), Keys("r", ("shift",))])
def test_bare_keys_go_only_to_the_plater_canvas(key):
    assert bare(key)
    assert refusal(key, PLATER) is None
    assert refusal(key, TYPING) == "typing"
    assert refusal(key, Studio(True, Tab.DEVICE, False)) == "tab device"
    assert refusal(key, Studio(True, Tab.OTHER, False)) == "tab other"
    assert refusal(key, Studio(False, Tab.PLATER, False)) == "not-front"
    assert refusal(key, UNKNOWN) == "not-front"


def test_command_keys_work_while_typing_but_never_off_the_plater():
    slice_ = Keys("r", ("command",))
    assert not bare(slice_)
    assert refusal(slice_, TYPING) is None
    assert refusal(slice_, Studio(True, Tab.DEVICE, False)) == "tab device"


def test_every_bare_key_in_the_pages_is_gated():
    bare_keys = {step.key for action in all_actions(HOME) for step in action.run
                 if isinstance(step, Keys) and bare(step)}
    assert bare_keys == {"a", "c", "f", "m", "r", "s", "z"}


def test_parse_state_reads_the_script_output():
    out = "front=true\nfocus=AXTextField\n" + "\n".join(f"text={t}" for t in PREPARE) + "\nsecond line of a text"
    assert macos.parse_state(out) == TYPING
    assert macos.parse_state("") == UNKNOWN


class FakeMac:
    def __init__(self, monkeypatch, state: Studio, menu: str = "ok"):
        self.sent: list[Keys] = []
        self.reads = 0
        self.menu = menu

        def read_state():
            self.reads += 1
            return state

        def send_keys(keys):
            self.sent.append(keys)
            return "ok"

        monkeypatch.setattr(macos, "read_state", read_state)
        monkeypatch.setattr(macos, "send_keys", send_keys)
        monkeypatch.setattr(macos, "menu_status", lambda step, click=False: self.menu)


def test_run_sends_a_bare_key_on_the_canvas(monkeypatch):
    mac = FakeMac(monkeypatch, PLATER)
    assert macos.run(Action("Arrange", "arrange", Keys("a"))) == "keys a"
    assert mac.sent == [Keys("a")]


@pytest.mark.parametrize("state", [TYPING, Studio(True, Tab.DEVICE, False), UNKNOWN])
def test_run_sends_nothing_when_refused(monkeypatch, state):
    mac = FakeMac(monkeypatch, state)
    with pytest.raises(macos.ActionError, match="nothing worked"):
        macos.run(Action("Lay Flat", "layflat", Keys("f")))
    assert mac.sent == []


def test_run_clicks_menus_without_reading_state(monkeypatch):
    mac = FakeMac(monkeypatch, UNKNOWN)
    assert macos.run(Action("Fit", "fit", Menu("View", "Fit Camera"), Keys("z"))) == "menu View > Fit Camera"
    assert mac.reads == 0


def test_run_falls_back_to_a_gated_key_when_the_menu_is_disabled(monkeypatch):
    mac = FakeMac(monkeypatch, TYPING, menu="disabled")
    with pytest.raises(macos.ActionError, match=r"menu disabled, keys typing"):
        macos.run(Action("Fit", "fit", Menu("View", "Fit Camera"), Keys("z")))
    assert mac.sent == []
    mac = FakeMac(monkeypatch, PLATER, menu="disabled")
    assert macos.run(Action("Fit", "fit", Menu("View", "Fit Camera"), Keys("z"))) == "keys z"
