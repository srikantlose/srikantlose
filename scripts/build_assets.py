#!/usr/bin/env python3
"""Build the pixel-art SVGs used by README.md.

GitHub strips CSS and JavaScript from a README, but it does play CSS
animations inside SVG images, so all of the motion on the profile lives in
these generated files. Everything is drawn from code (a 5x7 bitmap font,
small sprite grids and one palette), which keeps the art crisp at any zoom
and the files small.

Usage:
    python scripts/build_assets.py
"""

from __future__ import annotations

import json
import math
import random
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# --------------------------------------------------------------------------
# Palette (based on the Sweetie 16 palette, plus a few extras)
# --------------------------------------------------------------------------
INK = "#1a1c2c"
PLUM = "#5d275d"
RED = "#b13e53"
ORANGE = "#ef7d57"
YELLOW = "#ffcd75"
LIME = "#a7f070"
GREEN = "#38b764"
TEAL = "#257179"
NAVY = "#29366f"
BLUE = "#3b5dc9"
SKY = "#41a6f6"
CYAN = "#73eff7"
WHITE = "#f4f4f4"
SILVER = "#94b0c2"
SLATE = "#566c86"
CHARCOAL = "#333c57"
CREAM = "#fff3c4"
PEACH = "#ffb38a"
DUSK = "#8f4d82"
SKIN = "#d08b5b"
SKIN_SHADE = "#a0603d"
BROWN = "#8a4f2e"
PANEL = "#20233d"
DEEP = "#141526"
PINE = "#1d4f4a"
MOSS = "#2e9e5b"
VELVET = "#4a1f4a"
VELVET_DARK = "#33153a"

