# Kodi Idle Pause for macOS

Kodi can keep rendering while it sits idle in another app or full-screen Space. This small, inspectable macOS monitor pauses Kodi after it has been in the background for 30 seconds with no loaded video or audio. A playing or paused movie is kept awake, and Kodi wakes automatically when you return to it.

It supports the standard macOS Kodi app in `/Applications/Kodi.app` from Kodi 19 onward. Kodi 21 is tested. It uses `SIGSTOP` and `SIGCONT`, so paused Kodi consumes virtually no CPU. A three-finger swipe to another macOS Space is treated as Kodi moving to the background.

## Why this is safe to inspect

The complete implementation is seven small text files in this repository. It does not download software, collect data, call a cloud service, or require an account or token.

It queries only Kodi's existing HTTP service on `127.0.0.1` to determine whether a media player is loaded. Its local credentials stay on the Mac and are never logged or transmitted.

## Requirements

- macOS
- Kodi installed at `/Applications/Kodi.app`
- Python 3 available as `/usr/bin/python3` (install Apple's Command Line Tools if it is missing)
- Kodi's web server enabled in **Settings → Services → Control → Allow remote control via HTTP**

## Install

For the simplest install, download the repository as a ZIP from GitHub, unzip it, and double-click **Install Kodi Idle Pause.command**. Terminal asks for confirmation and shows the result.

### First launch on macOS

This project is not code-signed or notarized. On the first launch, macOS may block the downloaded `.command` file. In Finder, Control-click **Install Kodi Idle Pause.command**, choose **Open**, then confirm **Open** in the security prompt. You only need to do this once for that downloaded copy.

The source files are in the same folder and on GitHub for review before running it. Removing this macOS warning would require distributing a code-signed and notarized build through an Apple Developer account.

If you prefer Terminal, inspect the files and run:

```sh
./install.sh
```

The script copies one Python file to `~/Library/Application Support/Kodi Idle Pause/` and installs one LaunchAgent at `~/Library/LaunchAgents/com.kodi.idle-pause.plist`. macOS launches it at login.

The installer never asks for an administrator password.

## Commands

```sh
./status.sh     # monitor status, Kodi CPU state, and recent log lines
./stop.sh       # stop the monitor and wake Kodi immediately
./install.sh    # install or re-enable the monitor
./uninstall.sh  # remove the monitor and wake Kodi
```

## Behaviour

- Kodi must stay outside the foreground for 30 seconds before it can be paused.
- Kodi remains awake while video or audio is playing or paused.
- Kodi stays awake if the local playback check fails.
- When Kodi is paused, its background add-ons and scheduled jobs pause too. They resume when Kodi returns to the foreground.
- The monitor writes status messages to `~/Library/Logs/kodi-idle-pause.log`.

## Troubleshooting

Run `./status.sh`. If it reports a playback-check problem, make sure Kodi's web server is enabled and Kodi is running. If Python 3 is unavailable, install Apple's Command Line Tools with:

```sh
xcode-select --install
```

## License

[MIT](LICENSE)
