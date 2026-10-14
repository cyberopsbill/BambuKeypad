# Bambu Studio actions, verified

Checked on 2026-10-13 against **Bambu Studio 02.08.02.61** (macOS), from two sources:

1. The live menu bar, read through Accessibility. `python3 -m bambukeypad check`
   repeats this for every menu path in `bridge/bambukeypad/pages.py`; all 22 were found.
2. `src/slic3r/GUI/KBShortcutsDialog.cpp` at tag `v02.08.02.61`, which is the
   app's Help → Keyboard Shortcuts list. Its Global tab was also read on screen
   and matches.

On macOS, wxWidgets' "Ctrl" is ⌘.

| Key | How the bridge does it | Notes |
|---|---|---|
| Import | File › Import › Import 3MF/STL/STEP/SVG/OBJ/AMF... (⌘I) | |
| Slice | ⌘R | Not in the menus. |
| Print… | ⌘⇧G | "Print plate". Not ⌘P. Opens the Send print job dialog; nothing prints until you confirm there. |
| Arrange | A | Shift+A arranges selected plates only. |
| Orient | ⇧R | Auto-orient. Not A. |
| Lay Flat | F | "Place face on bed". L is SLA support points, not lay flat. |
| Move / Rotate / Scale / Cut | M / R / S / C | Gizmos. |
| Clone, Select All, Undo, Redo | Edit menu (⌘K, ⌘A, ⌘Z, ⌘Y) | |
| Fit | View › Fit Camera, or Z | |
| Views | View › Default/Top/Front/Left/Right/Isometric (⌘0, ⌘1, ⌘3, ⌘5, ⌘6, ⌘7) | Not the numpad. Bottom ⌘2, Rear ⌘4. |
| Overhang | View › Show Overhang (⌘L) | |
| Export Sliced | File › Export › Export plate sliced file... (⌘G) | ⌘G is this, not Export G-code. |
| Export G-code | File › Export › Export G-code... | No shortcut. |
| Save / Save As / Open / New | File menu (⌘S, ⌘⇧S, ⌘O, ⌘N) | |

## How actions are sent, and what we learned

- **Menu first, then keystroke.** A menu click goes through System Events.
  Keystrokes are sent only while Bambu Studio is the front app; otherwise nothing is sent.
- **Menu items read as disabled until a menu opens.** Bambu Studio (wxWidgets)
  refreshes enabled state lazily, and on the Device tab the Edit and View items
  really are disabled. When the bridge sees a disabled item it falls back to the
  keystroke, which worked in testing (Isometric by ⌘7).
- **Bare-letter keys go to whatever has focus.** A, F, R, M, S, C and Z are canvas
  shortcuts. If a text field has focus they type into it, and on the Device tab they
  do nothing useful. Phase 2 should only send them on the Prepare or Preview tab.
