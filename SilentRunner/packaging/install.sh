#!/bin/sh
# install.sh – Direct install helper (run ON the receiver via SSH)
#
# Copy the SilentRunner directory tree to the receiver first, then run
# this script from the root of the copied directory.
#
# Usage:
#   scp -r SilentRunner/ root@<receiver-ip>:/tmp/
#   ssh root@<receiver-ip> "cd /tmp && sh SilentRunner/packaging/install.sh"

set -e

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/SilentRunner"
SRCDIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "[SilentRunner] Installing to $PLUGIN_DIR ..."

mkdir -p "$PLUGIN_DIR/icons" "$PLUGIN_DIR/locale"

for f in __init__.py plugin.py main.py runner.py explorer.py \
          widgets.py skin.py utils.py version.py plugin.png; do
    cp "$SRCDIR/$f" "$PLUGIN_DIR/$f"
    echo "  copied $f"
done

cp "$SRCDIR/icons/"*.png "$PLUGIN_DIR/icons/" 2>/dev/null || true
echo "  copied icons/"

echo ""
echo "[SilentRunner] Installation complete."
echo "Restart Enigma2 or reload the plugin list to activate SilentRunner."
echo ""
echo "  killall -HUP enigma2   # soft restart"
echo "  init 6                 # full reboot"
