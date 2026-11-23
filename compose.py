import json, os
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M, G = 56, 14
INK, PAPER, MUTED, ACCENT = (20, 20, 20), (250, 248, 243), (110, 108, 102), (190, 25, 45)
FD = "/usr/share/fonts/truetype/dejavu/"
def font(name, size): return ImageFont.truetype(FD + name, size)
SERIF, SANS, SANSB = "DejaVuSerif-Bold.ttf", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"

data = json.load(open(os.path.join(HERE, "assets/stories.json")))
cards = [c for c in data["cards"] if c["img"]][:6]
for c in cards:
    assert len(c["head"].split()) <= 12, c["head"]

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def centered(text, y, f, fill, spacing=0):
    w = d.textlength(text, font=f)
    if spacing:
        w += spacing * (len(text) - 1)
        x = (W - w) / 2
        for ch in text:
            d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + spacing
    else:
        d.text(((W - w) / 2, y), text, font=f, fill=fill)

# masthead
def blend(fg, bg, a): return tuple(round(f * a + b * (1 - a)) for f, b in zip(fg, bg))
DECK = blend((10, 10, 10), PAPER, 0.75)                   # near-black deck at 0.75 alpha
ACCENT_D = (140, 16, 34)                                  # dark solid accent for tag chips
fnp = font("DejaVuSerifCondensed-Bold.ttf", 46)
x = M
for chn in "THE WORLD TODAY":                              # tight tracking
    d.text((x, 30), chn, font=fnp, fill=INK); x += d.textlength(chn, font=fnp) - 1
fa = font(SANSB, 11)
aw = d.textlength("AGENT EDITION", font=fa) + 14
d.rectangle([W - M - aw, 52, W - M - 1, 72], fill=ACCENT_D)
d.text((W - M - aw + 7, 56), "AGENT EDITION", font=fa, fill=(255, 255, 255))
d.rectangle([M, 88, W - M - 1, 90], fill=INK)             # double rule under nameplate
d.rectangle([M, 93, W - M - 1, 93], fill=INK)
centered(data["date"].upper(), 102, font(SERIF, 15), INK, spacing=3)
centered(data["lead"], 128, font(SANS, 12), MUTED)
d.rectangle([M, 152, W - M - 1, 152], fill=INK)

# grid
top, bottom = 168, 928
cw = (W - 2 * M - 2 * G) // 3
ch = (bottom - top - G) // 2          # fixed cell height (image + caption)
CAP = 140                              # fixed caption block height
iw, ih = cw, ch - CAP
ftag, fhead, fdeck = font(SANSB, 10), font(SERIF, 15), font(SANS, 12)
HEAD_Y, HEAD_LH, DECK_Y, DECK_LH = 26, 20, 74, 16   # shared baselines in every caption

def wrap(text, f, maxw, maxlines):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        while d.textlength(lines[-1] + "\u2026", font=f) > maxw: lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
        lines[-1] += "\u2026"
    return lines

def grade(im):                          # one grade for every panel
    im = ImageEnhance.Color(im).enhance(0.82)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.05 + 4)))
    g = g.point(lambda v: min(255, int(v * 1.01 + 3)))
    b = b.point(lambda v: int(v * 0.94 + 2))
    return Image.merge("RGB", (r, g, b))

for i, c in enumerate(cards):
    x = M + (i % 3) * (cw + G)
    y = top + (i // 3) * (ch + G)
    im = Image.open(os.path.join(HERE, "img", c["img"])).convert("RGB")
    img.paste(grade(ImageOps.fit(im, (iw, ih), Image.LANCZOS, centering=(0.5, 0.5))), (x, y))
    ty = y + ih + 10
    tw = d.textlength(c["region"], font=ftag) + 12
    d.rectangle([x, ty, x + tw, ty + 15], fill=ACCENT_D)   # white-on-dark tag chip
    d.text((x + 6, ty + 2), c["region"], font=ftag, fill=(255, 255, 255))
    for k, line in enumerate(wrap(c["head"], fhead, cw, 2)):
        d.text((x, ty + HEAD_Y + k * HEAD_LH), line, font=fhead, fill=INK)
    for k, line in enumerate(wrap(c["body"], fdeck, cw, 3)):
        d.text((x, ty + DECK_Y + k * DECK_LH), line, font=fdeck, fill=DECK)

# footer
d.rectangle([M, 950, W - M - 1, 950], fill=INK)
centered("world news in one image", 962, font(SERIF, 14), ACCENT_D)

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
img.save(os.path.join(HERE, "out/entry.png"))
print("saved out/entry.png", img.size)
