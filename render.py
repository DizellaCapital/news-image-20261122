#!/usr/bin/env python3
"""THE SUNDAY LEDGER v7 -- news-image-20261122 renderer (local only).

Draws the 1024x1024 front page for Sunday 22 November 2026. Runs locally
with PIL; the grader never runs this file (main.py is the stdlib-only
entry program that copies the rendered entry.png to the output dir).

v7 named change vs v6-fix: the COP31 lead is corrected -- the final text
LANDED on Sunday morning (headline + deck + kicker + UTC strip), the Iran
lead deck gains the Al-Riffa / Awali place names, the DATE CHECK drops the
uncorroborated Antarctic IPO item, and the world map is drawn as a
recognisable dotted world map instead of abstract blobs.
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

CREAM = (246, 239, 219)
INK = (20, 20, 20)
NAVY = (26, 42, 74)
RED = (163, 22, 33)
RED_DK = (140, 18, 28)
GRAY = (110, 110, 105)
LIGHT_BLUE = (207, 227, 242)
LAND = (168, 196, 138)
GREEN = (28, 120, 70)
GOLD = (176, 132, 20)
PURPLE = (106, 74, 158)
BLUE = (40, 90, 170)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(draw, t, f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, f, max_w, fill, leading, max_lines=None):
    lines = wrap(draw, text, f, max_w)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError("text overflows %d lines: %r -> %r" % (max_lines, text, lines))
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def chip(draw, x, y, text, bg, fg=(255, 255, 255), f=None, pad_x=5, pad_y=2):
    f = f or font(SANS_B, 9)
    tw = text_w(draw, text, f)
    th = f.size
    draw.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y],
                           radius=3, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), text, font=f, fill=fg)
    return tw + 2 * pad_x


def badge(draw, cx, cy, num, r=10):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY,
                 outline=(255, 255, 255), width=2)
    f = font(SANS_B, 11)
    t = str(num)
    draw.text((cx - text_w(draw, t, f) / 2, cy - 8), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- data

KICKER = ("COP31's final text lands at dawn \u00b7 186 drones over Ukraine "
          "overnight \u00b7 Iran claims US radars hit, Bahrain denies it")

KEY_NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed by air defence"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record total in NZ"),
    ("98.79%", "Hong Kong turnout by 5 pm"),
]

REGIONS = [
    ("EUROPE", 9, (46, 125, 107)),
    ("MIDDLE EAST", 3, (176, 48, 48)),
    ("ASIA-PACIFIC", 8, (74, 124, 46)),
    ("AMERICAS", 9, (106, 74, 158)),
    ("AFRICA", 2, (192, 122, 32)),
    ("OCEANIA", 3, (122, 74, 158)),
    ("WORLD", 2, (102, 102, 102)),
]

UTC_EVENTS = [
    ("01:00", "HK polls open"),
    ("03:00", "COP31 objections"),
    ("05:11", "Hamas seeks talks"),
    ("05:30", "Verstappen wins"),
    ("06:00", "COP31 approval due"),
    ("10:00", "HK polls close"),
    ("17:00", "ATP final"),
]

# leads: (num, dateline, certainty, label, headline, deck, sources)
LEADS = [
    (1, "ANTALYA, T\u00dcRKIYE \u00b7 CLIMATE", "ONGOING", "COP31: FINAL TEXT",
     "COP31 tables a final text \u2014 and admits 1.5\u00b0C will be missed",
     "The ten-page package drops the $120bn target, keeps the 35% "
     "clean-electricity goal for 2035, and admits 1.5\u00b0C will be missed. "
     "No fossil-fuel mention.",
     "Reuters \u00b7 BBC \u00b7 The Guardian"),
    (2, "KYIV REGION, UKRAINE \u00b7 WAR", "CONFIRMED", "186 DRONES OVERNIGHT",
     "Russia fires 186 drones at Ukraine",
     "Defences down or jam 161 of 186 drones; a block in Dymer is hit, "
     "seven feared trapped.",
     "Ukrainian Air Force \u00b7 Reuters"),
    (3, "MANAMA, BAHRAIN \u00b7 IRAN WAR", "CLAIM", "CLAIM VS DENIAL",
     "Iran claims two US radars hit; Bahrain denies it",
     "The IRGC claims two Patriot radars were hit at Al-Riffa and Awali; "
     "Bahrain says its defences intercepted the attack and a civilian "
     "site burned.",
     "IRGC \u00b7 Bahrain Interior Ministry"),
]

# medium: (num, dateline, certainty, label, headline, deck, sources)
MEDIUM = [
    (4, "STRAIT OF HORMUZ \u00b7 WAR", "REPORTED", "TANKER HIT",
     "Tankers hit off Oman as Gulf tensions surge",
     "An ADNOC vessel is struck; one crew member is missing.",
     "Reuters \u00b7 AP"),
    (5, "KYIV, UKRAINE \u00b7 WAR", "REPORTED", "BRIDGES HIT",
     "Russia strikes three Kyiv bridges",
     "Moscow answers the Crimea bridge attacks.",
     "Reuters \u00b7 Kyiv Independent"),
    (6, "GULF OF FINLAND \u00b7 WAR", "REPORTED", "SHIP ABLAZE",
     "Drones hit Russian cargo ship in the Baltic",
     "Finland tightens security after the strike.",
     "Finnish Forces \u00b7 Times of India"),
    (7, "TALLINN, ESTONIA \u00b7 SECURITY", "CONFIRMED", "1 DEC",
     "Estonia to shut its border with Russia",
     "Tallinn moves to close the frontier from 1 December.",
     "Reuters \u00b7 AP"),
    (8, "HONG KONG \u00b7 ELECTIONS", "CONFIRMED", "98.79% TURNOUT",
     "Hong Kong elects its Election Committee",
     "856 candidates chase 723 seats; turnout hits 98.79%.",
     "HK Government \u00b7 China Daily"),
    (9, "LAS VEGAS \u00b7 FORMULA 1", "CONFIRMED", "VERSTAPPEN WINS",
     "Verstappen wins the Las Vegas GP",
     "Verstappen beats Norris by 0.639s; Russell is third.",
     "FIA \u00b7 Formula1.com"),
    (10, "WELLINGTON \u00b7 CRICKET", "CONFIRMED", "720/9",
     "India declare on a record 720/9",
     "Rahul makes 136 and Pant 128 in the record total.",
     "AFP"),
    (11, "SINALOA, MEXICO \u00b7 CARTEL", "REPORTED", "CAPTURED",
     "El Chapo Isidro captured",
     "The army seizes cartel kingpin Fausto Isidro; Sinaloa erupts.",
     "Reuters \u00b7 AP"),
    (12, "BRAS\u00cdLIA \u00b7 HEALTH", "CONFIRMED", "IN INTENSIVE CARE",
     "Bolsonaro taken to intensive care",
     "Brazil's jailed ex-president is admitted to ICU.",
     "Reuters \u00b7 AP"),
    (13, "AUSTRALIA \u00b7 CRICKET", "CONFIRMED", "T20 STREAK ENDS",
     "Australia ends England's T20 streak",
     "England's seven-match winning run in T20 ends.",
     "ABC \u00b7 Reuters"),
]

# also: (num, region, headline, source)
ALSO = [
    (14, "WORLD", "World Court: Myanmar committed genocide", "Guardian"),
    (15, "MIDDLE EAST", "Gaza aid-vehicle strike kills three", "Reuters"),
    (16, "EUROPE", "Denmark expels Russian diplomat", "Al Jazeera"),
    (17, "AMERICAS", "FBI probes apparent database hack", "AP"),
    (18, "AMERICAS", "Trump threatens overseas AI-centre ban", "Reuters"),
    (19, "AMERICAS", "Melania Trump seeks Christmas ceasefire", "AP"),
    (20, "EUROPE", "Denmark ratifies US Greenland deal 109-0", "Reuters"),
    (21, "ASIA-PACIFIC", "North Korea expands Yongbyon plant", "IAEA"),
    (22, "ASIA-PACIFIC", "Bangladesh violence before Hasina return", "AP"),
    (23, "AMERICAS", "US signs new Venezuela military deal", "Reuters"),
    (24, "ASIA-PACIFIC", "Nepal PM to meet Modi in New Delhi", "PTI"),
    (25, "AFRICA", "South Africa votes in local elections", "Reuters"),
    (26, "AMERICAS", "Mamdani plans to close Rikers Island", "AP"),
    (27, "ASIA-PACIFIC", "Davao jet inquiry opens; all 146 safe", "Reuters"),
    (28, "AFRICA", "700,000 displaced around Moyale", "UN OCHA"),
    (29, "ASIA-PACIFIC", "Cyclone Akvan cancels 14 Ranchi flights", "PTI"),
    (30, "ASIA-PACIFIC", "Japan to train live-fire in India", "Reuters"),
    (31, "ASIA-PACIFIC", "Modi opens Nitish Setu bridge in Bihar", "PTI"),
    (32, "OCEANIA", "Cummins keeps Australia Test captaincy", "ABC"),
    (33, "WORLD", "AI may have cracked a famous maths problem", "Nature"),
    (34, "EUROPE", "Trafalgar tree leaves Oslo for London", "BBC"),
    (35, "EUROPE", "Alcaraz v Zverev in ATP Finals final", "ATP"),
    (36, "AMERICAS", "Wembanyama scores 50 as Spurs roll on", "AP"),
]

DATE_CHECK = ("Wires read to 23:59 UTC, Sunday 22 Nov 2026. Every story above "
              "happened, or was first reported, on 22 Nov in at least one "
              "time zone. Left out as other days' news: Peru quake "
              "(Fri 20 Nov) \u00b7 Russia's 400-drone barrage (19\u201320 Nov) "
              "\u00b7 Shenzhen summit (Thu 19 Nov) \u00b7 UK-EU reset deal "
              "agreed (Fri 20 Nov) \u00b7 Mongolia president quits "
              "(Thu 19 Nov) \u00b7 Bayelsa boat capsize (Fri 20 Nov) \u00b7 "
              "Kryvyi Rih double-tap strike (Fri 20 Nov)")

CERTAINTY_FILL = {
    "CONFIRMED": GREEN,
    "REPORTED": BLUE,
    "CLAIM": GOLD,
    "ONGOING": PURPLE,
}

# ---------------------------------------------------------------- scenes

def scene_cop31(d, x, y, w, h):
    """Conference hall: warm wall, delegate heads, long table, clock."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 214, 178))
    d.rectangle([x, y, x + w, y + 10], fill=(196, 160, 110))
    # sign, top-left, clear of the delegates
    d.rectangle([x + 10, y + 14, x + 112, y + 38], fill=(255, 255, 255),
                outline=RED, width=2)
    f = font(SANS_B, 10)
    d.text((x + 14, y + 18), "NO FOSSIL", font=f, fill=RED)
    d.text((x + 14, y + 29), "FUELS", font=f, fill=RED)
    # clock, top-right
    d.ellipse([x + w - 44, y + 10, x + w - 10, y + 44], fill=(250, 250, 245),
              outline=INK, width=2)
    d.line([x + w - 27, y + 27, x + w - 27, y + 15], fill=INK, width=2)
    d.line([x + w - 27, y + 27, x + w - 17, y + 31], fill=INK, width=2)
    # delegates along the bottom: heads above the table
    for i in range(5):
        cx = x + 36 + i * 58
        d.ellipse([cx - 10, y + 42, cx + 10, y + 62], fill=(90, 50, 40))
        d.polygon([(cx - 18, y + 72), (cx - 9, y + 60),
                   (cx + 9, y + 60), (cx + 18, y + 72)],
                  fill=[(120, 60, 50), (60, 90, 60), (60, 60, 110),
                        (150, 110, 40), (90, 90, 90)][i])
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(120, 82, 50))


