#!/bin/sh
# Install, remove or inspect the launchd agent that keeps the bridge running.
#   scripts/agent.sh install [python3]   start now and at every login
#   scripts/agent.sh uninstall           stop and remove
#   scripts/agent.sh status
# Accessibility permission belongs to the Python binary the agent runs, so use
# one stable interpreter (default: the python3 on PATH, resolved to its real file).
set -eu

LABEL=com.bambukeypad.bridge
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
BRIDGE="$(cd "$(dirname "$0")/../bridge" && pwd)"
DOMAIN="gui/$(id -u)"

case "${1:-}" in
install)
  PY="${2:-$(command -v python3)}"
  PY="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$PY")"
  mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
  cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>-m</string><string>bambukeypad</string><string>serve</string></array>
  <key>WorkingDirectory</key><string>$BRIDGE</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/BambuKeypad-bridge.stderr.log</string>
</dict>
</plist>
PLIST
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  launchctl bootstrap "$DOMAIN" "$PLIST"
  echo "installed $LABEL using $PY"
  echo "grant Accessibility to $PY if macOS hasn't asked yet"
  ;;
uninstall)
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "removed $LABEL"
  ;;
status)
  launchctl print "$DOMAIN/$LABEL" 2>/dev/null | grep -E "state|pid|program" || echo "$LABEL is not loaded"
  ;;
*)
  echo "usage: $0 install [python3] | uninstall | status" >&2
  exit 2
  ;;
esac
