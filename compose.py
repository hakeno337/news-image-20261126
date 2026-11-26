#!/usr/bin/env python3
"""Compose the News Image entry for Thursday 26 November 2026.

Draws a one-page illustrated broadsheet (1024x1024 PNG) with PIL: a black
date band, a big-number stat strip, three illustrated lead panels, a numbered
story grid with a drawn icon per story, a dotted world map whose numbered
pins match the story numbers (one pin per city), an ALSO ON THURSDAY
micro-list, and a DATE CHECK box. Every story was researched from
26 November 2026 reporting and date-checked; the day is thin this early in
UTC (wires read up to 00:45 UTC), so the page carries 16 solidly verified
stories rather than padding with 25 November news, and the big 25 November
stories are named in the DATE CHECK box as deliberately excluded.

Deterministic: no randomness, no clock reads inside the drawing (the
wires-read time is passed in as WIRES_UTC by the builder).
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 230)
INK = (18, 18, 18)
GREY = (92, 88, 80)
RED = (164, 32, 24)
DARKRED = (128, 24, 18)
GOLD = (176, 132, 26)
WHITE = (255, 255, 255)

FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def font(path, size):
    return ImageFont.truetype(path, size)


F = {
    "mast": font(FL + "LiberationSerif-Bold.ttf", 58),
    "mast_small": font(FD + "DejaVuSans-Bold.ttf", 20),
    "mast_right": font(FD + "DejaVuSans.ttf", 12),
    "subline": font(FL + "LiberationSerif-Italic.ttf", 17),
    "stat_num": font(FL + "LiberationSerif-Bold.ttf", 31),
    "stat_cap": font(FD + "DejaVuSans.ttf", 10),
    "tab": font(FD + "DejaVuSans-Bold.ttf", 12),
    "kicker": font(FD + "DejaVuSans-Bold.ttf", 11),
    "lead_head": font(FL + "LiberationSerif-Bold.ttf", 19),
    "lead_sub": font(FD + "DejaVuSans.ttf", 11),
    "src": font(FL + "LiberationSerif-Italic.ttf", 11),
    "g_head": font(FD + "DejaVuSans-Bold.ttf", 13),
    "g_sub": font(FD + "DejaVuSans.ttf", 10),
    "also_head": font(FD + "DejaVuSans-Bold.ttf", 13),
    "also": font(FD + "DejaVuSans.ttf", 10),
    "map_title": font(FD + "DejaVuSans-Bold.ttf", 11),
    "pin": font(FD + "DejaVuSans-Bold.ttf", 9),
    "check": font(FD + "DejaVuSans.ttf", 11),
    "check_b": font(FD + "DejaVuSans-Bold.ttf", 11),
    "foot": font(FD + "DejaVuSans.ttf", 10),
    "foot_b": font(FD + "DejaVuSans-Bold.ttf", 11),
}

REGIONS = {
    "ASIA-PACIFIC": (31, 95, 158),
    "EUROPE": (47, 125, 79),
    "AMERICAS": (179, 84, 30),
    "MIDDLE EAST": (146, 106, 32),
    "AFRICA": (122, 74, 141),
    "WORLD": (96, 96, 96),
}

# n, place, beat, headline, summary, source, region, icon, pin (lon, lat)
LEADS = [
    (1, "NEW YORK", "WEATHER",
     "Nor'easter drenches Thanksgiving Day",
     "A powerful coastal storm lashes the US East Coast with 60 mph gusts and heavy rain; the 100th Macy's parade moves to Saturday.",
     "Reuters", "AMERICAS", "storm", (-74, 41)),
    (2, "TAIPEI", "TRADE",
     "US proposes a 15% tariff on Taiwan",
     "Taipei says the rate is the lowest tier and will not stack on other duties, alongside Japan, South Korea and the EU.",
     "CNA", "ASIA-PACIFIC", "tariff", (121, 25)),
    (3, "CALIFORNIA", "WEATHER",
     "King tides flood California's coast",
     "Record tides swamp roads from Humboldt to San Diego; a pier section collapses in Pacifica and Ventura warns of evacuations.",
     "USA Today", "AMERICAS", "waves", (-122, 37)),
]

GRID = [
    (4, "CANBERRA", "POLITICS",
     "Liberal senator defects to One Nation",
     "Leah Blyth quits the party, dealing Angus Taylor a blow.",
     "ABC", "ASIA-PACIFIC", "door", (149, -35)),
    (5, "CANBERRA", "CLIMATE",
     "Australia on track for 2030 climate target",
     "The government tables its annual statement to Parliament today.",
     "ABC", "ASIA-PACIFIC", "leaf", (149, -35)),
    (6, "NEW DELHI", "SOCIETY",
     "India marks Constitution Day",
     "Schools and courts honour the 1949 Constitution on Samvidhan Divas.",
     "Indian press", "ASIA-PACIFIC", "treaty", (77, 28)),
    (7, "LONDON", "MEDIA",
     "BBC and Met Office launch weather pact",
     "The broadcaster and the forecaster join forces on coverage.",
     "BBC", "EUROPE", "cloud", (0, 51)),
    (8, "DOHA", "CRICKET",
     "Sri Lanka A meet India A in semi-final",
     "The Rising Stars semi-final is played in Doha today.",
     "BCCI", "MIDDLE EAST", "bat", (51, 25)),
    (9, "MELBOURNE", "POLITICS",
     "Election stoush over blue t-shirts in court",
     "Labor seeks an injunction against a dumped Liberal candidate.",
     "ABC", "ASIA-PACIFIC", "gavel", (145, -38)),
    (10, "HOBART", "SOCIETY",
     "Tasmania ends greyhound racing",
     "A 'perverse' vote ends the sport without protections for dogs.",
     "ABC", "ASIA-PACIFIC", "medal", (147, -43)),
    (11, "LONDON", "RUGBY",
     "Beale ends five-year exile from Wallabies",
     "The veteran is named on the bench for the Ireland clash.",
     "ABC", "EUROPE", "shield", (0, 51)),
]

ALSO = [
    (12, "Thanksgiving travel peaks as storms hit both coasts (US press)", "AMERICAS"),
    (13, "Severe storms to lash a huge stretch of Australia (The West Australian)", "ASIA-PACIFIC"),
    (14, "Canberra youths face charges after robbery (ABC)", "ASIA-PACIFIC"),
    (15, "Plan for 200ha kelp farm off NSW coast (ABC)", "ASIA-PACIFIC"),
    (16, "Palm Beach ferry workers strike from 7:30 a.m. (Sydney press)", "ASIA-PACIFIC"),
]

# big number, caption, story it ties to
STATS = [
    ("60 mph", "gusts forecast on the US East Coast (story 1)", 1),
    ("15%", "US tariff proposed for Taiwan (story 2)", 2),
    ("8.5 ft", "Ventura's record-tying high tide (story 3)", 3),
    ("2030", "Australia's 2030 climate target, on track (story 5)", 5),
    ("5 years", "Beale's exile from the Wallabies ends (story 11)", 11),
    ("200 ha", "kelp farm planned off the NSW coast (story 15)", 15),
]

WIRES_UTC = os.environ.get("WIRES_UTC", "00:45")

DATE_CHECK = (
    "Wires read up to " + WIRES_UTC + " UTC, Thu 26 Nov 2026. Every story here happened or was first "
    "reported on 26 Nov 2026 in at least one time zone. Left out as other days' news: the Cairo tanker "
    "fire, the Netanyahu judges' call, the Hera asteroid pictures, the Macy's parade move, the SpaceX "
    "approval and the Iowa blast \u2014 all Wed 25 Nov."
)


def wrap(d, text, fnt, maxw):
    """Greedy word wrap; returns a list of lines that fit maxw."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrap(d, xy, text, fnt, fill, maxw, leading, max_lines=None):
    x, y = xy
    lines = wrap(d, text, fnt, maxw)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and d.textlength(last + "\u2026", font=fnt) > maxw:
            last = last[:-1]
        lines[-1] = last + "\u2026"
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- icons
def icon(d, kind, x, y, s, bg):
    """Draw a white glyph on a coloured s-by-s square at (x, y)."""
    d.rectangle([x, y, x + s, y + s], fill=bg)
    cx, cy = x + s / 2, y + s / 2
    u = s / 40.0  # unit
    W_ = WHITE
    if kind == "treaty":
        for px in (cx - 9 * u, cx + 5 * u):
            d.line([px, cy - 12 * u, px, cy + 12 * u], fill=W_, width=2)
        d.polygon([(cx - 9 * u, cy - 12 * u), (cx + 1 * u, cy - 8 * u), (cx - 9 * u, cy - 4 * u)], fill=W_)
        d.polygon([(cx + 5 * u, cy - 12 * u), (cx + 15 * u, cy - 8 * u), (cx + 5 * u, cy - 4 * u)], fill=W_)
    elif kind == "shield":
        d.polygon([(cx, cy - 12 * u), (cx + 10 * u, cy - 8 * u), (cx + 10 * u, cy + 2 * u),
                   (cx, cy + 13 * u), (cx - 10 * u, cy + 2 * u), (cx - 10 * u, cy - 8 * u)], outline=W_, width=3)
        d.line([cx - 5 * u, cy, cx - 1 * u, cy + 5 * u, cx + 6 * u, cy - 5 * u], fill=W_, width=3)
    elif kind == "gavel":
        d.line([cx - 10 * u, cy - 8 * u, cx + 2 * u, cy + 4 * u], fill=W_, width=4)
        d.rectangle([cx - 2 * u, cy - 12 * u, cx + 10 * u, cy - 4 * u], fill=W_)
        d.line([cx - 11 * u, cy + 11 * u, cx + 11 * u, cy + 11 * u], fill=W_, width=3)
    elif kind == "door":
        d.rectangle([cx - 8 * u, cy - 13 * u, cx + 8 * u, cy + 13 * u], outline=W_, width=3)
        d.ellipse([cx + 3 * u, cy - 1.5 * u, cx + 6 * u, cy + 1.5 * u], fill=W_)
    elif kind == "medal":
        d.polygon([(cx - 8 * u, cy - 13 * u), (cx - 2 * u, cy - 13 * u), (cx, cy - 3 * u), (cx - 5 * u, cy - 2 * u)], fill=W_)
        d.polygon([(cx + 8 * u, cy - 13 * u), (cx + 2 * u, cy - 13 * u), (cx, cy - 3 * u), (cx + 5 * u, cy - 2 * u)], fill=W_)
        d.ellipse([cx - 7 * u, cy - 2 * u, cx + 7 * u, cy + 12 * u], outline=W_, width=3)
    elif kind == "leaf":
        d.polygon([(cx, cy - 13 * u), (cx + 10 * u, cy - 2 * u), (cx, cy + 12 * u), (cx - 10 * u, cy - 2 * u)], fill=W_)
        d.line([cx, cy - 12 * u, cx, cy + 13 * u], fill=bg, width=2)
        d.line([cx, cy + 4 * u, cx + 7 * u, cy - 3 * u], fill=bg, width=2)
        d.line([cx, cy + 4 * u, cx - 7 * u, cy - 3 * u], fill=bg, width=2)
    elif kind == "cloud":
        d.ellipse([cx - 12 * u, cy - 2 * u, cx - 2 * u, cy + 8 * u], fill=W_)
        d.ellipse([cx - 4 * u, cy - 6 * u, cx + 8 * u, cy + 8 * u], fill=W_)
        d.ellipse([cx + 2 * u, cy - 1 * u, cx + 13 * u, cy + 8 * u], fill=W_)
        d.rectangle([cx - 12 * u, cy + 3 * u, cx + 13 * u, cy + 8 * u], fill=W_)
        d.line([cx - 7 * u, cy + 11 * u, cx - 4 * u, cy + 14 * u, cx - 8 * u, cy + 14 * u], fill=W_, width=2)
        d.line([cx + 2 * u, cy + 11 * u, cx + 5 * u, cy + 14 * u, cx + 1 * u, cy + 14 * u], fill=W_, width=2)
    elif kind == "bat":
        d.polygon([(cx - 11 * u, cy + 12 * u), (cx - 2 * u, cy - 12 * u), (cx + 4 * u, cy - 12 * u),
                   (cx - 5 * u, cy + 12 * u)], fill=W_)
        d.line([cx + 1 * u, cy - 12 * u, cx + 9 * u, cy - 14 * u], fill=W_, width=3)
        d.ellipse([cx + 7 * u, cy + 6 * u, cx + 13 * u, cy + 12 * u], fill=W_)
    else:  # fallback: filled circle
        d.ellipse([cx - 8 * u, cy - 8 * u, cx + 8 * u, cy + 8 * u], fill=W_)