def scene_drones(d, x, y, w, h):
    """Night city under drone attack: lit windows, drones, searchlight."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 54))
    for i in range(30):
        sx = x + (i * 53) % w
        sy = y + (i * 29) % 26
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220))
    for bx, bw, bh in [(0, 70, 62), (78, 56, 78), (142, 66, 52), (216, 60, 70), (284, 36, 46)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(24, 34, 66))
        for wy in range(y + h - bh + 8, y + h - 6, 12):
            for wx in range(x + bx + 8, x + bx + bw - 8, 14):
                if (wx + wy) % 3 == 0:
                    d.rectangle([wx, wy, wx + 5, wy + 7], fill=(255, 214, 90))
    d.polygon([(x + w - 40, y + h), (x + w - 90, y + 6), (x + w - 60, y + 6)],
              fill=(220, 225, 240))
    for dx, dy in [(60, 22), (150, 14), (240, 30)]:
        d.line([x + dx - 8, y + dy, x + dx + 8, y + dy], fill=(255, 220, 100), width=2)
        d.line([x + dx, y + dy - 8, x + dx, y + dy + 8], fill=(255, 220, 100), width=2)
        d.ellipse([x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3],
                  fill=(255, 220, 100))


def scene_radars(d, x, y, w, h):
    """Two radar dishes under a night sky, flames, a ship, a curved arrow."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 54))
    for i in range(24):
        sx = x + (i * 47) % w
        sy = y + (i * 23) % 22
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220))
    d.ellipse([x + w - 60, y + 8, x + w - 20, y + 48], fill=(235, 230, 210))
    for cx in (x + 70, x + 210):
        d.rectangle([cx - 4, y + 52, cx + 4, y + h - 8], fill=(120, 120, 120))
        d.pieslice([cx - 40, y + 12, cx + 40, y + 76], 180, 360,
                   fill=(150, 150, 150), outline=(220, 220, 220))
        d.polygon([(cx - 10, y + 52), (cx, y + 30), (cx + 10, y + 52)],
                  fill=(255, 140, 40))
    d.rectangle([x + 8, y + h - 18, x + 90, y + h - 8], fill=(40, 40, 60))
    d.arc([x + 150, y + 30, x + 290, y + 90], 200, 340, fill=(255, 255, 255),
          width=3)


