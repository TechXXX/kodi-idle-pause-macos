#!/bin/sh
# Double-click this file after unzipping the GitHub download.

set -u
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

clear
echo "Kodi Idle Pause for macOS"
echo
echo "This installs a small local monitor that pauses Kodi after 30 seconds"
echo "in the background when nothing is playing. It wakes Kodi when you return."
echo
echo "No account, token, download, or administrator password is required."
echo "The source files are in this same folder for you to inspect."
echo
printf "Press Return to install, or close this window to cancel: "
read unused

if "$script_dir/install.sh"; then
  echo
  echo "Installation complete."
  echo "You can leave this window open or close it."
else
  echo
  echo "Installation did not complete. See the message above."
fi

echo
printf "Press Return to close: "
read unused