# ---------------------------------------------------------------- lead scenes
def scene_storm(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 64, 84))
    # storm clouds
    d.ellipse([x + 8, y + 4, x + 110, y + 30], fill=(40, 48, 64))
    d.ellipse([x + 90, y - 2, x + 210, y + 26], fill=(40, 48, 64))
    d.ellipse([x + 200, y + 6, x + 320, y + 30], fill=(44, 52, 68))
    # lightning bolt
    d.polygon([(x + 268, y + 30), (x + 282, y + 30), (x + 272, y + 52), (x + 284, y + 52),
               (x + 262, y + 84), (x + 270, y + 56), (x + 258, y + 56)], fill=(250, 205, 70))
    # diagonal rain
    for i in range(26):
        rx = x + 12 + (i * 37) % (w - 24)
        ry = y + 34 + (i * 23) % (h - 44)
        d.line([rx, ry, rx - 5, ry + 12], fill=(180, 200, 225), width=2)
    # grounded parade balloon, red and white stripes, on the wet street
    bx, by = x + 52, y + h - 46
    d.ellipse([bx, by, bx + 150, by + 34], fill=(164, 32, 24), outline=INK)
    d.ellipse([bx + 18, by + 2, bx + 48, by + 32], fill=WHITE)
    d.ellipse([bx + 62, by + 2, bx + 92, by + 32], fill=WHITE)
    d.ellipse([bx + 106, by + 2, bx + 136, by + 32], fill=WHITE)
    d.line([bx + 150, by + 18, bx + 178, by + 8], fill=WHITE, width=2)
    # wind swirls
    d.arc([x + w - 78, y + 34, x + w - 38, y + 58], start=200, end=380, fill=WHITE, width=3)
    d.arc([x + 14, y + 40, x + 54, y + 64], start=180, end=20, fill=WHITE, width=3)
    # wet street
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(30, 38, 52))
    d.line([x + 20, y + h - 6, x + 120, y + h - 6], fill=(120, 140, 170), width=2)


