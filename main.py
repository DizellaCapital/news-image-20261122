#!/usr/bin/env python3
"""THE SUNDAY LEDGER — Sunday 22 November 2026 front page (v6).

Fresh renderer written in this session. One named change vs v5:
every one of the 23 ALSO items now carries a REGION tag AND a source
(0 unsourced, 23/23 region-tagged) — the top band (#1, #2, #3, #50, #51)
sources every also item; v5 left 9 of 23 unsourced and tagged none.
All other content (stories, headlines, decks, strips, DATE CHECK) is the
same verified 22 Nov 2026 set as v5. PIL only, no external assets.
Deterministic: two renders must be byte-identical.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24
BG = (246, 241, 227)          # warm cream paper
INK = (26, 26, 26)            # near-black text
NAVY = (22, 30, 58)           # top bar / UTC strip / night sky
RED = (163, 22, 33)           # accent red
GOLD = (201, 162, 39)         # gold accent
GREY = (90, 90, 90)           # secondary text
LIGHT_LINE = (120, 110, 90)   # hairline rules

TAG_FILL = {
    "CONFIRMED": (30, 122, 52),
    "REPORTED": (29, 78, 158),
    "CLAIM": (176, 132, 11),
    "ONGOING": (106, 63, 160),
}
REGION_FILL = {
    "EUROPE": (15, 118, 110),
    "MIDDLE EAST": (185, 28, 28),
    "ASIA-PACIFIC": (21, 128, 61),
    "AMERICAS": (124, 58, 237),
    "AFRICA": (194, 65, 12),
    "OCEANIA": (3, 105, 161),
    "WORLD": (87, 83, 78),
}

FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"


def font(path, size):
    return ImageFont.truetype(path, size)


def serif_b(size):
    return font(f"{FD}/DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font(f"{FD}/DejaVuSerif.ttf", size)


def serif_i(size):
    return font(f"{FL}/LiberationSerif-Italic.ttf", size)


def sans(size):
    return font(f"{FD}/DejaVuSans.ttf", size)


def sans_b(size):
    return font(f"{FD}/DejaVuSans-Bold.ttf", size)


def text_w(s, f):
    return f.getlength(s)


def wrap(s, f, max_w):
    """Greedy word wrap to max_w pixels. Returns list of lines."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, lines, f, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- data
KEY_NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed by air defence"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record total in NZ"),
    ("98.79%", "Hong Kong turnout by 5 pm"),
]
REGION_COUNTS = [
    ("EUROPE", 9), ("MIDDLE EAST", 3), ("ASIA-PACIFIC", 8),
    ("AMERICAS", 9), ("AFRICA", 2), ("OCEANIA", 3), ("WORLD", 2),
]
UTC_ITEMS = [
    ("01:00", "HK polls open"), ("03:00", "COP31 objections"),
    ("05:11", "Hamas seeks talks"), ("05:30", "Verstappen wins"),
    ("06:00", "COP31 session"), ("10:00", "HK polls close"),
    ("17:00", "ATP final"),
]
SUBTITLE = ("COP31 still without a deal \u00b7 186 drones over Ukraine overnight \u00b7 "
            "Iran claims US radars hit, Bahrain denies it")