def scene_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 110))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(20, 40, 80))
    d.rectangle([x + 14, y + h - 30, x + w - 14, y + h - 14], fill=(150, 30, 30))
    for i, c in enumerate([(255, 200, 40), (40, 120, 200), (220, 220, 220)]):
        d.rectangle([x + 22 + i * 44, y + h - 44, x + 58 + i * 44, y + h - 30],
                    fill=c)


def scene_bridges(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 54))
    for i in range(12):
        d.ellipse([x + (i * 37) % w, y + (i * 17) % 14 + 2,
                   x + (i * 37) % w + 2, y + (i * 17) % 14 + 4],
                  fill=(255, 255, 220))
    d.arc([x - 10, y + 6, x + w // 2 + 10, y + h + 26], 180, 360,
          fill=(240, 240, 240), width=5)
    d.arc([x + w // 2 - 10, y + 6, x + w + 10, y + h + 26], 180, 360,
          fill=(240, 240, 240), width=5)
    d.ellipse([x + w - 24, y + 6, x + w - 10, y + 20], fill=(235, 230, 210))


def scene_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 110))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(20, 40, 80))
    d.rectangle([x + 30, y + h - 30, x + w - 30, y + h - 14], fill=(120, 120, 120))
    d.polygon([(x + w // 2 - 8, y + 6), (x + w // 2 + 8, y + 6),
               (x + w // 2, y + h - 30)], fill=(255, 140, 40))
    d.polygon([(x + w // 2 - 16, y + 14), (x + w // 2 + 16, y + 14),
               (x + w // 2, y + h - 30)], fill=(255, 200, 60))


def scene_fence(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 210, 200))
    for i in range(9):
        bx = x + 8 + i * 20
        d.rectangle([bx, y + 6, bx + 8, y + h - 6], fill=(90, 90, 90))
    d.rectangle([x, y + 10, x + w, y + 16], fill=(90, 90, 90))
    d.rectangle([x, y + h - 16, x + w, y + h - 10], fill=(90, 90, 90))
    d.rectangle([x + 8, y + 22, x + 44, y + 30], fill=(40, 90, 170))
    d.rectangle([x + 8, y + 30, x + 44, y + 38], fill=(20, 20, 20))
    d.rectangle([x + 8, y + 38, x + 44, y + 46], fill=(240, 240, 240))


def scene_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 244, 238))
    pts = [(x + 10, y + h - 12), (x + 50, y + h - 26), (x + 90, y + h - 20),
           (x + 130, y + h - 34), (x + 170, y + 10)]
    d.line(pts, fill=GREEN, width=3)
    for px, py in pts:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=GREEN)


def scene_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 54))
    d.ellipse([x + 30, y + h - 26, x + 58, y + h - 2], fill=(20, 20, 20),
              outline=(200, 200, 200), width=2)
    d.ellipse([x + w - 58, y + h - 26, x + w - 30, y + h - 2], fill=(20, 20, 20),
              outline=(200, 200, 200), width=2)
    d.polygon([(x + 44, y + h - 18), (x + 80, y + h - 30), (x + w - 60, y + h - 28),
               (x + w - 40, y + h - 16)], fill=(200, 30, 30))
    d.rectangle([x + 8, y + h - 12, x + w - 8, y + h - 8], fill=(90, 90, 90))


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(74, 140, 70))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(60, 120, 58))
    for i, sx in enumerate((x + 60, x + 68, x + 76)):
        d.rectangle([sx, y + 10, sx + 5, y + 30], fill=(240, 220, 120))
    d.ellipse([x + w - 40, y + 14, x + w - 26, y + 28], fill=(255, 255, 255),
              outline=BLUE, width=2)
    d.ellipse([x + 120, y + h - 26, x + 132, y + h - 14], fill=(255, 255, 255),
              outline=BLUE, width=2)