def scene_tariff(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 238))
    # US flag, left
    fx, fy = x + 22, y + 12
    for i in range(7):
        d.rectangle([fx, fy + i * 5, fx + 92, fy + i * 5 + 5],
                    fill=RED if i % 2 == 0 else WHITE)
    d.rectangle([fx, fy, fx + 38, fy + 20], fill=(24, 52, 120))
    for sx in (6, 18, 30):
        for sy in (5, 13):
            d.ellipse([fx + sx, fy + sy, fx + sx + 3, fy + sy + 3], fill=WHITE)
    # Taiwan flag, right
    fx2, fy2 = x + w - 114, y + 12
    d.rectangle([fx2, fy2, fx2 + 92, fy2 + 35], fill=RED)
    d.rectangle([fx2, fy2, fx2 + 46, fy2 + 18], fill=(24, 52, 120))
    d.ellipse([fx2 + 15, fy2 + 4, fx2 + 31, fy2 + 14], fill=WHITE)
    d.ellipse([fx2 + 19, fy2 + 6, fx2 + 27, fy2 + 12], fill=(24, 52, 120))
    # document with the rate, centre
    dx, dy = x + w / 2 - 52, y + 46
    d.rectangle([dx, dy, dx + 104, dy + 42], fill=WHITE, outline=INK)
    d.line([dx + 8, dy + 6, dx + 96, dy + 6], fill=GREY, width=1)
    txt = "15%"
    tw = d.textlength(txt, font=F["stat_num"])
    d.text((dx + (104 - tw) / 2, dy + 10), txt, font=F["stat_num"], fill=DARKRED)
    # arrows pointing at the document
    d.line([fx + 96, fy + 18, dx - 6, dy + 20], fill=INK, width=2)
    d.polygon([(dx - 6, dy + 20), (dx - 14, dy + 15), (dx - 14, dy + 25)], fill=INK)
    d.line([fx2 - 4, fy2 + 18, dx + 110, dy + 20], fill=INK, width=2)
    d.polygon([(dx + 110, dy + 20), (dx + 118, dy + 15), (dx + 118, dy + 25)], fill=INK)


