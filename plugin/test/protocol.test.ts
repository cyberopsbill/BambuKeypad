import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { DEFAULT_PORT, configuredPort } from '../src/protocol.ts';

function configFile(contents: string): string {
  const path = join(mkdtempSync(join(tmpdir(), 'bambu-keypad-')), 'config.json');
  writeFileSync(path, contents);
  return path;
}

test('the port comes from the config file', () => {
  assert.equal(configuredPort(configFile('{"port": 50000}')), 50000);
});

test('a missing, malformed or out-of-range config falls back to the default', () => {
  assert.equal(configuredPort('/nonexistent/config.json'), DEFAULT_PORT);
  assert.equal(configuredPort(configFile('not json')), DEFAULT_PORT);
  assert.equal(configuredPort(configFile('{"port": 70000}')), DEFAULT_PORT);
  assert.equal(configuredPort(configFile('{"port": "47833"}')), DEFAULT_PORT);
});
