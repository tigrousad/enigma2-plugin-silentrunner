"""
SilentRunner – skin definition.

Defines a 1280x720 screen layout compatible with HD (1280x720) receivers.
The skin is registered via Components.Skin.addSkin() in plugin.py.

Layout
------
  [0, 0, 1280, 720]
  ┌─────────────────────────────────────────────────────────┐
  │ Header bar  (title + running count)              y=0–60 │
  ├──────────────────────────────┬──────────────────────────┤
  │ Tasks panel (40 %)           │ Explorer panel (60 %)    │
  │ x=0  w=510  y=60  h=600     │ x=520 w=760  y=60 h=600  │
  ├──────────────────────────────┴──────────────────────────┤
  │ Button bar                                      y=660   │
  └─────────────────────────────────────────────────────────┘
"""

SKIN = """
<screen name="SilentRunnerScreen" position="center,center" size="1280,720" zPosition="1"
          backgroundColor="#12141a" flags="wfNoBorder" title="SilentRunner">

    <!-- ── Background panels ───────────────────────────────────────── -->
    <widget name="bg_tasks" position="0,60" size="510,600"
            backgroundColor="#1a1d26" zPosition="1" />
    <widget name="bg_explorer" position="520,60" size="760,600"
            backgroundColor="#1a1d26" zPosition="1" />

    <!-- ── Header ───────────────────────────────────────────────────── -->
    <widget name="header_title" position="20,10" size="600,44"
            font="Regular;32" foregroundColor="#e8e8f0" backgroundColor="#12141a"
            halign="left" valign="center" zPosition="2" />
    <widget name="header_running" position="640,10" size="620,44"
            font="Regular;24" foregroundColor="#4caf50" backgroundColor="#12141a"
            halign="right" valign="center" zPosition="2" />

    <!-- ── Panel labels ─────────────────────────────────────────────── -->
    <widget name="label_tasks" position="10,62" size="490,28"
            font="Regular;20" foregroundColor="#8888aa" backgroundColor="#1a1d26"
            halign="left" valign="center" zPosition="3" />
    <widget name="label_explorer" position="530,62" size="740,28"
            font="Regular;20" foregroundColor="#8888aa" backgroundColor="#1a1d26"
            halign="left" valign="center" zPosition="3" />

    <!-- ── Task list ─────────────────────────────────────────────────── -->
    <widget name="task_list" position="4,92" size="506,562"
            backgroundColor="#1a1d26" foregroundColor="#e0e0e0"
            selectionPixmap="" selectionDisabled="0"
            scrollbarMode="showOnDemand" zPosition="4" />

    <!-- ── File list ─────────────────────────────────────────────────── -->
    <widget name="file_list" position="524,92" size="752,562"
            backgroundColor="#1a1d26" foregroundColor="#e0e0e0"
            selectionPixmap="" selectionDisabled="0"
            scrollbarMode="showOnDemand" zPosition="4" />

    <!-- ── Active-panel indicator (thin left border) ───────────────── -->
    <widget name="indicator_tasks"    position="0,60"  size="4,600"
            backgroundColor="#5c6bc0" zPosition="5" />
    <widget name="indicator_explorer" position="516,60" size="4,600"
            backgroundColor="#5c6bc0" zPosition="5" />

    <!-- ── Separator line ───────────────────────────────────────────── -->
    <widget name="sep" position="512,60" size="8,600"
            backgroundColor="#0d0f14" zPosition="2" />

    <!-- ── Bottom button bar ─────────────────────────────────────────── -->
    <!-- RED -->
    <widget name="btn_red_icon" position="10,668" size="30,30"
            pixmap="SilentRunner/icons/red.png" alphaTest="1" zPosition="5" />
    <widget name="btn_red" position="44,666" size="130,34"
            font="Regular;22" foregroundColor="#ef5350" backgroundColor="#12141a"
            halign="left" valign="center" zPosition="5" />

    <!-- GREEN -->
    <widget name="btn_green_icon" position="200,668" size="30,30"
            pixmap="SilentRunner/icons/green.png" alphaTest="1" zPosition="5" />
    <widget name="btn_green" position="234,666" size="130,34"
            font="Regular;22" foregroundColor="#66bb6a" backgroundColor="#12141a"
            halign="left" valign="center" zPosition="5" />

    <!-- YELLOW -->
    <widget name="btn_yellow_icon" position="390,668" size="30,30"
            pixmap="SilentRunner/icons/yellow.png" alphaTest="1" zPosition="5" />
    <widget name="btn_yellow" position="424,666" size="130,34"
            font="Regular;22" foregroundColor="#ffca28" backgroundColor="#12141a"
            halign="left" valign="center" zPosition="5" />

    <!-- BLUE -->
    <widget name="btn_blue_icon" position="580,668" size="30,30"
            pixmap="SilentRunner/icons/blue.png" alphaTest="1" zPosition="5" />
    <widget name="btn_blue" position="614,666" size="160,34"
            font="Regular;22" foregroundColor="#42a5f5" backgroundColor="#12141a"
            halign="left" valign="center" zPosition="5" />

    <!-- ── Path bar ──────────────────────────────────────────────────── -->
    <widget name="path_bar" position="524,656" size="752,50"
            font="Regular;18" foregroundColor="#8888aa" backgroundColor="#12141a"
            halign="left" valign="center" zPosition="5" />

  </screen>
"""
