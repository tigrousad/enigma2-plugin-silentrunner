#!/bin/sh
# SilentRunner Online Installer (robust)

set -e

BASE="https://raw.githubusercontent.com/tigrousad/enigma2-plugin-silentrunner/main/SilentRunner"

PLUGIN="/usr/lib/enigma2/python/Plugins/Extensions/SilentRunner"
TMP="/tmp/SilentRunner"

# download URL -> out -> optional_expected_sha
# Robust strategy:
# 1) Prefer python3 streaming downloader (better socket control) if available
# 2) Try curl with --http1.1, timeouts, retries and speed checks
# 3) If curl GET stalls, use ranged chunked downloads (1 MiB chunks)
# 4) Fallback to wget
# Writes to a .part file then renames on success

download() {
    url="$1"
    out="$2"
    expected_sha="$3"
    tmp="${out}.part"
    mkdir -p "$(dirname "$out")"

    verify_sha() {
        if [ -z "$expected_sha" ]; then
            return 0
        fi
        if command -v sha256sum >/dev/null 2>&1; then
            got=$(sha256sum "$tmp" | awk '{print $1}')
        elif command -v python3 >/dev/null 2>&1; then
            got=$(python3 - <<PY
import sys,hashlib
h=hashlib.sha256()
with open('$tmp','rb') as f:
    for b in iter(lambda: f.read(65536), b''):
        h.update(b)
print(h.hexdigest())
PY
)
        else
            echo "[SilentRunner] No sha256 verification tool available" >&2
            return 1
        fi
        if [ "$got" = "$expected_sha" ]; then
            return 0
        else
            echo "[SilentRunner] SHA256 mismatch: expected $expected_sha got $got" >&2
            return 1
        fi
    }

    rm -f "$tmp"

    # 1) Python downloader (recommended when available)
    if command -v python3 >/dev/null 2>&1; then
        echo "[SilentRunner] using python3 downloader for $url"
        # run python code and check exit status explicitly (avoid complex if-with-heredoc in sh)
        python3 - "$url" "$tmp" <<'PY'
import sys,ssl,urllib.request,socket
url=sys.argv[1]
out=sys.argv[2]
req=urllib.request.Request(url, headers={'User-Agent':'silent-runner-installer/1.0','Accept-Encoding':'identity','Connection':'close'})
ctx=ssl.create_default_context()
# short connect timeout, longer read timeout via socket
try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        raw = getattr(r, 'fp', None)
        sock = None
        try:
            sock = raw.raw._sock
            sock.settimeout(30)
        except Exception:
            pass
        with open(out, 'wb') as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)
    sys.exit(0)
except Exception as e:
    sys.stderr.write('python downloader error: %s\n' % e)
    sys.exit(2)
PY
        rc=$?
        if [ $rc -eq 0 ]; then
            # python wrote to tmp
            if [ -f "$tmp" ] || [ -f "$out" ]; then
                if [ -f "$out" ] && [ ! -f "$tmp" ]; then
                    mv "$out" "$tmp" || true
                fi
                if verify_sha; then mv "$tmp" "$out"; return 0; fi
            fi
            echo "[SilentRunner] python downloader succeeded but sha check failed or file missing" >&2
        else
            echo "[SilentRunner] python downloader failed (rc=$rc), falling back" >&2
        fi
    fi

    # 2) curl GET
    if command -v curl >/dev/null 2>&1; then
        echo "[SilentRunner] trying curl GET for $url"
        if curl -f --silent --show-error --location --http1.1 \
            --connect-timeout 10 --max-time 300 \
            --retry 4 --retry-delay 2 --retry-max-time 60 \
            -H "Accept-Encoding: identity" -o "$tmp" "$url"; then
            if verify_sha; then mv "$tmp" "$out"; return 0; else echo "[SilentRunner] curl download sha mismatch" >&2; fi
        else
            echo "[SilentRunner] curl GET failed or stalled, will try ranged fallback" >&2
        fi

        # 3) ranged chunked download fallback
        echo "[SilentRunner] starting ranged chunked download"
        CHUNK=1048576
        pos=0
        rm -f "$tmp"
        while :; do
            end=$((pos + CHUNK - 1))
            echo "[SilentRunner] downloading bytes ${pos}-${end} ..."
            if curl -f --silent --show-error --location --http1.1 \
                --connect-timeout 10 --max-time 120 \
                -H "Accept-Encoding: identity" --range "${pos}-${end}" -o "${tmp}.chunk" "$url"; then
                cat "${tmp}.chunk" >> "$tmp"
                chunk_size=$(stat -c%s "${tmp}.chunk" 2>/dev/null || echo 0)
                rm -f "${tmp}.chunk"
                if [ "$chunk_size" -lt "$CHUNK" ] || [ "$chunk_size" = "0" ]; then
                    break
                fi
                pos=$((pos + chunk_size))
            else
                echo "[SilentRunner] chunk request failed at ${pos}, retrying up to 3 times" >&2
                tries=0
                success=0
                while [ "$tries" -lt 3 ]; do
                    sleep $((2 ** tries))
                    if curl -f --silent --show-error --location --http1.1 \
                        --connect-timeout 10 --max-time 120 \
                        -H "Accept-Encoding: identity" --range "${pos}-${end}" -o "${tmp}.chunk" "$url"; then
                        cat "${tmp}.chunk" >> "$tmp"
                        rm -f "${tmp}.chunk"
                        success=1
                        break
                    fi
                    tries=$((tries+1))
                done
                if [ "$success" -eq 0 ]; then
                    echo "[SilentRunner] failed to download chunk at ${pos} after retries" >&2
                    break
                else
                    # got a chunk, continue
                    chunk_size=$(stat -c%s "${tmp}.chunk" 2>/dev/null || echo 0)
                    if [ "$chunk_size" -lt "$CHUNK" ] || [ "$chunk_size" = "0" ]; then
                        break
                    fi
                    pos=$((pos + chunk_size))
                fi
            fi
        done

        if [ -f "$tmp" ] && [ -s "$tmp" ]; then
            if verify_sha; then mv "$tmp" "$out"; return 0; else echo "[SilentRunner] ranged download sha mismatch" >&2; fi
        fi
    fi

    # 4) fallback wget (BusyBox or GNU)
    if command -v wget >/dev/null 2>&1; then
        echo "[SilentRunner] trying wget for $url"
        # BusyBox wget may not support --timeout names the same; use --tries and --timeout
        if wget -q --tries=4 --timeout=15 -O "$tmp" "$url"; then
            if verify_sha; then mv "$tmp" "$out"; return 0; else echo "[SilentRunner] wget sha mismatch" >&2; fi
        else
            echo "[SilentRunner] wget failed" >&2
        fi
    fi

    echo "[SilentRunner] all download methods failed for $url" >&2
    rm -f "$tmp"
    return 1
}


echo "[SilentRunner] Downloading..."

rm -rf "$TMP"
mkdir -p "$TMP"
mkdir -p "$TMP/icons"
mkdir -p "$TMP/locale"

# main files
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
    download "$BASE/$f" "$TMP/$f"
done

# icons
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
    download "$BASE/icons/$f" "$TMP/icons/$f"
done

# locale
download "$BASE/locale/readme.txt" "$TMP/locale/readme.txt"

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
