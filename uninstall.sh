#!/bin/sh
set -eu

label="com.kodi.idle-pause"
plist="$HOME/Library/LaunchAgents/$label.plist"
domain="gui/$(id -u)"
if launchctl print "$domain/$label" >/dev/null 2>&1; then
  launchctl bootout "$domain/$label"
fi
pgrep -x Kodi | while IFS= read -r pid; do
  kill -CONT "$pid" 2>/dev/null || true
done
rm -f "$plist"
rm -rf "$HOME/Library/Application Support/Kodi Idle Pause"
echo "Removed the Kodi Idle Pause monitor. The log remains at ~/Library/Logs/kodi-idle-pause.log."