def scene_desert(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 186, 140))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(160, 120, 70))
    d.rectangle([x + 40, y + h - 34, x + 130, y + h - 18], fill=(60, 50, 40))
    d.ellipse([x + 150, y + 6, x + 166, y + 22], fill=(255, 220, 120))


def scene_hospital(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 240, 245))
    d.rectangle([x + 20, y + h - 22, x + w - 20, y + h - 10], fill=(255, 255, 255),
                outline=(150, 150, 150))
    d.rectangle([x + 30, y + h - 30, x + w - 60, y + h - 22], fill=(200, 220, 240))
    d.rectangle([x + 10, y + 8, x + 34, y + 32], fill=(255, 255, 255),
                outline=RED, width=2)
    d.rectangle([x + 16, y + 14, x + 28, y + 26], fill=RED)
    d.rectangle([x + 20, y + 18, x + 24, y + 22], fill=(255, 255, 255))


def scene_t20(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 54))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(74, 140, 70))
    d.polygon([(x + 90, y + 8), (x + 104, y + 8), (x + 98, y + h - 14),
               (x + 88, y + h - 14)], fill=(220, 190, 120))
    d.ellipse([x + 130, y + 12, x + 146, y + 28], fill=(255, 255, 255),
              outline=RED, width=2)


LEAD_SCENES = [scene_cop31, scene_drones, scene_radars]
MEDIUM_SCENES = [scene_tanker, scene_bridges, scene_ship, scene_fence,
                 scene_chart, scene_f1, scene_cricket, scene_desert,
                 scene_hospital, scene_t20]

