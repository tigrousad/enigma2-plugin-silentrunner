# -*- coding: utf-8 -*-
"""
SilentRunner – listbox content builders.

File rows use the user-supplied PNG icons (folder/sh/py) loaded via loadPNG.
Task rows use coloured text badges (no PNG needed — always reliable).

Color constants: 0x00RRGGBB (Enigma2 ignores the high byte).
"""

from enigma import RT_HALIGN_LEFT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, gFont
from Components.MultiContent import (
    MultiContentEntryText,
    MultiContentEntryPixmapAlphaTest,
)

from .runner import TaskStatus
from .explorer import Entry

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
COLOR_RUNNING    = 0x004caf50   # green
COLOR_FINISHED   = 0x009e9e9e   # grey
COLOR_STOPPED    = 0x00ef5350   # red
COLOR_FAILED     = 0x00ff7043   # orange

COLOR_DIR        = 0x00e8e8f0   # white
COLOR_SH         = 0x00ffca28   # yellow
COLOR_PY         = 0x0042a5f5   # blue
COLOR_DIMMED     = 0x00888899
COLOR_DEFAULT    = 0x00cccccc

# ---------------------------------------------------------------------------
# Row geometry  (folder icon is 50×50, py/sh are 40×40)
# ---------------------------------------------------------------------------
ROW_HEIGHT   = 56      # tall enough for the 50×50 folder icon
ICON_W_LG    = 50      # folder
ICON_H_LG    = 50
ICON_W_SM    = 40      # py / sh
ICON_H_SM    = 40
ICON_X       = 6       # left margin before icon
ICON_GAP     = 14      # gap between right edge of icon and start of text

# Text starts after the largest possible icon + gap
TEXT_X       = ICON_X + ICON_W_LG + ICON_GAP   # = 70

BADGE_W      = 6       # coloured left-stripe for task rows
BADGE_X      = 2
TASK_GAP     = 8
TASK_TEXT_X  = BADGE_X + BADGE_W + TASK_GAP    # = 16

FONT_MAIN    = gFont("Regular", 26)   # big, readable filename font
FONT_SMALL   = gFont("Regular", 20)   # secondary info (pid, elapsed, status)
FONT_BADGE   = gFont("Regular", 17)   # tag labels

# ---------------------------------------------------------------------------
# Status → colour / label
# ---------------------------------------------------------------------------
_STATUS_COLOR = {
    TaskStatus.RUNNING:  COLOR_RUNNING,
    TaskStatus.FINISHED: COLOR_FINISHED,
    TaskStatus.STOPPED:  COLOR_STOPPED,
    TaskStatus.FAILED:   COLOR_FAILED,
}


def _solid_tag(x: int, y: int, w: int, h: int, color: int,
               text: str = "") -> MultiContentEntryText:
    """Solid-colour rectangle via a backcolor-filled MultiContentEntryText."""
    return MultiContentEntryText(
        pos=(x, y), size=(w, h),
        font=2,
        flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
        text=text,
        color=0x00111111, color_sel=0x00111111,
        backcolor=color,  backcolor_sel=color,
    )


def _pixmap_entry(pm, x: int, icon_w: int, icon_h: int) -> list:
    """Return a MultiContentEntryPixmapAlphaTest entry, or [] if pm is None."""
    if pm is None:
        return []
    y = max(0, (ROW_HEIGHT - icon_h) // 2)
    return [MultiContentEntryPixmapAlphaTest(
        pos=(x, y),
        size=(icon_w, icon_h),
        png=pm,
        flags=0,
    )]


# ---------------------------------------------------------------------------
# Public builders
# ---------------------------------------------------------------------------

def build_file_row(entry: Entry, icon_map: dict, item_width: int) -> list:
    """
    File / directory row:
      [entry]  [PNG icon]  [name in large font]
    """
    if entry.is_dir:
        pm        = icon_map.get("folder")
        iw, ih    = ICON_W_LG, ICON_H_LG
        name_color = COLOR_DIR if entry.name != ".." else COLOR_DIMMED
    elif entry.ftype == "sh":
        pm        = icon_map.get("sh")
        iw, ih    = ICON_W_SM, ICON_H_SM
        name_color = COLOR_SH
    elif entry.ftype == "py":
        pm        = icon_map.get("py")
        iw, ih    = ICON_W_SM, ICON_H_SM
        name_color = COLOR_PY
    else:
        pm        = None
        iw, ih    = ICON_W_SM, ICON_H_SM
        name_color = COLOR_DEFAULT

    name_w = item_width - TEXT_X - 8

    # وضع كائن البيانات entry في بداية القائمة ليتعرف عليه Enigma2 ويظهر الشريط الأزرق
    row = [entry]

    pm_entries = _pixmap_entry(pm, ICON_X, iw, ih)
    if pm_entries:
        row.extend(pm_entries)

    row.append(MultiContentEntryText(
        pos=(TEXT_X, 0), size=(name_w, ROW_HEIGHT),
        font=0,
        flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
        text=entry.name,
        color=name_color, color_sel=name_color,
    ))
    return row


def build_task_row(task, icon_map: dict, item_width: int) -> list:
    """
    Task row:
      [task]  [colour stripe]  [name]  [pid]  [elapsed]  [status tag]
    """
    color  = _STATUS_COLOR.get(task.status, COLOR_DEFAULT)
    slabel = task.status_label

    STATUS_W  = 80
    ELAPSED_W = 88
    PID_W     = 72
    name_w    = item_width - TASK_TEXT_X - PID_W - ELAPSED_W - STATUS_W - 8

    pid_x     = TASK_TEXT_X + max(name_w, 60)
    elapsed_x = pid_x + PID_W
    status_x  = elapsed_x + ELAPSED_W

    stripe_y  = 6
    stripe_h  = ROW_HEIGHT - 12

    return [
        # وضع كائن البيانات task في بداية القائمة لتمكين التحديد الأزرق
        task,

        # Left colour stripe
        _solid_tag(BADGE_X, stripe_y, BADGE_W, stripe_h, color),

        # Script name
        MultiContentEntryText(
            pos=(TASK_TEXT_X, 0), size=(max(name_w, 60), ROW_HEIGHT),
            font=0,
            flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
            text=task.filename,
            color=color, color_sel=color,
        ),

        # PID
        MultiContentEntryText(
            pos=(pid_x, 0), size=(PID_W, ROW_HEIGHT),
            font=1,
            flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
            text=task.pid_str,
            color=COLOR_DIMMED, color_sel=COLOR_DIMMED,
        ),

        # Elapsed
        MultiContentEntryText(
            pos=(elapsed_x, 0), size=(ELAPSED_W, ROW_HEIGHT),
            font=1,
            flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
            text=task.elapsed_str,
            color=COLOR_DIMMED, color_sel=COLOR_DIMMED,
        ),

        # Status tag
        _solid_tag(status_x, 8, STATUS_W - 4, ROW_HEIGHT - 16, color, slabel),
    ]


def make_listbox_style(lb_component, item_width: int) -> None:
    """Apply fonts and item height to an eListboxPythonMultiContent."""
    l = lb_component.l
    l.setFont(0, FONT_MAIN)     # index 0 → filenames / task names
    l.setFont(1, FONT_SMALL)    # index 1 → pid / elapsed
    l.setFont(2, FONT_BADGE)    # index 2 → badge labels
    l.setItemHeight(ROW_HEIGHT)