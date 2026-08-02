"""
Branded poster template — koi external AI image API nahi (free tier ki
unreliability se bachne ke liye): dark gradient + grid texture + logo bar +
do-tier headline (chhota lead-in + bada punch word) + hand-drawn glowing
icon + info panel + footer. Palette variety.py se rotate hoti hai.
"""
import os, json, math, re, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONTS = os.path.join(HERE, "assets", "fonts")

F_BLACK = os.path.join(FONTS, "ArchivoBlack-Regular.ttf")
F_BOLD = os.path.join(FONTS, "Poppins-Bold.ttf")
F_SEMI = os.path.join(FONTS, "Poppins-SemiBold.ttf")
F_REG = os.path.join(FONTS, "Poppins-Regular.ttf")

ICONS = ["laptop", "phone", "cloud", "chart", "gear", "code", "camera", "pin"]


def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def _darker(hexc, f=0.55):
    r, g, b = _hex(hexc); return "#%02x%02x%02x" % (int(r*f), int(g*f), int(b*f))

def _tint(base, accent, f=0.14):
    b, a = _hex(base), _hex(accent)
    return tuple(int(b[i]*(1-f) + a[i]*f) for i in range(3))


def _gradient(w, h, top, bottom, accent):
    img = Image.new("RGB", (w, h))
    t, b = _hex(top), _tint(bottom, accent, 0.18)
    for y in range(h):
        r = y / h
        img.paste(tuple(int(t[i]+(b[i]-t[i])*r) for i in range(3)), (0, y, w, y+1))
    return img


