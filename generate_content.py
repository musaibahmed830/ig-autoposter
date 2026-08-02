"""
Roz ka content (Gemini API, free tier) — variety engine ke plan ke mutabiq:
har din alag topic + alag content style (tips/myth/story/stat...).
"""
import os, json
from google import genai
from google.genai import types
from variety import todays_plan

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# Manual "niche" dropdown se poori identity/persona switch ho jati hai (na sirf tone) —
# brand niche ki jagah ye description prompt mein chali jati hai.
NICHE_PRESETS = {
    "brand / business (as-is)": None,
    "event organizer": "event management company organizing and promoting live events",
    "traveller / travel blogger": "travel blogger sharing destinations, travel tips, and experiences",
    "lifestyle vlogger": "lifestyle vlogger sharing daily life, routines, and personal stories",
    "food blogger / restaurant": "food blogger and restaurant reviewer sharing food experiences and recipes",
    "fashion brand": "fashion brand showcasing style, outfits, and trends",
    "beauty & skincare brand": "beauty and skincare brand sharing tips and product highlights",
    "fitness coach": "fitness coach sharing workout tips and health motivation",
    "photographer": "professional photographer showcasing photography work and tips",
    "real estate agent": "real estate agent showcasing properties and home-buying tips",
    "automotive business": "automotive business sharing car tips, reviews, and deals",
    "finance advisor": "finance advisor sharing money tips and financial literacy",
    "educator / coach": "educator and coach sharing learning tips and knowledge",
    "musician / artist": "musician and artist sharing their creative work and performances",
    "comedian / entertainer": "comedian and entertainer sharing funny, relatable content",
    "gamer / streamer": "gamer and streamer sharing gaming content and highlights",
    "pet business": "pet care business sharing pet tips and cute pet content",
    "nonprofit / charity": "nonprofit organization sharing charitable causes and impact stories",
    "news / media page": "news and media page sharing current events and updates",
    "sports team / athlete": "sports page sharing athletic content and updates",
    "motivational speaker": "motivational speaker sharing inspiration and personal growth content",
    "parenting / family blogger": "parenting and family blogger sharing family tips and stories",
}


def generate(plan: dict) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    brand = os.environ.get("BRAND_NAME", "My Brand")
    niche = os.environ.get("NICHE", "digital marketing agency")
    city = os.environ.get("CITY", "Lahore")
    lang = os.environ.get("LANGUAGE", "English with a little Roman Urdu flavor")
    n = plan["n_slides"]

    category = os.environ.get("MANUAL_CATEGORY", "").strip()
    if category.lower().startswith("default"):
        category = ""

    niche_override = os.environ.get("MANUAL_NICHE", "").strip()
    identity_note = ""
    if niche_override and not niche_override.lower().startswith("default"):
        preset = NICHE_PRESETS.get(niche_override.lower())
        if preset:
            identity_note = (f"\nManual override: for this specific post, IGNORE the usual "
                              f"\"{niche}\" niche entirely. Instead write as if {brand} is a "
                              f"{preset}. Fully switch tone, framing, and hashtags to this new "
                              f"identity for this one post.\n")
            niche = preset
        else:
            niche_override = ""

    category_note = (f"\nManual override: this specific post is a **{category}** category post — "
                      f"adapt tone, framing, and hashtags for {category} content, even if it differs "
                      f"from the usual {niche} niche, while still representing {brand}.\n") if category else ""

    prompt = f"""You are a social media content writer for "{brand}", a {niche} based in {city}.
Today's topic: {plan['topic']}
Today's format: {plan['style_desc']} — follow this format strictly so today's post feels different from other days.
{identity_note}{category_note}
Write Instagram content in {lang}. Respond with ONLY a JSON object, no markdown fences, keys:
- "caption": 3-6 lines in the format above. First line = hook. Weave in 2-3 searchable keywords naturally. End with a CTA. No hashtags here.
- "hashtags": array of exactly 15 hashtags (no #): mix niche + topic + {city}/local. Small-to-medium tags, not only huge ones.
- "alt_text": one sentence image description with 1-2 keywords (under 100 chars).
- "slides": array of exactly {n} strings, each under 9 words, matching today's format (slide 1 = hook, last slide = CTA).
- "headline_small": 2-5 word lead-in phrase for the poster headline (e.g. "YOUR WEBSITE" or "BUILD A RELIABLE").
- "headline_big": 1-4 word punchy takeaway that completes the headline_small phrase, this is the big bold hero word(s) (e.g. "REIMAGINED" or "IT FOUNDATION").
- "panel_text": one short punchy sentence (under 14 words) summarizing the value prop, for a highlighted info box on the image.
"""
    resp = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=3000,
            response_mime_type="application/json",
        ),
    )
    data = json.loads(resp.text.replace("```json", "").replace("```", "").strip())
    data["hashtags"] = data.get("hashtags", [])[:15]
    data["slides"] = (data.get("slides", []) + [plan["topic"]] * n)[:n]
    data.setdefault("headline_small", "")
    data.setdefault("headline_big", plan["topic"])
    data.setdefault("panel_text", data["slides"][0])
    data["category"] = category
    data["niche_override"] = niche_override
    data.update(plan)
    return data


if __name__ == "__main__":
    plan = todays_plan()
    content = generate(plan)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "content.json"), "w") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print("Topic:", plan["topic"], "| Style:", plan["style"], "| Palette:", plan["palette"])
