# Bambu Studio actions, verified

Checked on 2026-11-12 against **Bambu Studio 02.09.01.70** (macOS), from two sources:

1. The live menu bar, read through Accessibility. `python3 -m bambukeypad check`
   repeats this for every menu path in `bridge/bambukeypad/pages.py`; all 22 were found.
2. `src/slic3r/GUI/KBShortcutsDialog.cpp` at tag `v02.09.01.70`, which is the
   app's Help → Keyboard Shortcuts list. It is identical to `v02.08.02.61`, where
   the Global tab was also read on screen and matched. The menu accelerators in
   `MainFrame.cpp` changed only for Show Labels, which the keypad doesn't use.

First checked on 2026-10-13 against 02.08.02.61. No key changed in 02.09.01.70.

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
- **Keystrokes are gated by what Bambu Studio shows** (`bridge/bambukeypad/studio.py`).
  Before an action's first keystroke the bridge reads the front window through
  Accessibility, read-only, and sends nothing unless Bambu Studio is in front and on
  Prepare or Preview. A bare key (A, F, M, R, S, C, Z, ⇧R) is also held back while a text
  field has focus, where it would type the letter. Menu clicks aren't gated. A refused key
  logs why: `not-front`, `tab device`, `tab other` or `typing`.
  `python3 -m bambukeypad state` prints what the bridge reads.

## What Bambu Studio exposes to Accessibility

Read on 2026-11-12 from **Bambu Studio 02.09.01.70**, by snapshots of the whole tree on each tab.

- **The top tabs (Prepare, Preview, Device, Project, Calibration) aren't in the tree.**
  Only the visible tab's controls are, so each tab is recognised by the window's static texts.
- **Prepare and Preview look identical.** Both show the settings sidebar, headed
  **Printer**, **Project Filaments** and **Process**. All three must be present.
- **Device** shows **Printing Progress**, **Camera** and **Control**, plus the job's layer,
  time and Pause/Stop buttons while printing. Keystrokes are never sent here.
- **Project** shows a web view (with project info, a "Model" web area); **Calibration**
  shows its help texts. Neither has the sidebar, so both count as "other".
- **The 3D view exposes nothing.** The object list isn't in the tree either, so
  neither the selection nor slicing progress can be read.
- **A focused setting field reads as `AXTextField`.** With the 3D view in use the focused
  element is the window itself.
- **Edit and View menu states are a weak hint at best.** They refresh only when a menu opens.
