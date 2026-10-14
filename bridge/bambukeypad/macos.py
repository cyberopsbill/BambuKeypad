"""Every macOS call: clicking Bambu Studio's menus and sending it keystrokes.

Both go through System Events, so the process running the bridge needs
Accessibility permission (System Settings → Privacy & Security → Accessibility).
Scripts take their inputs as arguments (`on run argv`), never by pasting text
into the script, and keystrokes are only sent while Bambu Studio is in front.
"""

from __future__ import annotations

import re
import subprocess

from .pages import BUNDLE_ID, Action, Keys, Menu

TIMEOUT_S = 5

_MENU_SCRIPT = """
on run argv
  set bundleId to item 1 of argv
  set doClick to (item 2 of argv) is "click"
  tell application "System Events"
    set p to first application process whose bundle identifier is bundleId
    set target to menu bar item (item 3 of argv) of menu bar 1 of p
    repeat with i from 4 to count of argv
      set target to menu item (item i of argv) of menu 1 of target
    end repeat
    if not (exists target) then return "missing"
    if doClick then
      if not (enabled of target) then return "disabled"
      click target
    end if
    return "ok"
  end tell
end run
"""

_KEY_SCRIPT = """
on run argv
  set bundleId to item 1 of argv
  set theKey to item 2 of argv
  set keyCode to (item 3 of argv) as integer
  set mods to {}
  repeat with i from 4 to count of argv
    set m to item i of argv
    if m is "command" then set end of mods to command down
    if m is "shift" then set end of mods to shift down
    if m is "option" then set end of mods to option down
    if m is "control" then set end of mods to control down
  end repeat
  tell application "System Events"
    set frontProc to first application process whose frontmost is true
    if bundle identifier of frontProc is not bundleId then return "not-front"
    if keyCode < 0 then
      keystroke theKey using mods
    else
      key code keyCode using mods
    end if
  end tell
  return "ok"
end run
"""

# Named keys go by key code; everything else must be one lowercase character.
_KEY_CODES = {"tab": 48, "return": 36, "escape": 53, "delete": 51, "space": 49}
_SINGLE_KEY = re.compile(r"[a-z0-9,./;'\[\]\\=-]")
MODIFIERS = frozenset({"command", "shift", "option", "control"})


class ActionError(RuntimeError):
    pass


def validate(step: Menu | Keys) -> None:
    """Raise ValueError for a step the scripts can't send as written."""
    if isinstance(step, Menu):
        if len(step.path) < 2 or not all(step.path):
            raise ValueError(f"menu path needs a menu and an item: {step.path}")
        return
    if step.key not in _KEY_CODES and not _SINGLE_KEY.fullmatch(step.key):
        raise ValueError(f"unsupported key {step.key!r}: use one lowercase character or one of {sorted(_KEY_CODES)}")
    if not set(step.modifiers) <= MODIFIERS:
        raise ValueError(f"unknown modifiers in {step.modifiers}")


def _osascript(script: str, args: list[str]) -> str:
    try:
        done = subprocess.run(
            ["osascript", "-", *args], input=script, capture_output=True, text=True, timeout=TIMEOUT_S
        )
    except subprocess.TimeoutExpired:
        raise ActionError("osascript timed out") from None
    if done.returncode != 0:
        raise ActionError(done.stderr.strip() or f"osascript exited {done.returncode}")
    return done.stdout.strip()


def menu_status(menu: Menu, click: bool = False) -> str:
    """"ok", "missing" or "disabled". With click=True an "ok" item was also clicked."""
    validate(menu)
    try:
        return _osascript(_MENU_SCRIPT, [BUNDLE_ID, "click" if click else "check", *menu.path])
    except ActionError as error:
        # System Events raises when a title along the path doesn't exist.
        if "-1728" in str(error) or "Can’t get" in str(error) or "Can't get" in str(error):
            return "missing"
        raise


def send_keys(keys: Keys) -> str:
    """"ok", or "not-front" when Bambu Studio isn't the front app (nothing is sent)."""
    validate(keys)
    code = _KEY_CODES.get(keys.key, -1)
    return _osascript(_KEY_SCRIPT, [BUNDLE_ID, keys.key, str(code), *keys.modifiers])


def run(action: Action) -> str:
    """Do the action by its first step that works. Returns a description for the log."""
    tried = []
    for step in action.run:
        if isinstance(step, Menu):
            status = menu_status(step, click=True)
            if status == "ok":
                return f"menu {' > '.join(step.path)}"
            tried.append(f"menu {status}")
        else:
            status = send_keys(step)
            if status == "ok":
                return f"keys {'+'.join((*step.modifiers, step.key))}"
            tried.append(f"keys {status}")
    raise ActionError(f"{action.label}: nothing worked ({', '.join(tried)})")