def _grid(img, accent, alpha=16, step=64):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    c = _hex(accent) + (alpha,)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=c, width=1)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=c, width=1)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _radial_glow(img, accent, cx_f=0.82, cy_f=0.12, r_f=0.55, alpha=90):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    cx, cy, r = w*cx_f, h*cy_f, w*r_f
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=_hex(accent) + (alpha,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(r * 0.5))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _tracked_text(d, xy, text, font, fill, tracking=0):
    """Letter-spacing ke saath text draw karta hai (uppercase headings ke liye)."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tracking
    return x


def _tracked_width(d, text, font, tracking=0):
    return sum(d.textlength(ch, font=font) + tracking for ch in text) - (tracking if text else 0)


# ---------- Icons: flat line-art, glow ke saath ----------

def _icon_laptop(d, cx, cy, s, color, w_stroke):
    sw, sh = s*1.05, s*0.68
    d.rounded_rectangle([cx-sw/2, cy-sh/2-s*0.18, cx+sw/2, cy+sh/2-s*0.18], radius=s*0.06, outline=color, width=w_stroke)
    d.polygon([(cx-sw*0.62, cy+sh*0.32), (cx+sw*0.62, cy+sh*0.32), (cx+sw*0.5, cy+sh*0.48), (cx-sw*0.5, cy+sh*0.48)], outline=color, width=w_stroke)

def _icon_phone(d, cx, cy, s, color, w_stroke):
    pw, ph = s*0.52, s*1.05
    d.rounded_rectangle([cx-pw/2, cy-ph/2, cx+pw/2, cy+ph/2], radius=s*0.12, outline=color, width=w_stroke)
    d.line([cx-pw*0.18, cy+ph*0.36, cx+pw*0.18, cy+ph*0.36], fill=color, width=w_stroke)

def _icon_cloud(d, cx, cy, s, color, w_stroke):
    r = s*0.28
    for dx, dy, rr in [(-r*1.1, r*0.25, r*0.85), (0, -r*0.35, r*1.05), (r*1.15, r*0.2, r*0.8)]:
        d.ellipse([cx+dx-rr, cy+dy-rr, cx+dx+rr, cy+dy+rr], outline=color, width=w_stroke)
    d.line([cx-r*1.7, cy+r*0.75, cx+r*1.85, cy+r*0.75], fill=color, width=w_stroke)

def _icon_chart(d, cx, cy, s, color, w_stroke):
    bars = [0.35, 0.55, 0.42, 0.8]
    bw = s*0.16
    base = cy + s*0.42
    x = cx - (len(bars)*bw*1.4)/2
    for f in bars:
        bh = s*0.85*f
        d.rounded_rectangle([x, base-bh, x+bw, base], radius=bw*0.25, outline=color, width=w_stroke)
        x += bw*1.4

def _icon_gear(d, cx, cy, s, color, w_stroke):
    r_out, r_in, teeth = s*0.42, s*0.24, 8
    for i in range(teeth):
        a = (2*math.pi/teeth)*i
        x1, y1 = cx+math.cos(a)*r_out, cy+math.sin(a)*r_out
        x2, y2 = cx+math.cos(a)*r_out*1.22, cy+math.sin(a)*r_out*1.22
        d.line([x1, y1, x2, y2], fill=color, width=w_stroke*2)
    d.ellipse([cx-r_out, cy-r_out, cx+r_out, cy+r_out], outline=color, width=w_stroke)
    d.ellipse([cx-r_in*0.55, cy-r_in*0.55, cx+r_in*0.55, cy+r_in*0.55], outline=color, width=w_stroke)

def _icon_code(d, cx, cy, s, color, w_stroke):
    o = s*0.3
    d.line([cx-o*1.5, cy-o*0.7, cx-o*2.3, cy, cx-o*1.5, cy+o*0.7], fill=color, width=w_stroke, joint="curve")
    d.line([cx+o*1.5, cy-o*0.7, cx+o*2.3, cy, cx+o*1.5, cy+o*0.7], fill=color, width=w_stroke, joint="curve")
    d.line([cx+o*0.35, cy-o*1.1, cx-o*0.35, cy+o*1.1], fill=color, width=w_stroke)

def _icon_camera(d, cx, cy, s, color, w_stroke):
    bw, bh = s*0.9, s*0.62
    d.rounded_rectangle([cx-bw/2, cy-bh/2, cx+bw/2, cy+bh/2], radius=s*0.08, outline=color, width=w_stroke)
    d.rectangle([cx-bw*0.18, cy-bh/2-s*0.14, cx+bw*0.1, cy-bh/2], outline=color, width=w_stroke)
    r = s*0.2
    d.ellipse([cx-r, cy-r+s*0.03, cx+r, cy+r+s*0.03], outline=color, width=w_stroke)

def _icon_pin(d, cx, cy, s, color, w_stroke):
    r = s*0.32
    top = cy - s*0.28
    d.ellipse([cx-r, top-r, cx+r, top+r], outline=color, width=w_stroke)
    d.polygon([(cx-r*0.55, top+r*0.75), (cx+r*0.55, top+r*0.75), (cx, cy+s*0.5)], outline=color, width=w_stroke)
    ir = r*0.4
    d.ellipse([cx-ir, top-ir, cx+ir, top+ir], outline=color, width=w_stroke)

ICON_FN = {"laptop": _icon_laptop, "phone": _icon_phone, "cloud": _icon_cloud,
           "chart": _icon_chart, "gear": _icon_gear, "code": _icon_code,
           "camera": _icon_camera, "pin": _icon_pin}


def _draw_icon_glow(img, name, cx, cy, s, accent):
    w, h = img.size
    w_stroke = max(3, int(s*0.045))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    ICON_FN[name](gd, cx, cy, s, _hex(accent) + (255,), w_stroke)
    blurred = glow.filter(ImageFilter.GaussianBlur(s*0.06))
    img = Image.alpha_composite(img.convert("RGBA"), blurred)
    crisp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(crisp)
    ICON_FN[name](cd, cx, cy, s, _hex(accent) + (255,), max(2, int(w_stroke*0.7)))
    return Image.alpha_composite(img, crisp).convert("RGB")


def split_headline(small, big):
    small = (small or "").strip()
    big = (big or "").strip()
    if not big:
        big = small; small = ""
    if not small:
        words = big.split()
        if len(words) > 3:
            small, big = " ".join(words[:-3]), " ".join(words[-3:])
    return small.upper(), big.upper()


def render(text, w, h, path, plan, slide_no=None, total=None, headline_small="", panel_text=""):
    bg, accent = plan["bg"], plan["accent"]
    brand = os.environ.get("BRAND_NAME", "My Brand")
    small, big = split_headline(headline_small, text)

    img = _gradient(w, h, _darker(bg, 0.45), _darker(bg, 0.7), accent)
    img = _grid(img, accent, alpha=14, step=int(w*0.06))
    img = _radial_glow(img, accent)
    d = ImageDraw.Draw(img)

    pad = int(w*0.075)

    # Logo bar
    logo_y = int(h*0.045)
    for i in range(3):
        bx = pad + i*10
        d.polygon([(bx, logo_y+26), (bx+8, logo_y), (bx+16, logo_y), (bx+8, logo_y+26)], fill=accent)
    brand_font = ImageFont.truetype(F_BOLD, int(w*0.042))
    d.text((pad+42, logo_y-4), brand, font=brand_font, fill="#ffffff")
    tag_font = ImageFont.truetype(F_REG, int(w*0.02))
    niche_override = plan.get("niche_override", "")
    if niche_override:
        tagline = niche_override[:34].upper()
    else:
        niche = os.environ.get("NICHE", "")
        tagline = "SOFTWARE · APPS · ERP" if "erp" in niche.lower() else niche[:34].upper()
    d.text((pad+43, logo_y+int(w*0.05)), tagline, font=tag_font, fill=_darker("#ffffff", 0.55))

    # Headline
    y = int(h * (0.2 if slide_no is None else 0.16))
    if small:
        sfont = ImageFont.truetype(F_SEMI, int(w*0.04))
        for line in textwrap.wrap(small, width=26):
            _tracked_text(d, (pad, y), line, sfont, "#e8ecf4", tracking=2)
            y += int(w*0.058)
        y += int(w*0.015)
    bfont_size = int(w * (0.108 if slide_no is None else 0.1))
    bfont = ImageFont.truetype(F_BLACK, bfont_size)
    max_w = w - 2*pad
    words, lines, cur = big.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=bfont) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    lines = lines[:2]
    line_h = int(bfont_size * 1.02)
    for line in lines:
        d.text((pad, y), line, font=bfont, fill=accent)
        y += line_h
    headline_bottom = y + int(w*0.02)

    # Icon
    icon_name = ICONS[(abs(hash(plan["date"])) + (slide_no or 0)) % len(ICONS)]
    panel_top = int(h * (0.66 if slide_no is None else 0.86))
    icon_area_top = headline_bottom + int(h*0.02)
    icon_area_h = max(int(h*0.12), panel_top - icon_area_top - int(h*0.05))
    icon_cy = icon_area_top + icon_area_h // 2
    icon_s = min(int(w*(0.3 if slide_no is None else 0.4)), icon_area_h*1.3)
    img = _draw_icon_glow(img, icon_name, w//2, icon_cy, icon_s, accent)
    d = ImageDraw.Draw(img)

    # Info panel (sirf main post ke liye)
    if slide_no is None and panel_text:
        pfont = ImageFont.truetype(F_REG, int(w*0.03))
        plines = textwrap.wrap(panel_text, width=46)[:4]
        line_h2 = int(w*0.045)
        box_h = int(w*0.05) + line_h2*len(plines) + int(w*0.05)
        box = [pad, panel_top, w-pad, panel_top+box_h]
        panel_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        pd = ImageDraw.Draw(panel_overlay)
        pd.rounded_rectangle(box, radius=16, fill=(0, 0, 0, 130), outline=_hex(accent)+(255,), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), panel_overlay).convert("RGB")
        d = ImageDraw.Draw(img)
        ty = panel_top + int(w*0.05)
        for line in plines:
            lw = d.textlength(line, font=pfont)
            d.text(((w-lw)/2, ty), line, font=pfont, fill="#e8ecf4")
            ty += line_h2
        footer_y = box[3] + int(h*0.035)
    else:
        footer_y = panel_top + int(h*0.02)

    # Footer
    handle = "@" + re.sub(r"[^a-z0-9]", "", brand.lower())
    ffont = ImageFont.truetype(F_SEMI, int(w*0.028))
    fw = d.textlength(handle, font=ffont)
    d.text(((w-fw)/2, min(footer_y, h - int(w*0.09))), handle, font=ffont, fill=accent)

    if slide_no:
        cfont = ImageFont.truetype(F_SEMI, int(w * 0.028))
        d.text((w - pad - d.textlength(f"{slide_no}/{total}", font=cfont), int(h*0.045)),
               f"{slide_no}/{total}", font=cfont, fill="#ffffff")

    img.save(path, "JPEG", quality=92)


def main():
    with open(os.path.join(OUT, "content.json")) as f:
        c = json.load(f)
    slides = c["slides"]
    render(c.get("headline_big", slides[0]), 1080, 1350, os.path.join(OUT, "post.jpg"), c,
           headline_small=c.get("headline_small", ""), panel_text=c.get("panel_text", ""))
    for i, s in enumerate(slides, 1):
        render(s, 1080, 1920, os.path.join(OUT, f"slide_{i}.jpg"), c, i, len(slides))
    print(f"Images ready — palette={c['palette']}")


if __name__ == "__main__":
    main()
