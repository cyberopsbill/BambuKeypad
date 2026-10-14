"""The keypad definition: every page and its keys, in keypad order.

This is the file to edit to change what the keypad offers.

- A key that does something in Bambu Studio is an `Action`. Its `run` lists the
  ways to do it, tried in order: a `Menu` path (clicked through Accessibility,
  which works whatever has focus) and then `Keys` (a keystroke, sent only while
  Bambu Studio is in front).
- A key that opens another page is a `Page`. Pages that don't fit get a More key.
- Menu titles must match Bambu Studio exactly, including "...". Run
  `python3 -m bambukeypad check` with Bambu Studio open to confirm every one.
- Every shortcut here was checked against Bambu Studio 02.08.02.61: its menu bar,
  and src/slic3r/GUI/KBShortcutsDialog.cpp at tag v02.08.02.61. See docs/shortcuts.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

BUNDLE_ID = "com.bambulab.bambu-studio"


@dataclass(frozen=True)
class Menu:
    """A menu item, by its titles from the menu bar down."""

    path: tuple[str, ...]

    def __init__(self, *path: str):
        object.__setattr__(self, "path", path)


@dataclass(frozen=True)
class Keys:
    """A keystroke: one lowercase key, or a named key, with modifiers."""

    key: str
    modifiers: tuple[str, ...] = ()


@dataclass(frozen=True)
class Action:
    label: str
    icon: str
    run: tuple[Menu | Keys, ...]

    def __init__(self, label: str, icon: str, *run: Menu | Keys):
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "icon", icon)
        object.__setattr__(self, "run", run)


@dataclass(frozen=True)
class Page:
    name: str
    icon: str
    items: tuple[Action | Page, ...] = field(default=())

    def __init__(self, name: str, icon: str, items: list[Action | Page]):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "icon", icon)
        object.__setattr__(self, "items", tuple(items))


CMD = ("command",)

EDIT = Page("Edit", "edit", [
    Action("Move", "move", Keys("m")),
    Action("Rotate", "rotate", Keys("r")),
    Action("Scale", "scale", Keys("s")),
    Action("Cut", "cut", Keys("c")),
    Action("Clone", "clone", Menu("Edit", "Clone selected"), Keys("k", CMD)),
    Action("Select All", "select", Menu("Edit", "Select all"), Keys("a", CMD)),
    Action("Undo", "undo", Menu("Edit", "Undo"), Keys("z", CMD)),
    Action("Redo", "redo", Menu("Edit", "Redo"), Keys("y", CMD)),
])

VIEW = Page("View", "view", [
    Action("Fit", "fit", Menu("View", "Fit Camera"), Keys("z")),
    Action("Iso", "iso", Menu("View", "Isometric"), Keys("7", CMD)),
    Action("Top", "top", Menu("View", "Top"), Keys("1", CMD)),
    Action("Front", "front", Menu("View", "Front"), Keys("3", CMD)),
    Action("Left", "left", Menu("View", "Left"), Keys("5", CMD)),
    Action("Right", "right", Menu("View", "Right"), Keys("6", CMD)),
    Action("Default", "default", Menu("View", "Default View"), Keys("0", CMD)),
    Action("Overhang", "overhang", Menu("View", "Show Overhang"), Keys("l", CMD)),
])

FILE = Page("File", "file", [
    Action("Save", "save", Menu("File", "Save Project"), Keys("s", CMD)),
    Action("Save As", "saveas", Menu("File", "Save Project as..."), Keys("s", ("command", "shift"))),
    Action("Export Sliced", "export", Menu("File", "Export", "Export plate sliced file..."), Keys("g", CMD)),
    Action("Export G-code", "gcode", Menu("File", "Export", "Export G-code...")),
    Action("Export STL", "stl", Menu("File", "Export", "Export all objects as one STL...")),
    Action("Export 3MF", "export", Menu("File", "Export", "Export Generic 3MF...")),
    Action("Open", "open", Menu("File", "Open Project..."), Keys("o", CMD)),
    Action("New", "new", Menu("File", "New Project"), Keys("n", CMD)),
    Action("Show Folder", "folder", Menu("File", "Show Project in Folder")),
])

HOME = Page("Home", "home", [
    Action("Import", "import", Menu("File", "Import", "Import 3MF/STL/STEP/SVG/OBJ/AMF..."), Keys("i", CMD)),
    Action("Slice", "slice", Keys("r", CMD)),
    # Opens the "Send print job" dialog; nothing prints until it is confirmed there.
    Action("Print…", "print", Keys("g", ("command", "shift"))),
    Action("Arrange", "arrange", Keys("a")),
    Action("Orient", "orient", Keys("r", ("shift",))),
    Action("Lay Flat", "layflat", Keys("f")),
    EDIT,
    VIEW,
    FILE,
])


def all_actions(page: Page = HOME) -> list[Action]:
    """Every action reachable from `page`, depth first."""
    found: list[Action] = []
    for item in page.items:
        found += all_actions(item) if isinstance(item, Page) else [item]
    return found
