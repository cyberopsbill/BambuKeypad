// Messages between this plugin and the Bambu Keypad bridge. docs/protocol.md is
// the specification; keep the two in step.
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

export const DEFAULT_PORT = 47833;
export const SLOT_COUNT = 9;

/** Shared with the bridge, which reads the same file (bridge/bambukeypad/config.py). */
export const CONFIG_PATH = join(homedir(), 'Library', 'Application Support', 'BambuKeypad', 'config.json');

/** The port from the shared config file, or the default when it is missing or unreadable. */
export function configuredPort(path: string = CONFIG_PATH): number {
  try {
    const port = (JSON.parse(readFileSync(path, 'utf8')) as { port?: unknown }).port;
    if (Number.isInteger(port) && (port as number) > 0 && (port as number) < 65536) return port as number;
  } catch {
    // No config file: use the default.
  }
  return DEFAULT_PORT;
}

export type KeyFace = { label: string; image: string | null };

/** Bridge → plugin: what all nine keys show. */
export type KeysMessage = { type: 'keys'; layout: number; keys: KeyFace[] };

/** Plugin → bridge: a key was pressed. */
export type PressMessage = { type: 'press'; slot: number; layout: number };
