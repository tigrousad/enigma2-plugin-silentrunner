# -*- coding: utf-8 -*-
"""
SilentRunner – main plugin screen.

Two-panel layout:
  LEFT  (40 %)  →  Running Tasks
  RIGHT (60 %)  →  Filesystem Explorer

Key bindings:
  LEFT / RIGHT  – switch active panel
  UP / DOWN     – move cursor within the active panel
  OK            – Explorer: open folder / run script
                  Tasks:    stop selected task
  RED           – exit plugin (scripts keep running)
  GREEN         – run highlighted script (alias for OK in explorer)
  YELLOW        – stop selected running task
  BLUE          – stop all running tasks
  BACK          – navigate up in explorer / exit
"""

import os

from enigma import eListboxPythonMultiContent, eTimer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText

from .runner import Runner, TaskStatus
from .explorer import ExplorerState
from .widgets import (
    build_task_row, build_file_row, make_listbox_style, ROW_HEIGHT
)
from .skin import SKIN
from .version import PLUGIN_NAME


class SilentRunnerScreen(Screen):
    """Main SilentRunner screen."""

    # Register skin
    skin = SKIN

    def __init__(self, session):
        Screen.__init__(self, session)

        self._runner   = Runner()
        self._explorer = ExplorerState()
        self._active_panel = "explorer"   # "explorer" | "tasks"

        # ── Load icons ────────────────────────────────────────────────
        self._icon_map = self._load_icons()

        # ── Static labels ───────────────────────────────────────────
        self["header_title"]   = Label(PLUGIN_NAME)
        self["header_running"] = Label("Running: 0")
        self["label_tasks"]    = Label("Running Tasks")
        self["label_explorer"] = Label(self._explorer.cwd)
        self["path_bar"]       = Label(self._explorer.cwd)

        # ── Button labels ────────────────────────────────────────────
        self["btn_red"]    = Label("Exit")
        self["btn_green"]  = Label("Run")
        self["btn_yellow"] = Label("Stop")
        self["btn_blue"]   = Label("Stop All")

        # ── Background / indicator placeholders ──────────────────────
        from Components.Pixmap import Pixmap
        self["bg_tasks"]            = Pixmap()
        self["bg_explorer"]         = Pixmap()
        self["sep"]                 = Pixmap()
        self["indicator_tasks"]     = Pixmap()
        self["indicator_explorer"]  = Pixmap()

        # Button icons (color dots)
        self["btn_red_icon"]    = Pixmap()
        self["btn_green_icon"]  = Pixmap()
        self["btn_yellow_icon"] = Pixmap()
        self["btn_blue_icon"]   = Pixmap()

        # ── Listboxes ─────────────────────────────────────────────────
        self["task_list"] = MenuList([], enableWrapAround=True,
                                     content=eListboxPythonMultiContent)
        self["file_list"] = MenuList([], enableWrapAround=False,
                                     content=eListboxPythonMultiContent)

        # ── Key map ───────────────────────────────────────────────────
        self["actions"] = ActionMap(
            ["OkCancelActions", "DirectionActions",
             "ColorActions", "SilentRunnerActions"],
            {
                "ok":     self._action_ok,
                "cancel": self._action_back,
                "back":   self._action_back,
                "up":     self._action_up,
                "down":   self._action_down,
                "left":   self._action_switch_panel,
                "right":  self._action_switch_panel,
                "red":    self._action_exit,
                "green":  self._action_run,
                "yellow": self._action_stop,
                "blue":   self._action_stop_all,
            },
            -1,
        )

        # ── Timer (1-second refresh) ──────────────────────────────────
        self._timer = eTimer()
        self._timer.callback.append(self._on_timer)
        self._timer.start(1000, False)

        self.onLayoutFinish.append(self._on_layout_finish)
        self.onClose.append(self._on_close)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _on_layout_finish(self):
        """Apply listbox fonts and perform the first render."""
        try:
            make_listbox_style(self["task_list"], 506)
            make_listbox_style(self["file_list"], 752)
        except Exception:
            pass
        self._render_explorer()
        self._render_tasks()
        self._update_indicators()

    def _on_close(self):
        try:
            self._timer.callback.remove(self._on_timer)
        except Exception:
            pass
        try:
            self._timer.stop()
        except Exception:
            pass
        for task in self._runner.tasks:
            try:
                if task.process is not None and task.process.poll() is not None:
                    task.process.wait()
            except Exception:
                pass

    def _on_timer(self):
        """Tick: poll running processes, update task list."""
        self._runner.poll_all()
        self._render_tasks()
        self._update_header()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_explorer(self):
        rows = [
            build_file_row(e, self._icon_map, 752)
            for e in self._explorer.entries
        ]
        self["file_list"].setList(rows)
        self["file_list"].moveToIndex(self._explorer.cursor)
        cwd = self._explorer.cwd
        self["label_explorer"].setText(cwd)
        self["path_bar"].setText(cwd)

    def _render_tasks(self):
        prev_idx = self["task_list"].getSelectedIndex()

        rows = [
            build_task_row(t, self._icon_map, 506)
            for t in self._runner.tasks
        ]
        self["task_list"].setList(rows)

        if prev_idx is not None and rows:
            self["task_list"].moveToIndex(min(prev_idx, len(rows) - 1))

        self._update_header()

    def _update_header(self):
        self["header_running"].setText(f"Running: {self._runner.running_count}")

    def _update_indicators(self):
        tasks_active    = self._active_panel == "tasks"
        explorer_active = self._active_panel == "explorer"

        # توجيه التركيز للمكون الفعال لكي يظهر الشريط الأزرق
        try:
            if explorer_active:
                self.setCurrentFocus(self["file_list"])
            else:
                self.setCurrentFocus(self["task_list"])
        except Exception:
            pass

        try:
            if tasks_active:
                self["indicator_tasks"].show()
                self["indicator_explorer"].hide()
            else:
                self["indicator_tasks"].hide()
                self["indicator_explorer"].show()
        except Exception:
            pass

        try:
            self["task_list"].instance.setSelectionEnable(tasks_active)
            self["file_list"].instance.setSelectionEnable(explorer_active)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Key actions
    # ------------------------------------------------------------------

    def _action_ok(self):
        if self._active_panel == "explorer":
            self._run_or_enter()
        else:
            self._stop_selected_task()

    def _action_back(self):
        if self._active_panel == "explorer":
            if self._explorer.cwd == ExplorerState.ROOT:
                self.close()
            else:
                self._explorer.go_up()
                self._render_explorer()
        else:
            self._action_switch_panel()

    def _action_up(self):
        if self._active_panel == "explorer":
            self._explorer.move_up()
            self["file_list"].moveToIndex(self._explorer.cursor)
        else:
            self["task_list"].up()

    def _action_down(self):
        if self._active_panel == "explorer":
            self._explorer.move_down()
            self["file_list"].moveToIndex(self._explorer.cursor)
        else:
            self["task_list"].down()

    def _action_switch_panel(self):
        self._active_panel = (
            "tasks" if self._active_panel == "explorer" else "explorer"
        )
        self._update_indicators()

    def _action_exit(self):
        self._timer.stop()
        self.close()

    def _action_run(self):
        if self._active_panel == "explorer":
            entry = self._explorer.current_entry
            if entry is not None and not entry.is_dir:
                self._runner.launch(entry.path)
                self._render_tasks()

    def _action_stop(self):
        self._stop_selected_task()

    def _action_stop_all(self):
        self._runner.stop_all()
        self._render_tasks()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _run_or_enter(self):
        entry = self._explorer.enter()
        if entry is None:
            self._render_explorer()
        else:
            self._runner.launch(entry.path)
            self._render_tasks()

    def _stop_selected_task(self):
        idx = self["task_list"].getSelectedIndex()
        tasks = self._runner.tasks
        if idx is None or not tasks:
            return
        if 0 <= idx < len(tasks):
            task = tasks[idx]
            if task.status == TaskStatus.RUNNING:
                self._runner.stop(task)
                self._render_tasks()

    def _load_icons(self) -> dict:
        try:
            from Tools.LoadPixmap import LoadPixmap
        except ImportError:
            return {}

        try:
            from enigma import getDesktop
            desktop = getDesktop(0)
        except Exception:
            desktop = None

        base = os.path.join(os.path.dirname(__file__), "icons")
        names = {
            "folder": "folder.png",
            "sh":     "sh.png",
            "py":     "py.png",
        }
        result = {}
        for key, filename in names.items():
            full_path = os.path.join(base, filename)
            try:
                result[key] = LoadPixmap(full_path, desktop=desktop, cached=True)
            except Exception:
                result[key] = None
        return result