# dotted world map: land as ellipses in a 0..100 x 0..50 space
LAND_ELLIPSES = [
    (18, 13, 13, 8), (6, 10, 4, 4), (20, 23, 4, 3),      # N America
    (33, 6, 3.5, 2.5),                                     # Greenland
    (30, 33, 6, 9), (31, 43, 2, 3),                        # S America
    (52, 11, 5, 4), (48, 8, 1.5, 1.5),                     # Europe + UK
    (55, 28, 7, 9),                                         # Africa
    (72, 13, 14, 8), (70, 24, 3, 4), (80, 24, 4, 3),       # Asia
    (88, 16, 1.5, 2.5), (82, 30, 4, 1.5),                  # Japan, Indonesia
    (84, 36, 5, 3.5), (92, 42, 1.5, 2),                    # Australia, NZ
]

# pin positions (story number -> (x, y) in the same 0..100 x 0..50 space)
PINS = {
    1: (55, 14), 2: (57, 10), 3: (63, 20), 4: (65, 21), 5: (58, 11),
    6: (54, 7), 7: (56, 6), 8: (82, 20), 9: (12, 18), 10: (94, 44),
    11: (10, 22), 12: (30, 36), 13: (88, 38),
}

# ---------------------------------------------------------------- page

def draw_header(d):
    d.rectangle([0, 0, W, 22], fill=NAVY)
    f = font(SANS_B, 11)
    d.text((12, 4), "THE WORLD IN ONE DAY", font=f, fill=(255, 255, 255))
    t = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - 12 - text_w(d, t, f), 4), t, font=f, fill=(255, 255, 255))


def draw_masthead(d):
    f = font(SERIF_B, 48)
    t = "Sunday 22 November 2026"
    d.text(((W - text_w(d, t, f)) / 2, 26), t, font=f, fill=INK)
    f2 = font(SERIF, 15)
    d.text(((W - text_w(d, KICKER, f2)) / 2, 80), KICKER, font=f2, fill=RED)


