"""Which page the keypad shows, and the rules that move it.

1. The keypad starts on Home. Bambu Studio tells us nothing, so only key
   presses move it (Phase 1 has no state awareness).
2. A page key opens that page. Back goes up one level. Home has no Back.
3. More steps through the screens of a page that doesn't fit, wrapping round.
4. An action key returns the action for the caller to run; the keypad stays put.
5. A press made against a layout that is no longer on screen is ignored, so a
   key can't act after it changed meaning.

Pure Python: nothing here touches macOS.
"""

from __future__ import annotations

from enum import Enum

from .pages import Action, Page

SLOT_COUNT = 9


class Nav(Enum):
    """Keys that move around the keypad rather than acting in Bambu Studio."""

    BACK = "back"
    MORE = "more"


Target = Action | Page | Nav


class Navigator:
    def __init__(self, root: Page):
        self._stack: list[Page] = [root]
        self.screen = 0
        self.layout = 1  # changes whenever what any key does changes

    @property
    def page(self) -> Page:
        return self._stack[-1]

    def slots(self) -> list[Target | None]:
        """What each key does, in reading order: Back first and More last when shown."""
        screens = self._screens(self.page)
        keys: list[Target | None] = [Nav.BACK] if self._below_root else []
        keys += screens[self.screen]
        keys += [None] * (SLOT_COUNT - len(keys))
        if len(screens) > 1:
            keys[-1] = Nav.MORE
        return keys

    def press(self, slot: int, layout: int) -> Action | None:
        """Handle a key press. Returns the action to run, if the key has one."""
        if layout != self.layout or not 0 <= slot < SLOT_COUNT:
            return None
        target = self.slots()[slot]
        if isinstance(target, Action):
            return target
        if isinstance(target, Page):
            self._stack.append(target)
            self._moved(screen=0)
        elif target is Nav.BACK:
            self._stack.pop()
            self._moved(screen=0)
        elif target is Nav.MORE:
            self._moved(screen=(self.screen + 1) % len(self._screens(self.page)))
        return None

    def home(self) -> None:
        if len(self._stack) > 1 or self.screen:
            del self._stack[1:]
            self._moved(screen=0)

    @property
    def _below_root(self) -> bool:
        return len(self._stack) > 1

    def _screens(self, page: Page) -> list[list[Action | Page]]:
        room = SLOT_COUNT - (1 if self._below_root else 0)
        items = list(page.items)
        if len(items) <= room:
            return [items]
        per = room - 1  # the last key becomes More
        return [items[i:i + per] for i in range(0, len(items), per)]

    def _moved(self, screen: int) -> None:
        self.screen = screen
        self.layout += 1