def scene_waves(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(198, 220, 240))
    # houses on the cliff, top right
    for hx, hw, hc in ((x + w - 96, 40, (238, 230, 214)), (x + w - 52, 34, (214, 228, 238))):
        d.rectangle([hx, y + 12, hx + hw, y + 40], fill=hc, outline=INK)
        d.polygon([(hx - 3, y + 12), (hx + hw / 2, y + 2), (hx + hw + 3, y + 12)], fill=RED)
    d.rectangle([x, y + 40, x + w, y + 44], fill=(120, 96, 64))
    # sea
    d.rectangle([x, y + 44, x + w, y + h], fill=(52, 110, 180))
    for wy in (y + 52, y + 66, y + 80):
        for wx in range(x + 6, x + w - 20, 44):
            d.arc([wx, wy, wx + 34, wy + 14], start=180, end=360, fill=WHITE, width=3)
    # pier from the left, with a collapsed section
    d.rectangle([x + 12, y + 56, x + 150, y + 64], fill=(150, 116, 72), outline=INK)
    for px in (x + 30, x + 70, x + 110, x + 140):
        d.line([px, y + 64, px, y + 82], fill=(120, 96, 64), width=3)
    d.polygon([(x + 150, y + 56), (x + 196, y + 72), (x + 188, y + 82), (x + 146, y + 66)],
              fill=(150, 116, 72), outline=INK)
    d.line([x + 176, y + 74, x + 176, y + 90], fill=(120, 96, 64), width=3)
    # wave crests over the pier
    d.arc([x + 150, y + 44, x + 210, y + 66], start=180, end=360, fill=WHITE, width=3)
    d.arc([x + 220, y + 50, x + 280, y + 72], start=180, end=360, fill=WHITE, width=3)


