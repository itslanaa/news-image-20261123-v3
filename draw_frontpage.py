#!/usr/bin/env python3
"""The World in One Day - Monday 23 November 2026 (v3).
Fresh renderer, written from scratch for the round-3 entry.
Front page, 1024x1024 PNG, deterministic. All stories date-checked for
Monday 23 November 2026. Pictures and map are original, drawn in code.
v3 vs v2: bigger and richer lead illustrations, larger headlines, shorter
summaries (less cramped), more breathing room, a bigger map.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (245, 239, 224)
PAPER = (250, 246, 232)
INK = (26, 26, 26)
RED = (178, 34, 34)
DARKRED = (139, 0, 0)
BLUE = (70, 110, 160)
SKY = (183, 214, 232)
SEA = (140, 185, 210)
SAND = (232, 220, 180)
GREY = (120, 120, 120)
LIGHTGREY = (200, 200, 200)
YELLOW = (255, 215, 0)
ORANGE = (230, 120, 40)
GREEN = (90, 140, 80)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS_I = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    for cand in (path, F_SANS, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(cand, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, f, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def draw_flag(draw, x, y, w, h, stripes):
    """Simple horizontal tricolour flag."""
    n = len(stripes)
    for i, c in enumerate(stripes):
        draw.rectangle([x, y + i * h // n, x + w, y + (i + 1) * h // n], fill=c)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


# ---------------------------------------------------------------- stories
STATS = [
    ("153", "DRONES IN ONE NIGHT"),
    ("258", "HOUSE SEATS FOR DEMS"),
    ("3", "TANKERS ATTACKED SAT."),
    ("11", "KILLED IN DYMER"),
    ("99%", "OF GAZA CONTAMINATED"),
    ("429", "FLIGHTS CANCELLED"),
]

LEADS = [
    dict(
        n=1, place="BAHRAIN", topic="WAR AT SEA", status="REPORTED",
        head="Iran hits US bases as tankers burn",
        body="Tehran claims two Patriot radars hit at al-Riffa and Awali; Bahrain counts two hurt at a torched site; 3 tankers attacked on Saturday.",
        art="bahrain",
    ),
    dict(
        n=2, place="ANTALYA", topic="COP31", status="CONFIRMED",
        head="COP31 collapses \u2014 no deal as talks end",
        body="Delegates reject the Antalya Pact on Sunday; fossil fuels stripped from the draft; the first COP collapse since Copenhagen 2009.",
        art="cop31",
    ),
    dict(
        n=3, place="UKRAINE", topic="OVERNIGHT ASSAULT", status="REPORTED",
        head="Russia\u2019s 153-drone night kills 11",
        body="A five-storey block collapses near Kyiv; 14 still missing as rescuers dig. 134 of 153 downed by 08:00; a kindergarten hit in Kharkiv.",
        art="ukraine",
    ),
]

MIDS = [
    dict(n=4, place="BENGHAZI", topic="SEA DRONES", status="REPORTED",
         head="Ukraine\u2019s sea drones sink a Russian warship",
         body="Corvette Merkury sinks; a cargo ship hit too."),
    dict(n=5, place="WASHINGTON", topic="VOTE", status="CONFIRMED",
         head="Democrats take 258 House seats",
         body="Hubbard beats Foxx by 330 votes; 44 seats gained."),
    dict(n=6, place="SEOUL", topic="EXAM", status="CONFIRMED",
         head="Korea\u2019s education chief quits over AI cheating",
         body="Choi Kyo-jin resigns Sunday; 550,000 sat the exam."),
    dict(n=7, place="BRUSSELS", topic="STRIKE", status="CONFIRMED",
         head="Belgium stops: national strike grounds country",
         body="Airspace shut 07:00\u201321:00; 429 flights hit."),
    dict(n=8, place="GAZA", topic="WEST BANK", status="REPORTED",
         head="Three killed in Gaza food-truck strike",
         body="WCK: the truck was not ours. Eisenkot blames settlers."),
    dict(n=9, place="DHAKA", topic="RETURN", status="CONFIRMED",
         head="Hasina will be jailed if she returns",
         body="Ex-PM faces a death sentence; her party is banned."),
    dict(n=10, place="SINALOA", topic="CAPTURE", status="CONFIRMED",
         head="\u2018Chapo Isidro\u2019 captured in Mexico",
         body="FBI Top-10 fugitive taken Friday night."),
    dict(n=11, place="BELGRADE", topic="FLOOD", status="CONFIRMED",
         head="Belgrade floods after a month\u2019s rain",
         body="A month\u2019s rain in 12 hours; streets under water."),
    dict(n=12, place="COPENHAGEN", topic="PLOT", status="REPORTED",
         head="Denmark expels Russian attach\u00e9",
         body="Rapper Kv\u00edstor targeted; two charged."),
    dict(n=13, place="BARRANQUILLA", topic="SPORT", status="CONFIRMED",
         head="Paredes collapses live on TV",
         body="Boca beat Atl\u00e9tico Mineiro 2\u20130; 32\u00b0C heat."),
]

MORE = [
    ("KRYVYI RIH", "A child and a woman killed; 25 blocks damaged."),
    ("BRUSSELS", "NATO meets after Russian missiles land in Poland."),
    ("ROSTOV", "Ukrainian drones hit oil sites in Rostov."),
    ("GAZA", "Oxfam: war left toxic contamination across 99%."),
    ("INDONESIA", "Candy factory fire: 24 killed, dozens missing."),
    ("RICHMOND", "States sue SpaceX over Grok sexual deepfakes."),
    ("MENLO PARK", "Meta AI chief: superintelligence is arriving."),
    ("VYSHNEVE", "Shahed drone hits a supermarket; several hurt."),
    ("GAZA", "Two more Palestinians killed on Sunday."),
    ("MANAMA", "US official: no damage to US personnel in Bahrain."),
    ("ANTALYA", "COP31 one win: 90+ sign electrification pledge."),
    ("HORMUZ", "37 tankers pass, down from 52 \u2014 nearly a third."),
    ("RYLST", "Ukraine hits Rubicon drone unit; depot blows up."),
    ("BALTIC", "Russian cargo ship Sparta II burns after strike."),
    ("WASHINGTON", "Putin \u2018privately agreed\u2019 to NATO guarantees. [REPORTED]"),
    ("DAKAR", "CAS to rule Tuesday on Senegal AFCON appeal. [FORECAST]"),
    ("DNIPRO", "Russian drone guts a flat in a ten-storey block."),
    ("CHERKASY", "Nine Russian drones downed; no injuries."),
    ("IZYUM", "Drone hits a railway station; a train catches fire."),
    ("BELGRADE", "Weather chief arrested for money laundering."),
]


# ---------------------------------------------------------------- art
def art_bahrain(draw, x, y, w, h):
    """War at sea: grey warship left, burning tanker right, smoke, waves."""
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    # sun haze
    draw.ellipse([x + w - 52, y + 8, x + w - 18, y + 42], fill=(255, 200, 90))
    # sea
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=SEA)
    for i in range(5):
        wx = x + 12 + i * 62
        draw.arc([wx, y + h - 30, wx + 34, y + h - 14], 200, 340, fill=(255, 255, 255), width=2)
    # warship (left)
    sx, sy = x + 14, y + h - 52
    draw.polygon([(sx, sy + 26), (sx + 96, sy + 26), (sx + 86, sy + 12), (sx + 10, sy + 12)], fill=(110, 110, 110))
    draw.rectangle([sx + 22, sy - 6, sx + 52, sy + 12], fill=(90, 90, 90))
    draw.rectangle([sx + 30, sy - 18, sx + 34, sy - 6], fill=(70, 70, 70))
    draw.rectangle([sx + 58, sy + 2, sx + 78, sy + 12], fill=(70, 70, 70))
    # tanker (right) with fire
    tx, ty = x + w - 128, y + h - 56
    draw.polygon([(tx, ty + 30), (tx + 112, ty + 30), (tx + 102, ty + 14), (tx + 8, ty + 14)], fill=(150, 80, 40))
    draw.rectangle([tx + 18, ty - 2, tx + 34, ty + 14], fill=(120, 60, 30))
    draw.rectangle([tx + 70, ty - 2, tx + 86, ty + 14], fill=(120, 60, 30))
    # flames
    for fx, fh in [(tx + 22, 26), (tx + 52, 34), (tx + 76, 24)]:
        draw.polygon([(fx, ty - 2), (fx + 8, ty - fh), (fx + 16, ty - 2)], fill=ORANGE)
        draw.polygon([(fx + 4, ty - 2), (fx + 8, ty - fh + 12), (fx + 12, ty - 2)], fill=YELLOW)
    # smoke
    for cx, cy, r in [(tx + 26, ty - 30, 12), (tx + 44, ty - 44, 15), (tx + 66, ty - 34, 11), (tx + 82, ty - 48, 13)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(80, 80, 80))
    # drone silhouette
    draw.polygon([(x + w // 2 - 4, y + 12), (x + w // 2 + 22, y + 18), (x + w // 2 - 4, y + 24)], fill=INK)


def art_cop31(draw, x, y, w, h):
    """COP31: globe left, thermometer right, NO DEAL stamp."""
    draw.rectangle([x, y, x + w, y + h], fill=(235, 240, 228))
    cx, cy, r = x + 78, y + h // 2 + 4, 52
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE)
    # continents (stylised blobs)
    draw.ellipse([cx - 34, cy - 30, cx - 2, cy + 2], fill=GREEN)
    draw.ellipse([cx + 4, cy - 12, cx + 34, cy + 26], fill=GREEN)
    draw.ellipse([cx - 12, cy + 22, cx + 14, cy + 40], fill=GREEN)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    # crossed-out fossil fuels label
    f = font(F_SANS_B, 15)
    draw.text((x + 150, y + 18), "FOSSIL", font=f, fill=INK)
    draw.text((x + 150, y + 38), "FUELS", font=f, fill=INK)
    draw.line([x + 148, y + 30, x + 212, y + 26], fill=RED, width=3)
    draw.line([x + 148, y + 50, x + 212, y + 46], fill=RED, width=3)
    # thermometer
    tx = x + w - 42
    draw.rectangle([tx, y + 14, tx + 16, y + h - 30], outline=INK, width=2, fill=(255, 255, 255))
    draw.ellipse([tx - 6, y + h - 34, tx + 22, y + h - 12], fill=RED, outline=INK, width=2)
    draw.rectangle([tx + 4, y + 34, tx + 12, y + h - 24], fill=RED)
    f2 = font(F_SANS_B, 13)
    draw.text((tx - 34, y + 30), "1.5\u00b0C", font=f2, fill=RED)
    draw.text((tx - 30, y + 48), "LIMIT", font=f2, fill=INK)
    # NO DEAL stamp
    f3 = font(F_SANS_B, 22)
    tw = draw.textlength("NO DEAL", font=f3)
    sx0, sy0 = x + 150, y + h - 44
    draw.rectangle([sx0 - 4, sy0 - 4, sx0 + tw + 4, sy0 + 26], outline=RED, width=3)
    draw.text((sx0, sy0), "NO DEAL", font=f3, fill=RED)


def art_ukraine(draw, x, y, w, h):
    """Overnight assault: apartment block, drone, explosion glow, 11 KILLED tag."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 228, 200))
    # night sky strip
    draw.rectangle([x, y, x + w, y + 26], fill=(60, 70, 100))
    # moon
    draw.ellipse([x + w - 46, y + 6, x + w - 20, y + 32], fill=(255, 230, 150))
    # apartment block
    bx, by, bw, bh = x + 22, y + 34, 150, h - 44
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(200, 180, 140), outline=INK, width=2)
    for r in range(4):
        for c in range(5):
            wx, wy = bx + 12 + c * 28, by + 12 + r * 22
            col = (60, 60, 60) if (r * 5 + c) % 3 else (255, 220, 120)
            draw.rectangle([wx, wy, wx + 18, wy + 14], fill=col, outline=INK, width=1)
    # collapsed corner (rubble)
    draw.polygon([(bx + bw - 46, by + bh), (bx + bw, by + bh - 40), (bx + bw, by + bh)], fill=(120, 110, 95))
    draw.polygon([(bx + bw - 60, by + bh), (bx + bw - 20, by + bh - 22), (bx + bw, by + bh)], fill=(90, 85, 75))
    # drone
    dx, dy = x + w - 110, y + 44
    draw.ellipse([dx, dy, dx + 44, dy + 10], fill=INK)
    draw.line([dx + 8, dy - 8, dx + 36, dy - 8], fill=INK, width=2)
    # explosion glow behind building
    draw.ellipse([bx - 14, by + 20, bx + 30, by + 64], fill=(255, 180, 60))
    draw.ellipse([bx - 4, by + 30, bx + 20, by + 54], fill=YELLOW)
    # 11 KILLED tag
    f = font(F_SANS_B, 15)
    tag = "11 KILLED"
    tw = draw.textlength(tag, font=f)
    draw.rectangle([x + w - tw - 18, y + h - 30, x + w - 8, y + h - 6], fill=RED)
    draw.text((x + w - tw - 13, y + h - 28), tag, font=f, fill=(255, 255, 255))