def draw_key_numbers(d):
    y0, y1 = 98, 148
    cw = (W - 24) / 6
    for i, (num, cap) in enumerate(KEY_NUMBERS):
        x0 = 12 + i * cw
        if i:
            d.line([x0, y0 + 4, x0, y1 - 4], fill=(200, 190, 165), width=1)
        f = font(SERIF_B, 28)
        d.text((x0 + (cw - text_w(d, num, f)) / 2, y0 + 2), num, font=f, fill=RED)
        f2 = font(SANS, 8)
        for ln_i, ln in enumerate(wrap(d, cap, f2, cw - 12)):
            d.text((x0 + (cw - text_w(d, ln, f2)) / 2, y0 + 34 + ln_i * 10),
                   ln, font=f2, fill=GRAY)


def draw_region_strip(d):
    y0, y1 = 152, 168
    total = sum(c for _, c, _ in REGIONS)
    x = 12
    for name, count, color in REGIONS:
        w = (W - 24) * count / total
        d.rectangle([x, y0, x + w, y1], fill=color)
        f = font(SANS_B, 10)
        t = "%s %d" % (name, count)
        d.text((x + (w - text_w(d, t, f)) / 2, y0 + 3), t, font=f,
               fill=(255, 255, 255))
        x += w


def draw_utc_strip(d):
    y0, y1 = 172, 188
    d.rectangle([0, y0, W, y1], fill=NAVY)
    f = font(SANS_B, 9)
    x = 12
    x += chip(d, x, y0 + 3, "THE DAY IN UTC", (255, 200, 40), (20, 20, 20),
              f=font(SANS_B, 9)) + 8
    for t, label in UTC_EVENTS:
        d.text((x, y0 + 4), t, font=font(SANS_B, 9), fill=(255, 200, 40))
        x += text_w(d, t, font(SANS_B, 9)) + 4
        d.text((x, y0 + 4), label, font=f, fill=(255, 255, 255))
        x += text_w(d, label, f) + 4
        if (t, label) != UTC_EVENTS[-1]:
            d.text((x, y0 + 4), "\u00b7", font=f, fill=(150, 150, 170))
            x += 10


def draw_leads(d):
    col_w, gap = 320, 20
    for i, (num, dateline, cert, label, headline, deck, sources) in enumerate(LEADS):
        x = 12 + i * (col_w + gap)
        y = 194
        LEAD_SCENES[i](d, x, y, col_w, 78)
        chip(d, x + 4, y + 4, label, RED, f=font(SANS_B, 9))
        badge(d, x + col_w - 14, y + 14, num)
        d.text((x, y + 84), "%d \u00b7 %s" % (num, dateline), font=font(SANS_B, 10),
               fill=RED)
        cw = chip(d, x + col_w - 62, y + 82, cert, CERTAINTY_FILL[cert],
                  f=font(SANS_B, 9))
        draw_wrapped(d, x, y + 100, headline, font(SERIF_B, 21), col_w, INK, 24,
                     max_lines=3)
        draw_wrapped(d, x, y + 176, deck, font(SERIF, 12), col_w, INK, 15,
                     max_lines=3)
        d.text((x, y + 224), "Sources: " + sources, font=font(SANS, 9), fill=GRAY)


def draw_medium(d):
    col_w, gap = 194, 7
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            num, dateline, cert, label, headline, deck, sources = MEDIUM[idx]
            x = 12 + col * (col_w + gap)
            y = 436 + row * 148
            MEDIUM_SCENES[idx](d, x, y, col_w, 40)
            chip(d, x + 3, y + 3, label, RED, f=font(SANS_B, 8))
            badge(d, x + col_w - 11, y + 11, num, r=9)
            d.text((x, y + 44), dateline, font=font(SANS_B, 8), fill=RED)
            draw_wrapped(d, x, y + 58, headline, font(SERIF_B, 13), col_w, INK,
                         15, max_lines=2)
            draw_wrapped(d, x, y + 90, deck, font(SERIF, 10), col_w, INK, 12,
                         max_lines=2)
            d.text((x, y + 128), sources, font=font(SANS, 8), fill=GRAY)
            chip(d, x + col_w - 58, y + 126, cert, CERTAINTY_FILL[cert],
                 f=font(SANS_B, 8))


