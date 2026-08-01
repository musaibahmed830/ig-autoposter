"""
Branded images — 3 layouts x 5 palettes rotate hote hain (variety plan se):
- center:    text center, accent underline
- left_band: left side accent band, text left-aligned
- boxed:     accent-border box ke andar text
Feed post (post.jpg) ke liye Pollinations.ai (free, no key) se ek AI hero
background banta hai — laptop/phone mockup + isometric icons — text uske
upar bottom-scrim ke saath overlay hota hai. Carousel/reel slides fast aur
consistent rehne ke liye purane flat-gradient style mein hi rehte hain.
"""
import io, os, json, textwrap, urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PALETTE_MOOD = {
    "midnight_amber":     "dark navy background, warm amber gold glowing accents",
    "plum_orchid":        "deep plum purple background, glowing orchid pink accents",
    "forest_mint":        "dark forest green background, glowing mint green accents",
    "espresso_tangerine": "dark espresso brown background, glowing tangerine orange accents",
    "deep_teal_sky":      "deep teal background, glowing sky blue accents",
}


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


def _apply_scrim(img, top_frac=0.5, max_alpha=235):
    """Bottom-up dark gradient overlay — AI background ke upar text readable rakhne ke liye."""
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    start_y = int(h * top_frac)
    for y in range(start_y, h):
        a = int(max_alpha * (y - start_y) / (h - start_y))
        overlay.paste((0, 0, 0, a), (0, y, w, y + 1))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def ai_hero_background(plan, w, h, variant=0):
    """Pollinations.ai (free, no API key) se professional tech marketing background.
    variant se har slide ka apna alag (lekin same-mood) visual milta hai.
    Free tier ~686px native resolution deta hai (chahe jitni width maango) — is liye
    prompt mein sharpness push karte hain aur baad mein unsharp-mask + contrast se
    upscale ka softness compensate karte hain."""
    mood = PALETTE_MOOD.get(plan["palette"], "dark navy background, warm amber gold glowing accents")
    niche = os.environ.get("NICHE", "software house")
    prompt = (f"modern 3d isometric product render for a {niche}, {mood}, "
              f"sleek closed or angled laptop silhouette with a plain glowing empty screen, "
              f"small floating isometric tech icons like gears code brackets mobile phone cloud "
              f"chart bars around it, minimal background with negative space, clean corporate "
              f"branding style, sharp focus, highly detailed, no screen interface, no UI, "
              f"no readable text, no words, no letters, no logo, no watermark")
    seed = (abs(hash(plan["date"])) + variant * 7919) % 100000
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt)
           + f"?width={w}&height={h}&nologo=true&seed={seed}")
    r = requests.get(url, timeout=45)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    img = ImageOps.fit(img, (w, h), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
    return ImageEnhance.Contrast(img).enhance(1.08)


def render(text, w, h, path, plan, slide_no=None, total=None):
    """Post + carousel/reel slides — AI background + bottom scrim + headline.
    AI fail ho (network/quota) to flat gradient par fallback hota hai."""
    bg, accent = plan["bg"], plan["accent"]
    brand = os.environ.get("BRAND_NAME", "My Brand")
    variant = slide_no or 0
    try:
        img = ai_hero_background(plan, w, h, variant=variant)
        img = _apply_scrim(img, top_frac=0.48 if slide_no is None else 0.42)
    except Exception as e:
        print(f"AI background fail hua ({e}) — flat gradient use kar raha hoon.")
        img = _gradient(w, h, bg, _darker(bg, 0.75), accent)

    d = ImageDraw.Draw(img)
    size = int(w * (0.066 if slide_no is None else 0.072))
    font = ImageFont.truetype(FONT_BOLD, size)
    bfont = ImageFont.truetype(FONT_REG, int(w * 0.032))
    line_h = int(size * 1.22)

    lines = textwrap.wrap(text, width=20 if slide_no is None else 16)
    y = h - int(h * 0.15) - line_h * len(lines)
    for line in lines:
        d.text((w * 0.08, y), line, font=font, fill="#ffffff"); y += line_h

    d.rectangle([w*0.08, y+18, w*0.08+180, y+27], fill=accent)
    d.text((w*0.08, h - int(w*0.075)), brand, font=bfont, fill=accent)

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
    print(f"Images ready — palette={c['palette']}")


if __name__ == "__main__":
    main()
