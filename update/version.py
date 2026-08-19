"""One canonical version read/compare — replaces the mismatched readers in the
old version.py (.strip()'d local read), github_api.py (unstripped readline()),
and the unstripped remote HTTP response, whose disagreement could make the
local==remote comparison lie in either direction on a trailing-newline mismatch.
"""
import requests

import config


def read_local_version():
    try:
        with open(config.VERSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def fetch_remote_version(timeout=10):
    response = requests.get(config.GITHUB_VERSION_URL, timeout=timeout)
    response.raise_for_status()
    return response.text.strip()


def check_for_update():
    """Returns (update_available, local_version, remote_version_or_None).
    Never raises — a failed network check just reports no update available."""
    local = read_local_version()
    try:
        remote = fetch_remote_version()
    except requests.RequestException:
        return False, local, None
    return (local != remote), local, remote
