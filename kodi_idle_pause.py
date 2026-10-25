#!/usr/bin/python3
"""Pause Kodi only while it is backgrounded and no media is playing.

Uses Kodi's loopback JSON-RPC service. No account, token, or network access is
needed; the service listens only on this Mac.
"""
import base64
import http.client
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

KODI_EXECUTABLE = "/Applications/Kodi.app/Contents/MacOS/Kodi"
KODI_SETTINGS = Path.home() / "Library/Application Support/Kodi/userdata/guisettings.xml"
LOG_PATH = Path.home() / "Library/Logs/kodi-idle-pause.log"
BACKGROUND_DELAY_SECONDS = 30
POLL_SECONDS = 2

logger = logging.getLogger("kodi-idle-pause")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=1)
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
logger.addHandler(handler)


def kodi_pid():
    """Return the PID for Kodi installed in /Applications, if it is running."""
    result = subprocess.run(
        ["/bin/ps", "-axo", "pid=,command="],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and (
            parts[1] == KODI_EXECUTABLE or parts[1].startswith(KODI_EXECUTABLE + " ")
        ):
            return int(parts[0])
    return None


def frontmost_pid():
    """Return the PID of the app in the active macOS Space."""
    front = subprocess.run(
        ["/usr/bin/lsappinfo", "front"], capture_output=True, text=True, timeout=2
    )
    asn = front.stdout.strip()
    if not asn.startswith("ASN:"):
        return None
    info = subprocess.run(
        ["/usr/bin/lsappinfo", "info", "-only", "pid", asn],
        capture_output=True,
        text=True,
        timeout=2,
    )
    match = re.search(r"\bpid\s*=\s*(\d+)", info.stdout)
    return int(match.group(1)) if match else None


def kodi_settings():
    """Read Kodi's local web-service settings without printing credentials."""
    root = ET.parse(KODI_SETTINGS).getroot()
    values = {item.get("id"): item.text for item in root.iter("setting")}
    if values.get("services.webserver") != "true":
        raise RuntimeError("Kodi web server is disabled")
    return (
        int(values.get("services.webserverport") or 8080),
        values.get("services.webserverusername") or "kodi",
        values.get("services.webserverpassword") or "",
    )


def kodi_rpc(method, params=None):
    port, username, password = kodi_settings()
    credentials = base64.b64encode((username + ":" + password).encode()).decode()
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        payload["params"] = params

    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request(
            "POST",
            "/jsonrpc",
            json.dumps(payload),
            {
                "Content-Type": "application/json",
                "Authorization": "Basic " + credentials,
            },
        )
        response = connection.getresponse()
        if response.status != 200:
            raise RuntimeError("Kodi API returned HTTP " + str(response.status))
        data = json.load(response)
        if "error" in data or "result" not in data:
            raise RuntimeError("Kodi API did not return a result")
        return data["result"]
    finally:
        connection.close()


def playback_active():
    """Return True for playing, False for stopped or paused, None if uncertain."""
    try:
        players = kodi_rpc("Player.GetActivePlayers")
        if not isinstance(players, list):
            return None
        for player in players:
            player_id = player.get("playerid")
            if player_id is None:
                return None
            properties = kodi_rpc(
                "Player.GetProperties",
                {"playerid": player_id, "properties": ["speed"]},
            )
            if not isinstance(properties, dict) or "speed" not in properties:
                return None
            if properties["speed"] != 0:
                return True
        return False
    except Exception as exc:
        logger.warning("Playback check unavailable; Kodi remains awake: %s", type(exc).__name__)
        return None


def resume(pid):
    if pid is not None:
        try:
            os.kill(pid, signal.SIGCONT)
            logger.info("Resumed Kodi pid %s", pid)
        except ProcessLookupError:
            pass


def monitor():
    paused_pid = None
    background_since = None

    def stop_monitor(signum, frame):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop_monitor)
    signal.signal(signal.SIGINT, stop_monitor)
    logger.info("Monitor started; background delay %s seconds", BACKGROUND_DELAY_SECONDS)
    try:
        while True:
            pid = kodi_pid()
            if pid != paused_pid and paused_pid is not None:
                resume(paused_pid)
                paused_pid = None

            if pid is None:
                background_since = None
                time.sleep(POLL_SECONDS)
                continue

            if frontmost_pid() == pid:
                if paused_pid == pid:
                    resume(pid)
                    paused_pid = None
                background_since = None
            elif paused_pid is None:
                now = time.monotonic()
                if background_since is None:
                    background_since = now
                elif now - background_since >= BACKGROUND_DELAY_SECONDS:
                    if playback_active() is False:
                        os.kill(pid, signal.SIGSTOP)
                        paused_pid = pid
                        logger.info("Paused background Kodi pid %s; no active playback", pid)
                    else:
                        background_since = now
            time.sleep(POLL_SECONDS)
    finally:
        resume(paused_pid)
        logger.info("Monitor stopped")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        pid = kodi_pid()
        print("Kodi PID:", pid)
        print("Frontmost PID:", frontmost_pid())
        print("Playback active:", playback_active() if pid else "Kodi is not running")
    else:
        monitor()
