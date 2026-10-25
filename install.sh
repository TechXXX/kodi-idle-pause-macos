#!/bin/sh
set -eu

label="com.kodi.idle-pause"
source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
install_dir="$HOME/Library/Application Support/Kodi Idle Pause"
launch_agents_dir="$HOME/Library/LaunchAgents"
plist="$launch_agents_dir/$label.plist"
domain="gui/$(id -u)"

if [ ! -x /usr/bin/python3 ]; then
  echo "macOS's built-in Python 3 was not found." >&2
  exit 1
fi
if [ ! -d /Applications/Kodi.app ]; then
  echo "Kodi was not found in /Applications. Install Kodi there, then run this again." >&2
  exit 1
fi

mkdir -p "$install_dir" "$launch_agents_dir" "$HOME/Library/Logs"
cp "$source_dir/kodi_idle_pause.py" "$install_dir/kodi_idle_pause.py"
chmod 755 "$install_dir/kodi_idle_pause.py"
/usr/bin/sed "s|__HOME__|$HOME|g" "$source_dir/com.kodi.idle-pause.plist.template" > "$plist"

if launchctl print "$domain/$label" >/dev/null 2>&1; then
  launchctl bootout "$domain/$label"
fi
launchctl bootstrap "$domain" "$plist"

echo "Installed. Kodi will pause after 30 seconds in the background when no media is playing."
echo "Run ./status.sh to check it, or ./uninstall.sh to remove it."
