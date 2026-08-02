#!/usr/bin/env python3
"""
Generates all SilentRunner PNG icons (24×24) using only stdlib.

Run once to populate the icons/ directory:
    python3 make_icons.py

No Pillow or other dependencies required.
"""

import os
import struct
import zlib


def make_png(width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    """
    Create a minimal RGBA PNG from a flat list of (r, g, b, a) tuples.
    pixels must contain width*height entries, in row-major order.
    """
    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)

    # Build raw scanlines (filter byte 0x00 prepended)
    raw = bytearray()
    for row in range(height):
        raw.append(0)  # filter = None
        for col in range(width):
            r, g, b, a = pixels[row * width + col]
            raw += bytes([r, g, b, a])
    idat_data = zlib.compress(bytes(raw), 9)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr_data)
        + chunk(b"IDAT", idat_data)
        + chunk(b"IEND", b"")
    )
    return png


def circle_pixels(
    size: int,
    fg: tuple[int, int, int, int],
    bg: tuple[int, int, int, int] = (0, 0, 0, 0),
    radius: float | None = None,
) -> list[tuple[int, int, int, int]]:
    """Filled antialiased circle."""
    if radius is None:
        radius = size / 2.0 - 1
    cx = cy = size / 2.0
    pixels = []
    for row in range(size):
        for col in range(size):
            dx = col + 0.5 - cx
            dy = row + 0.5 - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= radius - 0.7:
                pixels.append(fg)
            elif dist <= radius + 0.3:
                # Simple anti-alias blend
                t = (radius + 0.3 - dist) / 1.0
                t = max(0.0, min(1.0, t))
                r = int(fg[0] * t + bg[0] * (1 - t))
                g = int(fg[1] * t + bg[1] * (1 - t))
                b = int(fg[2] * t + bg[2] * (1 - t))
                a = int(fg[3] * t + bg[3] * (1 - t))
                pixels.append((r, g, b, a))
            else:
                pixels.append(bg)
    return pixels


def folder_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Simple folder shape."""
    fg = (232, 232, 240, 255)
    dark = (180, 180, 200, 255)
    bg = (0, 0, 0, 0)
    pixels = []
    tab_h = max(2, size // 6)
    body_y = tab_h
    for row in range(size):
        for col in range(size):
            in_tab   = (row < tab_h and col < size // 2)
            in_body  = (body_y <= row < size - 2 and 1 <= col < size - 1)
            if in_tab:
                pixels.append(dark)
            elif in_body:
                pixels.append(fg)
            else:
                pixels.append(bg)
    return pixels


def sh_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Yellow circle with 'S' suggestion (just a yellow dot for simplicity)."""
    return circle_pixels(size, (255, 202, 40, 255))


def py_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Blue circle for Python."""
    return circle_pixels(size, (66, 165, 245, 255))


def plugin_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Teal circle for plugin icon."""
    return circle_pixels(size, (38, 198, 218, 255))


def running_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Green circle."""
    return circle_pixels(size, (76, 175, 80, 255))


def finished_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Grey circle."""
    return circle_pixels(size, (158, 158, 158, 255))


def stopped_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Red circle."""
    return circle_pixels(size, (239, 83, 80, 255))


def failed_pixels(size: int) -> list[tuple[int, int, int, int]]:
    """Orange circle."""
    return circle_pixels(size, (255, 112, 67, 255))


# Button indicator dots (small, solid colour)
def dot_red(size: int)    -> list: return circle_pixels(size, (239, 83, 80, 255))
def dot_green(size: int)  -> list: return circle_pixels(size, (76, 175, 80, 255))
def dot_yellow(size: int) -> list: return circle_pixels(size, (255, 202, 40, 255))
def dot_blue(size: int)   -> list: return circle_pixels(size, (66, 165, 245, 255))


ICONS = {
    "plugin.png":   plugin_pixels,
    "running.png":  running_pixels,
    "finished.png": finished_pixels,
    "stopped.png":  stopped_pixels,
    "failed.png":   failed_pixels,
    "red.png":      dot_red,
    "green.png":    dot_green,
    "yellow.png":   dot_yellow,
    "blue.png":     dot_blue,
}

# folder.png / sh.png / py.png عمدًا غير موجودة في هذا القاموس أعلاه —
# هذه أيقوناتك الثابتة الخاصة، ولن يُعيد هذا السكربت توليدها أو الكتابة
# فوقها أبدًا مهما شُغّل من مرات.

ICON_SIZE = 24   # 24×24 px
PLUGIN_ICON_SIZE = 48  # plugin.png larger


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for filename, pixel_fn in ICONS.items():
        size = PLUGIN_ICON_SIZE if filename == "plugin.png" else ICON_SIZE
        pixels = pixel_fn(size)
        data = make_png(size, size, pixels)
        out_path = os.path.join(script_dir, filename)
        with open(out_path, "wb") as f:
            f.write(data)
        print(f"  wrote {filename}  ({size}×{size})")

    # Also write plugin.png one directory up (plugin root)
    parent = os.path.dirname(script_dir)
    plugin_pm = make_png(PLUGIN_ICON_SIZE, PLUGIN_ICON_SIZE, plugin_pixels(PLUGIN_ICON_SIZE))
    out = os.path.join(parent, "plugin.png")
    with open(out, "wb") as f:
        f.write(plugin_pm)
    print(f"  wrote ../plugin.png  ({PLUGIN_ICON_SIZE}×{PLUGIN_ICON_SIZE})")


if __name__ == "__main__":
    main()
