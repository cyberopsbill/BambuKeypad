# Bambu Keypad: working notes

A Python bridge (`bridge/`) drives Bambu Studio for a Logitech MX Keypad, through a thin
Logi plugin (Node.js/TypeScript, `plugin/`) adapted from Fusion-LogiMX @ 44b8185 (see NOTICE).
README.md covers setup, docs/protocol.md the link, and docs/shortcuts.md what each key sends.

## Rules

- **The bridge decides; the plugin relays.** New keys or pages never need a plugin change.
- **Pure core, thin edge.** `pages`, `navigator`, `faces`, `icons`, `protocol` and `config`
  never touch macOS and carry the tests. `macos.py` is the only module that runs osascript.
  `server.py` is the socket.
- **Never modify Bambu Studio.** Act only through its menus and shortcuts.
- **Verify before trusting.** Every menu path must pass `python3 -m bambukeypad check`.
  Every keystroke must come from the app's shortcut list (KBShortcutsDialog.cpp at the
  installed version's tag). Record both in docs/shortcuts.md.
- **Keystrokes only while Bambu Studio is in front.** The key script checks and sends nothing otherwise.
- **No secrets in the repo or logs.** The Phase 3 printer access code goes in the macOS Keychain.

## Conventions

- **Bridge.** Standard library only. Python 3.11+. pytest. ruff with the root `ruff.toml`.
- **Plugin.** Upstream's conventions apply: strict `tsc` for types only, esbuild bundles,
  and `node --test` strips types (so `.ts` imports and no enums).
  `@logitech/plugin-sdk` stays pinned at exactly 0.1.1 because `lps-bridge.ts` uses its private internals.
- **Port** 47833, from `~/Library/Application Support/BambuKeypad/config.json` on both sides.
  Upstream uses 47823 and 47824.

## Facts established (Bambu Studio 02.08.02.61, macOS, 2026-10-13)

- **Bundle id:** `com.bambulab.bambu-studio`. Process name: `BambuStudio`.
- **Shortcuts:**
  - Print plate is ⌘⇧G, not ⌘P.
  - ⌘G is Export plate sliced file. Export G-code is menu-only.
  - Auto-orient is ⇧R. Lay flat is F. Fit is Z. Views are ⌘0–⌘7.
- **Menu item enabled state is lazy (wxWidgets).**
  - Edit and View items can read disabled through AX until a menu opens.
  - On the Device tab they really are disabled.
  - `macos.run` treats disabled as "try the next step".
- **AppleScript:** `front` is a reserved word. Don't use it as a variable name.
- **Keyboard Shortcuts dialog:** its side tabs can't be clicked through AX from the background.
  Read KBShortcutsDialog.cpp instead.
- **Logi Plugin Service** runs the plugin on its own Node (22.19), as `BambuKeypad`, beside `FusionKeypad`.
