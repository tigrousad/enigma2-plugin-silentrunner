
# SilentRunner 🚀
**A powerful background script execution and management plugin for Enigma2 receivers.**
> Developed with ❤️ by **tigrousad**


**Version:** 1.0.0  
**Platform:** Enigma2 / OpenATV 7.6+ / Python 3.13+  
**Tested on:** Vu+ Solo2 (compatible with any OpenATV receiver)

---

## Overview

SilentRunner is a lightweight background script manager for Enigma2.  
It lets you browse the Linux filesystem and execute **Shell (.sh)** and **Python (.py)** scripts silently in the background — without opening any console window.

---

## Features

- Two-panel HD layout (1280×720): Explorer (right 60%) + Running Tasks (left 40%)
- Browse filesystem from `/`, directories first, `.sh`/`.py` files only
- Execute scripts with one keypress — no confirmation dialog
- Duplicate-run protection (one instance per script path)
- Graceful stop: SIGTERM → wait 1 s → SIGKILL on process group
- Live status updates every second (Running / Finished / Stopped / Failed)
- Color-coded status display
- No configuration, no settings, no popups

---

## Installation

### Option A — Direct file copy (development)

```sh
# On your PC / build host:
scp -r SilentRunner/ root@<receiver-ip>:/tmp/

# On the receiver:
cd /tmp
sh SilentRunner/packaging/install.sh
```

### Option B — Build IPK (requires Linux with `make`, Python 3, and `ar`)

```sh
cd SilentRunner/packaging
make          # builds ../icons/*.png and the .ipk
# then scp the .ipk to the receiver and:
opkg install enigma2-plugin-extensions-silentrunner_1.0.0_all.ipk
```

After installation, restart Enigma2:

```sh
killall -HUP enigma2   # soft restart
# or
init 6                 # full reboot
```

---

## File Structure

```
SilentRunner/
├── __init__.py      – package marker
├── plugin.py        – Enigma2 plugin registration
├── main.py          – SilentRunnerScreen (main UI)
├── runner.py        – Runner + Task (process management)
├── explorer.py      – ExplorerState (filesystem cursor)
├── widgets.py       – MultiContent row builders
├── skin.py          – Skin XML (HD 1280×720 layout)
├── utils.py         – Utility helpers
├── version.py       – Version constants
├── plugin.png       – Plugin menu icon (48×48)
├── icons/
│   ├── make_icons.py   – Icon generator (stdlib only)
│   ├── folder.png
│   ├── sh.png
│   ├── py.png
│   ├── running.png
│   ├── finished.png
│   ├── stopped.png
│   ├── failed.png
│   ├── red.png
│   ├── green.png
│   ├── yellow.png
│   └── blue.png
├── locale/          – Reserved for future translations
└── packaging/
    ├── CONTROL      – IPK package metadata
    ├── Makefile     – Build + package helper
    └── install.sh   – Direct SSH install script
```

---

## Key Bindings

| Key        | Action                                              |
|------------|-----------------------------------------------------|
| OK         | Explorer: enter folder / run script. Tasks: stop selected |
| LEFT/RIGHT | Switch active panel                                 |
| UP/DOWN    | Move cursor in active panel                         |
| RED        | Exit plugin (scripts keep running)                  |
| GREEN      | Run highlighted script (alias for OK in explorer)   |
| YELLOW     | Stop selected running task                          |
| BLUE       | Stop all running tasks                              |
| BACK       | Navigate up in explorer / switch to explorer panel  |

---

## Colors

| Element   | Color  |
|-----------|--------|
| Running   | Green  |
| Finished  | Grey   |
| Stopped   | Red    |
| Failed    | Orange |
| Directory | White  |
| .sh file  | Yellow |
| .py file  | Blue   |

---

## Design Notes

- Uses `subprocess.Popen` with `start_new_session=True` — never `Console.ePopen()`
- Uses `eListboxPythonMultiContent` — never `eListboxPythonStringContent`
- Uses `eTimer` for polling — never reads `/proc` or executes `ps`
- No global variables; all state owned by `Runner` and `ExplorerState`
- Session state is ephemeral — task list is cleared on plugin close
