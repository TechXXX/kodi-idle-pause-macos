#!/bin/sh
set -eu

label="com.kodi.idle-pause"
domain="gui/$(id -u)"
if launchctl print "$domain/$label" >/dev/null 2>&1; then
  echo "Monitor: active"
else
  echo "Monitor: stopped"
fi
ps -axo pid=,%cpu=,stat=,command= | /usr/bin/grep '/Applications/Kodi.app/Contents/MacOS/Kodi' | /usr/bin/grep -v grep || true
tail -5 "$HOME/Library/Logs/kodi-idle-pause.log" 2>/dev/null || true
