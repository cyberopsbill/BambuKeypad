# Bambu Keypad

Nine LCD keys on a Logitech MX Keypad that drive **Bambu Studio** on macOS: Import,
Slice, Print, Arrange, Orient and Lay Flat on the home page, plus Edit, View and File pages.

Adapted from [Fusion-LogiMX](https://github.com/craigulliott/Fusion-LogiMX) by Craig Ulliott
(MIT). See [NOTICE](NOTICE).

```
MX Keypad ⇄ Logi Options+ / Plugin Service ⇄ plugin/ (Node) ⇄ localhost:47833 ⇄ bridge/ (Python) ⇄ System Events ⇄ Bambu Studio
```

- **`plugin/`** is a thin Logi plugin. It shows the nine faces it is sent and reports
  presses by slot. It knows nothing about Bambu Studio.
- **`bridge/`** decides everything. It holds the pages (`bridge/bambukeypad/pages.py`)
  and runs each action by clicking Bambu Studio's menu through Accessibility, or by
  sending its keyboard shortcut while Bambu Studio is in front.

Bambu Studio has no plugin API and isn't modified in any way.

## Setup

You need Logi Options+ (it includes Logi Plugin Service), Node.js 22.18 or newer, and
Python 3.11 or newer. The bridge uses only the standard library.

**1. The plugin.**

```sh
cd plugin
npm install
npm run build
npm run link      # links dist/ into Logi Plugin Service and reloads it
```

`npm run unlink` removes it again. It installs as **BambuKeypad**, separately from
the Fusion keypad plugin, and both can be installed at once.

**2. The bridge.** Run it once in a terminal to try it:

```sh
cd bridge
python3 -m bambukeypad serve
```

To run it in the background at every login instead:

```sh
scripts/agent.sh install      # also: uninstall, status
```

**3. Accessibility (needs you).** macOS asks the first time the bridge clicks a menu.
Allow it in **System Settings → Privacy & Security → Accessibility** for whatever runs
the bridge: your terminal app when run by hand, or the Python binary that
`scripts/agent.sh install` prints for the agent. A Homebrew Python upgrade changes
that binary, so grant it again after one.

Then check that every menu item the keys use exists, with Bambu Studio open:

```sh
cd bridge && python3 -m bambukeypad check
```

**4. Logi Options+ (needs you).**
1. Select the MX Keypad and add an application profile for **Bambu Studio**. Options+
   switches to it whenever Bambu Studio is in front.
2. Under **All actions → Bambu Keypad → Bambu Keys**, drag **Bambu Key 1** to
   **Bambu Key 9** onto the nine keys in reading order: 1 is top-left, 9 bottom-right.

## Using it

| Home | | |
|---|---|---|
| Import | Slice | Print… |
| Arrange | Orient | Lay Flat |
| Edit › | View › | File › |

- **A key marked `›` opens a page**, and **‹ Back** returns. **More ›** appears on
  pages that don't fit (File).
- **Print…** opens Bambu Studio's Send print job dialog. Nothing is sent to the
  printer until you confirm there.
- **Edit**: Move, Rotate, Scale, Cut, Clone, Select All, Undo, Redo.
  **View**: Fit, Iso, Top, Front, Left, Right, Default, Overhang.
  **File**: Save, Save As, Export Sliced, Export G-code, Export STL, Export 3MF, Open, New, Show Folder.
- **The keypad doesn't follow Bambu Studio yet.** It moves only when you press its
  keys (state awareness is Phase 2).
- **Bare-letter keys need the 3D view focused.** Arrange (A), Orient (⇧R), Lay Flat (F),
  Move, Rotate, Scale, Cut and Fit's fallback (Z) are canvas shortcuts. Use them on the
  Prepare tab with nothing being typed into. In a text field they type the letter.

What each key sends, and how it was verified, is in [docs/shortcuts.md](docs/shortcuts.md).

## Changing the keys

Edit [`bridge/bambukeypad/pages.py`](bridge/bambukeypad/pages.py), then restart the bridge
(`scripts/agent.sh install` restarts the agent). An `Action` lists a `Menu(...)` path and/or
`Keys(...)`, tried in order. Icons are in `bridge/bambukeypad/icons.py`, and
`python3 -m bambukeypad icons /tmp/icons` writes them out as .svg files to look at.

## Port

The default is **47833**. To change it, put `{"port": 47900}` in
`~/Library/Application Support/BambuKeypad/config.json`. Both sides read it. Then run
`npm run link` again to reload the plugin and restart the bridge.

## Development

```sh
cd plugin && npm test && npm run typecheck
cd bridge && uv run --with pytest pytest     # or: python3 -m pytest
uvx ruff check --config ruff.toml bridge
```

The protocol is in [docs/protocol.md](docs/protocol.md). Logs are in
`~/Library/Logs/BambuKeypad-bridge.log` and `BambuKeypad-plugin.log` (`npm run log` follows the latter).

## Troubleshooting

| The keys show | Cause |
|---|---|
| "Bambu bridge offline" | The bridge isn't running, or it's on another port. |
| "Bambu Key 1" … "Bambu Key 9" | The plugin couldn't hook the Logitech SDK. Look for `FAIL` in the plugin log. |
| Nothing, or another app's keys | The keys aren't on the Bambu Studio profile in Options+, or Bambu Studio isn't in front. |

A key that does nothing logs why in the bridge log. `not-front` means Bambu Studio wasn't
the front app. An `-1743` or "not allowed assistive access" error means Accessibility
permission is missing.