ART = {"bahrain": art_bahrain, "cop31": art_cop31, "ukraine": art_ukraine}


# ---------------------------------------------------------------- page
def draw_map(draw, x, y, w, h):
    """Stylised world map with 13 pins (original, drawn in code)."""
    draw.rectangle([x, y, x + w, y + h], fill=(205, 225, 235), outline=INK, width=1)
    # land masses (very stylised)
    draw.polygon([(x + 18, y + 30), (x + 78, y + 22), (x + 96, y + 52), (x + 70, y + 88), (x + 30, y + 78)], fill=SAND, outline=INK)
    draw.polygon([(x + 110, y + 26), (x + 190, y + 18), (x + 210, y + 44), (x + 170, y + 66), (x + 120, y + 58)], fill=SAND, outline=INK)
    draw.polygon([(x + 210, y + 70), (x + 258, y + 64), (x + 272, y + 96), (x + 230, y + 118), (x + 208, y + 96)], fill=SAND, outline=INK)
    draw.polygon([(x + 120, y + 84), (x + 160, y + 78), (x + 168, y + 104), (x + 138, y + 118), (x + 118, y + 100)], fill=SAND, outline=INK)
    # pins: (rel x, rel y)
    pins = [(52, 40), (96, 34), (130, 30), (150, 38), (168, 30), (196, 36),
            (222, 76), (146, 92), (180, 90), (250, 84), (66, 66), (118, 48), (208, 52)]
    for px, py in pins:
        draw.ellipse([x + px - 4, y + py - 4, x + px + 4, y + py + 4], fill=RED, outline=(255, 255, 255), width=1)