def draw_map(d):
    x0, y0, x1, y1 = 12, 748, 262, 884
    d.text((x0, 726), "WHERE IT HAPPENED", font=font(SERIF_B, 13), fill=INK)
    d.rectangle([x0, y0, x1, y1], fill=LIGHT_BLUE)
    mw, mh = x1 - x0, y1 - y0
    # dotted land
    step = 7
    for gy in range(y0 + 3, y1 - 2, step):
        for gx in range(x0 + 3, x1 - 2, step):
            nx = (gx - x0) / mw * 100
            ny = (gy - y0) / mh * 50
            for cx, cy, rx, ry in LAND_ELLIPSES:
                if ((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2 <= 1:
                    d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=LAND)
                    break
    for num, (nx, ny) in PINS.items():
        px = x0 + nx / 100 * mw
        py = y0 + ny / 50 * mh
        badge(d, px, py, num, r=8)


def draw_also(d):
    x0 = 272
    d.text((x0, 726), "ALSO ON SUNDAY 22 NOVEMBER \u2014 23 MORE STORIES",
           font=font(SERIF_B, 13), fill=RED)
    f_num = font(SANS_B, 10)
    f_txt = font(SANS, 10)
    f_src = font(SANS, 10)
    for i, (num, region, headline, source) in enumerate(ALSO):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        x = x0 + col * 372
        y = 748 + row * 13
        d.text((x, y), "%d %s:" % (num, region), font=f_num, fill=RED)
        tx = x + text_w(d, "%d %s: " % (num, region), f_num)
        d.text((tx, y), headline, font=f_txt, fill=INK)
        sx = tx + text_w(d, headline, f_txt) + 4
        d.text((sx, y), "\u00b7 " + source, font=f_src, fill=GRAY)
        if sx + text_w(d, "\u00b7 " + source, f_src) > x0 + (col + 1) * 372 - 4:
            raise ValueError("ALSO item overflows column: %d %s" % (num, headline))


def draw_bottom(d):
    y0 = 920
    d.rectangle([12, y0, W - 12, y0 + 44], outline=RED, width=2)
    d.rectangle([12, y0, 104, y0 + 44], fill=RED)
    d.text((18, y0 + 14), "DATE CHECK", font=font(SANS_B, 11),
           fill=(255, 255, 255))
    draw_wrapped(d, 112, y0 + 4, DATE_CHECK, font(SERIF, 10), W - 12 - 112 - 8,
                 INK, 13, max_lines=3)
    f = font(SANS, 9)
    t = ("HOW TO READ THE TAGS \u2014 \u2713 CONFIRMED official / 2+ outlets "
         "\u00b7 REPORTED wires / one source \u00b7 CLAIM one party's claim, "
         "contested \u00b7 \u2713 ONGOING still developing")
    d.text(((W - text_w(d, t, f)) / 2, 970), t, font=f, fill=GRAY)
    f2 = font(SERIF_B, 14)
    t2 = "THE SUNDAY LEDGER \u00b7 SUNDAY 22 NOVEMBER 2026 \u00b7 36 STORIES \u00b7 7 REGIONS"
    d.text(((W - text_w(d, t2, f2)) / 2, 986), t2, font=f2, fill=INK)
    f3 = font(SANS, 8)
    t3 = "Scenes are drawn illustrations of reported events, not photographs. Sources named beside each story."
    d.text(((W - text_w(d, t3, f3)) / 2, 1004), t3, font=f3, fill=GRAY)


def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_header(d)
    draw_masthead(d)
    draw_key_numbers(d)
    draw_region_strip(d)
    draw_utc_strip(d)
    draw_leads(d)
    draw_medium(d)
    draw_map(d)
    draw_also(d)
    draw_bottom(d)
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img1 = render()
    img1.save(out, format="PNG")
    h1 = hashlib.sha256(open(out, "rb").read()).hexdigest()
    tmp = "/tmp/ni22-v7-render2.png"
    img2 = render()
    img2.save(tmp, format="PNG")
    h2 = hashlib.sha256(open(tmp, "rb").read()).hexdigest()
    print("wrote %s: %d bytes sha256=%s" % (out, os.path.getsize(out), h1))
    print("second render sha256=%s identical=%s" % (h2, h1 == h2))
    if h1 != h2:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
