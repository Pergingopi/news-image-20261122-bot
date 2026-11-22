#!/usr/bin/env python3
"""The World Today -- Sunday 22 November 2026.

Draws the day's front page as a PNG with the Python standard library only.
No network, no clock, no randomness: two runs write byte-identical files.
Writes entry.png into /output (or $MAKEFUN_OUTPUT_DIR) and sets mode 0644.

Design revision: bolder type throughout, ink date band, redrawn Gulf blast
(no more sun-like symmetry), richer pictograms; stories and wording unchanged.

Stories (each verified against reporting dated 22 November 2026):
  1. Gulf -- Iran hits US bases in Bahrain on Saturday night; tankers
     struck in the Strait of Hormuz (reported 22 Nov).
  2. Ukraine -- Russian missiles hit Zelenskyy's hometown; 2 killed in
     strikes across Ukraine (published 22 Nov 00:06 UTC).
  3. Climate -- COP31 talks deadlocked over fossil fuels (BBC, 22 Nov).
  4. United States -- FBI probes an apparent hack of its crime database
     (BBC world feed, 22 Nov).
  5. Europe -- Denmark accuses Russia of a plot to kill a US-Ukrainian
     rapper (BBC world feed, 22 Nov).
  6. India -- Modi opens the Nitish Setu bridge in Bihar (22 Nov list).
"""
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (245, 240, 230)
INK = (26, 26, 26)
GREY = (90, 86, 78)
RED = (179, 39, 30)
WHITE = (255, 255, 255)
SEA = (38, 84, 124)
SKY = (214, 228, 238)

# A 5x7 bitmap font, written for this poster. Each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
}