def main(out_path):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=3)
    MX = 24  # margin

    # ---- masthead
    f_top = font(F_SANS_B, 15)
    top = "THE WORLD IN ONE DAY  \u00b7  33 STORIES  \u00b7  SIX REGIONS  \u00b7  ALL FROM ONE DAY"
    tw = d.textlength(top, font=f_top)
    d.text(((W - tw) / 2, 12), top, font=f_top, fill=INK)
    f_title = font(F_SERIF, 60)
    title = "Monday 23 November 2026"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 32), title, font=f_title, fill=INK)
    f_sub = font(F_SANS_I, 16)
    sub = "Iran hits US bases in Bahrain  \u00b7  COP31 collapses with no deal  \u00b7  Russia\u2019s 153-drone night over Ukraine"
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, 96), sub, font=f_sub, fill=RED)
    d.line([MX, 118, W - MX, 118], fill=INK, width=2)

    # ---- stat boxes
    y0, bh = 126, 58
    bw = (W - 2 * MX - 5 * 8) // 6
    f_num = font(F_SANS_B, 28)
    f_lab = font(F_SANS_B, 10)
    for i, (num, lab) in enumerate(STATS):
        x0 = MX + i * (bw + 8)
        d.rectangle([x0, y0, x0 + bw, y0 + bh], outline=INK, width=2, fill=PAPER)
        nw = d.textlength(num, font=f_num)
        d.text((x0 + (bw - nw) / 2, y0 + 4), num, font=f_num, fill=RED)
        lw = d.textlength(lab, font=f_lab)
        d.text((x0 + (bw - lw) / 2, y0 + 40), lab, font=f_lab, fill=INK)
    f_reg = font(F_SANS_B, 13)
    reg = "EUROPE 14  \u00b7  MIDDLE EAST 6  \u00b7  AMERICAS 5  \u00b7  ASIA 3  \u00b7  GLOBAL 3  \u00b7  AFRICA 2   \u2014   33 STORIES IN ALL"
    tw = d.textlength(reg, font=f_reg)
    d.text(((W - tw) / 2, 190), reg, font=f_reg, fill=INK)

    # ---- leads (3 cards, taller so headlines + bodies fit)
    ly, lh = 212, 250
    cw = (W - 2 * MX - 2 * 10) // 3
    f_lead_head = font(F_SANS_B, 12)
    f_lead_title = font(F_SERIF, 22)
    f_lead_body = font(F_SANS, 13)
    for i, L in enumerate(LEADS):
        x0 = MX + i * (cw + 10)
        d.rectangle([x0, ly, x0 + cw, ly + lh], outline=INK, width=2, fill=PAPER)
        d.rectangle([x0, ly, x0 + cw, ly + 22], fill=INK)
        hdr = f"{L['n']} \u00b7 {L['place']}"
        d.text((x0 + 8, ly + 4), hdr, font=f_lead_head, fill=(255, 255, 255))
        sw = d.textlength(L["status"], font=f_lead_head)
        d.text((x0 + cw - sw - 8, ly + 4), L["status"], font=f_lead_head, fill=YELLOW)
        ART[L["art"]](d, x0 + 8, ly + 30, cw - 16, 95)
        d.rectangle([x0 + 8, ly + 30, x0 + cw - 8, ly + 125], outline=INK, width=1)
        y = ly + 133
        y = text_block(d, x0 + 8, y, wrap(d, L["head"], f_lead_title, cw - 16)[:2], f_lead_title, INK, 27)
        text_block(d, x0 + 8, y + 3, wrap(d, L["body"], f_lead_body, cw - 16)[:3], f_lead_body, INK, 15)

    # ---- mids (10 cards, 2 rows x 5; header = number + place only)
    my, mh = 470, 86
    mw = (W - 2 * MX - 4 * 8) // 5
    f_mid_head = font(F_SANS_B, 9)
    f_mid_title = font(F_SANS_B, 14)
    f_mid_body = font(F_SANS, 11)
    for i, M in enumerate(MIDS):
        r, c = divmod(i, 5)
        x0 = MX + c * (mw + 8)
        y0 = my + r * (mh + 8)
        d.rectangle([x0, y0, x0 + mw, y0 + mh], outline=INK, width=1, fill=PAPER)
        hdr = f"{M['n']}. {M['place']}"
        d.text((x0 + 6, y0 + 4), hdr, font=f_mid_head, fill=RED)
        sw = d.textlength(M["status"], font=f_mid_head)
        d.text((x0 + mw - sw - 6, y0 + 4), M["status"], font=f_mid_head, fill=DARKRED)
        y = y0 + 20
        y = text_block(d, x0 + 6, y, wrap(d, M["head"], f_mid_title, mw - 12)[:2], f_mid_title, INK, 16)
        text_block(d, x0 + 6, y + 1, wrap(d, M["body"], f_mid_body, mw - 12)[:2], f_mid_body, INK, 13)

    # ---- UTC timeline (shortened to fit one line)
    ty = 656
    d.rectangle([MX, ty, W - MX, ty + 22], fill=INK)
    f_tl = font(F_SANS_B, 11)
    tl = "UTC \u2014 SUN 18:00 drones launched  \u00b7  MON 07:00 Belgium shuts airspace  \u00b7  MON 08:00 134 of 153 downed  \u00b7  NATO meets  \u00b7  COP31 pact rejected"
    tw = d.textlength(tl, font=f_tl)
    d.text(((W - tw) / 2, ty + 4), tl, font=f_tl, fill=(255, 255, 255))

    # ---- bottom: map + more stories
    by = 686
    f_sec = font(F_SANS_B, 13)
    map_w = 300
    d.text((MX, by), "WHERE IT HAPPENED \u2014 13 PLACES PINNED", font=f_sec, fill=INK)
    draw_map(d, MX, by + 20, map_w, 185)
    d.text((MX, by + 211), "Pins: Bahrain \u00b7 Antalya \u00b7 Kyiv \u00b7 Benghazi \u00b7 Gaza \u00b7 Dhaka \u00b7", font=font(F_SANS, 10), fill=INK)
    d.text((MX, by + 225), "Belgrade \u00b7 Copenhagen \u00b7 Brussels \u00b7 Seoul \u00b7 Sinaloa \u00b7 Barranquilla", font=font(F_SANS, 10), fill=INK)
    rx = MX + map_w + 16
    rw = W - MX - rx
    d.text((rx, by), "ALSO ON MONDAY 23 NOVEMBER \u2014 20 MORE STORIES", font=f_sec, fill=INK)
    f_more_n = font(F_SANS_B, 10)
    f_more = font(F_SANS, 10)
    col_w = (rw - 12) // 2
    y = by + 20
    for i, (place, txt) in enumerate(MORE):
        col = 0 if i < 10 else 1
        row = i % 10
        x0 = rx + col * (col_w + 12)
        y0 = y + row * 21
        d.text((x0, y0), f"{14 + i}.", font=f_more_n, fill=RED)
        lines = wrap(d, f"{place} \u2014 {txt}", f_more, col_w - 22)
        text_block(d, x0 + 22, y0, lines[:1], f_more, INK, 12)

    # ---- date check (taller, proper wrap)
    dy = 924
    d.rectangle([MX, dy, W - MX, dy + 52], outline=RED, width=2, fill=PAPER)
    f_dc = font(F_SANS_B, 12)
    f_dcb = font(F_SANS, 11)
    dc1 = "DATE CHECK \u2713  Every story on this page happened, or was first reported, on Monday 23 November 2026."
    dc2 = "Weekend events appear only where Monday moved them on: the Bahrain strikes (Sat), COP31\u2019s collapse (Sun), the Gaza truck (Sat), the 258th House seat (Sun). LEFT OUT AS OTHER DAYS\u2019 NEWS \u2014 20 NOV: COP31\u2019s scheduled close."
    d.text((MX + 10, dy + 5), dc1, font=f_dc, fill=DARKRED)
    yy = dy + 24
    for ln in wrap(d, dc2, f_dcb, W - 2 * MX - 20)[:2]:
        d.text((MX + 10, yy), ln, font=f_dcb, fill=INK)
        yy += 13

    # ---- sources
    f_src = font(F_SANS, 9)
    src = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Yonhap, WSJ, CNN, UKMTO. Pictures and map: original, drawn in code. Confidence: CONFIRMED = two or more outlets \u00b7 REPORTED = named sources, one side\u2019s claim where stated \u00b7 FORECAST = due date or draft."
    y = 984
    for ln in wrap(d, src, f_src, W - 2 * MX):
        d.text((MX, y), ln, font=f_src, fill=GREY)
        y += 11

    img.save(out_path, "PNG", optimize=True)
    h = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
    print(f"wrote {out_path} sha256={h} size={img.size}")


if __name__ == "__main__":
    import sys, os
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    main(os.path.join(out, "entry.png"))
