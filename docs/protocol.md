# The bridge ⇄ plugin link

The Logi plugin (`plugin/`) draws the keypad; the bridge (`bridge/`) decides what
the keys show and does what they ask in Bambu Studio. This is the protocol of
upstream Fusion-LogiMX's add-in ⇄ plugin link, unchanged except for the port.

## Connection

- The bridge listens on `127.0.0.1`, port **47833** by default. Both sides read
  `~/Library/Application Support/BambuKeypad/config.json` (`{"port": 47833}`), so
  change the port there. `BAMBU_KEYPAD_PORT` overrides it for the bridge only.
  (Upstream uses 47823 for its plugin and 47824 for its MCP server, so the Fusion
  and Bambu keypads can run side by side.)
- A client connects, and retries once a second while nothing is listening.
- Messages are UTF-8 JSON objects, one per line (`\n`-terminated).
- On connecting, a client is sent the current `keys`, and again whenever they change.
- The bridge disconnects a client that sends a line that isn't a JSON object, so
  an HTTP request (from a web page, say) never reaches Bambu Studio.
- Nothing is queued while a client is disconnected.

## Bridge → plugin: `keys`

```json
{"type": "keys", "layout": 3, "keys": [{"label": "‹ Back", "image": "PHN2Zy…"}, …]}
```

| Field | Meaning |
|---|---|
| `layout` | Identifies what the keys *do*. It changes whenever the keypad moves to another page or screen. |
| `keys` | Exactly 9 entries in reading order: key 1 is top-left, key 9 bottom-right. |
| `keys[].label` | The text on the key. An empty string gives a blank label. |
| `keys[].image` | A base64-encoded PNG or SVG, or `null` for a text-only key. |

## Plugin → bridge: `press`

```json
{"type": "press", "slot": 3, "layout": 3}
```

| Field | Meaning |
|---|---|
| `slot` | The key's index, 0 to 8, in the same order as `keys`. |
| `layout` | The `layout` of the `keys` message on screen when the key was pressed. |

The bridge ignores a press whose `layout` isn't the current one, so a press can't
act on a key that changed meaning just before.

While the connection is down, the plugin shows a "Bambu bridge offline" face.
