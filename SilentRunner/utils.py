"""
SilentRunner – utility helpers.
"""

import os
import time


def format_elapsed(seconds: float) -> str:
    """Return a human-readable elapsed time string (e.g. '1h 02m 33s')."""
    seconds = int(seconds)
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def is_runnable(filename: str) -> bool:
    """Return True if the file has a supported script extension."""
    return filename.endswith(".sh") or filename.endswith(".py")


def script_type(filename: str) -> str:
    """Return 'sh', 'py', or '' based on the file extension."""
    if filename.endswith(".sh"):
        return "sh"
    if filename.endswith(".py"):
        return "py"
    return ""


def safe_listdir(path: str):
    """
    List a directory, returning (dirs, files) tuples.

    Hides dot-files and dot-directories.
    Only includes .sh and .py files.
    Both lists are sorted alphabetically (case-insensitive).
    """
    dirs = []
    files = []
    try:
        entries = os.listdir(path)
    except OSError:
        return [], []

    for name in entries:
        if name.startswith("."):
            continue
        full = os.path.join(path, name)
        try:
            if os.path.isdir(full):
                dirs.append(name)
            elif os.path.isfile(full) and is_runnable(name):
                files.append(name)
        except OSError:
            continue

    dirs.sort(key=str.lower)
    files.sort(key=str.lower)
    return dirs, files


def now_ts() -> float:
    """Return current monotonic timestamp."""
    return time.monotonic()


def wall_time() -> float:
    """Return current wall-clock time."""
    return time.time()