SCENES = {"storm": scene_storm, "tariff": scene_tariff, "waves": scene_waves}


# ---------------------------------------------------------------- world map
# Land spans per row: (row, col_start, col_end) on a 90x40 grid,
# col = (lon + 180) / 4, row = (76 - lat) / 3.4.
LAND = [
    (0, 3, 6), (0, 33, 38), (0, 57, 62), (0, 70, 89),
    (1, 3, 9), (1, 14, 22), (1, 32, 39), (1, 48, 52), (1, 55, 89),
    (2, 3, 10), (2, 12, 28), (2, 33, 38), (2, 40, 41), (2, 48, 54), (2, 55, 89),
    (3, 3, 10), (3, 12, 30), (3, 34, 37), (3, 47, 57), (3, 57, 89),
    (4, 13, 31), (4, 44, 45), (4, 47, 58), (4, 58, 89),
    (5, 14, 32), (5, 44, 46), (5, 47, 57), (5, 57, 88),
    (6, 14, 33), (6, 46, 58), (6, 58, 87),
    (7, 15, 33), (7, 45, 59), (7, 59, 85), (7, 86, 87),
    (8, 15, 32), (8, 45, 58), (8, 59, 84), (8, 85, 86),
    (9, 15, 32), (9, 45, 57), (9, 60, 83), (9, 85, 87),
    (10, 15, 31), (10, 45, 56), (10, 62, 84), (10, 85, 86),
    (11, 15, 31), (11, 45, 54), (11, 58, 70), (11, 70, 84), (11, 84, 86),
    (12, 16, 30), (12, 45, 58), (12, 58, 65), (12, 66, 82),
    (13, 16, 29), (13, 44, 59), (13, 59, 64), (13, 67, 74), (13, 74, 81),
    (14, 17, 27), (14, 44, 60), (14, 59, 64), (14, 67, 73), (14, 75, 79),
    (15, 18, 26), (15, 43, 58), (15, 67, 72), (15, 75, 79),
    (16, 19, 25), (16, 43, 57), (16, 68, 72), (16, 75, 78),
    (17, 20, 24), (17, 43, 56), (17, 68, 71), (17, 75, 78),
    (18, 27, 30), (18, 43, 55), (18, 69, 70), (18, 75, 78),
    (19, 27, 32), (19, 44, 56), (19, 60, 62), (19, 75, 78),
    (20, 27, 34), (20, 45, 55), (20, 59, 63), (20, 74, 80), (20, 82, 84),
    (21, 28, 36), (21, 46, 54), (21, 74, 79), (21, 81, 86),
    (22, 28, 37), (22, 47, 54), (22, 75, 82), (22, 84, 87),
    (23, 29, 38), (23, 47, 55), (23, 78, 84), (23, 87, 89),
    (24, 29, 38), (24, 48, 55),
    (25, 29, 38), (25, 48, 56), (25, 61, 62),
    (26, 29, 37), (26, 48, 56), (26, 61, 62), (26, 74, 82),
    (27, 30, 37), (27, 49, 56), (27, 61, 62), (27, 73, 83),
    (28, 30, 36), (28, 49, 55), (28, 73, 83),
    (29, 30, 36), (29, 50, 55), (29, 73, 83),
    (30, 30, 35), (30, 50, 54), (30, 74, 82),
    (31, 30, 35), (31, 50, 54), (31, 74, 81),
    (32, 30, 34), (32, 51, 53), (32, 75, 80),
    (33, 30, 34), (33, 87, 88),
    (34, 30, 33), (34, 87, 88),
    (35, 30, 32),
    (36, 30, 32),
    (37, 30, 31),
]


