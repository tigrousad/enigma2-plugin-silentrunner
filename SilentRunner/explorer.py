"""
SilentRunner – filesystem explorer state.

ExplorerState keeps track of the current directory and the list of
visible entries (dirs + runnable files).  It does not touch any UI.
"""

import os
from typing import NamedTuple

from .utils import safe_listdir, script_type


class Entry(NamedTuple):
    name: str       # display name
    path: str       # absolute path
    is_dir: bool    # True → directory, False → script file
    ftype: str      # '', 'sh', or 'py'


class ExplorerState:
    """Pure filesystem cursor – no Enigma2 dependencies."""

    ROOT = "/"

    def __init__(self):
        self._cwd: str = self.ROOT
        self._entries: list[Entry] = []
        self._cursor: int = 0
        self._refresh()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def cwd(self) -> str:
        return self._cwd

    @property
    def entries(self) -> list[Entry]:
        return self._entries

    @property
    def cursor(self) -> int:
        return self._cursor

    @cursor.setter
    def cursor(self, value: int) -> None:
        if self._entries:
            self._cursor = max(0, min(value, len(self._entries) - 1))

    @property
    def current_entry(self) -> Entry | None:
        if not self._entries:
            return None
        return self._entries[self._cursor]

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def enter(self) -> Entry | None:
        """
        Act on the current entry.

        - Directory → descend, return None.
        - Script    → return the Entry (caller should execute it).
        """
        entry = self.current_entry
        if entry is None:
            return None
        if entry.is_dir:
            self._cwd = entry.path
            self._cursor = 0
            self._refresh()
            return None
        return entry

    def go_up(self) -> None:
        """Navigate to the parent directory (stops at '/')."""
        if self._cwd == self.ROOT:
            return
        parent = os.path.dirname(self._cwd)
        if not parent:
            parent = self.ROOT
        child_name = os.path.basename(self._cwd)
        self._cwd = parent
        self._refresh()
        # Try to place cursor on the directory we came from.
        for i, e in enumerate(self._entries):
            if e.name == child_name:
                self._cursor = i
                break

    def move_up(self) -> None:
        if self._cursor > 0:
            self._cursor -= 1

    def move_down(self) -> None:
        if self._cursor < len(self._entries) - 1:
            self._cursor += 1

    def refresh(self) -> None:
        """Re-read the current directory from disk."""
        self._refresh()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        dirs, files = safe_listdir(self._cwd)
        entries = []

        # Parent directory entry (go-up) if not already at root
        if self._cwd != self.ROOT:
            parent = os.path.dirname(self._cwd) or self.ROOT
            entries.append(Entry(name="..", path=parent, is_dir=True, ftype=""))

        for name in dirs:
            path = os.path.join(self._cwd, name)
            entries.append(Entry(name=name, path=path, is_dir=True, ftype=""))

        for name in files:
            path = os.path.join(self._cwd, name)
            entries.append(Entry(name=name, path=path, is_dir=False,
                                  ftype=script_type(name)))

        self._entries = entries
        # Clamp cursor
        if self._entries:
            self._cursor = max(0, min(self._cursor, len(self._entries) - 1))
        else:
            self._cursor = 0
