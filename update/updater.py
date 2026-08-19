"""Self-update: stage -> verify -> atomic swap -> relaunch.

Replaces download_repository.py/github_api.py's clone-then-delete-then-copy
flow, where a bare `except Exception: pass` around the clone meant a failed
download was treated as success, and delete_files_except_script() wiped the
whole install directory *before* confirming the replacement was any good — a
failure partway through could leave the app's own source deleted with nothing
copied back. Every step here raises a specific UpdateError instead of
swallowing failures, and nothing live is touched until the download is staged
and verified.
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time

import config


class UpdateError(Exception):
    pass


def install_dir():
    return os.path.dirname(os.path.abspath(config.VERSION_FILE))


def _force_remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_tree(path):
    """rmtree that clears read-only attributes instead of silently giving up
    on them like ignore_errors=True does. Git marks packed object files
    read-only on Windows, so a plain ignore_errors rmtree of a partial clone
    can leave the directory (and its contents) behind untouched — which is
    exactly what made a later clone into the same path fail with "destination
    path ... already exists and is not an empty directory"."""
    if os.path.isdir(path):
        shutil.rmtree(path, onerror=_force_remove_readonly)


def stage_download(staging_dir):
    import git

    try:
        _remove_tree(staging_dir)
    except OSError as e:
        raise UpdateError(f"Could not clear the previous download folder ({staging_dir}): {e}") from e
    try:
        git.Repo.clone_from(config.GITHUB_REPO_URL, staging_dir)
    except Exception as e:
        raise UpdateError(f"Failed to download the latest version: {e}") from e


def verify_staging(staging_dir):
    entry_point = os.path.join(staging_dir, "main.py")
    version_file = os.path.join(staging_dir, "version.txt")
    if not os.path.isfile(entry_point):
        raise UpdateError("Downloaded update is missing main.py — aborting, your installation was not modified.")
    if not os.path.isfile(version_file):
        raise UpdateError("Downloaded update is missing version.txt — aborting, your installation was not modified.")
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            f.read()
    except OSError as e:
        raise UpdateError(f"Downloaded update's version.txt is unreadable: {e}") from e


def _rename_with_retry(src, dst, attempts=6, delay=0.3):
    """os.rename, retrying briefly on failure. On Windows, transient external
    file locks (antivirus scanners, the search indexer, etc. momentarily
    touching a file) can make a rename fail with the same "used by another
    process" error as a real lock — those usually clear within a second."""
    for attempt in range(1, attempts + 1):
        try:
            os.rename(src, dst)
            return
        except OSError:
            if attempt == attempts:
                raise
            time.sleep(delay)


def atomic_swap(live_dir, staging_dir):
    """Rename live -> .old, staging -> live, then delete .old. If the second
    rename fails, .old is renamed back — the app is never left half-deleted."""
    parent = os.path.dirname(live_dir)
    old_dir = os.path.join(parent, os.path.basename(live_dir) + ".old")
    try:
        _remove_tree(old_dir)
    except OSError as e:
        raise UpdateError(f"Could not clear a leftover backup folder ({old_dir}): {e}") from e

    try:
        _rename_with_retry(live_dir, old_dir)
    except OSError as e:
        raise UpdateError(f"Could not move the current installation aside: {e}. "
                           "Your installation was not modified.") from e

    try:
        _rename_with_retry(staging_dir, live_dir)
    except OSError as e:
        try:
            _rename_with_retry(old_dir, live_dir)
        except OSError:
            raise UpdateError(
                f"Could not move the update into place ({e}), and the rollback also failed. "
                f"Your previous installation is preserved at: {old_dir}"
            ) from e
        raise UpdateError(f"Could not move the update into place: {e}. "
                           "Rolled back — your installation is unchanged.") from e

    try:
        _remove_tree(old_dir)
    except OSError:
        pass  # harmless leftover backup — the update itself already succeeded


def relaunch(live_dir):
    main_py = os.path.join(live_dir, "main.py")
    subprocess.Popen([sys.executable, main_py], cwd=live_dir)
    os._exit(0)


def run_update(progress_callback=None):
    """Full update flow. progress_callback(str) is called with human-readable
    status at each stage. Raises UpdateError on any failure; on success this
    function does not return (it replaces the current process)."""
    def report(msg):
        if progress_callback:
            progress_callback(msg)

    live_dir = install_dir()
    staging_dir = live_dir + ".staging"

    report("Downloading latest version...")
    stage_download(staging_dir)

    report("Verifying download...")
    verify_staging(staging_dir)

    report("Installing update...")
    # Windows refuses to rename a directory that is any process's current
    # working directory, even with no individual file open — and that's
    # exactly what live_dir is for this process (start.bat cd's into it
    # before launching main.py). Step out of it before the swap, or the
    # rename fails with WinError 32 ("used by another process").
    os.chdir(tempfile.gettempdir())
    atomic_swap(live_dir, staging_dir)

    report("Update installed. Relaunching...")
    relaunch(live_dir)
