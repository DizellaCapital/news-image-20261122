#!/usr/bin/env python3
"""v4 renderer — news-image-20261122 front page, 1024x1024.

Written fresh in this session. Renders the Sunday 22 November 2026
front page ("THE SUNDAY LEDGER") from the story data below, as a
single deterministic PNG. No external assets: all art is drawn with
PIL primitives, all text set in DejaVu.

Layout (1024x1024, cream paper):
  navy kicker band | giant date masthead | red sub-headline |
  key-numbers strip | region chips | THE DAY IN UTC timeline |
  3 lead stories | 10 pictured cards | world map + briefs |
  DATE CHECK | certainty legend | footer
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 241, 222)
INK = (26, 26, 26)
RED = (176, 30, 36)
NAVY = (20, 33, 61)
MUTED = (107, 101, 88)
LIGHT_LINE = (180, 172, 150)
MAP_SEA = (220, 233, 238)
MAP_LAND = (201, 214, 168)
WHITE = (255, 255, 255)
GREEN = (46, 125, 91)
AMBER = (176, 120, 20)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, fnt, fill=INK, leading=None, align="left", box_w=None):
    """Draw lines; returns y after the last line."""
    lh = leading or int(fnt.size * 1.22)
    for ln in lines:
        if align == "center":
            tw = d.textlength(ln, font=fnt)
            d.text((x + (box_w - tw) / 2, y), ln, font=fnt, fill=fill)
        else:
            d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def chip(d, x, y, w, h, label, bg, fg=WHITE, fnt=None):
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg)
    tw = d.textlength(label, font=fnt)
    d.text((x + (w - tw) / 2, y + (h - fnt.size) / 2 - 1), label, font=fnt, fill=fg)


# ---------------------------------------------------------------- story data
# status: CONFIRMED = official / 2+ outlets; REPORTED = wires / one source;
# CLAIM = one party's contested claim; PENDING = not settled yet.
LEADS = [
    dict(n=1, place="ANTALYA, TÜRKIYE", cat="CLIMATE", status="ONGOING",
         kicker="COP31: NO DEAL YET",
         head="COP31 deadlock deepens into Sunday",
         summ="No deal in Antalya as the draft drops every fossil-fuel mention; the $120bn adaptation target is gone and the finish is expected late tonight.",
         src="Health Policy Watch · Carbon Brief", art="cop31"),
    dict(n=2, place="KYIV REGION, UKRAINE", cat="WAR", status="CONFIRMED",
         kicker="186 DRONES OVERNIGHT",
         head="Russia fires 186 drones at Ukraine",
         summ="Air defences down or jam 161 of 186 strike drones; a five-storey block in Dymer is hit, seven feared trapped.",
         src="Ukrainian Air Force · Reuters", art="drones"),
    dict(n=3, place="MANAMA, BAHRAIN", cat="IRAN WAR", status="CLAIM",
         kicker="CLAIM VS DENIAL",
         head="Iran claims two US radars hit; Bahrain denies it",
         summ="The IRGC says it destroyed two Patriot radars; Bahrain says a civilian industrial site burned, no casualties.",
         src="IRGC · Bahrain Interior Ministry", art="radar"),
]

CARDS = [
    dict(n=4, place="STRAIT OF HORMUZ", cat="WAR", status="REPORTED",
         kicker="TANKER HIT", head="Tankers hit off Oman as Gulf tensions surge",
         summ="ADNOC vessel struck; one crew member missing, eleven injured.",
         src="Reuters · AP", art="tanker"),
    dict(n=5, place="KYIV, UKRAINE", cat="WAR", status="REPORTED",
         kicker="BRIDGES HIT", head="Russia strikes three Kyiv bridges",
         summ="Moscow answers the Crimea bridge attacks; spans hit overnight.",
         src="Reuters · Kyiv Independent", art="bridges"),
    dict(n=6, place="GULF OF FINLAND", cat="WAR", status="REPORTED",
         kicker="SHIP ABLAZE", head="Drones hit Russian cargo ship in the Baltic",
         summ="Finland tightens security after the strike; Kyiv is seen as likely behind it.",
         src="Finnish Forces · Times of India", art="ship"),
    dict(n=7, place="TALLINN, ESTONIA", cat="SECURITY", status="CONFIRMED",
         kicker="1 DEC", head="Estonia to shut its border with Russia",
         summ="Tallinn moves to close the frontier; Moscow denounces a 'new Iron Curtain'.",
         src="Reuters · AP", art="fence"),
    dict(n=8, place="HONG KONG", cat="ELECTIONS", status="CONFIRMED",
         kicker="98.79% TURNOUT", head="Hong Kong elects its Election Committee",
         summ="856 candidates chase 723 seats; turnout 98.79% by 5 pm.",
         src="HK Government · China Daily", art="ballot"),
    dict(n=9, place="LAS VEGAS", cat="FORMULA 1", status="CONFIRMED",
         kicker="VERSTAPPEN WINS", head="Verstappen wins the Las Vegas GP",
         summ="Beats Norris by 0.639s; Russell joins him on the podium.",
         src="FIA · Formula1.com", art="f1"),
    dict(n=10, place="WELLINGTON", cat="CRICKET", status="CONFIRMED",
         kicker="124 NOT OUT", head="Rahul 124 not out in Wellington",
         summ="India 344 for 2 replying to New Zealand's 368 as the Test heads into day three.",
         src="AFP", art="cricket"),
    dict(n=11, place="SINALOA, MEXICO", cat="CARTELS", status="REPORTED",
         kicker="CAPTURED", head="El Chapo Isidro captured; Sinaloa erupts",
         summ="Army seizes cartel kingpin Fausto Isidro Meza Flores; 11 killed in the backlash.",
         src="Reuters · AP", art="convoy"),
    dict(n=12, place="BRASÍLIA", cat="HEALTH", status="CONFIRMED",
         kicker="IN INTENSIVE CARE", head="Bolsonaro taken to intensive care",
         summ="Brazil's jailed ex-president admitted to ICU with an acute bowel obstruction.",
         src="Reuters · AP", art="hospital"),
    dict(n=13, place="AUSTRALIA", cat="CRICKET", status="CONFIRMED",
         kicker="T20 STREAK ENDS", head="Australia ends England's T20 streak",
         summ="England's seven-match winning run in T20 cricket is broken in Australia.",
         src="ABC · Reuters", art="t20"),
]

BRIEFS = [
    (14, "World Court: Myanmar committed genocide", "ICJ · Reuters"),
    (15, "Gaza aid-vehicle strike kills three", "Reuters"),
    (16, "Denmark expels Russian diplomat", "Al Jazeera"),
    (17, "FBI probes apparent database hack", "Reuters · AP"),
    (18, "Trump threatens overseas AI-centre ban", "Reuters"),
    (19, "Melania Trump seeks Christmas ceasefire", "AP"),
    (20, "Denmark ratifies US Greenland deal 109-0", "Reuters"),
    (21, "North Korea expands Yongbyon plant", "IAEA"),
    (22, "Bangladesh violence before Hasina return", "Reuters"),
    (23, "US signs new Venezuela military deal", "Reuters"),
    (24, "Nepal PM to meet Modi in New Delhi", "PTI"),
    (25, "South Africa votes in local elections", "Reuters"),
    (26, "Mamdani plans to close Rikers Island", "AP"),
    (27, "Davao jet inquiry opens; all 146 safe", "CAAP · AP"),
    (28, "700,000 displaced around Moyale", "UN OCHA"),
    (29, "Cyclone Akvan cancels 14 Ranchi flights", "PTI"),
    (30, "Japan to train live-fire in India", "Reuters"),
    (31, "Modi opens Nitish Setu bridge in Bihar", "PTI"),
    (32, "Cummins keeps Australia Test captaincy", "Cricket Australia"),
    (33, "AI may have cracked a famous maths problem", "ABC · CLAIM"),
    (34, "Trafalgar tree leaves Oslo for London", "BBC"),
    (35, "Alcaraz v Zverev in ATP Finals final", "ATP"),
    (36, "Wembanyama scores 50 as Spurs roll on", "AP · Reuters"),
]

NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed by air defence"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record total in NZ"),
    ("98.79%", "Hong Kong turnout by 5 pm"),
]

REGIONS = [
    ("EUROPE", 9, (31, 78, 121)),
    ("MIDDLE EAST", 3, (139, 30, 30)),
    ("ASIA-PACIFIC", 8, (46, 125, 91)),
    ("AMERICAS", 9, (107, 58, 140)),
    ("AFRICA", 2, (140, 106, 31)),
    ("OCEANIA", 3, (46, 107, 140)),
    ("WORLD", 2, (74, 74, 74)),
]

UTC_EVENTS = [
    ("01:00", "HK polls open"),
    ("03:00", "COP31 objections"),
    ("05:11", "Hamas seeks talks"),
    ("05:30", "Verstappen wins"),
    ("06:00", "COP31 session"),
    ("10:00", "HK polls close"),
    ("17:00", "ATP final"),
]

DATE_CHECK_LEFT_OUT = [
    "Peru quake (Fri 20 Nov)",
    "Russia's 400-drone barrage (19–20 Nov)",
    "Shenzhen summit (Thu 19 Nov)",
    "Anthropic $81.3bn IPO (Thu 19 Nov)",
    "UK-EU reset deal agreed (Fri 20 Nov)",
    "Mongolia president quits (Fri 20 Nov)",
    "Bayelsa boat capsize (Fri 20 Nov)",
    "Kryvyi Rih double-tap strike (Fri 20 Nov)",
]

# (story n, lon, lat) for the map pins
PINS = [
    (1, 30.7, 36.9), (2, 30.5, 50.4), (3, 50.6, 26.2), (4, 56.5, 27.0),
    (5, 34.5, 48.5), (6, 22.0, 60.0), (7, 27.5, 58.0), (8, 114.2, 22.3),
    (9, -115.1, 36.2), (10, 174.8, -41.3), (11, -107.4, 24.8),
    (12, -47.9, -15.8), (13, 151.2, -33.9),
]

STATUS_FILL = {
    "CONFIRMED": (30, 110, 70),
    "REPORTED": (31, 78, 121),
    "CLAIM": (176, 120, 20),
    "PENDING": (120, 90, 20),
    "ONGOING": (139, 30, 30),
}


# ---------------------------------------------------------------- illustrations
# Each takes (d, x, y, w, h) and draws a flat scene inside that box.
# All coordinates are fractions of w/h so leads and cards share them.

def _sky(d, x, y, w, h, top, bot):
    for i in range(int(h)):
        t = i / max(1, int(h) - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)


def art_cop31(d, x, y, w, h):
    _sky(d, x, y, w, h, (44, 62, 92), (120, 130, 150))
    d.ellipse([x + w * 0.78, y + h * 0.08, x + w * 0.90, y + h * 0.08 + w * 0.12], outline=(247, 241, 222), width=max(2, int(w * 0.015)))
    d.line([x + w * 0.84, y + h * 0.08 + w * 0.06, x + w * 0.84, y + h * 0.08 + w * 0.02], fill=(247, 241, 222), width=max(2, int(w * 0.012)))
    d.line([x + w * 0.84, y + h * 0.08 + w * 0.06, x + w * 0.88, y + h * 0.08 + w * 0.06], fill=(247, 241, 222), width=max(2, int(w * 0.012)))
    # plenary dome + desks
    d.pieslice([x + w * 0.06, y + h * 0.30, x + w * 0.46, y + h * 0.95], 180, 360, fill=(214, 190, 130))
    for i in range(5):
        cx = x + w * (0.10 + i * 0.07)
        d.ellipse([cx, y + h * 0.62, cx + w * 0.035, y + h * 0.62 + w * 0.035], fill=(176, 30, 36))
        d.rectangle([cx - w * 0.01, y + h * 0.70, cx + w * 0.045, y + h * 0.78], fill=(90, 70, 50))
    d.rectangle([x + w * 0.55, y + h * 0.55, x + w * 0.95, y + h * 0.92], fill=(247, 241, 222))
    d.rectangle([x + w * 0.55, y + h * 0.55, x + w * 0.95, y + h * 0.62], fill=(176, 30, 36))
    d.text((x + w * 0.58, y + h * 0.66), "NO FOSSIL", font=font(SANS_B, max(8, int(w * 0.055))), fill=(176, 30, 36))
    d.text((x + w * 0.58, y + h * 0.66 + int(w * 0.07)), "FUELS", font=font(SANS_B, max(8, int(w * 0.055))), fill=(176, 30, 36))


def art_drones(d, x, y, w, h):
    _sky(d, x, y, w, h, (10, 14, 34), (40, 52, 90))
    import random
    rnd = random.Random(7)
    for _ in range(14):
        sx, sy = x + rnd.random() * w, y + rnd.random() * h * 0.5
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 240, 180))
    # buildings with lit windows
    for i, bw in enumerate([0.16, 0.22, 0.14, 0.20]):
        bx = x + w * (0.04 + i * 0.24)
        bh = h * (0.45 + (i % 2) * 0.2)
        d.rectangle([bx, y + h - bh, bx + w * bw, y + h], fill=(24, 28, 48))
        for wy in range(3):
            for wx in range(2):
                if (i + wy + wx) % 2 == 0:
                    d.rectangle([bx + w * 0.03 + wx * w * 0.08, y + h - bh + 6 + wy * 12,
                                 bx + w * 0.06 + wx * w * 0.08, y + h - bh + 12 + wy * 12], fill=(255, 210, 90))
    # drones
    for dx, dy in [(0.55, 0.22), (0.72, 0.32), (0.85, 0.18)]:
        cx, cy = x + w * dx, y + h * dy
        d.line([cx - 8, cy, cx + 8, cy], fill=(255, 200, 80), width=2)
        d.line([cx, cy - 5, cx, cy + 5], fill=(255, 200, 80), width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 200, 80))
    # explosion flash
    fx, fy = x + w * 0.68, y + h * 0.62
    d.polygon([(fx, fy - 14), (fx + 6, fy - 4), (fx + 15, fy), (fx + 5, fy + 5), (fx + 2, fy + 14),
               (fx - 4, fy + 5), (fx - 14, fy + 2), (fx - 6, fy - 6)], fill=(255, 170, 40))


def art_radar(d, x, y, w, h):
    _sky(d, x, y, w, h, (16, 22, 48), (70, 80, 110))
    d.ellipse([x + w * 0.72, y + h * 0.06, x + w * 0.86, y + h * 0.06 + w * 0.14], fill=(240, 230, 200))
    # sea
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(28, 60, 90))
    # radar dishes
    for rx in (0.18, 0.48):
        bx = x + w * rx
        d.line([bx, y + h * 0.72, bx, y + h * 0.45], fill=(200, 200, 200), width=max(2, int(w * 0.012)))
        d.pieslice([bx - w * 0.11, y + h * 0.28, bx + w * 0.11, y + h * 0.28 + w * 0.22], 180, 360, fill=(220, 220, 220))
        d.line([bx - w * 0.11, y + h * 0.42, bx + w * 0.11, y + h * 0.42], fill=(160, 160, 160), width=2)
    # flames
    for fx in (0.30, 0.68):
        cx = x + w * fx
        d.polygon([(cx, y + h * 0.42), (cx + w * 0.05, y + h * 0.58), (cx, y + h * 0.70), (cx - w * 0.05, y + h * 0.58)], fill=(255, 140, 30))


def art_tanker(d, x, y, w, h):
    _sky(d, x, y, w, h, (120, 150, 180), (210, 205, 180))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(40, 90, 120))
    # hull + containers
    d.polygon([(x + w * 0.05, y + h * 0.62), (x + w * 0.95, y + h * 0.62), (x + w * 0.88, y + h * 0.78), (x + w * 0.12, y + h * 0.78)], fill=(90, 40, 40))
    for i, col in enumerate([(176, 30, 36), (46, 125, 91), (31, 78, 121), (220, 170, 40)]):
        d.rectangle([x + w * (0.14 + i * 0.17), y + h * 0.42, x + w * (0.28 + i * 0.17), y + h * 0.60], fill=col)
    d.rectangle([x + w * 0.82, y + h * 0.34, x + w * 0.92, y + h * 0.60], fill=(240, 240, 240))
    # smoke plume (kept inside the box: diagonal drift, radii relative to h)
    for i in range(4):
        r = h * (0.08 + i * 0.02)
        cx = x + w * (0.58 + i * 0.02)
        cy = y + h * (0.30 - i * 0.03)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 90, 95))


def art_bridges(d, x, y, w, h):
    _sky(d, x, y, w, h, (12, 18, 44), (60, 70, 110))
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(20, 40, 70))
    # bridge spans
    for bx in (0.05, 0.38, 0.70):
        d.arc([x + w * bx, y + h * 0.45, x + w * (bx + 0.26), y + h * 0.95], 180, 360, fill=(220, 220, 220), width=max(2, int(w * 0.012)))
        d.line([x + w * bx, y + h * 0.72, x + w * (bx + 0.26), y + h * 0.72], fill=(220, 220, 220), width=max(2, int(w * 0.012)))
    # flashes
    for fx, fy in [(0.30, 0.30), (0.62, 0.22), (0.85, 0.35)]:
        cx, cy = x + w * fx, y + h * fy
        d.polygon([(cx, cy - 10), (cx + 4, cy - 3), (cx + 10, cy), (cx + 3, cy + 4), (cx, cy + 10),
                   (cx - 4, cy + 3), (cx - 10, cy), (cx - 3, cy - 4)], fill=(255, 200, 60))


def art_ship(d, x, y, w, h):
    _sky(d, x, y, w, h, (140, 160, 180), (210, 215, 200))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(50, 100, 130))
    d.polygon([(x + w * 0.10, y + h * 0.60), (x + w * 0.90, y + h * 0.60), (x + w * 0.82, y + h * 0.76), (x + w * 0.18, y + h * 0.76)], fill=(70, 70, 80))
    for i, col in enumerate([(176, 30, 36), (220, 170, 40), (46, 125, 91)]):
        d.rectangle([x + w * (0.22 + i * 0.18), y + h * 0.44, x + w * (0.36 + i * 0.18), y + h * 0.58], fill=col)
    # fire on deck
    d.polygon([(x + w * 0.70, y + h * 0.30), (x + w * 0.75, y + h * 0.44), (x + w * 0.70, y + h * 0.56), (x + w * 0.65, y + h * 0.44)], fill=(255, 140, 30))
    d.ellipse([x + w * 0.66, y + h * 0.18, x + w * 0.74, y + h * 0.18 + w * 0.08], fill=(90, 90, 95))
    # drone above
    cx, cy = x + w * 0.45, y + h * 0.20
    d.line([cx - 7, cy, cx + 7, cy], fill=(40, 40, 40), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(40, 40, 40))


def art_fence(d, x, y, w, h):
    _sky(d, x, y, w, h, (150, 170, 190), (215, 210, 190))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(140, 160, 120))
    # fence posts + wire
    for i in range(7):
        px = x + w * (0.06 + i * 0.15)
        d.line([px, y + h * 0.30, px, y + h * 0.78], fill=(60, 60, 60), width=max(2, int(w * 0.012)))
    for wy in (0.38, 0.52, 0.66):
        d.line([x, y + h * wy, x + w, y + h * wy], fill=(60, 60, 60), width=1)
    # Estonian flag (blue-black-white) left, Russian flag (white-blue-red) right
    for fx, cols in [(0.10, [(0, 90, 170), (0, 0, 0), (255, 255, 255)]), (0.68, [(255, 255, 255), (0, 60, 160), (200, 30, 30)])]:
        for j, col in enumerate(cols):
            d.rectangle([x + w * fx, y + h * (0.10 + j * 0.05), x + w * (fx + 0.20), y + h * (0.15 + j * 0.05)], fill=col)
        d.line([x + w * fx, y + h * 0.10, x + w * fx, y + h * 0.30], fill=(60, 60, 60), width=2)


def art_ballot(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 210, 220), (235, 230, 215))
    # skyline
    for i, bh in enumerate([0.35, 0.55, 0.42, 0.62, 0.38]):
        bx = x + w * (0.04 + i * 0.19)
        d.rectangle([bx, y + h * (0.85 - bh), bx + w * 0.15, y + h * 0.85], fill=(90, 100, 120))
    # ballot box
    d.rectangle([x + w * 0.32, y + h * 0.48, x + w * 0.68, y + h * 0.88], fill=(176, 30, 36))
    d.rectangle([x + w * 0.28, y + h * 0.42, x + w * 0.72, y + h * 0.50], fill=(139, 30, 30))
    d.rectangle([x + w * 0.44, y + h * 0.44, x + w * 0.56, y + h * 0.48], fill=(247, 241, 222))
    # ballot paper + check
    d.rectangle([x + w * 0.72, y + h * 0.18, x + w * 0.94, y + h * 0.46], fill=(255, 255, 255))
    d.line([x + w * 0.75, y + h * 0.36, x + w * 0.80, y + h * 0.42, x + w * 0.91, y + h * 0.22], fill=(30, 110, 70), width=max(2, int(w * 0.02)))


def art_f1(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 30, 60), (90, 40, 90))
    # track
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(50, 50, 55))
    d.line([x, y + h * 0.72, x + w, y + h * 0.72], fill=(255, 255, 255), width=2)
    # car body
    d.polygon([(x + w * 0.10, y + h * 0.62), (x + w * 0.30, y + h * 0.50), (x + w * 0.70, y + h * 0.50),
               (x + w * 0.88, y + h * 0.60), (x + w * 0.85, y + h * 0.66), (x + w * 0.12, y + h * 0.66)], fill=(176, 30, 36))
    d.rectangle([x + w * 0.82, y + h * 0.38, x + w * 0.92, y + h * 0.52], fill=(20, 20, 20))
    wd = h * 0.20
    d.ellipse([x + w * 0.22, y + h * 0.60, x + w * 0.22 + wd, y + h * 0.60 + wd], fill=(15, 15, 15))
    d.ellipse([x + w * 0.66, y + h * 0.60, x + w * 0.66 + wd, y + h * 0.60 + wd], fill=(15, 15, 15))
    # chequered flag
    for i in range(4):
        for j in range(3):
            col = (20, 20, 20) if (i + j) % 2 == 0 else (255, 255, 255)
            d.rectangle([x + w * (0.06 + i * 0.045), y + h * (0.08 + j * 0.07), x + w * (0.105 + i * 0.045), y + h * (0.15 + j * 0.07)], fill=col)
    d.line([x + w * 0.06, y + h * 0.08, x + w * 0.06, y + h * 0.34], fill=(20, 20, 20), width=2)


def art_cricket(d, x, y, w, h):
    _sky(d, x, y, w, h, (140, 190, 150), (210, 225, 190))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(90, 140, 80))
    d.rectangle([x + w * 0.10, y + h * 0.68, x + w * 0.90, y + h * 0.92], fill=(190, 170, 120))
    # stumps
    for sx in (0.68, 0.72, 0.76):
        d.line([x + w * sx, y + h * 0.42, x + w * sx, y + h * 0.62], fill=(220, 180, 60), width=max(2, int(w * 0.012)))
    # batsman + bat
    d.ellipse([x + w * 0.42, y + h * 0.30, x + w * 0.50, y + h * 0.30 + w * 0.08], fill=(40, 40, 40))
    d.rectangle([x + w * 0.43, y + h * 0.42, x + w * 0.49, y + h * 0.62], fill=(20, 90, 160))
    d.line([x + w * 0.50, y + h * 0.44, x + w * 0.62, y + h * 0.62], fill=(200, 160, 100), width=max(3, int(w * 0.02)))
    # ball
    d.ellipse([x + w * 0.78, y + h * 0.55, x + w * 0.78 + w * 0.05, y + h * 0.55 + w * 0.05], fill=(176, 30, 36))


def art_convoy(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 170, 120), (225, 205, 160))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(120, 110, 95))
    # buildings
    for i, bh in enumerate([0.30, 0.42, 0.34]):
        bx = x + w * (0.05 + i * 0.30)
        d.rectangle([bx, y + h * (0.66 - bh), bx + w * 0.24, y + h * 0.66], fill=(160, 120, 80))
    # trucks
    for tx in (0.12, 0.52):
        d.rectangle([x + w * tx, y + h * 0.50, x + w * (tx + 0.30), y + h * 0.66], fill=(60, 90, 50))
        d.rectangle([x + w * (tx + 0.22), y + h * 0.44, x + w * (tx + 0.30), y + h * 0.52], fill=(60, 90, 50))
        d.ellipse([x + w * (tx + 0.05), y + h * 0.62, x + w * (tx + 0.11), y + h * 0.62 + w * 0.06], fill=(20, 20, 20))
        d.ellipse([x + w * (tx + 0.20), y + h * 0.62, x + w * (tx + 0.26), y + h * 0.62 + w * 0.06], fill=(20, 20, 20))


def art_hospital(d, x, y, w, h):
    _sky(d, x, y, w, h, (170, 200, 210), (225, 230, 225))
    d.rectangle([x + w * 0.10, y + h * 0.28, x + w * 0.90, y + h * 0.88], fill=(240, 240, 235))
    d.rectangle([x + w * 0.10, y + h * 0.28, x + w * 0.90, y + h * 0.36], fill=(31, 78, 121))
    # cross
    cx, cy = x + w * 0.50, y + h * 0.50
    d.rectangle([cx - w * 0.02, cy - h * 0.10, cx + w * 0.02, cy + h * 0.10], fill=(176, 30, 36))
    d.rectangle([cx - w * 0.06, cy - h * 0.03, cx + w * 0.06, cy + h * 0.03], fill=(176, 30, 36))
    # monitor line
    d.line([x + w * 0.14, y + h * 0.76, x + w * 0.30, y + h * 0.76, x + w * 0.36, y + h * 0.66,
            x + w * 0.44, y + h * 0.84, x + w * 0.52, y + h * 0.76, x + w * 0.86, y + h * 0.76],
           fill=(30, 110, 70), width=max(2, int(w * 0.012)))


def art_t20(d, x, y, w, h):
    _sky(d, x, y, w, h, (60, 90, 140), (140, 170, 200))
    d.rectangle([x, y + h * 0.60, x + w, y + h], fill=(90, 140, 80))
    # stadium stands
    d.rectangle([x, y + h * 0.30, x + w, y + h * 0.60], fill=(80, 80, 100))
    for i in range(10):
        d.ellipse([x + w * (0.05 + i * 0.09), y + h * 0.38, x + w * (0.08 + i * 0.09), y + h * 0.38 + w * 0.03],
                  fill=(220, 200, 160) if i % 2 else (200, 80, 80))
    # stumps + ball
    for sx in (0.44, 0.48, 0.52):
        d.line([x + w * sx, y + h * 0.44, x + w * sx, y + h * 0.60], fill=(220, 180, 60), width=max(2, int(w * 0.012)))
    d.ellipse([x + w * 0.70, y + h * 0.30, x + w * 0.70 + w * 0.06, y + h * 0.30 + w * 0.06], fill=(176, 30, 36))


ART = {
    "cop31": art_cop31, "drones": art_drones, "radar": art_radar,
    "tanker": art_tanker, "bridges": art_bridges, "ship": art_ship,
    "fence": art_fence, "ballot": art_ballot, "f1": art_f1,
    "cricket": art_cricket, "convoy": art_convoy, "hospital": art_hospital,
    "t20": art_t20,
}

# Rough continent outlines in (lon, lat), drawn equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66), (-80, 62),
     (-76, 58), (-70, 58), (-65, 60), (-60, 52), (-55, 47), (-70, 44), (-75, 39),
     (-80, 32), (-84, 30), (-90, 21), (-97, 26), (-105, 20), (-110, 23), (-117, 33),
     (-125, 40), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
    # South America
    [(-79, 9), (-72, 12), (-62, 9), (-52, 5), (-44, -3), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -41), (-70, -52), (-74, -44), (-73, -30),
     (-70, -18), (-77, -12), (-81, -5), (-80, 1)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59), (18, 56),
     (21, 55), (24, 58), (28, 60), (30, 62), (32, 70), (40, 68), (44, 68), (40, 60),
     (38, 52), (36, 46), (30, 46), (28, 44), (23, 40), (19, 42), (12, 44), (8, 44),
     (3, 43), (-2, 37)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12), (51, 11), (48, 2),
     (41, -4), (36, -18), (32, -26), (26, -34), (19, -35), (16, -28), (12, -18),
     (13, -10), (9, 4), (-8, 5), (-15, 12), (-17, 15)],
    # Asia
    [(32, 70), (45, 68), (60, 69), (75, 72), (90, 75), (105, 77), (120, 73),
     (135, 72), (150, 70), (160, 66), (162, 60), (158, 53), (142, 50), (140, 40),
     (130, 38), (122, 32), (120, 25), (110, 20), (105, 10), (100, 8), (95, 16),
     (90, 22), (80, 15), (76, 8), (72, 20), (66, 25), (58, 25), (52, 26),
     (48, 29), (44, 29), (40, 32), (36, 36), (33, 42), (30, 46), (28, 52),
     (25, 60), (22, 66)],
    # Australia
    [(114, -22), (122, -14), (132, -12), (137, -15), (142, -11), (146, -19),
     (150, -23), (153, -27), (150, -37), (146, -39), (140, -38), (135, -35),
     (130, -32), (124, -33), (118, -35), (114, -31)],
]


def draw_map(d, x, y, w, h):
    """Equirectangular world map; returns pin positions in px."""
    d.rectangle([x, y, x + w, y + h], fill=MAP_SEA)
    for poly in CONTINENTS:
        pts = []
        for lon, lat in poly:
            px = x + (lon + 180) / 360.0 * w
            py = y + (90 - lat) / 180.0 * h
            pts.append((px, py))
        d.polygon(pts, fill=MAP_LAND, outline=(160, 175, 130))
    pins = {}
    for n, lon, lat in PINS:
        px = x + (lon + 180) / 360.0 * w
        py = y + (90 - lat) / 180.0 * h
        pins[n] = (px, py)
    return pins


def draw_pin(d, px, py, n, r=8):
    d.ellipse([px - r, py - r, px + r, py + r], fill=RED, outline=WHITE, width=1)
    fnt = font(SANS_B, 10)
    tw = d.textlength(str(n), font=fnt)
    d.text((px - tw / 2, py - 5), str(n), font=fnt, fill=WHITE)


# ---------------------------------------------------------------- layout

def section_rule(d, y):
    d.line([(6, y), (W - 6, y)], fill=INK, width=2)


def status_tag(d, x, y, status):
    """Small filled tag; returns width used."""
    fnt = font(SANS_B, 9)
    label = "✓ " + status if status in ("CONFIRMED", "ONGOING") else status
    tw = d.textlength(label, font=fnt)
    w_ = tw + 10
    d.rounded_rectangle([x, y, x + w_, y + 14], radius=3, fill=STATUS_FILL[status])
    d.text((x + 5, y + 2), label, font=fnt, fill=WHITE)
    return w_


def draw_lead(d, s, x, y, w, h):
    ART[s["art"]](d, x, y, w, 132)
    # kicker banner on the illustration, top-left
    kf = font(SANS_B, 11)
    kw = d.textlength(s["kicker"], font=kf) + 12
    d.rectangle([x, y, x + kw, y + 19], fill=RED)
    d.text((x + 6, y + 3), s["kicker"], font=kf, fill=WHITE)
    # number badge, top-right of illustration
    nb = font(SANS_B, 12)
    d.ellipse([x + w - 26, y + 4, x + w - 4, y + 26], fill=NAVY)
    tw = d.textlength(str(s["n"]), font=nb)
    d.text((x + w - 15 - tw / 2, y + 8), str(s["n"]), font=nb, fill=WHITE)
    cy = y + 138
    # place + status tag
    pf = font(SANS_B, 11)
    d.text((x, cy), f"{s['n']} · {s['place']} · {s['cat']}", font=pf, fill=RED)
    status_tag(d, x + w - 92, cy - 1, s["status"])
    cy += 18
    # headline (max 3 lines)
    hf = font(SERIF_B, 20)
    lines = wrap(d, s["head"], hf, w)[:3]
    cy = text_lines(d, x, cy, lines, hf, leading=23)
    cy += 3
    # summary (2 lines)
    sf = font(SERIF, 12)
    slines = wrap(d, s["summ"], sf, w)[:2]
    cy = text_lines(d, x, cy, slines, sf, leading=15)
    # source, bottom of card
    d.text((x, y + h - 14), "Sources: " + s["src"], font=font(SANS, 9), fill=MUTED)


def draw_card(d, s, x, y, w, h):
    ART[s["art"]](d, x, y, w, 50)
    kf = font(SANS_B, 8)
    kw = d.textlength(s["kicker"], font=kf) + 8
    d.rectangle([x, y, x + kw, y + 13], fill=RED)
    d.text((x + 4, y + 2), s["kicker"], font=kf, fill=WHITE)
    nb = font(SANS_B, 9)
    d.ellipse([x + w - 18, y + 2, x + w - 2, y + 18], fill=NAVY)
    tw = d.textlength(str(s["n"]), font=nb)
    d.text((x + w - 10 - tw / 2, y + 5), str(s["n"]), font=nb, fill=WHITE)
    cy = y + 54
    pf = font(SANS_B, 8)
    d.text((x, cy), f"{s['place']} · {s['cat']}", font=pf, fill=RED)
    status_tag(d, x + w - 78, cy - 1, s["status"])
    cy += 12
    hf = font(SERIF_B, 12)
    lines = wrap(d, s["head"], hf, w)[:2]
    cy = text_lines(d, x, cy, lines, hf, leading=14)
    sf = font(SANS, 9)
    slines = wrap(d, s["summ"], sf, w)[:1]
    text_lines(d, x, cy + 1, slines, sf, leading=11)
    d.text((x, y + h - 10), s["src"], font=font(SANS, 8), fill=MUTED)


def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # navy kicker band
    d.rectangle([0, 0, W, 28], fill=NAVY)
    bf = font(SANS_B, 12)
    d.text((8, 7), "THE WORLD IN ONE DAY", font=bf, fill=WHITE)
    right = "36 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    rf = font(SANS_B, 11)
    d.text((W - 8 - d.textlength(right, font=rf), 8), right, font=rf, fill=WHITE)

    # masthead: the DATE is the giant headline
    mf = font(SERIF_B, 64)
    title = "Sunday 22 November 2026"
    tw = d.textlength(title, font=mf)
    d.text(((W - tw) / 2, 34), title, font=mf, fill=INK)
    # red sub-headline
    sh = "COP31 still without a deal  ·  186 drones over Ukraine overnight  ·  Iran claims US radars hit, Bahrain denies it"
    sf = font(SERIF, 17)
    d.text(((W - d.textlength(sh, font=sf)) / 2, 112), sh, font=sf, fill=RED)
    section_rule(d, 135)

    # key-numbers strip
    cell_w = (W - 12) // 6
    for i, (val, lab) in enumerate(NUMBERS):
        cx = 6 + i * cell_w
        if i:
            d.line([(cx, 143), (cx, 185)], fill=LIGHT_LINE, width=1)
        vf = font(SERIF_B, 30)
        d.text((cx + 8, 141), val, font=vf, fill=RED)
        lf = font(SANS, 10)
        for li, ln in enumerate(wrap(d, lab, lf, cell_w - 16)):
            d.text((cx + 8, 172 + li * 11), ln, font=lf, fill=MUTED)

    # region chips
    total_w = 0
    rf2 = font(SANS_B, 12)
    widths = []
    for name, cnt, _ in REGIONS:
        label = f"{name} {cnt}"
        widths.append(d.textlength(label, font=rf2) + 18)
    total_w = sum(widths) + 6 * (len(REGIONS) - 1)
    cx = (W - total_w) // 2
    for (name, cnt, col), w_ in zip(REGIONS, widths):
        chip(d, cx, 197, w_, 20, f"{name} {cnt}", col, fnt=rf2)
        cx += w_ + 6

    # THE DAY IN UTC timeline strip
    d.rectangle([6, 221, W - 6, 241], fill=(232, 226, 205))
    uf = font(SANS_B, 10)
    d.text((10, 227), "THE DAY IN UTC", font=uf, fill=NAVY)
    ux = 118
    ef = font(SANS, 10)
    for t, ev in UTC_EVENTS:
        d.ellipse([ux, 230, ux + 5, 235], fill=RED)
        label = f"{t} {ev}"
        d.text((ux + 8, 227), label, font=ef, fill=INK)
        ux += 8 + d.textlength(label, font=ef) + 10
    section_rule(d, 243)

    # 3 lead stories
    lead_w, lead_h, gap = 328, 252, 14
    for i, s in enumerate(LEADS):
        draw_lead(d, s, 6 + i * (lead_w + gap), 246, lead_w, lead_h)
    section_rule(d, 498)

    # 10 pictured cards, 2 rows x 5
    card_w, card_h, cgap, rgap = 196, 113, 8, 10
    for i, s in enumerate(CARDS):
        row, col = divmod(i, 5)
        draw_card(d, s, 6 + col * (card_w + cgap), 502 + row * (card_h + rgap), card_w, card_h)
    section_rule(d, 737)

    # bottom band: map (left) + briefs (right)
    d.text((6, 742), "WHERE IT HAPPENED", font=font(SANS_B, 12), fill=RED)
    d.text((180, 744), "pins match story numbers", font=font(SANS, 9), fill=MUTED)
    pins = draw_map(d, 6, 760, 470, 146)
    for n, (px, py) in pins.items():
        draw_pin(d, px, py, n)
    bx = 492
    d.text((bx, 742), "ALSO ON SUNDAY 22 NOVEMBER — 23 MORE STORIES", font=font(SANS_B, 12), fill=RED)
    bf2 = font(SANS, 10)
    bfb = font(SANS_B, 10)
    col_w = 258
    for i, (n, head, src) in enumerate(BRIEFS):
        col, row = divmod(i, 12)
        x0 = bx + col * (col_w + 8)
        y0 = 760 + row * 12
        d.text((x0, y0), f"{n}", font=bfb, fill=RED)
        d.text((x0 + 20, y0), head, font=bf2, fill=INK)
        # source in muted, only if it fits on the same line
        hw = d.textlength(head, font=bf2)
        sw = d.textlength(" · " + src, font=bf2)
        if 20 + hw + sw <= col_w:
            d.text((x0 + 20 + hw, y0), " · " + src, font=bf2, fill=MUTED)

    # DATE CHECK — lists ONLY stories NOT on the page
    d.rectangle([6, 910, W - 6, 962], outline=RED, width=2)
    d.text((12, 915), "DATE CHECK", font=font(SANS_B, 12), fill=RED)
    dcf = font(SANS, 11)
    dc = ("Wires read to 23:59 UTC, Sunday 22 Nov 2026. Every story above happened, or was first "
          "reported, on 22 Nov in at least one time zone. Left out as other days' news: " +
          " · ".join(DATE_CHECK_LEFT_OUT) + ".")
    text_lines(d, 12, 931, wrap(d, dc, dcf, W - 24), dcf, leading=13)

    # certainty legend
    ly = 970
    d.text((6, ly), "HOW TO READ THE TAGS —", font=font(SANS_B, 10), fill=INK)
    lx = 6 + d.textlength("HOW TO READ THE TAGS — ", font=font(SANS_B, 10))
    leg = [("CONFIRMED", "official / 2+ outlets"), ("REPORTED", "wires / one source"),
           ("CLAIM", "one party's claim, contested"), ("ONGOING", "still developing")]
    lf2 = font(SANS, 10)
    for status, desc in leg:
        wtag = status_tag(d, lx, ly - 1, status)
        d.text((lx + wtag + 4, ly), desc, font=lf2, fill=MUTED)
        lx += wtag + 4 + d.textlength(desc, font=lf2) + 18

    # footer
    ff = font(SANS_B, 11)
    foot = "THE SUNDAY LEDGER  ·  SUNDAY 22 NOVEMBER 2026  ·  36 STORIES, 7 REGIONS"
    d.text(((W - d.textlength(foot, font=ff)) / 2, 996), foot, font=ff, fill=INK)
    f2 = "Scenes are drawn illustrations of reported events, not photographs. Sources named beside each story."
    f2f = font(SANS, 9)
    d.text(((W - d.textlength(f2, font=f2f)) / 2, 1011), f2, font=f2f, fill=MUTED)

    return img


def main():
    img = render()
    assert img.size == (1024, 1024), img.size
    img.save("entry.png", format="PNG")
    h = hashlib.sha256(open("entry.png", "rb").read()).hexdigest()
    print("entry.png", img.size, "sha256", h)


if __name__ == "__main__":
    main()
