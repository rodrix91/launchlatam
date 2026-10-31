"""Per-page OG images (1200x630) in the LaunchLatam palette: espresso bg, sand title, burnt-orange customs stamp."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
VOLCAN, ARENA, ACHIOTE, SAL, LINE = "#1E1412", "#F2DCC0", "#E2522B", "#FFF6EA", "#5E4A42"
def _font(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(HERE, "fonts", name), size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f
def _wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
def make(out, kicker, title, foot, stamp="APTA"):
    im = Image.new("RGB", (1200, 630), VOLCAN); d = ImageDraw.Draw(im)
    d.rectangle([24, 24, 1176, 606], outline=LINE, width=2)
    for x in range(48, 1160, 18): d.line([x, 540, x+8, 540], fill=LINE, width=2)  # perforation
    mono = _font("jbmono.ttf", 26)
    d.text((70, 70), kicker.upper(), font=mono, fill=ACHIOTE)
    size = 70
    while True:
        tf = _font("bricolage.ttf", size, 780); lines = _wrap(d, title, tf, 820)
        if len(lines) <= 4 or size <= 44: break
        size -= 4
    y = 130
    for i, ln in enumerate(lines[:4]):
        d.text((70, y), ln, font=tf, fill=ARENA if i < len(lines)-1 or len(lines) == 1 else ARENA); y += int(size*1.1)
    d.text((70, 560), foot, font=_font("jbmono.ttf", 22), fill=ARENA)
    # customs stamp
    st = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.ellipse([10, 10, 290, 290], outline=ACHIOTE, width=8); sd.ellipse([34, 34, 266, 266], outline=ACHIOTE, width=3)
    fs = 54
    while _font("bricolage.ttf", fs, 800).getlength(stamp) > 190: fs -= 2
    sf = _font("bricolage.ttf", fs, 800); sm = _font("jbmono.ttf", 20)
    for txt, f, yy in (("LAUNCH", sm, 88), (stamp, sf, 150 - fs*0.6), ("LATAM", sm, 192)):
        w = sd.textlength(txt, font=f); sd.text(((300-w)/2, yy), txt, font=f, fill=ACHIOTE)
    st = st.rotate(-14, resample=Image.BICUBIC)
    im.paste(st, (880, 150), st)
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out, optimize=True)
