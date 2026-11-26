#!/usr/bin/env python3
"""Draw the illustrated broadsheet for Thursday 26 November 2026.

Renders one 1024x1024 PNG (entry.png) with PIL only: masthead band,
headline, stat strip, region strip, three drawn lead panels, a numbered
eight-story grid, a DATE CHECK box, a dotted world map with numbered
pins, an ALSO ON list and a footer band. No network access.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
MARGIN = 12

PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (176, 30, 36)
DARK_RED = (142, 47, 47)
BLUE = (31, 95, 168)
GREEN = (46, 125, 79)
BROWN = (168, 90, 30)
PURPLE = (106, 74, 142)
GREY = (102, 102, 102)
LIGHT_GREY = (210, 205, 192)
SKY = (214, 228, 238)
SEA = (46, 110, 178)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = load("DejaVuSerif-Bold.ttf", 52)
F_SUB = load("DejaVuSerif.ttf", 17)
F_BAND = load("DejaVuSans-Bold.ttf", 26)
F_BAND_SMALL = load("DejaVuSans.ttf", 12)
F_STAT_NUM = load("DejaVuSerif-Bold.ttf", 27)
F_STAT_CAP = load("DejaVuSans.ttf", 11)
F_REGION = load("DejaVuSans-Bold.ttf", 12)
F_KICK = load("DejaVuSans-Bold.ttf", 12)
F_LEAD_HEAD = load("DejaVuSans-Bold.ttf", 19)
F_LEAD_SUM = load("DejaVuSans.ttf", 13)
F_SOURCE = load("DejaVuSerif.ttf", 11)
F_GRID_HEAD = load("DejaVuSans-Bold.ttf", 15)
F_GRID_SUM = load("DejaVuSans.ttf", 12)
F_GRID_KICK = load("DejaVuSans-Bold.ttf", 11)
F_CHECK_LABEL = load("DejaVuSans-Bold.ttf", 13)
F_CHECK_BODY = load("DejaVuSans.ttf", 12)
F_SECTION = load("DejaVuSans-Bold.ttf", 13)
F_ALSO_NUM = load("DejaVuSans-Bold.ttf", 13)
F_ALSO_TXT = load("DejaVuSans.ttf", 12)
F_FOOT = load("DejaVuSans.ttf", 11)
F_FOOT_BOLD = load("DejaVuSans-Bold.ttf", 11)
F_PIN = load("DejaVuSans-Bold.ttf", 11)
F_TAG = load("DejaVuSerif-Bold.ttf", 26)


def wrap(text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if font.getlength(trial) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(draw, x, y, lines, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- data

STATS = [
    ("60 mph", "gusts forecast on the US East Coast (story 1)"),
    ("15%", "US tariff proposed for Taiwan (story 2)"),
    ("8.5 ft", "Ventura's record-tying high tide (story 3)"),
    ("2030", "Australia's 2030 climate target, on track (story 5)"),
    ("5 years", "Beale's exile from the Wallabies ends (story 11)"),
    ("200 ha", "kelp farm planned off the NSW coast (story 15)"),
]

REGIONS = [
    ("ASIA-PACIFIC 10", 300, BLUE),
    ("EUROPE 2", 150, GREEN),
    ("AMERICAS 3", 170, BROWN),
    ("MIDDLE EAST 1", 180, DARK_RED),
    ("AFRICA 0", 110, PURPLE),
    ("WORLD 0", 90, GREY),
]

LEADS = [
    {
        "num": "1", "place": "NEW YORK", "topic": "WEATHER",
        "bar": (168, 90, 30),
        "head": "Nor'easter drenches Thanksgiving Day",
        "summary": ("A powerful coastal storm lashes the US East Coast with "
                    "60 mph gusts and heavy rain on Thanksgiving Day."),
        "source": "(Reuters)",
    },
    {
        "num": "2", "place": "TAIPEI", "topic": "TRADE",
        "bar": BLUE,
        "head": "US proposes a 15% tariff on Taiwan",
        "summary": ("Taipei says the rate is the lowest tier and will not "
                    "stack on other duties, alongside Japan, South Korea "
                    "and the EU."),
        "source": "(CNA)",
    },
    {
        "num": "3", "place": "CALIFORNIA", "topic": "WEATHER",
        "bar": (168, 90, 30),
        "head": "King tides flood California's coast",
        "summary": ("Record tides swamp roads from Humboldt to San Diego; "
                    "a pier section collapses in Pacifica and Ventura "
                    "warns of evacuations."),
        "source": "(USA Today)",
    },
]

GRID = [
    ("4", "CANBERRA", "POLITICS", BLUE, "door",
     "Liberal senator defects to One Nation",
     "Leah Blyth quits the party, dealing Angus Taylor a blow. (ABC)"),
    ("5", "CANBERRA", "CLIMATE", GREEN, "leaf",
     "Australia on track for 2030 climate target",
     "The government tables its annual statement to Parliament today. (ABC)"),
    ("6", "NEW DELHI", "SOCIETY", BLUE, "columns",
     "India marks Constitution Day",
     "Schools and courts honour the 1949 Constitution on Samvidhan Divas. (Indian press)"),
    ("7", "LONDON", "MEDIA", GREEN, "cloud",
     "BBC and Met Office launch weather pact",
     "The broadcaster and the forecaster join forces on coverage. (BBC)"),
    ("8", "DOHA", "CRICKET", BROWN, "bat",
     "Sri Lanka A meet India A in semi-final",
     "The Rising Stars semi-final is played in Doha today. (BCCI)"),
    ("9", "MELBOURNE", "POLITICS", BLUE, "ballot",
     "Election stoush over blue t-shirts in court",
     "Labor seeks an injunction against a dumped Liberal candidate. (ABC)"),
    ("10", "HOBART", "SOCIETY", BLUE, "paw",
     "Tasmania ends greyhound racing",
     "A 'perverse' vote ends the sport without protections for dogs. (ABC)"),
    ("11", "LONDON", "RUGBY", GREEN, "shield",
     "Beale ends five-year exile from Wallabies",
     "The veteran is named on the bench for the Ireland clash. (ABC)"),
]

CHECK_BODY = (
    "Wires read up to 00:45 UTC, Thu 26 Nov 2026. Every story here happened "
    "or was first reported on 26 Nov 2026 in at least one time zone. Left out "
    "as other days' news: the Cairo tanker fire, the Netanyahu judges' call, "
    "the Hera asteroid pictures, the Macy's parade move, the SpaceX approval "
    "and the Iowa blast \u2014 all Wed 25 Nov."
)

ALSO = [
    ("12", "Thanksgiving travel peaks as storms hit both coasts (US press)"),
    ("13", "Severe storms to lash a huge stretch of Australia (The West Australian)"),
    ("14", "Canberra youths face charges after aggravated robbery (ABC)"),
    ("15", "Plan for 200ha kelp farm off NSW coast (ABC)"),
    ("16", "Palm Beach ferry workers strike from 7:30 a.m. (Sydney press)"),
]

# Coarse landmass boxes as (lon_min, lat_min, lon_max, lat_max).
LAND_BOXES = [
    (-168, 60, -140, 71), (-140, 49, -95, 70), (-125, 25, -66, 49),
    (-100, 15, -83, 31), (-92, 8, -79, 18),
    (-58, 60, -20, 83),
    (-78, -5, -48, 10), (-72, -25, -38, -5), (-68, -40, -52, -25),
    (-70, -55, -58, -40),
    (-10, 50, 30, 70), (-10, 36, 10, 50), (10, 42, 30, 55),
    (-6, 50, 2, 59),
    (-17, 15, 32, 32), (8, -5, 42, 15), (12, -35, 33, -5),
    (43, -25, 50, -12),
    (30, 55, 180, 71), (45, 40, 90, 55), (75, 20, 122, 40),
    (35, 12, 60, 35), (68, 8, 90, 35),
    (95, 5, 106, 28), (95, -11, 141, 6),
    (113, -22, 153, -11), (114, -39, 141, -22), (141, -38, 150, -25),
    (166, -47, 179, -34),
]

PINS = [
    ("1", -74.0, 40.7),
    ("2", 121.5, 25.0),
    ("3", -122.4, 37.8),
    ("4", 149.1, -35.3),
    ("6", 77.2, 28.6),
    ("7", -0.1, 51.5),
    ("8", 51.5, 25.3),
]


# ------------------------------------------------------- lead illustrations

def draw_storm(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(52, 62, 74))
    for cx, cy, cw in [(x + 20, y + 8, 120), (x + 130, y + 2, 140),
                       (x + 230, y + 14, 90)]:
        draw.ellipse([cx, cy, cx + cw, cy + 26], fill=(38, 46, 56))
        draw.ellipse([cx + 18, cy - 8, cx + cw - 10, cy + 16],
                     fill=(44, 52, 64))
    for i in range(14):
        rx = x + 12 + i * 23
        draw.line([rx, y + 40, rx - 8, y + 62], fill=(170, 190, 205), width=2)
    bolt = [(x + 268, y + 30), (x + 284, y + 30), (x + 274, y + 52),
            (x + 286, y + 52), (x + 262, y + 84), (x + 270, y + 56),
            (x + 260, y + 56)]
    draw.polygon(bolt, fill=(250, 210, 60))
    draw.ellipse([x + 96, y + 44, x + 196, y + 76], fill=(178, 40, 40))
    for cx in (116, 146, 176):
        draw.ellipse([cx - 11, y + 50, cx + 11, y + 70], fill=(245, 245, 245))
    draw.ellipse([x + 126, y + 54, x + 166, y + 66], fill=(52, 62, 74))
    for i in range(5):
        wx = x + 8 + i * 64
        draw.arc([wx, y + h - 16, wx + 52, y + h + 6], 180, 360,
                 fill=(235, 240, 244), width=3)


def draw_trade(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    fx, fy, fw, fh = x + 14, y + 14, 92, 48
    for i in range(7):
        colour = (178, 34, 34) if i % 2 == 0 else (245, 245, 245)
        draw.rectangle([fx, fy + i * 7, fx + fw, fy + (i + 1) * 7], fill=colour)
    draw.rectangle([fx, fy, fx + 38, fy + 27], fill=(40, 60, 140))
    for r in range(3):
        for c in range(4):
            draw.ellipse([fx + 5 + c * 9, fy + 5 + r * 8,
                          fx + 9 + c * 9, fy + 9 + r * 8],
                         fill=(255, 255, 255))
    tx, ty, tw, th = x + w - 106, y + 14, 92, 48
    draw.rectangle([tx, ty, tx + tw, ty + th], fill=(178, 34, 34))
    draw.rectangle([tx, ty, tx + 46, ty + 24], fill=(40, 60, 140))
    cx, cy = tx + 23, ty + 12
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    for k in range(12):
        a = math.radians(k * 30)
        draw.line([cx + 7 * math.cos(a), cy + 7 * math.sin(a),
                   cx + 11 * math.cos(a), cy + 11 * math.sin(a)],
                  fill=(255, 255, 255), width=2)
    tag_x, tag_y = x + w // 2 - 52, y + 40
    draw.rectangle([tag_x, tag_y, tag_x + 104, tag_y + 40],
                   fill=(255, 255, 255), outline=RED, width=2)
    draw.text((tag_x + 52, tag_y + 20), "15%", font=F_TAG,
              fill=RED, anchor="mm")
    draw.polygon([(fx + 46, fy + fh), (fx + 52, fy + fh + 12),
                  (fx + 40, fy + fh + 12)], fill=INK)
    draw.polygon([(tx + 46, ty + th), (tx + 52, ty + th + 12),
                  (tx + 40, ty + th + 12)], fill=INK)


def draw_tides(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(226, 232, 236))
    for hx in (x + w - 96, x + w - 52):
        draw.rectangle([hx, y + 16, hx + 40, y + 40], fill=(240, 234, 220))
        draw.polygon([(hx - 4, y + 16), (hx + 20, y + 2), (hx + 44, y + 16)],
                     fill=(178, 40, 40))
        draw.rectangle([hx + 15, y + 28, hx + 25, y + 40], fill=(90, 70, 50))
    draw.rectangle([x, y + 44, x + w, y + h], fill=SEA)
    for yy in (y + 52, y + 66, y + 80):
        for i in range(6):
            wx = x + 4 + i * 56
            draw.arc([wx, yy, wx + 44, yy + 16], 180, 360,
                     fill=(235, 244, 250), width=3)
    draw.polygon([(x + 10, y + 58), (x + 150, y + 58), (x + 150, y + 66),
                  (x + 10, y + 66)], fill=(120, 86, 52))
    draw.polygon([(x + 176, y + 70), (x + 300, y + 82), (x + 300, y + 90),
                  (x + 176, y + 78)], fill=(120, 86, 52))
    for px, py in [(x + 40, y + 66), (x + 110, y + 66), (x + 210, y + 78),
                   (x + 270, y + 84)]:
        draw.line([px, py, px, y + h - 2], fill=(96, 68, 40), width=4)


# ---------------------------------------------------------------- icons

def draw_icon(draw, x, y, size, colour, kind):
    draw.rectangle([x, y, x + size, y + size], fill=colour)
    cx, cy = x + size // 2, y + size // 2
    white = (255, 255, 255)
    if kind == "door":  # defection: an open door
        draw.rectangle([x + 12, y + 8, x + 32, y + 38], outline=white, width=3)
        draw.line([x + 12, y + 8, x + 38, y + 14], fill=white, width=3)
        draw.line([x + 12, y + 38, x + 38, y + 32], fill=white, width=3)
        draw.ellipse([x + 28, y + 22, x + 32, y + 26], fill=white)
    elif kind == "leaf":  # climate
        draw.ellipse([x + 10, y + 12, x + 36, y + 34], fill=white)
        draw.line([x + 14, y + 34, x + 30, y + 12], fill=colour, width=2)
    elif kind == "columns":  # constitution
        draw.rectangle([x + 10, y + 10, x + 36, y + 14], fill=white)
        for bx in (12, 20, 28):
            draw.rectangle([x + bx, y + 16, x + bx + 4, y + 32], fill=white)
        draw.rectangle([x + 10, y + 34, x + 36, y + 38], fill=white)
    elif kind == "cloud":  # weather pact
        draw.ellipse([x + 9, y + 18, x + 25, y + 30], fill=white)
        draw.ellipse([x + 20, y + 12, x + 38, y + 30], fill=white)
        draw.ellipse([x + 24, y + 22, x + 38, y + 32], fill=white)
    elif kind == "bat":  # cricket
        draw.rectangle([x + 12, y + 10, x + 22, y + 34], fill=white)
        draw.line([x + 17, y + 34, x + 26, y + 40], fill=white, width=3)
        draw.ellipse([x + 30, y + 28, x + 40, y + 38], fill=(250, 210, 60))
    elif kind == "ballot":  # election
        draw.rectangle([x + 10, y + 16, x + 36, y + 38], outline=white, width=3)
        draw.line([x + 14, y + 28, x + 20, y + 34], fill=white, width=3)
        draw.line([x + 20, y + 34, x + 32, y + 18], fill=white, width=3)
    elif kind == "paw":  # greyhounds
        draw.ellipse([cx - 8, cy - 2, cx + 8, cy + 12], fill=white)
        for ox, oy in [(-12, -8), (-4, -12), (4, -12), (12, -8)]:
            draw.ellipse([cx + ox - 3, cy + oy - 3, cx + ox + 3, cy + oy + 3],
                         fill=white)
    elif kind == "shield":  # rugby
        draw.polygon([(cx, y + 8), (x + 36, y + 14), (x + 36, y + 28),
                      (cx, y + 40), (x + 10, y + 28), (x + 10, y + 14)],
                     outline=white, width=3)
        draw.line([cx, y + 14, cx, y + 34], fill=white, width=3)


# ------------------------------------------------------------------ map

def on_land(lon, lat):
    return any(lo <= lon <= hi and la0 <= lat <= la1
               for lo, la0, hi, la1 in LAND_BOXES)


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 234, 222),
                   outline=LIGHT_GREY)
    for lon in range(-150, 181, 30):
        gx = x + (lon + 180) / 360 * w
        draw.line([gx, y, gx, y + h], fill=(228, 224, 210))
    for lat in (-60, -30, 0, 30, 60):
        gy = y + (85 - lat) / 145 * h
        draw.line([x, gy, x + w, gy], fill=(228, 224, 210))
    step = 6
    for gy in range(y + 4, y + h - 2, step):
        for gx in range(x + 4, x + w - 2, step):
            lon = (gx - x) / w * 360 - 180
            lat = 85 - (gy - y) / h * 145
            if on_land(lon, lat):
                draw.ellipse([gx - 2, gy - 2, gx + 2, gy + 2],
                             fill=(178, 164, 138))
    for num, lon, lat in PINS:
        px = x + (lon + 180) / 360 * w
        py = y + (85 - lat) / 145 * h
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                     outline=(255, 255, 255), width=2)
        tw = F_PIN.getlength(num)
        draw.text((px - tw / 2, py - 7), num, font=F_PIN, fill=(255, 255, 255))


# ----------------------------------------------------------------- page

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top black band
    d.rectangle([0, 0, W, 46], fill=INK)
    d.text((MARGIN + 2, 10), "THE WORLD ON THURSDAY", font=F_BAND,
           fill=(255, 255, 255))
    right = "16 STORIES \u00b7 4 REGIONS \u00b7 EVERY ONE DATED THURSDAY 26 NOVEMBER 2026"
    d.text((W - MARGIN - 2, 17), right, font=F_BAND_SMALL,
           fill=(220, 220, 220), anchor="ra")

    # --- headline + red subhead
    d.text((MARGIN, 52), "Thursday 26 November 2026", font=F_TITLE, fill=INK)
    d.text((MARGIN, 116),
           "Nor'easter drenches Thanksgiving \u00b7 US proposes 15% tariff "
           "on Taiwan \u00b7 King tides flood California",
           font=F_SUB, fill=RED)
    d.line([MARGIN, 142, W - MARGIN, 142], fill=INK, width=2)

    # --- stat strip
    col_w = (W - 2 * MARGIN) / 6
    for i, (num, cap) in enumerate(STATS):
        cx = MARGIN + i * col_w
        if i:
            d.line([cx - 4, 150, cx - 4, 196], fill=LIGHT_GREY, width=1)
        d.text((cx + 4, 148), num, font=F_STAT_NUM, fill=RED)
        text_block(d, cx + 4, 180, wrap(cap, F_STAT_CAP, col_w - 14),
                   F_STAT_CAP, INK, 13)

    # --- region strip
    rx = MARGIN
    for label, width, colour in REGIONS:
        d.rectangle([rx, 206, rx + width, 228], fill=colour)
        d.text((rx + width / 2, 217), label, font=F_REGION,
               fill=(255, 255, 255), anchor="mm")
        rx += width

    # --- three lead panels
    panel_w = 326
    gap = 11
    art_h = 88
    for i, lead in enumerate(LEADS):
        px = MARGIN + i * (panel_w + gap)
        py = 234
        if i == 0:
            draw_storm(d, px, py, panel_w, art_h)
        elif i == 1:
            draw_trade(d, px, py, panel_w, art_h)
        else:
            draw_tides(d, px, py, panel_w, art_h)
        d.rectangle([px, py + art_h, px + panel_w, py + art_h + 18],
                    fill=lead["bar"])
        d.text((px + 6, py + art_h + 9),
               f"{lead['num']}  {lead['place']} \u2014 {lead['topic']}",
               font=F_KICK, fill=(255, 255, 255), anchor="lm")
        hy = py + art_h + 24
        text_block(d, px, hy, wrap(lead["head"], F_LEAD_HEAD, panel_w),
                   F_LEAD_HEAD, INK, 23)
        sy = hy + 48
        text_block(d, px, sy, wrap(lead["summary"], F_LEAD_SUM, panel_w),
                   F_LEAD_SUM, INK, 16)
        sw = F_SOURCE.getlength(lead["source"])
        d.text((px + panel_w - sw, sy + 50), lead["source"], font=F_SOURCE,
               fill=GREY)

    d.line([MARGIN, 458, W - MARGIN, 458], fill=INK, width=1)

    # --- numbered grid, 2 columns x 4 rows
    grid_y = 464
    row_h = 66
    col_x = [MARGIN, MARGIN + 506]
    for idx, (num, place, topic, colour, kind, head, summary) in enumerate(GRID):
        gx = col_x[idx % 2]
        gy = grid_y + (idx // 2) * row_h
        draw_icon(d, gx, gy + 4, 46, colour, kind)
        tx = gx + 56
        d.text((tx, gy + 2), f"{num} \u00b7 {place} \u2014 {topic}",
               font=F_GRID_KICK, fill=colour)
        d.text((tx, gy + 17), head, font=F_GRID_HEAD, fill=INK)
        text_block(d, tx, gy + 36,
                   wrap(summary, F_GRID_SUM, 438)[:2],
                   F_GRID_SUM, (60, 60, 60), 14)

    # --- DATE CHECK box
    cy = 736
    d.rectangle([MARGIN, cy, W - MARGIN, cy + 54], outline=RED, width=2)
    d.rectangle([MARGIN, cy, MARGIN + 118, cy + 54], fill=RED)
    d.text((MARGIN + 59, cy + 27), "DATE CHECK", font=F_CHECK_LABEL,
           fill=(255, 255, 255), anchor="mm")
    text_block(d, MARGIN + 128, cy + 5,
               wrap(CHECK_BODY, F_CHECK_BODY, W - MARGIN - (MARGIN + 128) - 8),
               F_CHECK_BODY, INK, 15)

    # --- map + ALSO ON
    my = 798
    d.text((MARGIN, my), "WHERE IT HAPPENED \u2014 pins match story numbers "
           "(one pin per city)", font=F_SECTION, fill=INK)
    draw_map(d, MARGIN, my + 20, 488, 172)
    ax = 518
    d.text((ax, my), "ALSO ON THURSDAY \u2014 5 MORE STORIES",
           font=F_SECTION, fill=INK)
    for j, (num, text) in enumerate(ALSO):
        ix = ax + (0 if j < 3 else 252)
        iy = my + 22 + (j % 3) * 62
        d.text((ix, iy), num, font=F_ALSO_NUM, fill=RED)
        text_block(d, ix + 26, iy, wrap(text, F_ALSO_TXT, 220),
                   F_ALSO_TXT, INK, 15)

    # --- footer band
    d.rectangle([0, 996, W, H], fill=INK)
    d.text((MARGIN, 1005),
           "Sources: Reuters, BBC, ABC Australia, CNA, USA Today, BCCI and "
           "Indian press \u2014 every story names its outlet.",
           font=F_FOOT, fill=(225, 225, 225))
    d.text((W - MARGIN, 1005), "ONE PAGE \u00b7 THURSDAY 26 NOVEMBER 2026",
           font=F_FOOT_BOLD, fill=(255, 255, 255), anchor="ra")

    img.save(OUT, "PNG")
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