# (label, dateline, tag, headline, deck, sources)
LEADS = [
    ("COP31: NO DEAL YET", "1 \u00b7 ANTALYA, T\u00dcRKIYE \u00b7 CLIMATE", "ONGOING",
     "COP31 deadlock deepens into Sunday",
     "No deal in Antalya: the draft drops every fossil-fuel mention and the $120bn target.",
     "Sources: Health Policy Watch \u00b7 Carbon Brief"),
    ("186 DRONES OVERNIGHT", "2 \u00b7 KYIV REGION, UKRAINE \u00b7 WAR", "CONFIRMED",
     "Russia fires 186 drones at Ukraine",
     "Defences down or jam 161 of 186 drones; a block in Dymer is hit, seven feared trapped.",
     "Sources: Ukrainian Air Force \u00b7 Reuters"),
    ("CLAIM VS DENIAL", "3 \u00b7 MANAMA, BAHRAIN \u00b7 IRAN WAR", "CLAIM",
     "Iran claims two US radars hit; Bahrain denies it",
     "The IRGC claims two Patriot radars were hit; Bahrain says a civilian site burned.",
     "Sources: IRGC \u00b7 Bahrain Interior Ministry"),
]
MEDIUM = [
    ("TANKER HIT", "STRAIT OF HORMUZ \u00b7 WAR", "REPORTED",
     "Tankers hit off Oman as Gulf tensions surge",
     "An ADNOC vessel is struck; one crew member is missing.",
     "Reuters \u00b7 AP"),
    ("BRIDGES HIT", "KYIV, UKRAINE \u00b7 WAR", "REPORTED",
     "Russia strikes three Kyiv bridges",
     "Moscow answers the Crimea bridge attacks.",
     "Reuters \u00b7 Kyiv Independent"),
    ("SHIP ABLAZE", "GULF OF FINLAND \u00b7 WAR", "REPORTED",
     "Drones hit Russian cargo ship in the Baltic",
     "Finland tightens security after the strike.",
     "Finnish Forces \u00b7 Times of India"),
    ("1 DEC", "TALLINN, ESTONIA \u00b7 SECURITY", "CONFIRMED",
     "Estonia to shut its border with Russia",
     "Tallinn moves to close the frontier from 1 December.",
     "Reuters \u00b7 AP"),
    ("98.79% TURNOUT", "HONG KONG \u00b7 ELECTIONS", "CONFIRMED",
     "Hong Kong elects its Election Committee",
     "856 candidates chase 723 seats; turnout hits 98.79%.",
     "HK Government \u00b7 China Daily"),
    ("VERSTAPPEN WINS", "LAS VEGAS \u00b7 FORMULA 1", "CONFIRMED",
     "Verstappen wins the Las Vegas GP",
     "Verstappen beats Norris by 0.639s; Russell is third.",
     "FIA \u00b7 Formula1.com"),
    ("720/9", "WELLINGTON \u00b7 CRICKET", "CONFIRMED",
     "India declare on a record 720/9",
     "Rahul makes 136 and Pant 128 in the record total.",
     "AFP"),
    ("CAPTURED", "SINALOA, MEXICO \u00b7 CARTEL", "REPORTED",
     "El Chapo Isidro captured",
     "The army seizes cartel kingpin Fausto Isidro; Sinaloa erupts.",
     "Reuters \u00b7 AP"),
    ("IN INTENSIVE CARE", "BRAS\u00cdLIA \u00b7 HEALTH", "CONFIRMED",
     "Bolsonaro taken to intensive care",
     "Brazil's jailed ex-president is admitted to ICU.",
     "Reuters \u00b7 AP"),
    ("T20 STREAK ENDS", "AUSTRALIA \u00b7 CRICKET", "CONFIRMED",
     "Australia ends England's T20 streak",
     "England's seven-match winning run in T20 ends.",
     "ABC \u00b7 Reuters"),
]
# ALSO items: (number, region, headline, source) — v6: every item sourced
# and region-tagged. Region assignments match the page's region counts
# (EUROPE 9 / MIDDLE EAST 3 / ASIA-PACIFIC 8 / AMERICAS 9 / AFRICA 2 /
# OCEANIA 3 / WORLD 2) — verified by counting numbered + also stories.
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
DATE_CHECK = (
    "DATE CHECK \u2014 Wires read to 23:59 UTC, Sunday 22 Nov 2026. Every story above "
    "happened, or was first reported, on 22 Nov in at least one time zone. Left out as "
    "other days' news: Peru quake (Fri 20 Nov) \u00b7 Russia's 400-drone barrage (19\u201320 Nov) \u00b7 "
    "Shenzhen summit (Thu 19 Nov) \u00b7 Anthropic $81.3bn IPO (Thu 19 Nov) \u00b7 UK-EU reset deal "
    "agreed (Fri 20 Nov) \u00b7 Mongolia president quits (Thu 19 Nov) \u00b7 Bayelsa boat capsize "
    "(Fri 20 Nov) \u00b7 Kryvyi Rih double-tap strike (Fri 20 Nov)")

# ------------------------------------------------------------- pictures
# Flat vector scenes, drawn fresh in this session. Each takes the box
# (x0, y0, x1, y1) and a draw object; compositions match the v5 page.

