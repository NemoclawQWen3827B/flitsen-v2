#!/usr/bin/env python3
"""Synthetic painting: warm canvas + a few isolated white flash specs."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    import struct, zlib

    def write_png(path, w, h, rgba):
        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        raw = b"".join(b"\x00" + rgba[y * w * 4 : (y + 1) * w * 4] for y in range(h))
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(raw, 9))
        png += chunk(b"IEND", b"")
        path.write_bytes(png)

    w, h = 640, 480
    px = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            px[i] = 118 + (x // 40) % 3 * 8
            px[i + 1] = 92 + (y // 35) % 4 * 6
            px[i + 2] = 64
            px[i + 3] = 255
            # canvas rib (should NOT detect)
            if y % 18 == 0:
                px[i] = min(255, px[i] + 28)
                px[i + 1] = min(255, px[i + 1] + 22)
                px[i + 2] = min(255, px[i + 2] + 16)
    flashes = [(160, 133, 2), (310, 205, 3), (420, 259, 2), (500, 115, 2)]
    for cx, cy, r in flashes:
        for y in range(cy - r - 2, cy + r + 3):
            for x in range(cx - r - 2, cx + r + 3):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if d2 <= (r + 1) ** 2:
                    i = (y * w + x) * 4
                    t = max(0.0, 1.0 - (d2 ** 0.5) / (r + 1.5))
                    px[i] = int(255 * t + px[i] * (1 - t))
                    px[i + 1] = int(255 * t + px[i + 1] * (1 - t))
                    px[i + 2] = int(250 * t + px[i + 2] * (1 - t))
    out = Path(__file__).resolve().parent / "photo.png"
    write_png(out, w, h, bytes(px))
    print(f"wrote {out} ({w}x{h})")
else:
    w, h = 640, 480
    im = Image.new("RGB", (w, h), (118, 92, 64))
    d = ImageDraw.Draw(im)
    for y in range(0, h, 18):
        d.line([(0, y), (w, y)], fill=(146, 114, 80), width=1)
    for cx, cy, r in [(160, 133, 2), (310, 205, 3), (420, 259, 2), (500, 115, 2)]:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 250))
    out = Path(__file__).resolve().parent / "photo.png"
    im.save(out)
    print(f"wrote {out} ({w}x{h})")