# --------------------------------------------------------------------------
# 5x7 bitmap font
# --------------------------------------------------------------------------
FONT = {
    " ": ["....."] * 7,
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    ",": [".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    "/": [".....", "....#", "...#.", "..#..", ".#...", "#....", "....."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "@": [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "%": ["##...", "##..#", "...#.", "..#..", ".#...", "#..##", "...##"],
    "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "◆": [".....", "..#..", ".###.", "#####", ".###.", "..#..", "....."],
    "▶": ["#....", "##...", "###..", "####.", "###..", "##...", "#...."],
    "▼": [".....", ".....", "#####", ".###.", "..#..", ".....", "....."],
    "♥": [".....", ".#.#.", "#####", "#####", ".###.", "..#..", "....."],
    "★": ["..#..", "..#..", "#####", ".###.", ".#.#.", "#...#", "....."],
}
ADV = 6  # glyph advance in font pixels (5 wide + 1 gap)


def tw(text: str, scale: int) -> int:
    """Pixel width of a string at a given scale."""
    return (len(text) * ADV - 1) * scale


def gid(ch: str) -> str:
    return f"g{ord(ch):x}"


def run_paths(rows, pal):
    """Merge horizontal runs into one path per colour: {colour: d}."""
    paths: dict[str, list[str]] = {}
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            n = 1
            while x + n < len(row) and row[x + n] == ch:
                n += 1
            if ch in pal:
                paths.setdefault(pal[ch], []).append(f"M{x} {y}h{n}v1h-{n}z")
            x += n
    return {col: "".join(d) for col, d in paths.items()}


def glyph_d(ch: str) -> str:
    return run_paths(FONT[ch], {"#": "x"})["x"] if ch != " " else ""


# --------------------------------------------------------------------------
# Sprite helpers
# --------------------------------------------------------------------------
def outline(rows, k="K"):
    """Pad a sprite by one pixel and add a 4-connected outline around it."""
    h, w = len(rows), max(len(r) for r in rows)
    grid = [["."] * (w + 2) for _ in range(h + 2)]
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            grid[y + 1][x + 1] = c
    out = [r[:] for r in grid]
    for y in range(h + 2):
        for x in range(w + 2):
            if grid[y][x] != ".":
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w + 2 and 0 <= yy < h + 2 and grid[yy][xx] != ".":
                    out[y][x] = k
                    break
    return ["".join(r) for r in out]


def shape(w, h, fn):
    """Build sprite rows from a function (x, y) -> char or None."""
    return ["".join(fn(x, y) or "." for x in range(w)) for y in range(h)]


def sprite(rows, pal, x, y, scale, attrs=""):
    widths = {len(r) for r in rows}
    assert len(widths) == 1, f"ragged sprite rows: {widths}"
    paths = run_paths(rows, pal)
    inner = "".join(f'<path fill="{c}" d="{d}"/>' for c, d in paths.items())
    return f'<g transform="translate({x} {y}) scale({scale})"{attrs}>{inner}</g>'


def srect(x, y, w, h, c=4, steps=2):
    """Path for a rectangle with stair-stepped (pixel-rounded) corners."""
    if steps == 0:
        return f"M{x} {y}h{w}v{h}h{-w}z"
    if steps == 1:
        return (f"M{x + c} {y}H{x + w - c}V{y + c}H{x + w}V{y + h - c}H{x + w - c}"
                f"V{y + h}H{x + c}V{y + h - c}H{x}V{y + c}H{x + c}Z")
    a, b = c, 2 * c
    return (f"M{x + b} {y}H{x + w - b}V{y + a}H{x + w - a}V{y + b}H{x + w}"
            f"V{y + h - b}H{x + w - a}V{y + h - a}H{x + w - b}V{y + h}H{x + b}"
            f"V{y + h - a}H{x + a}V{y + h - b}H{x}V{y + b}H{x + a}V{y + a}H{x + b}Z")


def frame(x, y, w, h, fill, border=WHITE, edge=INK, c=4):
    """RPG window: dark edge, coloured border, thin inner line, then fill."""
    return (f'<path fill="{edge}" d="{srect(x, y, w, h, c, 2)}"/>'
            f'<path fill="{border}" d="{srect(x + c, y + c, w - 2 * c, h - 2 * c, c, 1)}"/>'
            f'<path fill="{edge}" d="{srect(x + 2 * c, y + 2 * c, w - 4 * c, h - 4 * c, c, 1)}"/>'
            f'<path fill="{fill}" d="{srect(x + 2 * c + 2, y + 2 * c + 2, w - 4 * c - 4, h - 4 * c - 4, 2, 1)}"/>')


def rect(x, y, w, h, fill, attrs=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{attrs}/>'


def disc(cx, cy, r, u=4):
    """Pixel circle as a path, snapped to a u-pixel grid."""
    d = []
    for yy in range(-r, r, u):
        mid = yy + u / 2
        half = int(math.sqrt(max(r * r - mid * mid, 0)) // u) * u
        if half > 0:
            d.append(f"M{cx - half} {cy + yy}h{2 * half}v{u}h{-2 * half}z")
    return "".join(d)


# --------------------------------------------------------------------------
# SVG document
# --------------------------------------------------------------------------
BASE_CSS = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.glyphs: set[str] = set()
        self.defs: list[str] = []
        self.css: list[str] = [BASE_CSS]
        self.body: list[str] = []
        self._n = 0

    def uid(self, prefix="t"):
        self._n += 1
        return f"{prefix}{self._n}"

    def add(self, *parts):
        self.body.extend(parts)

    def style(self, css):
        self.css.append(css)

    def textdef(self, text, scale):
        text = text.upper()
        tid = self.uid()
        uses = []
        for i, ch in enumerate(text):
            if ch not in FONT:
                raise KeyError(f"no glyph for {ch!r} in {text!r}")
            if ch == " ":
                continue
            self.glyphs.add(ch)
            uses.append(f'<use href="#{gid(ch)}" x="{i * ADV}"/>')
        self.defs.append(f'<g id="{tid}" transform="scale({scale})">{"".join(uses)}</g>')
        return tid

    def text(self, text, x, y, scale=2, fill=WHITE, anchor="start", stroke=None,
             shadow=None, attrs=""):
        """Place bitmap text. stroke draws a 1-font-pixel outline; shadow is (dx, dy, colour)."""
        width = tw(text, scale)
        if anchor == "middle":
            x -= width // 2
        elif anchor == "end":
            x -= width
        tid = self.textdef(text, scale)

        def use(dx, dy, f, s):
            st = (f' stroke="{s}" stroke-width="2" paint-order="stroke" stroke-linejoin="miter"'
                  if s else "")
            return f'<use href="#{tid}" x="{x + dx}" y="{y + dy}" fill="{f}"{st}/>'

        parts = []
        if shadow:
            dx, dy, col = shadow
            parts.append(use(dx, dy, col, col if stroke else None))
        parts.append(use(0, 0, fill, stroke))
        out = "".join(parts)
        return f"<g{attrs}>{out}</g>" if attrs or len(parts) > 1 else out

    def render(self):
        glyphs = "".join(f'<path id="{gid(c)}" d="{glyph_d(c)}"/>' for c in sorted(self.glyphs))
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" shape-rendering="crispEdges" role="img" '
            f'aria-labelledby="title desc">'
            f'<title id="title">{escape(self.title)}</title>'
            f'<desc id="desc">{escape(self.desc)}</desc>'
            f'<style>{"".join(self.css)}</style>'
            f'<defs>{glyphs}{"".join(self.defs)}</defs>'
            f'{"".join(self.body)}</svg>'
        )

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / name
        path.write_text(self.render(), encoding="utf-8")
        print(f"  {name:<28} {path.stat().st_size / 1024:6.1f} KB")


def pct(t, total):
    return f"{t / total * 100:.2f}%"


# --------------------------------------------------------------------------
# Sprites
# --------------------------------------------------------------------------
HERO = [
    "....KKKKKKKK....",
    "...KHHHHHHHHK...",
    "..KHHhhHHHHHHK..",
    ".KHHhHHHHHHHHHK.",
    ".KHHHHHHHHHHHHK.",
    "KGKHHSSSSSSHHKGK",
    "KGKHSSSSSSSSHKGK",
    "KgKSSKSSSSKSSKgK",
    "KGKSSKSSSSKSSKGK",
    ".KKsSSSSSSSSsKK.",
    "..KsSSSKKSSSsK..",
    "...KKsSSSSsKK...",
    "...KBBBWWBBBK...",
    "..KBBLBWWBBBBK..",
    ".KBBLBBBBBBBBBK.",
    ".KBLBBBBBBBBBBK.",
    "KSSKbbbbbbbbKSSK",
    ".KKKBBBBBBBBKKK.",
    "....KPPPPPPK....",
    "....KPPKKPPK....",
    "....KPPKKPPK....",
    "...KRRRKKRRRK...",
    "...KKKKKKKKKK...",
]
HERO_PAL = {"K": INK, "H": CHARCOAL, "h": SLATE, "S": SKIN, "s": SKIN_SHADE,
            "G": GREEN, "g": LIME, "B": BLUE, "b": NAVY, "L": SKY, "W": WHITE,
            "P": CHARCOAL, "R": RED}
HERO_EYES = [(5, 7), (10, 7), (5, 8), (10, 8)]

BOT = [
    ".....KK.....",
    ".....KY.....",
    "....KKKK....",
    "..KKWWWWKK..",
    ".KWWWWWWWWK.",
    "KWWKKKKKKWWK",
    "KWKCKKKKCKWK",
    "KWWKKKKKKWWK",
    "KsWWWWWWWWsK",
    ".KssssssssK.",
    "..KKKKKKKK..",
    "...KK..KK...",
]
BOT_FLAME = ["...YO..OY...", "....O..O...."]
BOT_PAL = {"K": INK, "W": WHITE, "s": SILVER, "C": CYAN, "Y": YELLOW, "O": ORANGE}

CLOUD_BIG = [
    "......LLLL..........",
    "...LLLLLLLLL..LLL...",
    ".LLLLLLLLLLLLLLLLLL.",
    "LLLLLLLLLLLLLLLLLLLL",
    ".SSSSSSSSSSSSSSSSSS.",
]
CLOUD_SMALL = [
    "...LLLL.....",
    ".LLLLLLLLL..",
    "LLLLLLLLLLLL",
    ".SSSSSSSSSS.",
]
PINE_TREE = ["..D..", ".DDD.", "..D..", ".DDD.", "DDDDD", ".DDD.", "DDDDD", "..N.."]
TUFT = ["L..L..L", "LL.L.LL", ".LLGLL."]
FLOWER = [".F.", "FCF", ".F.", ".G."]
SPARKLE = ["..W..", "..W..", "WWWWW", "..W..", "..W.."]

SHIELD = [
    "FFFFFFFFFFFFFF",
    "FfFFFFFFFFFFFF",
    "FfFFFFWWFFFFFF",
    "FfFFFWFFWFFFFF",
    "FfFFWWWWWWFFFF",
    "FfFFWWKKWWFFFF",
    "FfFFWWKKWWFFFF",
    "FfFFWWWWWWFFFF",
    ".FfFFFFFFFFFF.",
    ".FFfFFFFFFFFF.",
    "..FFFFFFFFFF..",
    "...FFFFFFFF...",
    "....FFFFFF....",
    ".....FFFF.....",
    "......FF......",
]
SIGNPOST = [
    "......NN......",
    ".YYYYYYYYYYY..",
    ".YKKYKKKYYYYY.",
    ".YYYYYYYYYYY..",
    "......NN......",
    "..CCCCCCCCCCC.",
    ".CCCKKCKKKCCC.",
    "..CCCCCCCCCCC.",
    "......NN......",
    "......NN......",
    "......NN......",
    "....GGGGGG....",
    "..GGgGGGGgGG..",
]
TV = [
    "...K......K...",
    "....K....K....",
    ".....K..K.....",
    "DDDDDDDDDDDDDD",
    "DCCCCCCCCCCDSD",
    "DCCWCCCCCCCDDD",
    "DCCCCRCCCCCDSD",
    "DCCCCRRCCCCDDD",
    "DCCCCRRRCCCDSD",
    "DCCCCRRCCCCDDD",
    "DCCCCRCCCCCDDD",
    "DCCCCCCCCCCDDD",
    "DDDDDDDDDDDDDD",
    ".DD........DD.",
]
HEART = [
    "..RRR....RRR..",
    ".RRRRR..RRRRR.",
    "RRrRRRRRRRRRRR",
    "RrRRRRWWRRRRRR",
    "RRRRRRWWRRRRRR",
    "RRRRWWWWWWRRRR",
    ".RRRWWWWWWRRR.",
    "..RRRRWWRRRR..",
    "...RRRWWRRR...",
    "....RRRRRR....",
    ".....RRRR.....",
    "......RR......",
]
TEMPLE = [
    "......NOO.....",
    "......NOO.....",
    "......N.......",
    "......RR......",
    ".....RRRR.....",
    "....RRRRRR....",
    "...RRRRRRRR...",
    ".WWWWWWWWWWWW.",
    "..YYYYYYYYYY..",
    "..YDYYDDYYDY..",
    "..YDYYDDYYDY..",
    "..YYYYDDYYYY..",
    ".SSSSSSSSSSSS.",
    "SSSSSSSSSSSSSS",
]
FLOPPY = [
    "BBSSSSSSSBB",
    "BBSSSKSSSBB",
    "BBSSSKSSSBB",
    "BBSSSSSSSBB",
    "BBBBBBBBBBB",
    "BWWWWWWWWWB",
    "BWKKKKKKKWB",
    "BWWWWWWWWWB",
    "BWKKKKKWWWB",
    "BWWWWWWWWWB",
]
ENVELOPE = [
    "KKKKKKKKKKK",
    "KKWWWWWWWKK",
    "KWKWWWWWKWK",
    "KWWKWWWKWWK",
    "KWWWKKKWWWK",
    "KWWWWWWWWWK",
    "KWWWWWWWWWK",
    "KKKKKKKKKKK",
]
BRIEFCASE = [
    "...KKKKK...",
    "...K...K...",
    "KKKKKKKKKKK",
    "KBBBBBBBBBK",
    "KBBBBYBBBBK",
    "KKKKKYKKKKK",
    "KBBBBBBBBBK",
    "KBBBBBBBBBK",
    "KKKKKKKKKKK",
]
GAMEPAD = [
    ".KKKKKKKKKKK.",
    "KWWWWWWWWWWWK",
    "KWWKWWWWWWRWK",
    "KWKKKWWWWRWWK",
    "KWWKWWWWWWWWK",
    "KWWWWWWWWWWWK",
    "KWWWKKKKKWWWK",
    ".KKK.....KKK.",
]


def moon_icon():
    def fn(x, y):
        a = (x - 6.5) ** 2 + (y - 6.5) ** 2 <= 6.6 ** 2
        b = (x - 9.8) ** 2 + (y - 4.2) ** 2 <= 5.4 ** 2
        if a and not b:
            if (x, y) in {(3, 5), (2, 8), (4, 10), (6, 12)}:
                return "y"
            return "Y" if x > 1 else "W"
        return None
    return shape(14, 14, fn)


def badge_cloud():
    rows = [
        "....CCCCCC....",
        "..CCCCCCCCCC..",
        ".CWCCCCCCCCCC.",
        "CWCCCCCCCCCCCC",
        "CCCCCWWWCCCCCC",
        "CCCCWWWWWWCCCC",
        "CCCWWWWWWWWCCC",
        "CCCWWWWWWWWCCC",
        "CCCCCCCCCCCCCC",
        "CCCCCCCCCCCCCd",
        ".CCCCCCCCCCCd.",
        "..CCCCCCCCdd..",
        "....CCCCdd....",
    ]
    return rows


def badge_radar():
    def fn(x, y):
        dx, dy = x - 6.5, y - 6.5
        d = math.hypot(dx, dy)
        if d > 6.9:
            return None
        if d < 1.3:
            return "W"
        if 3.2 < d < 4.4:
            return "k"
        if abs(dx) < 0.6 or abs(dy) < 0.6:
            return "k"
        if dx < -2 and dy < -2 and d > 4.6:
            return "g"
        return "G"
    return shape(14, 14, fn)


def badge_eye():
    def fn(x, y):
        dx, dy = x - 6.5, y - 6.5
        if abs(dx) + abs(dy) > 7.2:
            return None
        if math.hypot(dx, dy) < 1.3:
            return "K"
        if math.hypot(dx, dy) < 2.4:
            return "B"
        if (dx / 5.0) ** 2 + (dy / 2.6) ** 2 <= 1:
            return "W"
        if dx < 0 and dy < 0 and abs(dx) + abs(dy) > 5:
            return "r"
        return "R"
    return shape(14, 14, fn)


def badge_star():
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = 7.2 if i % 2 == 0 else 3.1
        pts.append((6.5 + rad * math.cos(ang), 7.0 + rad * math.sin(ang)))

    def inside(px, py):
        hit = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                hit = not hit
            j = i
        return hit

    def fn(x, y):
        if not inside(x + 0.5, y + 0.5):
            return None
        if x + y < 11 and x < 7:
            return "y"
        return "O"
    return shape(14, 14, fn)


def badge_101():
    digits = {
        "1": [".#.", "##.", ".#.", ".#.", "###"],
        "0": ["###", "#.#", "#.#", "#.#", "###"],
    }

    def fn(x, y):
        dx, dy = x - 6.5, y - 6.5
        if abs(dx) > 6.6 or abs(dy) > 6.6 or abs(dx) + abs(dy) > 9.6:
            return None
        gx, gy = x - 1, y - 4
        if 0 <= gy < 5:
            for i, dch in enumerate("101"):
                cx = gx - i * 4
                if 0 <= cx < 3 and digits[dch][gy][cx] == "#":
                    return "K"
        if dy < -3 and dx < 2:
            return "y"
        return "Y"
    return shape(14, 14, fn)


ICON_PAL = {"K": INK, "W": WHITE, "F": RED, "f": ORANGE, "N": BROWN, "Y": YELLOW,
            "y": "#e8a85a", "C": CYAN, "G": GREEN, "g": LIME, "D": CHARCOAL,
            "R": RED, "r": ORANGE, "O": ORANGE, "S": SILVER, "B": BLUE, "k": TEAL,
            "d": SKY}


# --------------------------------------------------------------------------
# Shared CSS snippets
# --------------------------------------------------------------------------
CSS_BOB = ("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
           ".bob{animation:bob 1s steps(1,end) infinite}")
CSS_FLOAT = ("@keyframes fl{0%,100%{transform:translateY(0)}25%,75%{transform:translateY(-3px)}"
             "50%{transform:translateY(-6px)}}.fl{animation:fl 1.6s steps(1,end) infinite}")
CSS_BLINK = ("@keyframes bl{0%,55%{opacity:1}56%,100%{opacity:0}}"
             ".bl{animation:bl 1.1s steps(1,end) infinite}")
CSS_FLICKER = ("@keyframes fk{0%,100%{opacity:1}50%{opacity:.35}}"
               ".fk{animation:fk .25s steps(1,end) infinite}")
CSS_EYES = ("@keyframes ey{0%,91%{opacity:0}92%,96%{opacity:1}97%,100%{opacity:0}}"
            ".ey{opacity:0;animation:ey 4.2s steps(1,end) infinite}")


def hero_sprite(x, y, scale):
    eyes = "".join(f"M{ex} {ey}h1v1h-1z" for ex, ey in HERO_EYES)
    return (f'<g class="bob">{sprite(HERO, HERO_PAL, x, y, scale)}'
            f'<g transform="translate({x} {y}) scale({scale})"><path class="ey" fill="{SKIN}" d="{eyes}"/></g></g>')


def bot_sprite(x, y, scale, cls="fl"):
    return (f'<g class="{cls}">{sprite(BOT, BOT_PAL, x, y, scale)}'
            f'{sprite(BOT_FLAME, BOT_PAL, x, y + 12 * scale, scale, attrs=" class=\"fk\"")}'
            f'<g transform="translate({x} {y}) scale({scale})">'
            f'<path class="bl" fill="{RED}" d="M6 1h1v1h-1z"/></g></g>')


# --------------------------------------------------------------------------
# Assets
# --------------------------------------------------------------------------
def build_hero():
    W, H = 840, 360
    s = Svg(W, H, "G. Srikaanth: title screen",
            "Animated pixel-art title screen. A sunset sky with twinkling stars and drifting "
            "clouds over mountains, a hero in a blue hoodie with a floating robot companion. "
            "Text: G. Srikaanth. Cybersecurity, AI/ML, Full-stack. Press start.")
    rnd = random.Random(7)
    s.style(CSS_BOB + CSS_FLOAT + CSS_BLINK + CSS_FLICKER + CSS_EYES)
    s.style("@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}.tw{animation:tw 3s steps(3,end) infinite}"
            "@keyframes dr{to{transform:translateX(-840px)}}"
            ".far{animation:dr 140s steps(420,end) infinite}.near{animation:dr 70s steps(420,end) infinite}"
            "@keyframes sw{0%,100%{transform:translateX(0)}50%{transform:translateX(4px)}}"
            ".sw{animation:sw 1.4s steps(1,end) infinite}"
            "@keyframes sh{0%{transform:translate(0,0);opacity:0}1%{opacity:1}"
            "9%{transform:translate(240px,120px);opacity:0}100%{transform:translate(240px,120px);opacity:0}}"
            ".sh{opacity:0;animation:sh 9s linear 2s infinite}"
            "@keyframes wv{0%,50%,100%{transform:translateY(0)}10%,30%{transform:translateY(-6px)}"
            "20%{transform:translateY(-12px)}}.wv{animation:wv 2.6s steps(1,end) infinite}")

    # Sky bands with a two-step dither between each pair.
    bands = [(0, INK), (72, NAVY), (124, PLUM), (168, RED), (208, ORANGE)]
    for i, (y0, col) in enumerate(bands):
        y1 = bands[i + 1][0] if i + 1 < len(bands) else 304
        s.add(rect(0, y0, W, y1 - y0, col))
    for i, (y0, col) in enumerate(bands[1:], start=1):
        half, quarter = f"dh{i}", f"dq{i}"
        s.defs.append(
            f'<pattern id="{half}" width="8" height="8" patternUnits="userSpaceOnUse">'
            f'{rect(4, 0, 4, 4, col)}{rect(0, 4, 4, 4, col)}</pattern>'
            f'<pattern id="{quarter}" width="16" height="4" patternUnits="userSpaceOnUse">'
            f'{rect(0, 0, 4, 4, col)}</pattern>')
        s.add(rect(0, y0 - 12, W, 4, f"url(#{quarter})"), rect(0, y0 - 8, W, 8, f"url(#{half})"))

    # Stars, kept clear of the title and subtitle.
    stars = []
    while len(stars) < 46:
        x, y = rnd.randrange(1, 209) * 4, rnd.randrange(1, 29) * 4
        if 196 < x < 652 and 28 < y < 96:
            continue
        if 96 < x < 744 and 96 <= y < 134:
            continue
        if any(abs(x - a) < 20 and abs(y - b) < 16 for a, b in stars):
            continue
        stars.append((x, y))
    for x, y in stars:
        col = rnd.choice([WHITE, WHITE, CYAN, YELLOW, PEACH])
        dur, delay = rnd.uniform(1.6, 4.2), -rnd.uniform(0, 4)
        if rnd.random() < 0.3:
            d = f"M{x} {y - 4}h4v12h-4zM{x - 4} {y}h12v4h-12z"
        else:
            d = f"M{x} {y}h4v4h-4z"
        s.add(f'<path class="tw" style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s" '
              f'fill="{col}" d="{d}"/>')

    # Shooting star.
    trail = "".join(rect(-4 * k, -2 * k, 4, 4, c, f' opacity="{1 - k * 0.15:.2f}"')
                    for k, c in enumerate([WHITE, CYAN, CYAN, SILVER, SILVER, SLATE]))
    s.add(f'<g transform="translate(560 12)"><g class="sh">{trail}</g></g>')

    # Setting sun.
    s.add(f'<path fill="{YELLOW}" d="{disc(196, 216, 56)}"/>',
          f'<path fill="{CREAM}" d="{disc(196, 216, 46)}"/>')

    # Clouds: each layer is drawn twice, 840px apart, and scrolls left forever.
    def cloud_layer(shape_rows, pal, spots, cls):
        g = "".join(sprite(shape_rows, pal, x + off, y, 4) for off in (0, W) for x, y in spots)
        return f'<g class="{cls}">{g}</g>'

    s.add(cloud_layer(CLOUD_SMALL, {"L": DUSK, "S": PLUM},
                      [(40, 84), (300, 100), (520, 80), (740, 104)], "far"))

    # Far mountains with snow caps.
    peaks = [(40, 64), (150, 92), (270, 70), (400, 104), (520, 78), (650, 96), (790, 72)]
    base = 276
    d_m, d_snow = [f"M0 {H}"], []
    for c in range(0, W, 4):
        best, top = None, base
        for px, ph in peaks:
            t = base - ph + abs(c + 2 - px) * 0.9
            if t < top:
                best, top = (px, ph), t
        top = int(top // 4) * 4
        d_m.append(f"V{top}H{c + 4}")
        if best and best[1] >= 88:
            cap = base - best[1] + 16
            if top < cap:
                d_snow.append(f"M{c} {top}h4v{int(cap - top)}h-4z")
    d_m.append(f"V{H}Z")
    s.add(f'<path fill="{CHARCOAL}" d="{"".join(d_m)}"/>', f'<path fill="{SILVER}" d="{"".join(d_snow)}"/>')

    s.add(cloud_layer(CLOUD_BIG, {"L": PEACH, "S": ORANGE},
                      [(120, 180), (430, 168), (690, 186)], "near"))

    # Rolling hills with a lit rim.
    def hill_top(x):
        v = 18 + 14 * math.sin(x / 61) + 8 * math.sin(x / 23 + 2)
        return 296 - int(v // 4) * 4

    d_rim, d_hill = [f"M0 {H}"], [f"M0 {H}"]
    for c in range(0, W, 4):
        t = hill_top(c)
        d_rim.append(f"V{t}H{c + 4}")
        d_hill.append(f"V{t + 4}H{c + 4}")
    s.add(f'<path fill="{GREEN}" d="{"".join(d_rim)}V{H}Z"/>',
          f'<path fill="{TEAL}" d="{"".join(d_hill)}V{H}Z"/>')
    for x in [24, 92, 236, 284, 356, 440, 488, 540, 760, 808]:
        s.add(sprite(PINE_TREE, {"D": PINE, "N": BROWN}, x, hill_top(x) - 20, 4))

    # Ground.
    s.add(rect(0, 304, W, H - 304, GREEN), rect(0, 304, W, 4, LIME))
    specks = []
    for _ in range(70):
        x, y = rnd.randrange(0, 210) * 4, rnd.randrange(79, 90) * 4
        specks.append(f"M{x} {y}h4v4h-4z")
    s.add(f'<path fill="{MOSS}" d="{"".join(specks)}"/>')
    for _ in range(16):
        x, y = rnd.randrange(2, 205) * 4, rnd.randrange(78, 87) * 4
        if 560 < x < 740:
            continue
        col = rnd.choice([RED, YELLOW, WHITE, CYAN])
        s.add(sprite(FLOWER, {"F": col, "C": YELLOW if col != YELLOW else ORANGE, "G": MOSS}, x, y, 4))
    for i in range(18):
        x, y = rnd.randrange(0, 205) * 4, rnd.randrange(76, 86) * 4
        cls = ' class="sw"' if i % 3 == 0 else ""
        delay = f' style="animation-delay:-{rnd.uniform(0, 1.4):.2f}s"' if cls else ""
        s.add(f"<g{cls}{delay}>{sprite(TUFT, {'L': LIME, 'G': MOSS}, x, y, 4)}</g>")

    # Welcome sign.
    s.add(rect(94, 312, 8, 32, BROWN), rect(94, 312, 8, 4, INK))
    s.add(f'<path fill="{INK}" d="{srect(32, 272, 132, 44, 4, 1)}"/>',
          f'<path fill="{BROWN}" d="{srect(36, 276, 124, 36, 4, 1)}"/>',
          rect(40, 280, 116, 4, "#a8663d"))
    s.add(s.text("WELCOME!", 98, 288, 2, YELLOW, anchor="middle"))

    # Hero and companion.
    s.add(rect(604, 336, 56, 8, MOSS))
    s.add(hero_sprite(600, 248, 4))
    s.add(bot_sprite(684, 232, 3))

    # Title with a wave, then subtitle and the blinking prompt.
    title = "G. SRIKAANTH"
    scale = 6
    x0 = (W - tw(title, scale)) // 2
    s.defs.append(f'<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="{CREAM}"/><stop offset=".43" stop-color="{CREAM}"/>'
                  f'<stop offset=".43" stop-color="{YELLOW}"/><stop offset=".72" stop-color="{YELLOW}"/>'
                  f'<stop offset=".72" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ORANGE}"/>'
                  f'</linearGradient>')
    for i, ch in enumerate(title):
        if ch == " ":
            continue
        letter = s.text(ch, x0 + i * ADV * scale, 40, scale, "url(#tg)", stroke=INK,
                        shadow=(0, 8, PLUM))
        s.add(f'<g class="wv" style="animation-delay:{i * 0.09:.2f}s">{letter}</g>')
    s.add(s.text("CYBERSECURITY ◆ AI/ML ◆ FULL-STACK", W // 2, 112, 3, WHITE, "middle",
                 stroke=INK, shadow=(0, 3, INK)))
    s.add(f'<g class="bl">{s.text("▶ PRESS START", W // 2, 150, 3, YELLOW, "middle", stroke=INK)}</g>')
    s.save("hero.svg")


def build_dialog():
    W, H = 840, 176
    pages = [
        ["HI THERE! I'M SRIKAANTH, A CS STUDENT",
         "SPECIALIZING IN CYBERSECURITY. I BREAK",
         "SYSTEMS SO I CAN BUILD THEM SAFER."],
        ["I ALSO BUILD WITH AI/ML AND FULL-STACK",
         "WEB DEV. RIGHT NOW I'M EXPLORING AGENTIC",
         "AI AND APPLIED CRYPTOGRAPHY. LET'S TALK!"],
    ]
    s = Svg(W, H, "Dialogue: hi, I'm Srikaanth",
            " ".join(" ".join(p) for p in pages).capitalize())
    s.style(CSS_BLINK)
    T, page_len, speed = 18.0, 9.0, 0.045
    s.style("@keyframes p0{0%{opacity:1}50%,100%{opacity:0}}@keyframes p1{0%{opacity:0}50%,100%{opacity:1}}"
            f".p0{{animation:p0 {T}s steps(1,end) infinite}}.p1{{opacity:0;animation:p1 {T}s steps(1,end) infinite}}"
            "@keyframes nx{0%,100%{transform:translateY(0)}50%{transform:translateY(4px)}}"
            ".nx{animation:nx .8s steps(1,end) infinite}")

    s.add(frame(8, 32, 824, 140, WHITE, border=SKY))
    s.add(frame(24, 6, 196, 46, BLUE, border=WHITE))
    s.add(s.text("SRIKAANTH", 122, 19, 3, WHITE, "middle", stroke=INK))

    lx, ly, lh, scale = 40, 70, 30, 3
    s.defs.append(f'<clipPath id="inner"><rect x="22" y="46" width="796" height="112"/></clipPath>')
    for p, lines in enumerate(pages):
        t = p * page_len + 0.5
        parts, covers = [], []
        for i, line in enumerate(lines):
            parts.append(s.text(line, lx, ly + i * lh, scale, INK))
            n = len(line)
            dur = n * speed
            L = n * ADV * scale + 4
            name = f"c{p}{i}"
            s.style(f"@keyframes {name}{{0%{{transform:translateX(0)}}"
                    f"{pct(t, T)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
                    f"{pct(t + dur, T)},100%{{transform:translateX({L}px)}}}}"
                    f".{name}{{transform:translateX({L}px);animation:{name} {T}s linear infinite}}")
            covers.append(rect(lx - 2, ly + i * lh - 3, L, 27, WHITE, f' class="{name}"'))
            t += dur + 0.25
        s.add(f'<g class="p{p}">{"".join(parts)}<g clip-path="url(#inner)">{"".join(covers)}</g></g>')
    s.add(f'<g class="nx">{s.text("▼", 792, 146, 3, RED)}</g>')
    s.save("dialog.svg")


def build_button(name, label, icon, icon_pal, bg, shade):
    scale, pad, gap = 3, 20, 14
    iw, ih = len(icon[0]) * 3, len(icon) * 3
    W = pad + iw + gap + tw(label, scale) + pad
    H = 64
    s = Svg(W, H, label.title(), f"Pixel-art button: {label.title()}")
    s.style("@keyframes sn{0%,70%{transform:translateX(-80px)}100%{transform:translateX(" + str(W + 40) + "px)}}"
            ".sn{animation:sn 4s linear infinite}")
    s.add(f'<path fill="{INK}" d="{srect(0, 4, W, H - 4, 4, 2)}"/>')
    s.add(f'<path fill="{INK}" d="{srect(0, 0, W, H - 6, 4, 2)}"/>')
    s.add(f'<path fill="{shade}" d="{srect(4, 4, W - 8, H - 14, 4, 1)}"/>')
    s.add(f'<path fill="{bg}" d="{srect(4, 4, W - 8, H - 20, 4, 1)}"/>')
    s.add(rect(12, 8, W - 24, 4, "#ffffff", ' opacity=".35"'))
    s.defs.append(f'<clipPath id="bc"><path d="{srect(4, 4, W - 8, H - 14, 4, 1)}"/></clipPath>')
    s.add(f'<g clip-path="url(#bc)"><g class="sn"><path fill="#ffffff" opacity=".25" '
          f'd="M0 0h16l-24 64h-16zM24 0h6l-24 64h-6z"/></g></g>')
    s.add(sprite(icon, icon_pal, pad, (H - 10 - ih) // 2 + 2, 3))
    s.add(s.text(label, pad + iw + gap, (H - 10 - 21) // 2 + 2, scale, WHITE, stroke=INK))
    s.save(name)


def build_card():
    W, H = 840, 344
    s = Svg(W, H, "Player card: G. Srikaanth",
            "Player card. Name: G. Srikaanth. Class: CS student, cybersecurity. Guild: MS Ramaiah "
            "Institute of Technology. Degree: B.E. CSE (Cybersecurity). CGPA 8.88 out of 10. Last job: "
            "Software Engineer Intern at GS3 Software. Moves: pentesting, vulnerability assessment, "
            "secure system design. Current quest: agentic AI and applied cryptography. Types: SEC, AI, WEB.")
    s.style(CSS_BOB + CSS_FLOAT + CSS_BLINK + CSS_FLICKER + CSS_EYES)
    s.style("@keyframes sh{0%,62%{transform:translateX(-360px)}100%{transform:translateX(1200px)}}"
            ".shine{animation:sh 7s linear infinite}"
            "@keyframes fill{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}"
            ".bar{transform-box:fill-box;transform-origin:left;animation:fill 2.4s steps(24,end) .4s both}")

    s.defs.append(f'<pattern id="stripes" width="16" height="16" patternUnits="userSpaceOnUse">'
                  f'<path fill="#2f3f7f" d="M0 12h4v4h-4zM4 8h4v4h-4zM8 4h4v4h-4zM12 0h4v4h-4z"/></pattern>'
                  f'<pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">'
                  f'{rect(0, 0, 16, 2, "#2c8a8f")}{rect(0, 0, 2, 16, "#2c8a8f")}</pattern>'
                  f'<pattern id="dots" width="8" height="2" patternUnits="userSpaceOnUse">'
                  f'{rect(0, 0, 4, 2, "#3b4a8a")}</pattern>')
    s.add(frame(4, 4, W - 8, H - 8, NAVY, border=YELLOW))
    s.add(rect(14, 14, W - 28, H - 28, "url(#stripes)"))
    # header strip
    s.add(f'<path fill="{RED}" d="{srect(20, 20, W - 40, 44, 4, 1)}"/>', rect(24, 56, W - 48, 4, PLUM))
    s.add(s.text("★ PLAYER CARD", 36, 31, 3, WHITE, stroke=INK))
    s.add(s.text("GITHUB.COM/SRIKANTLOSE", W - 36, 35, 2, YELLOW, "end", stroke=INK))

    # portrait
    s.add(frame(24, 76, 204, 244, TEAL, border=WHITE))
    s.add(rect(36, 88, 180, 220, "url(#grid)"))
    s.add(f'<path fill="{GREEN}" d="{srect(60, 268, 132, 20, 4, 1)}"/>', rect(64, 268, 124, 4, LIME))
    s.add(hero_sprite(78, 132, 6))
    s.add(bot_sprite(172, 98, 3))

    # fields
    lx, vx = 252, 384
    rows = [
        ("CLASS", "CS STUDENT // CYBERSECURITY"),
        ("GUILD", "MS RAMAIAH INSTITUTE OF TECHNOLOGY"),
        ("DEGREE", "B.E. CSE (CYBERSECURITY)"),
        ("CGPA", "8.88 / 10"),
        ("LAST JOB", "SWE INTERN @ GS3 SOFTWARE"),
        ("MOVES", "PENTESTING ◆ VULN ASSESSMENT"),
        ("", "SECURE SYSTEM DESIGN"),
        ("QUEST", "AGENTIC AI + APPLIED CRYPTO"),
    ]
    s.add(s.text("NAME", lx, 86, 2, CYAN))
    s.add(s.text("G. SRIKAANTH", vx, 80, 3, YELLOW, stroke=INK))
    cx = 628
    for label, col, fg in [("SEC", RED, WHITE), ("AI", PLUM, WHITE), ("WEB", BLUE, WHITE)]:
        w = tw(label, 2) + 16
        s.add(f'<path fill="{INK}" d="{srect(cx - 2, 76, w + 4, 30, 2, 1)}"/>',
              f'<path fill="{col}" d="{srect(cx, 78, w, 26, 2, 1)}"/>')
        s.add(s.text(label, cx + 8, 84, 2, fg))
        cx += w + 10
    s.add(rect(lx, 108, 556, 2, "url(#dots)"))
    y = 120
    for label, value in rows:
        if label:
            s.add(s.text(label, lx, y, 2, CYAN))
        s.add(s.text(value, vx, y, 2, WHITE))
        if label == "CGPA":
            bx, bw = 508, 296
            s.add(f'<path fill="{INK}" d="{srect(bx, y - 4, bw, 22, 2, 1)}"/>',
                  rect(bx + 4, y, bw - 8, 14, CHARCOAL))
            fill_w = int((bw - 8) * 0.888)
            s.add(f'<g class="bar">{rect(bx + 4, y, fill_w, 14, GREEN)}{rect(bx + 4, y, fill_w, 4, LIME)}</g>')
        y += 24 if label == "MOVES" else 26
        if label != "MOVES":
            s.add(rect(lx, y - 8, 556, 2, "url(#dots)"))

    # shine sweep
    s.defs.append(f'<clipPath id="cc"><path d="{srect(4, 4, W - 8, H - 8, 4, 2)}"/></clipPath>')
    s.add(f'<g clip-path="url(#cc)"><g class="shine"><path fill="#ffffff" opacity=".10" '
          f'd="M120 0h48l-130 {H}h-48zM196 0h16l-130 {H}h-16z"/></g></g>')
    s.save("player-card.svg")


def build_header(name, title, sub, accent, icon, icon_pal, icon_scale=3):
    W, H = 840, 64
    s = Svg(W, H, title.title(), f"Section header: {title.title()}. {sub.capitalize()}")
    s.style(CSS_BLINK + CSS_FLOAT + CSS_FLICKER)
    s.add(f'<path fill="{INK}" d="{srect(4, 6, W - 8, 52, 4, 2)}"/>')
    s.add(f'<path fill="{PANEL}" d="{srect(8, 10, W - 16, 40, 4, 1)}"/>')
    s.add(rect(12, 50, W - 24, 4, accent))
    ih = len(icon) * icon_scale
    s.add(f'<g class="fl">{sprite(icon, icon_pal, 24, 30 - ih // 2, icon_scale)}</g>')
    tx = 24 + len(icon[0]) * icon_scale + 16
    s.add(s.text(title, tx, 20, 3, accent, stroke=INK))
    s.add(s.text(sub, W - 28, 24, 2, SILVER, "end"))
    s.add(f'<g class="bl">{s.text("▶", tx + tw(title, 3) + 14, 24, 2, WHITE)}</g>')
    s.save(name)


GH = "https://github.com/srikantlose/"
PROJECTS = [
    dict(slug="sentinelai", name="SENTINEL AI", icon=SHIELD, accent=RED, repo=GH + "SentinelAI",
         blurb="Real-time network intrusion detection for botnet traffic: Scapy packet capture, "
               "ML flow classification and SHAP explanations for every flag.",
         desc=["REAL-TIME BOTNET", "DETECTION (NIDS)"],
         chips=[("PYTHON", WHITE, INK), ("SEC", RED, WHITE), ("AI", PLUM, WHITE)]),
    dict(slug="cheaproute", name="CHEAPROUTE", icon=SIGNPOST, accent=ORANGE, repo=GH + "cheaproute-agent",
         blurb="AMD Developer Hackathon ACT II, Track 1. Answers with a small local Gemma model "
               "and only escalates to the cloud when confidence drops.",
         desc=["TOKEN-EFFICIENT LLM", "ROUTING AGENT"],
         chips=[("PYTHON", WHITE, INK), ("AI", PLUM, WHITE), ("AGENT", ORANGE, INK)]),
    dict(slug="fourtakes", name="FOURTAKES", icon=TV, accent=CYAN, repo=GH + "fourtakes",
         blurb="AMD Developer Hackathon ACT II, Track 2. Captions short videos in four voices: "
               "formal, sarcastic, techie and non-techie humour.",
         desc=["VIDEO CAPTIONS IN 4", "DISTINCT VOICES"],
         chips=[("PYTHON", WHITE, INK), ("AI", PLUM, WHITE), ("VISION", CYAN, INK)]),
    dict(slug="penumbra", name="PENUMBRA", icon=None, accent=YELLOW, repo=GH + "Penumbra",
         blurb="A chess platform mapping the solved frontier of chess. The Fog Index measures how "
               "unsolved a position is; engines and community compute push it back.",
         desc=["MAPPING THE SOLVED", "FRONTIER OF CHESS"],
         chips=[("TYPESCRIPT", WHITE, INK), ("RUST", ORANGE, INK), ("WEB", BLUE, WHITE)]),
    dict(slug="sanjeevani", name="SANJEEVANI", icon=HEART, accent=LIME, repo=GH + "ProjectSanjeevani",
         blurb="Final-year project: spots road accidents in traffic-camera footage within seconds "
               "and drives a golden-hour emergency response.",
         desc=["AI ACCIDENT DETECTION", "+ GOLDEN-HOUR RESPONSE"],
         chips=[("PYTHON", WHITE, INK), ("AI", PLUM, WHITE), ("CV", TEAL, WHITE)]),
    dict(slug="devyatra", name="DEVYATRA", icon=TEMPLE, accent=SKY, repo=GH + "DevYatra",
         blurb="AI crowd management for Gujarat's pilgrimage sites, submitted to GUJCOST: crowd "
               "density vision, virtual queues and emergency alerts.",
         desc=["AI CROWD MANAGEMENT", "FOR PILGRIMAGE SITES"],
         chips=[("TYPESCRIPT", WHITE, INK), ("AI", PLUM, WHITE), ("WEB", BLUE, WHITE)]),
]


def build_party_card(i, p):
    W, H = 410, 140
    s = Svg(W, H, p["name"].title(),
            f"Party member {i + 1}: {p['name'].title()}. {' '.join(p['desc']).capitalize()}. "
            f"Tags: {', '.join(c[0] for c in p['chips'])}.")
    s.style(CSS_BOB)
    s.add(frame(2, 2, W - 4, H - 4, PANEL, border=p["accent"]))
    s.add(f'<path fill="{DEEP}" d="{srect(18, 22, 92, 96, 4, 1)}"/>')
    s.add(rect(22, 106, 84, 8, p["accent"], ' opacity=".35"'))
    icon = outline(p["icon"] or moon_icon())
    iw, ih = len(icon[0]) * 5, len(icon) * 5
    s.add(f'<g class="bob" style="animation-delay:-{i * 0.17:.2f}s">'
          f'{sprite(icon, ICON_PAL, 18 + (92 - iw) // 2, 22 + (92 - ih) // 2, 5)}</g>')
    s.add(s.text(f"NO.{i + 1}", W - 20, 22, 2, p["accent"], "end"))
    s.add(s.text(p["name"], 124, 20, 3, WHITE, stroke=INK))
    cx = 124
    for label, bg, fg in p["chips"]:
        w = tw(label, 2) + 12
        s.add(f'<path fill="{INK}" d="{srect(cx, 52, w, 24, 2, 1)}"/>',
              f'<path fill="{bg}" d="{srect(cx, 50, w, 22, 2, 1)}"/>')
        s.add(s.text(label, cx + 6, 54, 2, fg))
        cx += w + 8
    for j, line in enumerate(p["desc"]):
        s.add(s.text(line, 124, 86 + j * 20, 2, SILVER if j else WHITE))
    s.save(f"party-{p['slug']}.svg")


CERTS = [
    (badge_cloud, "GOOGLE CLOUD", "CYBERSECURITY", "Google Cloud Cybersecurity Certificate", "Google"),
    (badge_radar, "IBM: THREAT", "INTEL & HUNT",
     "Getting Started with Threat Intelligence and Hunting", "IBM SkillsBuild"),
    (badge_eye, "IBM: SOC IN", "PRACTICE", "Security Operations Center in Practice", "IBM SkillsBuild"),
    (badge_star, "ANTHROPIC:", "AI FLUENCY", "AI Fluency: Framework & Foundations", "Anthropic"),
    (badge_101, "ANTHROPIC:", "CLAUDE 101", "Claude 101", "Anthropic"),
]


def build_badges():
    W, H = 840, 252
    certs = [(fn(), l1, l2) for fn, l1, l2, *_ in CERTS]
    s = Svg(W, H, "Badge case: certifications",
            "Badge case with five certifications: Google Cloud Cybersecurity Certificate; "
            "IBM SkillsBuild Getting Started with Threat Intelligence and Hunting; IBM SkillsBuild "
            "Security Operations Center in Practice; Anthropic AI Fluency Framework and Foundations; "
            "Anthropic Claude 101.")
    s.style(CSS_FLOAT)
    s.style("@keyframes sp{0%,100%{opacity:0}5%,15%{opacity:1}20%{opacity:0}}"
            ".sp{opacity:0;animation:sp 5s steps(1,end) infinite}"
            "@keyframes sp2{0%,100%{transform:translate(0,0)}10%{transform:translate(0,-2px)}}")
    s.add(frame(4, 4, W - 8, H - 8, VELVET, border=YELLOW))
    s.add(s.text("BADGE CASE", 32, 26, 3, YELLOW, stroke=INK))
    s.add(s.text("CERTIFICATIONS ◆ 5 EARNED", W - 32, 30, 2, PEACH, "end"))
    s.add(rect(24, 56, W - 48, 4, VELVET_DARK))
    for i, (rows, l1, l2) in enumerate(certs):
        cx = 96 + i * 162
        x = cx - 80
        s.add(f'<path fill="{VELVET_DARK}" d="{srect(x + 16, 72, 128, 104, 4, 2)}"/>',
              rect(x + 24, 164, 112, 4, "#2a1030"))
        icon = outline(rows)
        iw, ih = len(icon[0]) * 5, len(icon) * 5
        bx, by = cx - iw // 2, 124 - ih // 2
        s.add(rect(bx + 8, by + ih + 2, iw - 16, 6, "#2a1030"))
        s.add(f'<g class="fl" style="animation-delay:-{i * 0.3:.1f}s">{sprite(icon, ICON_PAL, bx, by, 5)}</g>')
        s.add(f'<g class="sp" style="animation-delay:{i:.1f}s">'
              f'{sprite(SPARKLE, {"W": WHITE}, bx + iw - 14, by - 4, 4)}</g>')
        s.add(s.text(l1, cx, 190, 2, WHITE, "middle"), s.text(l2, cx, 210, 2, PEACH, "middle"))
    s.save("badges.svg")


POCKETS = [
    ("LANGUAGES", YELLOW, INK, [
        ("PYTHON", "Main weapon. Powers SentinelAI, CheapRoute, FourTakes and Sanjeevani."),
        ("TYPESCRIPT", "Typed JS behind Penumbra, DevYatra and GyaanGuru."),
        ("JAVASCRIPT", "The web's native tongue. Runs the FourTakes demo."),
        ("C++", "The classic. AIQuiz and AIParkingSpotFinder are written in it."),
        ("RUST", "Penumbra's verifier and prover crates."),
        ("SQL", "Postgres schemas, queries and PL/pgSQL."),
    ]),
    ("AI / ML", LIME, INK, [
        ("XGBOOST", "Gradient-boosted trees behind the botnet detectors."),
        ("SHAP", "Explains exactly why SentinelAI flagged a flow."),
        ("YOLO", "Real-time vision for crowd density in DevYatra."),
        ("LLAMA.CPP", "Runs a local Gemma model inside CheapRoute, on CPU."),
        ("QISKIT", "Quantum circuits for the error-mitigation bench."),
        ("GEMINI", "Generates personalised learning roadmaps in GyaanGuru."),
    ]),
    ("WEB / APP", SKY, INK, [
        ("NEXT.JS", "React framework behind GyaanGuru."),
        ("NODE.JS", "Runtime for the Penumbra platform."),
        ("FASTAPI", "SentinelAI's inference and logging API."),
        ("STREAMLIT", "Live security dashboards for SentinelAI and CyberShield."),
        ("SUPABASE", "Auth and Postgres backend for GyaanGuru."),
    ]),
    ("SECURITY", RED, WHITE, [
        ("PENTESTING", "Finding the cracks before someone else does."),
        ("VULN ASSESSMENT", "Scoping, scanning and prioritising weaknesses."),
        ("SCAPY", "Packet capture and flow features for SentinelAI."),
        ("NIDS", "Network intrusion detection, built ML-first."),
    ]),
    ("INFRA", CYAN, INK, [
        ("DOCKER", "Ships CheapRoute and FourTakes as hackathon containers."),
        ("POSTGRESQL", "Penumbra's main datastore."),
        ("REDIS", "Penumbra's in-memory store."),
        ("MINIO", "S3-compatible object storage for Penumbra."),
        ("GIT", "Save points for code."),
    ]),
]


def build_bag():
    pockets = [(label, bg, fg, [name for name, _ in items]) for label, bg, fg, items in POCKETS]
    row_h, top = 42, 76
    W, H = 840, top + len(pockets) * row_h + 24
    s = Svg(W, H, "Bag: tech inventory",
            "Tech inventory. " + " ".join(f"{p[0].title()}: {', '.join(p[3])}." for p in pockets))
    s.style(CSS_BLINK)
    n = len(pockets)
    kf = "".join(f"{pct(i * 2.2, n * 2.2)}{{transform:translateY({i * row_h}px)}}" for i in range(n))
    s.style(f"@keyframes cur{{{kf}100%{{transform:translateY({(n - 1) * row_h}px)}}}}"
            f".cur{{animation:cur {n * 2.2}s steps(1,end) infinite}}")
    s.add(frame(4, 4, W - 8, H - 8, PANEL, border=LIME))
    s.add(s.text("BAG", 32, 26, 3, LIME, stroke=INK))
    s.add(s.text("TECH INVENTORY ◆ ITEMS I USE", W - 32, 30, 2, SILVER, "end"))
    s.add(rect(24, 56, W - 48, 4, DEEP))
    s.add(f'<g class="cur">{rect(20, top - 8, W - 40, row_h - 4, "#2b2f55")}'
          f'<g class="bl">{s.text("▶", 28, top + 4, 2, WHITE)}</g></g>')
    for i, (label, bg, fg, items) in enumerate(pockets):
        y = top + i * row_h
        s.add(s.text(label, 48, y + 4, 2, bg))
        cx = 196
        for item in items:
            w = tw(item, 2) + 16
            assert cx + w <= W - 20, f"bag row {label!r} overflows"
            s.add(f'<path fill="{INK}" d="{srect(cx, y + 2, w, 24, 2, 1)}"/>',
                  f'<path fill="{bg}" d="{srect(cx, y, w, 22, 2, 1)}"/>')
            s.add(s.text(item, cx + 8, y + 4, 2, fg))
            cx += w + 8
    s.save("bag.svg")


def build_footer():
    W, H = 840, 168
    s = Svg(W, H, "Thanks for playing!",
            "Saving... Don't turn off the power. Thanks for playing! See you next time, traveler.")
    s.style(CSS_FLICKER + CSS_BLINK)
    T = 10
    s.style(f"@keyframes pa{{0%{{opacity:1}}40%,100%{{opacity:0}}}}@keyframes pb{{0%{{opacity:0}}40%,100%{{opacity:1}}}}"
            f".pa{{opacity:0;animation:pa {T}s steps(1,end) infinite}}.pb{{animation:pb {T}s steps(1,end) infinite}}"
            f"@keyframes ld{{0%{{transform:scaleX(0)}}32%,100%{{transform:scaleX(1)}}}}"
            f".ld{{transform-box:fill-box;transform-origin:left;animation:ld {T}s steps(20,end) infinite}}"
            f"@keyframes fly{{0%{{transform:translateX(-80px)}}100%{{transform:translateX(920px)}}}}"
            f".fly{{animation:fly {T}s linear infinite}}"
            "@keyframes hb{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
            ".hb{animation:hb .9s steps(1,end) infinite}")
    s.add(frame(4, 4, W - 8, H - 8, INK, border=SKY))
    # page A: saving
    pa = [s.text("SAVING...", W // 2, 40, 3, WHITE, "middle"),
          f'<path fill="{SLATE}" d="{srect(220, 76, 400, 24, 2, 1)}"/>', rect(224, 80, 392, 16, DEEP),
          f'<g class="ld">{rect(224, 80, 392, 16, GREEN)}{rect(224, 80, 392, 4, LIME)}</g>',
          s.text("DON'T TURN OFF THE POWER.", W // 2, 116, 2, SILVER, "middle")]
    s.add(f'<g class="pa">{"".join(pa)}</g>')
    # page B: thanks
    pb = [s.text("THANKS FOR PLAYING!", W // 2, 36, 4, YELLOW, "middle", stroke=INK, shadow=(0, 8, RED)),
          f'<g class="hb">{s.text("♥", 196, 92, 3, RED)}</g>',
          f'<g class="hb" style="animation-delay:-.45s">{s.text("♥", 628, 92, 3, RED)}</g>',
          s.text("SEE YOU NEXT TIME, TRAVELER", W // 2, 94, 2, CYAN, "middle")]
    s.add(f'<g class="pb">{"".join(pb)}</g>')
    s.add(f'<g class="fly">{bot_sprite(0, 124, 2, cls="")}</g>')
    s.save("footer.svg")


def build_web_data():
    """Export sprites and profile data for the interactive page in docs/."""
    def pack(rows, pal):
        used = sorted({c for r in rows for c in r if c != "."})
        return {"rows": rows, "pal": {c: pal[c] for c in used}}

    data = {
        "hero": pack(HERO, HERO_PAL),
        "heroEyes": HERO_EYES,
        "bot": pack(BOT, BOT_PAL),
        "flame": pack(BOT_FLAME, BOT_PAL),
        "pine": pack(PINE_TREE, {"D": PINE, "N": BROWN}),
        "cloudBig": pack(CLOUD_BIG, {"L": PEACH, "S": ORANGE}),
        "cloudSmall": pack(CLOUD_SMALL, {"L": DUSK, "S": PLUM}),
        "projects": [{
            "name": p["name"], "repo": p["repo"], "accent": p["accent"], "blurb": p["blurb"],
            "chips": [{"label": c[0], "bg": c[1], "fg": c[2]} for c in p["chips"]],
            "icon": pack(outline(p["icon"] or moon_icon()), ICON_PAL),
        } for p in PROJECTS],
        "certs": [{"name": full, "issuer": issuer, "icon": pack(outline(fn()), ICON_PAL)}
                  for fn, _, _, full, issuer in CERTS],
        "pockets": [{"label": label, "color": bg, "fg": fg,
                     "items": [{"name": n, "desc": d} for n, d in items]}
                    for label, bg, fg, items in POCKETS],
    }
    out = ROOT / "docs" / "sprites.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("// Generated by scripts/build_assets.py. Do not edit by hand.\n"
                   f"window.SPRITES = {json.dumps(data, separators=(',', ':'))};\n", encoding="utf-8")
    print(f"  {'../docs/sprites.js':<28} {out.stat().st_size / 1024:6.1f} KB")


def main():
    print("Building assets ->", OUT.relative_to(ROOT))
    build_hero()
    build_dialog()
    build_button("btn-email.svg", "EMAIL", ENVELOPE, {"K": INK, "W": WHITE}, RED, PLUM)
    build_button("btn-linkedin.svg", "LINKEDIN", BRIEFCASE,
                 {"K": INK, "B": BROWN, "Y": YELLOW}, BLUE, NAVY)
    build_button("btn-play.svg", "PRESS START", GAMEPAD,
                 {"K": INK, "W": WHITE, "R": RED}, GREEN, TEAL)
    build_card()
    build_header("header-party.svg", "PARTY", "PINNED PROJECTS ◆ CLICK ONE TO INSPECT", ORANGE,
                 outline(BOT[3:10]), {**BOT_PAL, "K": INK})
    build_header("header-save.svg", "SAVE DATA", "LIVE GITHUB STATS ◆ UPDATED DAILY", CYAN,
                 outline(FLOPPY), {"K": INK, "B": BLUE, "S": SILVER, "W": WHITE})
    for i, p in enumerate(PROJECTS):
        build_party_card(i, p)
    build_badges()
    build_bag()
    build_footer()
    build_web_data()


if __name__ == "__main__":
    main()
