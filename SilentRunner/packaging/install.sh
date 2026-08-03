#!/bin/sh
# install.sh – Direct and Remote install helper for SilentRunner

set -e

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/SilentRunner"

# تحديد مسار الملفات بناءً على طريقة التشغيل (محلية أو مؤقتة)
if [ -d "$(dirname "$0")/../SilentRunner" ]; then
    SRCDIR="$(cd "$(dirname "$0")/../SilentRunner" && pwd)"
elif [ -d "$(dirname "$0")" ] && [ -f "$(dirname "$0")/plugin.py" ]; then
    SRCDIR="$(cd "$(dirname "$0")" && pwd)"
else
    # في حال تم تشغيله مباشرة من مجلد مؤقت أو رابط خارجي
    SRCDIR="/tmp/SilentRunner"
fi

echo "[SilentRunner] Installing to $PLUGIN_DIR ..."

mkdir -p "$PLUGIN_DIR/icons" "$PLUGIN_DIR/locale"

# نسخ الملفات الأساسية مع التحقق من وجودها
for f in __init__.py plugin.py main.py runner.py explorer.py \
          widgets.py skin.py utils.py version.py plugin.png; do
    if [ -f "$SRCDIR/$f" ]; then
        cp "$SRCDIR/$f" "$PLUGIN_DIR/$f"
        echo "  copied $f"
    fi
done

# نسخ الأيقونات إن وجدت
if [ -d "$SRCDIR/icons" ]; then
    cp "$SRCDIR/icons/"*.png "$PLUGIN_DIR/icons/" 2>/dev/null || true
    echo "  copied icons/"
fi

echo ""
echo "[SilentRunner] Installation complete."
echo "Restart Enigma2 or reload the plugin list to activate SilentRunner."
echo ""
echo "  killall -HUP enigma2   # soft restart"
echo "  init 6                 # full reboot"
