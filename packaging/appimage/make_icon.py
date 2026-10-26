#!/usr/bin/env python3
"""Draw an original 256x256 icon for the KOF '97 recompilation.

No SNK artwork is used: a dark field, a red diagonal band, and block letters
drawn from a tiny bitmap font.
"""
import os
import struct
import zlib

W = H = 256
px = bytearray(W * H * 3)


def put(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = r
        px[i + 1] = g
        px[i + 2] = b


def rect(x0, y0, x1, y1, r, g, b):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            put(x, y, r, g, b)


# Background: deep blue-black with a vertical gradient.
for y in range(H):
    for x in range(W):
        put(x, y, 6 + y // 40, 8 + y // 32, 20 + y // 14)

# Red diagonal band.
for y in range(H):
    for x in range(W):
        if 44 <= (x + y) % 256 <= 78:
            put(x, y, 176, 26, 30)

# Dark panel behind the lettering.
rect(10, 74, 246, 196, 8, 8, 14)
rect(12, 76, 244, 194, 14, 10, 22)

# 5x7 bitmap font for the few glyphs used.
FONT = {
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
}


def draw_text(text, x, y, scale, r, g, b):
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph:
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        rect(cx + gx * scale, y + gy * scale,
                             cx + (gx + 1) * scale, y + (gy + 1) * scale, r, g, b)
        cx += 6 * scale


draw_text("KOF", 40, 88, 8, 244, 214, 62)
draw_text("'97", 92, 150, 6, 240, 72, 46)

# A thin baseline and a few speed streaks.
rect(24, 176, 232, 180, 120, 20, 24)
for i, y in enumerate((188, 194, 200)):
    rect(40 + i * 12, y, 216 - i * 24, y + 2, 60, 20, 26)

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += px[y * W * 3:(y + 1) * W * 3]


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


out = b"\x89PNG\r\n\x1a\n"
out += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
out += chunk(b"IEND", b"")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kof97.png")
with open(path, "wb") as f:
    f.write(out)
print("wrote", path, len(out), "bytes")
