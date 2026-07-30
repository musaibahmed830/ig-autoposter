"""
Branded images — 3 layouts x 5 palettes rotate hote hain (variety plan se):
- center:    text center, accent underline
- left_band: left side accent band, text left-aligned
- boxed:     accent-border box ke andar text
"""
import os, json, textwrap
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def _darker(hexc, f=0.55):
    r, g, b = _hex(hexc); return "#%02x%02x%02x" % (int(r*f), int(g*f), int(b*f))

def _tint(base, accent, f=0.14):
    b, a = _hex(base), _hex(accent)
    return tuple(int(b[i]*(1-f) + a[i]*f) for i in range(3))

def _gradient(w, h, top, bottom, accent):
    """Top = base color, bottom = base tinted with accent — har palette ka apna mood."""
    img = Image.new("RGB", (w, h))
    t, b = _hex(top), _tint(bottom, accent, 0.18)
    for y in range(h):
        r = y / h
        img.paste(tuple(int(t[i]+(b[i]-t[i])*r) for i in range(3)), (0, y, w, y+1))
    return img


def render(text, w, h, path, plan, slide_no=None, total=None):
    bg, accent, layout = plan["bg"], plan["accent"], plan["layout"]
    brand = os.environ.get("BRAND_NAME", "My Brand")
    img = _gradient(w, h, bg, _darker(bg, 0.75), accent)
    d = ImageDraw.Draw(img)
    size = int(w * 0.072)
    font = ImageFont.truetype(FONT_BOLD, size)
    bfont = ImageFont.truetype(FONT_REG, int(w * 0.033))
    line_h = int(size * 1.25)

    if layout == "left_band":
        d.rectangle([0, 0, int(w*0.03), h], fill=accent)
        lines = textwrap.wrap(text, width=16)
        y = (h - line_h*len(lines)) // 2
        for line in lines:
            d.text((w*0.1, y), line, font=font, fill="#ffffff"); y += line_h
        d.rectangle([w*0.1, y+22, w*0.1+200, y+32], fill=accent)
        d.text((w*0.1, h - int(w*0.09)), brand, font=bfont, fill=accent)
    elif layout == "boxed":
        m = int(w*0.08)
        d.rectangle([m, int(h*0.22), w-m, int(h*0.78)], outline=accent, width=6)
        lines = textwrap.wrap(text, width=15)
        y = (h - line_h*len(lines)) // 2
        for line in lines:
            lw = d.textlength(line, font=font)
            d.text(((w-lw)/2, y), line, font=font, fill="#ffffff"); y += line_h
        bw = d.textlength(brand, font=bfont)
        d.text(((w-bw)/2, h - int(w*0.09)), brand, font=bfont, fill=accent)
    else:  # center
        d.rectangle([0, 0, w, 14], fill=accent)
        lines = textwrap.wrap(text, width=18)
        y = (h - line_h*len(lines)) // 2
        for line in lines:
            lw = d.textlength(line, font=font)
            d.text(((w-lw)/2, y), line, font=font, fill="#ffffff"); y += line_h
        d.rectangle([(w-220)/2, y+24, (w+220)/2, y+34], fill=accent)
        bw = d.textlength(brand, font=bfont)
        d.text(((w-bw)/2, h - int(w*0.09)), brand, font=bfont, fill=accent)

    if slide_no:
        cfont = ImageFont.truetype(FONT_REG, int(w * 0.03))
        d.text((w*0.05, h*0.035), f"{slide_no}/{total}", font=cfont, fill="#ffffff")
    img.save(path, "JPEG", quality=92)


def main():
    with open(os.path.join(OUT, "content.json")) as f:
        c = json.load(f)
    slides = c["slides"]
    render(slides[0], 1080, 1350, os.path.join(OUT, "post.jpg"), c)
    for i, s in enumerate(slides, 1):
        render(s, 1080, 1920, os.path.join(OUT, f"slide_{i}.jpg"), c, i, len(slides))
    print(f"Images ready — layout={c['layout']}, palette={c['palette']}")


if __name__ == "__main__":
    main()
