"""
Variety engine — roz sab kuch alag rakhta hai, repeat nahi hone deta.
Deterministic (date-seeded) taake GitHub Actions retry par same output aaye.
"""
import os, json, random, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
HISTORY = os.path.join(HERE, "history.json")

CONTENT_STYLES = [
    ("quick_tips",   "a numbered quick-tips list (3 tips)"),
    ("myth_bust",    "a myth vs reality format (bust one common myth)"),
    ("question_hook","open with a bold question, answer it"),
    ("mini_story",   "a tiny relatable story of a business owner, with a lesson"),
    ("stat_shock",   "open with one surprising statistic, explain what to do about it"),
    ("how_to",       "a mini how-to with concrete steps"),
    ("hot_take",     "a contrarian opinion, respectfully argued"),
]

PALETTES = [  # (bg, accent, name)
    ("#0f1b2d", "#f7b32b", "midnight_amber"),
    ("#1a1423", "#e07be0", "plum_orchid"),
    ("#0d2318", "#7ee787", "forest_mint"),
    ("#231a10", "#ff9e57", "espresso_tangerine"),
    ("#101c24", "#5bc9e8", "deep_teal_sky"),
]

LAYOUTS = ["center", "left_band", "boxed"]
TRANSITIONS = ["fade", "slideleft", "slideup", "circleopen", "wipeleft", "smoothup", "fadeblack"]


def load_history():
    if os.path.exists(HISTORY):
        with open(HISTORY) as f:
            return json.load(f)
    return {"posted": []}


def save_history(h):
    with open(HISTORY, "w") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)


def todays_plan(date=None):
    """Aaj ka plan: topic (no recent repeat) + style + palette + layout + transition."""
    date = date or datetime.date.today()
    with open(os.path.join(HERE, "topics.json")) as f:
        topics = json.load(f)

    hist = load_history()
    recent_topics = [p["topic"] for p in hist["posted"][-45:]]   # last 45 din repeat nahi
    recent_styles = [p.get("style") for p in hist["posted"][-3:]]  # 3 din same style nahi

    rng = random.Random(date.toordinal())
    fresh = [t for t in topics if t not in recent_topics] or topics
    topic = rng.choice(fresh)

    styles = [s for s in CONTENT_STYLES if s[0] not in recent_styles] or CONTENT_STYLES
    style = rng.choice(styles)

    # Palette/layout/transition: din ke hisab se rotate + shuffle
    palette = PALETTES[date.toordinal() % len(PALETTES)]
    layout = LAYOUTS[date.toordinal() % len(LAYOUTS)]
    transition = TRANSITIONS[date.toordinal() % len(TRANSITIONS)]
    slide_sec = round(3.0 + rng.random() * 1.0, 1)   # 3.0–4.0s variance
    n_slides = rng.choice([4, 4, 5])                  # kabhi 5 slides

    return {
        "date": date.isoformat(), "topic": topic,
        "style": style[0], "style_desc": style[1],
        "bg": palette[0], "accent": palette[1], "palette": palette[2],
        "layout": layout, "transition": transition,
        "slide_sec": slide_sec, "n_slides": n_slides,
    }


if __name__ == "__main__":
    print(json.dumps(todays_plan(), indent=2))
