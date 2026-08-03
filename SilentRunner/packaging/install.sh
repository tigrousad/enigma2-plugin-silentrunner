#!/bin/sh
# SilentRunner Online Installer

set -e

BASE="https://raw.githubusercontent.com/tigrousad/enigma2-plugin-silentrunner/main/SilentRunner"

PLUGIN="/usr/lib/enigma2/python/Plugins/Extensions/SilentRunner"
TMP="/tmp/SilentRunner"

echo "[SilentRunner] Downloading..."

rm -rf "$TMP"
mkdir -p "$TMP"
mkdir -p "$TMP/icons"
mkdir -p "$TMP/locale"

# الملفات الرئيسية
for f in \
__init__.py \
plugin.py \
main.py \
runner.py \
explorer.py \
widgets.py \
skin.py \
utils.py \
version.py \
plugin.png
do
    wget -q -O "$TMP/$f" "$BASE/$f"
done

# الأيقونات
for f in \
blue.png \
failed.png \
finished.png \
folder.png \
green.png \
plugin.png \
py.png \
red.png \
running.png \
sh.png \
stopped.png \
yellow.png
do
    wget -q -O "$TMP/icons/$f" "$BASE/icons/$f"
done

# locale
wget -q -O "$TMP/locale/readme.txt" "$BASE/locale/readme.txt"

echo "[SilentRunner] Installing..."

rm -rf "$PLUGIN"
mkdir -p /usr/lib/enigma2/python/Plugins/Extensions

cp -a "$TMP" "$PLUGIN"

if command -v python3 >/dev/null 2>&1; then
    python3 -m compileall "$PLUGIN" >/dev/null 2>&1 || true
fi

rm -rf "$TMP"

sync

echo ""
echo "[SilentRunner] Installation completed successfully."
echo ""
echo "Restart Enigma2:"
echo "killall -HUP enigma2"
echo "or"
echo "init 6"
