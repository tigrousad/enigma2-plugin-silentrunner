"""
SilentRunner – process management.

Runner   : manages a collection of Tasks.
Task     : represents a single launched script process.
"""

import os
import signal
import subprocess
import time
from enum import Enum, auto
from typing import Optional

from .utils import now_ts, format_elapsed, script_type


class TaskStatus(Enum):
    RUNNING = auto()
    FINISHED = auto()
    STOPPED = auto()
    FAILED = auto()


STATUS_LABEL = {
    TaskStatus.RUNNING:  "Running",
    TaskStatus.FINISHED: "Finished",
    TaskStatus.STOPPED:  "Stopped",
    TaskStatus.FAILED:   "Failed",
}


# ---------------------------------------------------------------------------
# Process-wide task registry
# ---------------------------------------------------------------------------
# SilentRunnerScreen.__init__ builds a brand-new Runner() every time the
# plugin is opened from the plugin menu (session.open() creates a fresh
# Screen instance, which creates a fresh Runner()). A Runner that stores its
# tasks as a plain instance list (self._tasks = []) therefore forgets every
# previously-launched script the moment the screen is closed and reopened —
# even though the scripts themselves are still alive (they were started with
# start_new_session=True specifically so they survive the screen closing).
#
# A Python *module* is only imported/executed once per Enigma2 process
# lifetime (later "from .runner import Runner" calls hit sys.modules and do
# not re-run this file), so a module-level list survives every screen
# open/close cycle for as long as Enigma2 itself keeps running. Every
# Runner() instance below shares this same list instead of allocating its
# own, which is what makes a still-running task visible again after you
# leave the plugin and come back.
#
# Scope of this fix, stated plainly: it survives closing/reopening the
# SilentRunnerScreen. It does NOT survive a full GUI restart (init 4) or a
# receiver reboot, because that ends the Python process this list lives in.
# Surviving that would require writing task state to disk (a PID file per
# task under /media/hdd or /tmp) and reconciling it against /proc on the next
# open — a reasonable follow-up if you need it, but a separate, larger change
# from what was asked for here, so it isn't included.
_SHARED_TASKS: "list[Task]" = []


class Task:
    """Represents one launched script process."""

    def __init__(self, path: str):
        self.path: str = path
        self.filename: str = os.path.basename(path)
        self.pid: int = -1
        self.process: Optional[subprocess.Popen] = None
        self.start_ts: float = now_ts()
        self.finish_ts: Optional[float] = None
        self.status: TaskStatus = TaskStatus.RUNNING
        self.return_code: Optional[int] = None

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def poll(self) -> None:
        """Update status by polling the subprocess (non-blocking)."""
        if self.status != TaskStatus.RUNNING:
            return
        if self.process is None:
            return
        rc = self.process.poll()
        if rc is not None:
            self.finish_ts = now_ts()
            self.return_code = rc
            if rc == 0:
                self.status = TaskStatus.FINISHED
            else:
                self.status = TaskStatus.FAILED

    @property
    def elapsed(self) -> float:
        """Elapsed seconds since the process started."""
        end = self.finish_ts if self.finish_ts is not None else now_ts()
        return end - self.start_ts

    @property
    def elapsed_str(self) -> str:
        return format_elapsed(self.elapsed)

    @property
    def status_label(self) -> str:
        return STATUS_LABEL[self.status]

    @property
    def pid_str(self) -> str:
        return str(self.pid) if self.pid > 0 else "—"

    def stop(self) -> None:
        """
        Gracefully stop the process.

        1. Send SIGTERM to the whole process group.
        2. Wait ~1 second.
        3. If still alive, send SIGKILL to the process group.
        """
        if self.status != TaskStatus.RUNNING:
            return
        if self.process is None:
            return

        try:
            pgid = os.getpgid(self.process.pid)
        except OSError:
            pgid = None

        # Step 1 – SIGTERM
        try:
            if pgid is not None:
                os.killpg(pgid, signal.SIGTERM)
            else:
                self.process.send_signal(signal.SIGTERM)
        except OSError:
            pass

        # Step 2 – wait ~1 second
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                break
            time.sleep(0.05)

        # Step 3 – SIGKILL if still alive
        if self.process.poll() is None:
            try:
                if pgid is not None:
                    os.killpg(pgid, signal.SIGKILL)
                else:
                    self.process.send_signal(signal.SIGKILL)
            except OSError:
                pass

        self.finish_ts = now_ts()
        self.return_code = self.process.poll()
        self.status = TaskStatus.STOPPED


# ---------------------------------------------------------------------------


class Runner:
    """Manages all Tasks for the current plugin session."""

    def __init__(self):
        # Deliberately NOT self._tasks = [] — see _SHARED_TASKS above.
        # Every Runner() instance points at the same process-wide list, so
        # tasks launched by a previous SilentRunnerScreen are still visible
        # (and still pollable) after the screen is closed and reopened.
        self._tasks: list[Task] = _SHARED_TASKS

    # ------------------------------------------------------------------
    # Read access
    # ------------------------------------------------------------------

    @property
    def tasks(self) -> list[Task]:
        return self._tasks

    @property
    def running_count(self) -> int:
        return sum(1 for t in self._tasks if t.status == TaskStatus.RUNNING)

    def is_running(self, path: str) -> bool:
        """Return True if a task for *path* is currently running."""
        return any(
            t.path == path and t.status == TaskStatus.RUNNING
            for t in self._tasks
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def launch(self, path: str) -> Optional[Task]:
        """
        Launch *path* as a detached subprocess.

        Returns the new Task, or None if the script is already running
        or if the launch fails (in which case a FAILED task is still
        appended so the user can see the error).
        """
        # Duplicate-protection
        if self.is_running(path):
            return None

        task = Task(path)
        self._tasks.append(task)

        stype = script_type(path)
        if stype == "py":
            cmd = ["/usr/bin/python3", path]
        elif stype == "sh":
            cmd = ["/bin/sh", path]
        else:
            task.status = TaskStatus.FAILED
            task.finish_ts = now_ts()
            return task

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
                start_new_session=True,
            )
            task.process = proc
            task.pid = proc.pid
        except Exception:
            task.status = TaskStatus.FAILED
            task.finish_ts = now_ts()

        return task

    def stop(self, task: Task) -> None:
        """Stop a single task."""
        task.stop()

    def stop_all(self) -> None:
        """Stop every currently running task."""
        for task in self._tasks:
            if task.status == TaskStatus.RUNNING:
                task.stop()

    def poll_all(self) -> None:
        """Poll every running task (call once per timer tick)."""
        for task in self._tasks:
            task.poll()

    def clear(self) -> None:
        """Remove all tasks (called when the plugin is closed)."""
        self.stop_all()
        self._tasks.clear()
