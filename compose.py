import json, os
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M, G = 50, 12
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
centered("23 NOVEMBER 2026", 46, font(SERIF, 44), INK, spacing=3)
d.rectangle([M, 112, W - M - 1, 112], fill=INK)            # thin rule
centered(data["lead"], 126, font(SANS, 14), MUTED)

# grid
top, bottom = 164, 944
cw = (W - 2 * M - 2 * G) // 3
ch = (bottom - top - G) // 2
iw, ih = cw, 296
ftag, fcap = font(SANSB, 11), font(SANSB, 14)

def wrap(text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]

for i, c in enumerate(cards):
    x = M + (i % 3) * (cw + G)
    y = top + (i // 3) * (ch + G)
    im = Image.open(os.path.join(HERE, "img", c["img"])).convert("RGB")
    img.paste(ImageOps.fit(im, (iw, ih), Image.LANCZOS, centering=(0.5, 0.5)), (x, y))
    ty = y + ih + 12
    d.rectangle([x, ty + 1, x + 3, ty + 12], fill=ACCENT)   # accent tick + tag
    d.text((x + 10, ty), c["region"], font=ftag, fill=ACCENT)
    cy = ty + 24
    for line in wrap(c["head"], fcap, cw)[:4]:
        d.text((x, cy), line, font=fcap, fill=INK); cy += 20

# footer
d.rectangle([M, 962, W - M - 1, 962], fill=INK)
centered("world news in one image", 976, font(SERIF, 15), ACCENT)

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
img.save(os.path.join(HERE, "out/entry.png"))
print("saved out/entry.png", img.size)