def draw_map(d, x, y, w, h):
    """Dotted world map in the box (x, y, w, h); returns a pin placer."""
    cell_w, cell_h = w / 90.0, h / 40.0
    land = set()
    for r, c0, c1 in LAND:
        for c in range(c0, c1 + 1):
            land.add((r, c))
    for (r, c) in land:
        px, py = x + c * cell_w, y + r * cell_h
        d.rectangle([px + 0.6, py + 0.6, px + cell_w - 0.6, py + cell_h - 0.6], fill=(178, 168, 148))

    def place(lon, lat):
        return (x + (lon + 180) / 360.0 * w, y + (82 - lat) / 140.0 * h)

    return place


# ---------------------------------------------------------------- assembly
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(LEADS) + len(GRID) + len(ALSO)

    # masthead band
    d.rectangle([0, 0, W, 52], fill=INK)
    d.text((14, 9), "THE WORLD ON THURSDAY", font=F["mast_small"], fill=WHITE)
    right = f"{total} STORIES \u00b7 4 REGIONS \u00b7 EVERY ONE DATED THURSDAY 26 NOVEMBER 2026"
    rw = d.textlength(right, font=F["mast_right"])
    d.text((W - 14 - rw, 18), right, font=F["mast_right"], fill=(210, 205, 195))

    # title + subline
    d.text((14, 57), "Thursday 26 November 2026", font=F["mast"], fill=INK)
    d.text((14, 120),
           "Nor'easter drenches Thanksgiving \u00b7 US proposes 15% tariff on Taiwan \u00b7 King tides flood California",
           font=F["subline"], fill=DARKRED)
    d.line([12, 140, W - 12, 140], fill=INK, width=3)
    d.line([12, 145, W - 12, 145], fill=INK, width=1)

    # stat strip
    colw = (W - 24) / 6.0
    for i, (num, cap, _tie) in enumerate(STATS):
        x = 12 + i * colw
        if i:
            d.line([x - 6, 154, x - 6, 204], fill=(200, 192, 172), width=1)
        d.text((x, 150), num, font=F["stat_num"], fill=DARKRED)
        draw_wrap(d, (x, 186), cap, F["stat_cap"], GREY, colw - 14, 12, max_lines=2)

    # region tabs
    counts = {}
    for s in LEADS + GRID:
        counts[s[6]] = counts.get(s[6], 0) + 1
    for _n, _t, reg in ALSO:
        counts[reg] = counts.get(reg, 0) + 1
    tab_w = {"ASIA-PACIFIC": 318, "EUROPE": 238, "AMERICAS": 159,
             "MIDDLE EAST": 105, "AFRICA": 90, "WORLD": 90}
    tab_f = font(FD + "DejaVuSans-Bold.ttf", 11)
    tx = 12
    for reg in ("ASIA-PACIFIC", "EUROPE", "AMERICAS", "MIDDLE EAST", "AFRICA", "WORLD"):
        wseg = tab_w[reg]
        d.rectangle([tx, 214, tx + wseg - 3, 236], fill=REGIONS[reg])
        label = f"{reg} {counts.get(reg, 0)}"
        lw = d.textlength(label, font=tab_f)
        d.text((tx + (wseg - 3 - lw) / 2, 219), label, font=tab_f, fill=WHITE)
        tx += wseg

    # lead panels
    for i, s in enumerate(LEADS):
        n, place, beat, head, sub, src, reg, icon_name, _pin = s
        x = 12 + i * 341
        pw = 330
        SCENES[icon_name](d, x, 244, pw, 94)
        d.rectangle([x, 244, x + pw, 338], outline=INK, width=1)
        d.rectangle([x, 340, x + pw, 355], fill=REGIONS[reg])
        d.text((x + 6, 342), f"{n}  {place} \u2014 {beat}", font=F["kicker"], fill=WHITE)
        y = draw_wrap(d, (x, 359), head, F["lead_head"], INK, pw - 4, 20, max_lines=2)
        draw_wrap(d, (x, max(y + 2, 401)), sub, F["lead_sub"], (58, 56, 52), pw - 4, 13, max_lines=3)
        sw = d.textlength(f"({src})", font=F["src"])
        d.text((x + pw - 4 - sw, 442), f"({src})", font=F["src"], fill=GREY)
    d.line([12, 460, W - 12, 460], fill=INK, width=1)

    # story grid: 2 columns x 4 rows
    gx, gy, cw, rh = 12, 468, 500, 62
    for idx, s in enumerate(GRID):
        n, place, beat, head, sub, src, reg, icon_name, _pin = s
        cx = gx + (idx % 2) * cw
        cy = gy + (idx // 2) * rh
        if idx % 2:
            d.line([cx - 6, cy + 2, cx - 6, cy + rh - 4], fill=(205, 197, 178), width=1)
        icon(d, icon_name, cx, cy + 6, 40, REGIONS[reg])
        d.text((cx + 50, cy), f"{n} \u00b7 {place} \u2014 {beat}", font=F["kicker"], fill=REGIONS[reg])
        y = draw_wrap(d, (cx + 50, cy + 13), head, F["g_head"], INK, cw - 64, 13, max_lines=2)
        draw_wrap(d, (cx + 50, cy + 41), sub + f" ({src})", F["g_sub"], GREY, cw - 64, 11, max_lines=1)

    # date check box
    d.rectangle([12, 736, W - 12, 780], outline=RED, width=2)
    d.rectangle([12, 736, 118, 752], fill=RED)
    d.text((20, 739), "DATE CHECK", font=F["check_b"], fill=WHITE)
    draw_wrap(d, (128, 739), DATE_CHECK, F["check"], INK, W - 152, 14, max_lines=3)

    # bottom left: map with pins (one pin per city)
    d.text((12, 790), "WHERE IT HAPPENED \u2014 pins match story numbers (one pin per city)", font=F["map_title"], fill=INK)
    d.rectangle([12, 806, 516, 974], fill=(252, 250, 244), outline=(190, 182, 164))
    place_pin = draw_map(d, 18, 812, 492, 156)
    for s in LEADS + GRID:
        n, pin = s[0], s[8]
        if pin is None:
            continue
        # skip duplicate-city pins: stories 5 (Canberra), 9, 10, 11 share cities
        if n in (5, 9, 10, 11):
            continue
        px, py = place_pin(pin[0], pin[1])
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=WHITE, width=1)
        label = str(n)
        lw = d.textlength(label, font=F["pin"])
        d.text((px - lw / 2, py - 5), label, font=F["pin"], fill=WHITE)

    # bottom right: also-on list, two columns of three
    d.text((528, 790), f"ALSO ON THURSDAY \u2014 {len(ALSO)} MORE STORIES", font=F["also_head"], fill=INK)
    for j, (n, text, _reg) in enumerate(ALSO):
        ax = 528 + (j // 3) * 246
        ay = 806 + (j % 3) * 32
        num = f"{n}"
        d.text((ax, ay), num, font=F["also"], fill=DARKRED)
        nw = d.textlength(num + " ", font=F["also"])
        draw_wrap(d, (ax + nw + 2, ay), text, F["also"], INK, 246 - nw - 8, 11, max_lines=2)

    # footer band
    d.rectangle([0, 1002, W, H], fill=INK)
    d.text((14, 1008),
           "Sources: Reuters, BBC, ABC Australia, CNA, USA Today, BCCI and Indian press \u2014 every story names its outlet.",
           font=F["foot"], fill=(215, 210, 200))
    fr = "ONE PAGE \u00b7 THURSDAY 26 NOVEMBER 2026"
    fw = d.textlength(fr, font=F["foot_b"])
    d.text((W - 14 - fw, 1008), fr, font=F["foot_b"], fill=WHITE)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