def _sky(d, box, top, bot):
    d.rectangle(box, fill=top)
    x0, y0, x1, y1 = box
    for i in range(0, (y1 - y0) // 3 + 1):
        t = i / max(1, (y1 - y0) // 3)
        c = tuple(int(top[j] + (bot[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i * 3), (x1, y0 + i * 3)], fill=c)


def _stars(d, box, n, seed):
    import random
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = rnd.randint(x0 + 4, x1 - 4)
        y = rnd.randint(y0 + 4, y0 + (y1 - y0) // 2)
        r = rnd.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 220))


def pic_cop31(d, box):
    # Antalya conference hall: beige sky, domed hall, flags, sign.
    x0, y0, x1, y1 = box
    _sky(d, box, (232, 214, 170), (214, 190, 140))
    d.rectangle([x0, y1 - 42, x1, y1], fill=(196, 168, 118))
    # domed hall
    d.rectangle([x0 + 18, y1 - 95, x1 - 18, y1 - 42], fill=(176, 138, 88))
    d.pieslice([x0 + 70, y1 - 118, x1 - 70, y1 - 60], 180, 360, fill=(196, 158, 100))
    # columns / flags
    for i, cx in enumerate(range(x0 + 34, x1 - 30, 34)):
        d.rectangle([cx, y1 - 78, cx + 8, y1 - 42], fill=(90, 60, 40))
        d.ellipse([cx - 1, y1 - 88, cx + 9, y1 - 78], fill=(163, 22, 33))
    # NO FOSSIL FUELS sign
    d.rectangle([x1 - 150, y1 - 78, x1 - 14, y1 - 40], fill=(255, 255, 255),
                outline=(163, 22, 33), width=2)
    d.text((x1 - 142, y1 - 74), "NO FOSSIL", font=sans_b(13), fill=(163, 22, 33))
    d.text((x1 - 142, y1 - 58), "FUELS", font=sans_b(13), fill=(163, 22, 33))
    # clock
    d.ellipse([x1 - 52, y0 + 8, x1 - 12, y0 + 48], fill=(255, 255, 255),
              outline=(60, 60, 60), width=2)
    d.line([(x1 - 32, y0 + 28), (x1 - 32, y0 + 14)], fill=(60, 60, 60), width=2)
    d.line([(x1 - 32, y0 + 28), (x1 - 20, y0 + 28)], fill=(60, 60, 60), width=2)


def pic_drones(d, box):
    # Night city, searchlights, drone crosses.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 22, 48))
    _stars(d, box, 26, 7)
    # buildings
    import random
    rnd = random.Random(11)
    bx = x0 + 6
    while bx < x1 - 30:
        bw = rnd.randint(28, 52)
        bh = rnd.randint(50, 110)
        d.rectangle([bx, y1 - bh, bx + bw, y1], fill=(28, 34, 66))
        for wy in range(y1 - bh + 8, y1 - 8, 12):
            for wx in range(bx + 5, bx + bw - 5, 11):
                if rnd.random() < 0.55:
                    d.rectangle([wx, wy, wx + 5, wy + 6], fill=(240, 200, 90))
        bx += bw + 6
    # searchlight beam
    d.polygon([(x1 - 70, y1), (x1 - 30, y1), (x1 - 10, y0 + 18)], fill=(200, 210, 235))
    # drones (small crosses with glow)
    for cx, cy in [(x0 + 60, y0 + 42), (x0 + 150, y0 + 26), (x1 - 120, y0 + 58)]:
        d.line([(cx - 9, cy), (cx + 9, cy)], fill=(255, 120, 90), width=2)
        d.line([(cx, cy - 9), (cx, cy + 9)], fill=(255, 120, 90), width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 120))
    # moon / flare
    d.ellipse([x1 - 130, y1 - 92, x1 - 104, y1 - 66], fill=(245, 200, 110))


def pic_radars(d, box):
    # Two radar domes at night, orange markers.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 22, 48))
    _stars(d, box, 22, 21)
    d.ellipse([x1 - 90, y0 + 12, x1 - 46, y0 + 56], fill=(235, 225, 200))
    for cx in (x0 + 70, x1 - 90):
        d.rectangle([cx - 6, y1 - 70, cx + 6, y1], fill=(90, 95, 110))
        d.pieslice([cx - 62, y1 - 116, cx + 62, y1 - 10], 180, 360, fill=(225, 225, 225))
    for cx, cy in [(x0 + 150, y1 - 96), (x1 - 30, y1 - 70)]:
        d.polygon([(cx, cy - 12), (cx + 12, cy), (cx, cy + 12), (cx - 12, cy)],
                  fill=(240, 140, 40))


def pic_tanker(d, box):
    # Tanker at sea, containers, smoke. Fits a 40px-tall box: every
    # element is drawn inside the box (no drawing above y0).
    x0, y0, x1, y1 = box
    _sky(d, box, (170, 205, 225), (200, 220, 230))
    d.rectangle([x0, y1 - 14, x1, y1], fill=(70, 110, 140))
    d.rectangle([x0 + 8, y1 - 24, x1 - 8, y1 - 14], fill=(150, 40, 40))
    for i, c in enumerate([(220, 60, 60), (60, 160, 90), (230, 200, 60), (70, 110, 200)]):
        d.rectangle([x0 + 14 + i * 40, y1 - 33, x0 + 48 + i * 40, y1 - 24], fill=c)
    d.rectangle([x0 + 172, y1 - 38, x0 + 182, y1 - 24], fill=(240, 240, 240))


def pic_bridges(d, box):
    # Three arches over water at night. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(18, 24, 52))
    _stars(d, box, 14, 33)
    d.rectangle([x0, y1 - 10, x1, y1], fill=(40, 70, 110))
    for cx in (x0 + 40, x0 + 95, x0 + 150):
        d.arc([cx - 20, y1 - 32, cx + 20, y1 - 2], 180, 360,
              fill=(230, 230, 230), width=4)
    d.ellipse([x1 - 30, y0 + 4, x1 - 18, y0 + 16], fill=(245, 200, 90))


def pic_ship(d, box):
    # Cargo ship with containers, sun. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    _sky(d, box, (120, 160, 200), (190, 210, 225))
    d.rectangle([x0, y1 - 12, x1, y1], fill=(60, 100, 130))
    d.rectangle([x0 + 10, y1 - 20, x1 - 10, y1 - 12], fill=(40, 60, 90))
    for i, c in enumerate([(200, 60, 60), (60, 170, 100), (235, 200, 70)]):
        d.rectangle([x0 + 18 + i * 38, y1 - 28, x0 + 50 + i * 38, y1 - 20], fill=c)
    d.ellipse([x1 - 28, y0 + 4, x1 - 16, y0 + 16], fill=(245, 190, 80))


def pic_border(d, box):
    # Border fence with flag. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    _sky(d, box, (200, 210, 220), (220, 222, 225))
    d.rectangle([x0, y1 - 10, x1, y1], fill=(140, 150, 140))
    for fx in range(x0 + 8, x1 - 4, 12):
        d.line([(fx, y0 + 6), (fx, y1 - 10)], fill=(80, 85, 95), width=2)
    d.line([(x0, y0 + 8), (x1, y0 + 8)], fill=(80, 85, 95), width=2)
    d.line([(x0, y0 + 18), (x1, y0 + 18)], fill=(80, 85, 95), width=2)
    # Estonian flag
    d.rectangle([x0 + 14, y0 + 22, x0 + 44, y0 + 27], fill=(0, 114, 206))
    d.rectangle([x0 + 14, y0 + 27, x0 + 44, y0 + 31], fill=(0, 0, 0))
    d.rectangle([x0 + 14, y0 + 31, x0 + 44, y0 + 35], fill=(255, 255, 255))


def pic_hk(d, box):
    # Turnout chart rising. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(240, 238, 230))
    d.rectangle([x0 + 10, y1 - 18, x0 + 56, y1 - 6], fill=(163, 22, 33))
    d.rectangle([x0 + 64, y1 - 12, x0 + 110, y1 - 6], fill=(200, 200, 200))
    pts = [(x0 + 118, y1 - 14), (x0 + 138, y1 - 22), (x0 + 158, y1 - 12),
           (x0 + 178, y1 - 6)]
    d.line(pts, fill=(30, 122, 52), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(30, 122, 52))


def pic_f1(d, box):
    # Red F1 car, night. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 18, 52))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(40, 40, 60))
    d.rounded_rectangle([x0 + 20, y1 - 22, x1 - 20, y1 - 10], 6, fill=(200, 30, 40))
    d.polygon([(x0 + 55, y1 - 22), (x0 + 100, y1 - 32), (x0 + 135, y1 - 22)],
              fill=(200, 30, 40))
    for cx in (x0 + 50, x1 - 50):
        d.ellipse([cx - 9, y1 - 14, cx + 9, y1 - 2], fill=(20, 20, 20))


def pic_cricket(d, box):
    # Green outfield, pitch, stumps. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(90, 160, 90))
    d.rectangle([x0 + 40, y0 + 4, x1 - 40, y1 - 4], fill=(214, 190, 140))
    for sx in (x0 + 58, x1 - 58):
        for k in range(3):
            d.rectangle([sx + k * 5 - 6, y1 - 16, sx + k * 5 - 3, y1 - 6],
                        fill=(240, 210, 60))
    d.ellipse([x0 + 100, y0 + 8, x0 + 112, y0 + 20], fill=(255, 255, 255))
    d.ellipse([x0 + 92, y1 - 22, x0 + 104, y1 - 10], fill=(40, 80, 200))


def pic_cartel(d, box):
    # Desert road, truck, mountains. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    _sky(d, box, (220, 200, 160), (200, 180, 140))
    d.polygon([(x0, y1 - 12), (x0 + 55, y0 + 8), (x0 + 110, y1 - 12)],
              fill=(150, 120, 90))
    d.rectangle([x0, y1 - 12, x1, y1], fill=(190, 170, 130))
    d.rectangle([x0 + 55, y1 - 24, x0 + 135, y1 - 14], fill=(120, 90, 60))
    for cx in (x0 + 72, x0 + 118):
        d.ellipse([cx - 7, y1 - 15, cx + 7, y1 - 3], fill=(20, 20, 20))


def pic_hospital(d, box):
    # White ward, red cross. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(235, 240, 245))
    d.rectangle([x0 + 10, y1 - 12, x1 - 10, y1 - 4], fill=(200, 210, 215))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 2
    d.rectangle([cx - 5, cy - 13, cx + 5, cy + 13], fill=(200, 30, 40))
    d.rectangle([cx - 13, cy - 5, cx + 13, cy + 5], fill=(200, 30, 40))


def pic_t20(d, box):
    # Night cricket: stumps, ball. Fits a 40px-tall box.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(18, 28, 70))
    d.rectangle([x0, y1 - 10, x1, y1], fill=(70, 140, 80))
    for sx in (x0 + 80, x1 - 100):
        for k in range(3):
            d.rectangle([sx + k * 5 - 6, y1 - 22, sx + k * 5 - 3, y1 - 12],
                        fill=(240, 210, 60))
    d.ellipse([x0 + 36, y1 - 18, x0 + 48, y1 - 6], fill=(255, 255, 255))
    d.ellipse([x1 - 48, y1 - 18, x1 - 36, y1 - 6], fill=(255, 255, 255))


LEAD_PICS = [pic_cop31, pic_drones, pic_radars]
MEDIUM_PICS = [pic_tanker, pic_bridges, pic_ship, pic_border, pic_hk,
               pic_f1, pic_cricket, pic_cartel, pic_hospital, pic_t20]


def draw_map(d, box, pins):
    """Simplified world map: beige land blobs on pale blue + numbered pins."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(205, 225, 235))
    land = (198, 214, 170)
    # North America
    d.ellipse([x0 + 8, y0 + 18, x0 + 108, y0 + 78], fill=land)
    d.ellipse([x0 + 30, y0 + 72, x0 + 88, y0 + 118], fill=land)
    # South America
    d.ellipse([x0 + 62, y0 + 122, x0 + 108, y0 + 178], fill=land)
    # Europe / Africa / Asia
    d.ellipse([x0 + 150, y0 + 8, x0 + 330, y0 + 78], fill=land)
    d.ellipse([x0 + 168, y0 + 72, x0 + 232, y0 + 138], fill=land)
    # Australia
    d.ellipse([x0 + 300, y0 + 128, x0 + 352, y0 + 162], fill=land)
    # pins: (number, fx, fy) fractions of box
    for num, fx, fy in pins:
        px, py = x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(163, 22, 33),
                  outline=(255, 255, 255), width=1)
        f = sans_b(9)
        tw = f.getlength(str(num))
        d.text((px - tw / 2, py - 6), str(num), font=f, fill=(255, 255, 255))


MAP_PINS = [
    (1, 0.52, 0.40), (2, 0.46, 0.24), (3, 0.62, 0.55), (4, 0.66, 0.52),
    (5, 0.42, 0.18), (6, 0.46, 0.08), (7, 0.52, 0.10), (8, 0.82, 0.32),
    (9, 0.12, 0.40), (10, 0.88, 0.85), (11, 0.16, 0.58), (12, 0.24, 0.72),
    (13, 0.86, 0.76),
]

# ------------------------------------------------------------ sections

def tag_chip(d, x, y, tag, size=10):
    """Right-aligned certainty tag chip; returns left edge."""
    f = sans_b(size)
    tw = f.getlength(tag)
    w = tw + 10
    h = size + 5
    d.rounded_rectangle([x - w, y, x, y + h], 3, fill=TAG_FILL[tag])
    d.text((x - w + 5, y + 2), tag, font=f, fill=(255, 255, 255))
    return x - w


def draw_top(d, y):
    d.rectangle([0, y, W, y + 20], fill=NAVY)
    d.text((MARGIN, y + 4), "THE WORLD IN ONE DAY", font=sans_b(11),
           fill=(255, 255, 255))
    right = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    f = sans_b(10)
    d.text((W - MARGIN - f.getlength(right), y + 5), right, font=f,
           fill=(200, 205, 220))
    return y + 20


def draw_masthead(d, y):
    f = serif_b(60)
    t = "Sunday 22 November 2026"
    d.text(((W - f.getlength(t)) / 2, y), t, font=f, fill=INK)
    y += 66
    f2 = serif_i(15)
    d.text(((W - f2.getlength(SUBTITLE)) / 2, y), SUBTITLE, font=f2, fill=RED)
    return y + 22


def draw_key_numbers(d, y):
    col_w = (W - 2 * MARGIN) / 6
    fnum = serif_b(28)
    fcap = sans(9)
    for i, (num, cap) in enumerate(KEY_NUMBERS):
        x0 = MARGIN + i * col_w
        d.text((x0 + (col_w - fnum.getlength(num)) / 2, y), num, font=fnum,
               fill=RED)
        lines = wrap(cap, fcap, col_w - 8)
        ly = y + 32
        for ln in lines:
            d.text((x0 + (col_w - fcap.getlength(ln)) / 2, ly), ln, font=fcap,
                   fill=GREY)
            ly += 11
        if i:
            d.line([(x0, y + 4), (x0, y + 44)], fill=(200, 190, 170), width=1)
    return y + 50


def draw_region_strip(d, y):
    x = MARGIN
    f = sans_b(10)
    avail = W - 2 * MARGIN
    total_len = sum(len(f"{name} {cnt}") for name, cnt in REGION_COUNTS)
    for name, cnt in REGION_COUNTS:
        label = f"{name} {cnt}"
        w = avail * len(label) / total_len
        d.rectangle([x, y, x + w - 3, y + 20], fill=REGION_FILL[name])
        d.text((x + (w - 3 - f.getlength(label)) / 2, y + 4), label, font=f,
               fill=(255, 255, 255))
        x += w
    return y + 20


def draw_utc_strip(d, y):
    d.rectangle([0, y, W, y + 20], fill=NAVY)
    # pick the largest font size whose full strip fits the page width
    chosen = None
    for size in (10, 9, 8.5, 8):
        f = sans_b(size)
        fr = sans(size)
        w = MARGIN + f.getlength("THE DAY IN UTC") + 14
        for i, (t, label) in enumerate(UTC_ITEMS):
            w += 12 + f.getlength(t) + 5 + fr.getlength(label)
            if i < len(UTC_ITEMS) - 1:
                w += 14
        if w <= W - MARGIN:
            chosen = (size, f, fr)
            break
    size, f, fr = chosen or (8, sans_b(8), sans(8))
    x = MARGIN
    d.text((x, y + 4), "THE DAY IN UTC", font=f, fill=GOLD)
    x += f.getlength("THE DAY IN UTC") + 14
    for i, (t, label) in enumerate(UTC_ITEMS):
        d.text((x, y + 4), "\u25c6", font=f, fill=(200, 205, 220))
        x += 12
        d.text((x, y + 4), t, font=f, fill=GOLD)
        x += f.getlength(t) + 5
        d.text((x, y + 4), label, font=fr, fill=(255, 255, 255))
        x += fr.getlength(label)
        if i < len(UTC_ITEMS) - 1:
            x += 14
    return y + 20


def draw_leads(d, y, img_h):
    col_w = (W - 2 * MARGIN - 16) / 3
    f_head = serif_b(21)
    f_deck = serif(13)
    f_src = sans(10)
    f_date = sans_b(10)
    for i, (label, dateline, tag, head, deck, src) in enumerate(LEADS):
        x0 = MARGIN + i * (col_w + 8)
        x1 = x0 + col_w
        # illustration with label + number
        LEAD_PICS[i](d, (int(x0), y, int(x1), y + img_h))
        d.rectangle([x0, y, x0 + 150, y + 18], fill=RED)
        d.text((x0 + 6, y + 2), label, font=sans_b(10), fill=(255, 255, 255))
        num = str(i + 1)
        fn = sans_b(13)
        d.ellipse([x1 - 26, y + 6, x1 - 6, y + 26], fill=NAVY)
        d.text((x1 - 26 + (20 - fn.getlength(num)) / 2, y + 8), num, font=fn,
               fill=(255, 255, 255))
        ty = y + img_h + 6
        d.text((x0, ty), dateline, font=f_date, fill=RED)
        tag_chip(d, x1, ty - 1, tag)
        hy = ty + 18
        hlines = wrap(head, f_head, col_w)
        assert len(hlines) <= 2, f"lead headline overflow: {head}"
        hy = draw_wrapped(d, x0, hy, hlines, f_head, INK, 24)
        assert deck.endswith("."), f"lead deck must be a full sentence: {deck}"
        dlines = wrap(deck, f_deck, col_w)
        assert len(dlines) <= 2, f"lead deck overflow: {deck}"
        hy = draw_wrapped(d, x0, hy + 2, dlines, f_deck, INK, 16)
        d.text((x0, hy + 2), src, font=f_src, fill=GREY)
    return y + img_h + 6 + 18 + 48 + 34 + 14


def draw_medium(d, y, img_h, row_h=136):
    col_w = (W - 2 * MARGIN - 32) / 5
    f_head = serif_b(14)
    f_deck = serif(11)
    f_src = sans(8)
    f_date = sans_b(8)
    for row in range(2):
        for col in range(5):
            i = row * 5 + col
            label, dateline, tag, head, deck, src = MEDIUM[i]
            x0 = MARGIN + col * (col_w + 8)
            x1 = x0 + col_w
            yy = y + row * row_h
            MEDIUM_PICS[i](d, (int(x0), yy, int(x1), yy + img_h))
            flab = sans_b(9)
            lw = flab.getlength(label) + 10
            d.rectangle([x0, yy, x0 + lw, yy + 15], fill=RED)
            d.text((x0 + 5, yy + 2), label, font=flab,
                   fill=(255, 255, 255))
            num = str(i + 4)
            fn = sans_b(11)
            d.ellipse([x1 - 22, yy + 4, x1 - 4, yy + 22], fill=NAVY)
            d.text((x1 - 22 + (18 - fn.getlength(num)) / 2, yy + 6), num,
                   font=fn, fill=(255, 255, 255))
            ty = yy + img_h + 4
            d.text((x0, ty), dateline, font=f_date, fill=RED)
            hy = ty + 15
            hlines = wrap(head, f_head, col_w)
            assert len(hlines) <= 2, f"medium headline overflow: {head}"
            hy = draw_wrapped(d, x0, hy, hlines, f_head, INK, 17)
            assert deck.endswith("."), f"medium deck must end with '.': {deck}"
            dlines = wrap(deck, f_deck, col_w)
            assert len(dlines) <= 2, f"medium deck overflow: {deck}"
            hy = draw_wrapped(d, x0, hy + 1, dlines, f_deck, INK, 14)
            d.text((x0, hy + 1), src, font=f_src, fill=GREY)
            # certainty chip right-aligned on the sources line: the
            # dateline alone is too long to share its line with a chip
            tag_chip(d, x1, hy, tag, 8)
    return y + 2 * row_h

# ------------------------------------------------------- also / bottom

def also_item_lines(num, region, head, src, max_w, size):
    """Lay one ALSO item into at most 2 lines.
    Line 1: 'N REGION: ' (bold) + headline words; ' · Source' (grey) at end.
    Returns list of segment lists; each segment is (text, font, fill)."""
    f_num = sans_b(size)
    f_reg = sans_b(size)
    f_txt = sans(size)
    f_src = sans(size)
    prefix = [(f"{num} ", f_num, RED), (f"{region}: ", f_reg, INK)]
    suffix = [(f" \u00b7 {src}", f_src, GREY)]
    words = head.split()
    # greedy wrap over segments
    lines = []
    cur = list(prefix)
    cur_w = sum(f.getlength(t) for t, f, _ in cur)
    idx = 0
    while idx < len(words):
        w = words[idx]
        ww = f_txt.getlength(w + " ")
        if cur_w + ww <= max_w or not any(t.strip() for t, _, _ in cur[2:]):
            cur.append((w + " ", f_txt, INK))
            cur_w += ww
            idx += 1
        else:
            lines.append(cur)
            cur = []
            cur_w = 0
            if len(lines) == 2:
                return None  # needs a third line: caller shrinks font
    # append source suffix to the last line if it fits, else own line
    suf_w = sum(f.getlength(t) for t, f, _ in suffix)
    if cur_w + suf_w <= max_w:
        cur.extend(suffix)
        lines.append(cur)
    else:
        lines.append(cur)
        if len(lines) == 2:
            return None
        lines.append(suffix)
    return lines


def draw_also(d, x, y, w, band_h):
    """Draw the ALSO list (2 columns). Returns the height used.
    Tries font sizes 11, 10.5, 10 until the content fits band_h."""
    header = "ALSO ON SUNDAY 22 NOVEMBER \u2014 23 MORE STORIES"
    fh = sans_b(13)
    d.text((x, y), header, font=fh, fill=RED)
    col_w = (w - 14) / 2
    top = y + 20
    avail = band_h - 20
    for size in (11, 10.5, 10):
        leading = size + 2.5
        left = ALSO[:12]
        right = ALSO[12:]
        ok = True
        col_lines = []
        for col in (left, right):
            lines = []
            for num, region, head, src in col:
                ls = also_item_lines(num, region, head, src, col_w, size)
                if ls is None:
                    ok = False
                    break
                lines.extend(ls)
            col_lines.append(lines)
            if not ok:
                break
        if not ok:
            continue
        need = max(len(col_lines[0]), len(col_lines[1])) * leading
        if need <= avail:
            for ci, lines in enumerate(col_lines):
                cx = x + ci * (col_w + 14)
                yy = top
                for segs in lines:
                    xx = cx
                    for t, f, fill in segs:
                        d.text((xx, yy), t, font=f, fill=fill)
                        xx += f.getlength(t)
                    yy += leading
            return top - y + need
    raise AssertionError("ALSO list does not fit the bottom band")


def draw_bottom_band(d, y, band_h):
    map_w = 250
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=sans_b(13), fill=RED)
    f_small = sans(8)
    note = "pins match story numbers"
    d.text((MARGIN + 152, y + 3), note, font=f_small, fill=GREY)
    draw_map(d, (MARGIN, y + 20, MARGIN + map_w, y + band_h), MAP_PINS)
    ax = MARGIN + map_w + 14
    aw = W - MARGIN - ax
    draw_also(d, ax, y, aw, band_h)
    return y + band_h


def date_check_height():
    f = sans(10)
    fl = sans_b(10)
    lw = fl.getlength("DATE CHECK") + 10
    max_w = W - 2 * MARGIN - 16
    body = DATE_CHECK[len("DATE CHECK \u2014 "):]
    lines = wrap(body, f, max_w - lw)
    return max(30, len(lines) * 13 + 10)


def draw_date_check(d, y):
    f = sans(10)
    max_w = W - 2 * MARGIN - 16
    # first line carries the red DATE CHECK label
    label = "DATE CHECK"
    fl = sans_b(10)
    lw = fl.getlength(label) + 10
    body = DATE_CHECK[len("DATE CHECK \u2014 "):]
    lines = wrap(body, f, max_w - lw)
    box_h = max(30, len(lines) * 13 + 10)
    d.rectangle([MARGIN, y, W - MARGIN, y + box_h], outline=RED, width=2)
    d.rectangle([MARGIN, y, MARGIN + lw, y + box_h], fill=RED)
    d.text((MARGIN + 5, y + box_h / 2 - 6), label, font=fl, fill=(255, 255, 255))
    yy = y + 5
    for ln in lines:
        d.text((MARGIN + lw + 6, yy), ln, font=f, fill=INK)
        yy += 13
    return y + box_h


def draw_footer(d, y):
    f = sans(10)
    legend = ("HOW TO READ THE TAGS \u2014 \u2713 CONFIRMED official / 2+ outlets \u00b7 "
              "REPORTED wires / one source \u00b7 CLAIM one party's claim, contested \u00b7 "
              "\u2713 ONGOING still developing")
    d.text((MARGIN, y), legend, font=f, fill=GREY)
    y += 16
    f2 = serif_b(15)
    t = "THE SUNDAY LEDGER \u00b7 SUNDAY 22 NOVEMBER 2026 \u00b7 36 STORIES \u00b7 7 REGIONS"
    d.text(((W - f2.getlength(t)) / 2, y), t, font=f2, fill=INK)
    y += 20
    f3 = sans(9)
    t2 = "Scenes are drawn illustrations of reported events, not photographs. Sources named beside each story."
    d.text(((W - f3.getlength(t2)) / 2, y), t2, font=f3, fill=GREY)
    return y + 14


# ---------------------------------------------------------------- main

def render():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = 0
    y = draw_top(d, y)                    # 20
    y = draw_masthead(d, y)               # 88
    y = draw_key_numbers(d, y)            # 50
    y = draw_region_strip(d, y)           # 20
    y = draw_utc_strip(d, y)              # 20
    # 198 so far; leads + medium must leave room for bottom band + checks
    y = draw_leads(d, y, 120)             # 240 -> 438
    y = draw_medium(d, y, 40)             # 272 -> 710
    dc_h = date_check_height()
    band_h = 1024 - y - 4 - dc_h - 2 - 50  # gaps + date check + footer
    assert band_h >= 190, f"bottom band too small: {band_h}"
    y = draw_bottom_band(d, y, band_h)
    y = draw_date_check(d, y + 4)
    y = draw_footer(d, y + 2)
    assert y <= H, f"page overflow: y={y}"
    return img


def main():
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img1 = render()
    img1.save(out, format="PNG")
    h1 = hashlib.sha256(open(out, "rb").read()).hexdigest()
    img2 = render()
    img2.save("/tmp/ni22-v6-render2.png", format="PNG")
    h2 = hashlib.sha256(open("/tmp/ni22-v6-render2.png", "rb").read()).hexdigest()
    assert img1.size == (1024, 1024), f"bad size {img1.size}"
    assert h1 == h2, f"non-deterministic render: {h1} != {h2}"
    print(f"entry.png {os.path.getsize(out)} bytes sha256 {h1} deterministic OK")


if __name__ == "__main__":
    main()