class Canvas:
    """An RGB pixel buffer with tiny shape and text helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        row = bytes(bg) * w
        for y in range(h):
            self.px[y * w * 3:(y + 1) * w * 3] = row

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = row

    def line(self, x0, y0, x1, y1, c, w=1):
        """Bresenham line with a square brush of side w."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = w // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, w, w, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        """Filled circle by scanlines."""
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r_out, r_in, c, bg):
        self.circle(cx, cy, r_out, c)
        self.circle(cx, cy, r_in, bg)

    def text_w(self, s, scale, bold=False):
        if not s:
            return 0
        return len(s) * 6 * scale - scale + (1 if bold else 0)

    def text(self, s, x, y, scale, color, bold=False):
        # Bold stamps each glyph four times with 1 px offsets, thickening
        # every stroke by one pixel -- cheap, deterministic, and it reads
        # far better when the poster is shrunk to ~300 px.
        offsets = ((0, 0), (1, 0), (0, 1), (1, 1)) if bold else ((0, 0),)
        for ox, oy in offsets:
            cx = x + ox
            for ch in s:
                g = FONT.get(ch, FONT[" "])
                for r in range(7):
                    row = g[r]
                    for col in range(5):
                        if row[col] == "1":
                            self.fill_rect(cx + col * scale, y + oy + r * scale,
                                           scale, scale, color)
                cx += 6 * scale

    def text_center(self, s, y, scale, color, x0, x1, bold=False):
        tw = self.text_w(s, scale, bold)
        self.text(s, x0 + (x1 - x0 - tw) // 2, y, scale, color, bold)


def png_bytes(cv):
    """Encode the canvas as a deterministic RGB PNG."""
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def tint(c, f):
    """Mix a colour toward the paper colour by factor f (0..1)."""
    return tuple(int(c[i] + (PAPER[i] - c[i]) * f) for i in range(3))


def icon_gulf(cv, x, y, w, h, accent):
    """A tanker on the sea under a missile strike -- an irregular fireball
    with incoming trails and dark smoke, never a symmetric sun."""
    cv.fill_rect(x, y, w, h, tint(SEA, 0.82))
    cv.fill_rect(x, y + 118, w, h - 118, tint(SEA, 0.45))
    # incoming missile trails, converging on the blast from both corners
    cv.line(x + 14, y + 6, x + 140, y + 56, (200, 198, 192), 3)
    cv.line(x + 16, y + 10, x + 142, y + 60, (255, 255, 255), 2)
    cv.line(x + 302, y + 10, x + 176, y + 56, (200, 198, 192), 3)
    cv.line(x + 300, y + 14, x + 174, y + 60, (255, 255, 255), 2)
    # blast: long angular shards at irregular angles and lengths, then a
    # lumpy fireball of overlapping flame circles at clearly different
    # centres, so the outline is a burst cloud, not a round sun
    bx, by = x + 158, y + 62
    for ang, ln, wd in ((8, 62, 9), (55, 70, 8), (105, 58, 9), (150, 66, 8),
                        (205, 60, 9), (250, 52, 8), (305, 64, 9)):
        dx = int(ln * math.cos(math.radians(ang)))
        dy = int(ln * math.sin(math.radians(ang)))
        cv.line(bx, by, bx + dx, by + dy, (214, 90, 20), wd)
    cv.circle(bx - 16, by + 8, 22, (200, 60, 20))
    cv.circle(bx + 12, by - 12, 24, (232, 126, 32))
    cv.circle(bx + 20, by + 14, 16, (232, 126, 32))
    cv.circle(bx - 2, by - 18, 14, (240, 196, 66))
    cv.circle(bx + 26, by - 2, 11, (240, 196, 66))
    cv.circle(bx - 24, by - 10, 10, (232, 126, 32))
    # dark smoke columns rising from the blast
    cv.circle(x + 116, y + 30, 13, (70, 66, 60))
    cv.circle(x + 100, y + 18, 10, (90, 86, 80))
    cv.circle(x + 198, y + 26, 12, (70, 66, 60))
    cv.circle(x + 212, y + 14, 9, (90, 86, 80))
    # tanker hull and containers
    hx, hy = x + 38, y + 128
    cv.fill_rect(hx, hy, 244, 26, INK)
    cv.fill_rect(hx + 8, hy - 22, 60, 22, (70, 70, 70))
    for i, cc in enumerate(((179, 39, 30), (38, 84, 124), (46, 107, 52))):
        cv.fill_rect(hx + 84 + i * 52, hy - 20, 46, 20, cc)
    cv.fill_rect(hx + 206, hy - 34, 10, 34, INK)
    cv.fill_rect(hx + 200, hy - 40, 22, 6, INK)
    # small fire on the tanker deck -- the tanker was hit
    cv.circle(hx + 226, hy - 46, 10, (232, 126, 32))
    cv.circle(hx + 226, hy - 46, 5, (240, 196, 66))
    # waves
    cv.line(x + 30, y + 168, x + 90, y + 168, (255, 255, 255), 2)
    cv.line(x + 200, y + 176, x + 270, y + 176, (255, 255, 255), 2)


def icon_ukraine(cv, x, y, w, h, accent):
    """A city skyline under a missile blast."""
    cv.fill_rect(x, y, w, h, tint(accent, 0.85))
    # buildings first, so the blast lands ON the tallest tower
    base = y + h - 8
    for bxx, bw, bh in ((x + 24, 62, 96), (x + 100, 74, 128),
                        (x + 188, 58, 88), (x + 256, 44, 112)):
        cv.fill_rect(bxx, base - bh, bw, bh, (44, 44, 52))
        for wy in range(base - bh + 12, base - 10, 18):
            for wx in range(bxx + 10, bxx + bw - 10, 16):
                cv.fill_rect(wx, wy, 7, 9, (240, 196, 66))
    # missile arcs with smoke trails, from both sides
    cv.line(x + 26, y + 14, x + 146, y + 62, (200, 198, 192), 3)
    cv.line(x + 30, y + 18, x + 150, y + 66, INK, 3)
    cv.line(x + 292, y + 26, x + 176, y + 70, (200, 198, 192), 3)
    cv.line(x + 290, y + 30, x + 174, y + 74, INK, 2)
    # impact blast on the tallest tower: jagged shards, off-centre core
    bx, by = x + 158, y + 66
    for ang, ln in ((10, 44), (80, 52), (150, 38), (215, 46), (285, 40)):
        dx = int(ln * math.cos(math.radians(ang)))
        dy = int(ln * math.sin(math.radians(ang)))
        cv.line(bx, by, bx + dx, by + dy, (214, 90, 20), 6)
    cv.circle(bx - 4, by, 28, (200, 60, 20))
    cv.circle(bx, by, 22, (232, 126, 32))
    cv.circle(bx + 3, by - 3, 13, (240, 196, 66))
    # smoke column above the impact
    cv.circle(bx - 18, by - 34, 11, (70, 66, 60))
    cv.circle(bx - 30, by - 46, 9, (90, 86, 80))


def icon_climate(cv, x, y, w, h, accent):
    """A warming globe with a thermometer."""
    cv.fill_rect(x, y, w, h, tint(accent, 0.88))
    cx, cy, r = x + 126, y + 96, 66
    cv.circle(cx, cy, r, INK)
    cv.circle(cx, cy, r - 4, SEA)
    # land: one continent cluster, not scattered dots
    cv.circle(cx - 26, cy - 16, 22, (46, 107, 52))
    cv.circle(cx + 24, cy + 12, 17, (46, 107, 52))
    cv.circle(cx + 2, cy - 34, 13, (46, 107, 52))
    cv.circle(cx - 8, cy + 30, 9, (46, 107, 52))
    cv.circle(cx + 34, cy - 22, 8, (46, 107, 52))
    # thermometer with tick marks
    tx = x + 238
    cv.fill_rect(tx - 2, y + 32, 20, 102, INK)
    cv.fill_rect(tx, y + 34, 16, 96, WHITE)
    cv.fill_rect(tx + 2, y + 36, 12, 94, (200, 200, 200))
    cv.fill_rect(tx + 5, y + 60, 6, 68, RED)
    cv.circle(tx + 8, y + 134, 16, RED)
    cv.circle(tx + 8, y + 134, 10, (232, 126, 32))
    for ty in (y + 48, y + 68, y + 88, y + 108):
        cv.fill_rect(tx - 6, ty, 6, 3, INK)
    # rising arrow
    cv.line(x + 226, y + 168, x + 226, y + 44, RED, 5)
    cv.line(x + 226, y + 44, x + 212, y + 62, RED, 5)
    cv.line(x + 226, y + 44, x + 240, y + 62, RED, 5)


def icon_fbi(cv, x, y, w, h, accent):
    """A server stack under a magnifying glass."""
    cv.fill_rect(x, y, w, h, tint(accent, 0.88))
    sx = x + 34
    for i in range(3):
        yy = y + 40 + i * 44
        cv.fill_rect(sx, yy, 120, 34, (44, 44, 52))
        cv.fill_rect(sx + 10, yy + 12, 10, 10, (90, 200, 120))
        cv.fill_rect(sx + 28, yy + 12, 10, 10, (240, 196, 66))
        cv.fill_rect(sx + 46, yy + 12, 56, 10, (120, 120, 128))
    # crack across the middle server -- the breach
    cv.line(sx + 60, y + 84, sx + 72, y + 96, (200, 200, 200), 2)
    cv.line(sx + 72, y + 96, sx + 64, y + 108, (200, 200, 200), 2)
    cv.line(sx + 64, y + 108, sx + 76, y + 118, (200, 200, 200), 2)
    # magnifier over the stack, red-ringed lens
    mx, my = x + 218, y + 96
    cv.ring(mx, my, 50, 40, RED, tint(accent, 0.88))
    cv.ring(mx, my, 46, 36, INK, tint(accent, 0.88))
    cv.line(mx + 34, my + 34, mx + 64, my + 64, INK, 9)
    cv.line(mx - 18, my, mx + 18, my, RED, 5)
    cv.line(mx, my - 18, mx, my + 18, RED, 5)


def icon_denmark(cv, x, y, w, h, accent):
    """A target with crosshairs."""
    cv.fill_rect(x, y, w, h, tint(accent, 0.88))
    cx, cy = x + w // 2, y + h // 2 + 4
    cv.circle(cx, cy, 62, RED)
    cv.circle(cx, cy, 48, WHITE)
    cv.circle(cx, cy, 34, RED)
    cv.circle(cx, cy, 20, WHITE)
    cv.circle(cx, cy, 9, RED)
    cv.circle(cx, cy, 4, INK)
    cv.line(cx - 84, cy, cx - 66, cy, INK, 5)
    cv.line(cx + 66, cy, cx + 84, cy, INK, 5)
    cv.line(cx, cy - 84, cx, cy - 66, INK, 5)
    cv.line(cx, cy + 66, cx, cy + 84, INK, 5)


def icon_india(cv, x, y, w, h, accent):
    """A suspension bridge over a river."""
    cv.fill_rect(x, y, w, h, tint(accent, 0.88))
    # soft clouds
    cv.fill_rect(x + 24, y + 22, 64, 10, (255, 250, 240))
    cv.fill_rect(x + 40, y + 34, 44, 8, (255, 250, 240))
    # sun with a halo
    cv.circle(x + 268, y + 34, 26, (250, 220, 130))
    cv.circle(x + 268, y + 34, 20, (240, 196, 66))
    cv.fill_rect(x, y + 138, w, h - 138, tint(SEA, 0.45))
    # towers and deck
    cv.fill_rect(x + 76, y + 44, 14, 100, INK)
    cv.fill_rect(x + 230, y + 44, 14, 100, INK)
    cv.fill_rect(x + 20, y + 138, 280, 10, INK)
    cv.fill_rect(x + 20, y + 134, 280, 3, INK)
    for tx in (76, 230):
        for dx in (-56, -28, 28, 56):
            cv.line(x + tx + 7, y + 48, x + tx + 7 + dx, y + 138,
                    (90, 86, 78), 3)
    # a small train of cars on the deck
    cv.fill_rect(x + 120, y + 122, 26, 14, RED)
    cv.fill_rect(x + 160, y + 122, 26, 14, (38, 84, 124))
    cv.fill_rect(x + 200, y + 122, 26, 14, (46, 107, 52))
    # waves on the river
    cv.line(x + 30, y + 162, x + 90, y + 162, (255, 255, 255), 2)
    cv.line(x + 120, y + 174, x + 190, y + 174, (255, 255, 255), 2)
    cv.line(x + 210, y + 164, x + 280, y + 164, (255, 255, 255), 2)


ICONS = {
    "gulf": icon_gulf,
    "ukraine": icon_ukraine,
    "climate": icon_climate,
    "fbi": icon_fbi,
    "denmark": icon_denmark,
    "india": icon_india,
}

STORIES = [
    {
        "kicker": "THE GULF",
        "accent": (169, 50, 38),
        "icon": "gulf",
        "headline": ["IRAN HITS", "US BASES IN", "BAHRAIN"],
        "sub": ["MISSILES AND DRONES", "TANKERS HIT IN HORMUZ"],
    },
    {
        "kicker": "UKRAINE",
        "accent": (36, 113, 163),
        "icon": "ukraine",
        "headline": ["MISSILES HIT", "ZELENSKYY'S", "HOMETOWN"],
        "sub": ["2 KILLED, DOZENS HURT", "IN STRIKES ON UKRAINE"],
    },
    {
        "kicker": "CLIMATE",
        "accent": (30, 132, 73),
        "icon": "climate",
        "headline": ["COP31 TALKS", "DEADLOCKED"],
        "sub": ["TALKS IN OVERTIME", "NO DEAL ON FUELS"],
    },
    {
        "kicker": "UNITED STATES",
        "accent": (44, 62, 80),
        "icon": "fbi",
        "headline": ["FBI PROBES HACK", "OF CRIME FILES"],
        "sub": ["REPORTED BREACH OF", "CRIME DATABASE"],
    },
    {
        "kicker": "EUROPE",
        "accent": (108, 52, 131),
        "icon": "denmark",
        "headline": ["DENMARK ACCUSES", "RUSSIA OF PLOT", "TO KILL RAPPER"],
        "sub": ["TARGET IS US-UKRAINIAN", "RAPPER, DENMARK SAYS"],
    },
    {
        "kicker": "INDIA",
        "accent": (185, 119, 14),
        "icon": "india",
        "headline": ["MODI OPENS", "NITISH SETU", "BRIDGE"],
        "sub": ["PATNA TO VAISHALI", "IN BIHAR, INDIA"],
    },
]


PANEL_W, PANEL_H = 320, 397
GRID_X = (16, 352, 688)
GRID_Y = (176, 585)


def draw_panel(cv, story, px, py):
    accent = story["accent"]
    # frame
    cv.fill_rect(px, py, PANEL_W, PANEL_H, PAPER)
    cv.fill_rect(px, py, PANEL_W, 2, accent)
    cv.fill_rect(px, py + PANEL_H - 2, PANEL_W, 2, accent)
    cv.fill_rect(px, py, 2, PANEL_H, accent)
    cv.fill_rect(px + PANEL_W - 2, py, 2, PANEL_H, accent)
    # kicker strip
    cv.fill_rect(px + 2, py + 2, PANEL_W - 4, 32, accent)
    cv.text(story["kicker"], px + 12, py + 10, 2, WHITE, bold=True)
    # pictogram
    ICONS[story["icon"]](cv, px + 2, py + 34, PANEL_W - 4, 190, accent)
    # thin accent rule under the picture, separating it from the type
    cv.fill_rect(px + 2, py + 224, PANEL_W - 4, 2, accent)
    # headline (bold, so it still reads at ~300 px)
    hy = py + 238
    for i, line in enumerate(story["headline"]):
        cv.text_center(line, hy + i * 27, 3, INK, px, px + PANEL_W, bold=True)
    # divider
    dy = hy + len(story["headline"]) * 27 + 8
    cv.fill_rect(px + (PANEL_W - 48) // 2, dy, 48, 4, accent)
    # sub-caption (darker than before, bold, for legibility)
    sy = dy + 14
    for i, line in enumerate(story["sub"]):
        cv.text_center(line, sy + i * 18, 2, (58, 55, 49), px, px + PANEL_W,
                       bold=True)


def build():
    cv = Canvas(W, H, PAPER)
    # header: red rule, bigger bold masthead, ink date band, standfirst
    cv.fill_rect(16, 14, 992, 6, RED)
    cv.text_center("THE WORLD TODAY", 28, 7, INK, 16, 1008, bold=True)
    cv.fill_rect(16, 86, 992, 46, INK)
    cv.text_center("SUNDAY, 22 NOVEMBER 2026", 91, 5, WHITE, 16, 1008,
                   bold=True)
    cv.fill_rect(16, 132, 992, 3, RED)
    cv.text_center("SIX STORIES FROM AROUND THE WORLD", 143, 2, (58, 55, 49),
                   16, 1008, bold=True)
    cv.fill_rect(16, 165, 992, 3, INK)
    # story grid
    for i, story in enumerate(STORIES):
        draw_panel(cv, story, GRID_X[i % 3], GRID_Y[i // 3])
    # footer
    cv.text_center("EVENTS OF 22 NOVEMBER 2026, AS REPORTED THAT DAY",
                   996, 2, (58, 55, 49), 16, 1008, bold=True)
    return png_bytes(cv)


def main(argv):
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    for i, a in enumerate(argv):
        if a == "--output" and i + 1 < len(argv):
            outdir = argv[i + 1]
    os.makedirs(outdir, exist_ok=True)
    data = build()
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)
    mode = oct(os.stat(path).st_mode & 0o777)
    print("wrote %s %d bytes mode %s" % (path, len(data), mode))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
