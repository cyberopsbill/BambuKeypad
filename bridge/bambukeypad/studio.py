"""What Bambu Studio is showing, and whether a keystroke may be sent into it.

`macos.read_state` reads the front window through Accessibility and hands the
raw facts to `classify`. Everything here is pure, so the rules are tested
without macOS.

What Bambu Studio 02.09.01.70 exposes (docs/shortcuts.md has the detail):

- The top tabs aren't in the Accessibility tree, but only the visible tab's
  controls are, so the window's static texts tell the tabs apart.
- Prepare and Preview share the settings sidebar, headed Printer, Project
  Filaments and Process. They can't be told apart from each other.
- Device shows Printing Progress, Camera and Control.
- The 3D view exposes nothing, so neither the selection nor slicing is visible.
- A focused setting field reads as AXTextField; the 3D view leaves the window focused.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from .pages import Keys


class Tab(Enum):
    PLATER = "prepare/preview"
    DEVICE = "device"
    OTHER = "other"  # Project, Calibration, a dialog, or nothing readable


PLATER_MARKERS = frozenset({"Printer", "Project Filaments", "Process"})
DEVICE_MARKERS = frozenset({"Printing Progress", "Camera", "Control"})
TEXT_ROLES = frozenset({"AXTextField", "AXTextArea", "AXComboBox", "AXSearchField"})


@dataclass(frozen=True)
class Studio:
    front: bool
    tab: Tab
    typing: bool  # a text field has keyboard focus

    def __str__(self) -> str:
        return f"{self.tab.value}{', typing' if self.typing else ''}{'' if self.front else ', not front'}"


UNKNOWN = Studio(front=False, tab=Tab.OTHER, typing=False)


def classify(front: bool, texts: Iterable[str], focus_role: str | None) -> Studio:
    """Name the tab from the focused window's static texts. Needs every marker of a tab."""
    seen = {text.strip() for text in texts}
    if PLATER_MARKERS <= seen:
        tab = Tab.PLATER
    elif DEVICE_MARKERS <= seen:
        tab = Tab.DEVICE
    else:
        tab = Tab.OTHER
    return Studio(front=front, tab=tab, typing=focus_role in TEXT_ROLES)


def bare(keys: Keys) -> bool:
    """A key without ⌘ goes to whatever has focus: the 3D view, or a text field."""
    return "command" not in keys.modifiers


def refusal(keys: Keys, studio: Studio) -> str | None:
    """Why `keys` must not be sent now, or None when it may be.

    1. Only into Bambu Studio while it is the front app.
    2. Only on Prepare or Preview. Never on Device, where a print may be running,
       nor anywhere the tab can't be recognised.
    3. A bare key (A, F, M, R, S, C, Z, ⇧R) never while a text field has focus,
       where it would type the letter.
    """
    if not studio.front:
        return "not-front"
    if studio.tab is not Tab.PLATER:
        return f"tab {studio.tab.value}"
    if studio.typing and bare(keys):
        return "typing"
    return None
