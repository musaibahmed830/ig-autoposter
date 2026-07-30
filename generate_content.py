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


def generate(plan: dict) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    brand = os.environ.get("BRAND_NAME", "My Brand")
    niche = os.environ.get("NICHE", "digital marketing agency")
    city = os.environ.get("CITY", "Lahore")
    lang = os.environ.get("LANGUAGE", "English with a little Roman Urdu flavor")
    n = plan["n_slides"]

    prompt = f"""You are a social media content writer for "{brand}", a {niche} based in {city}.
Today's topic: {plan['topic']}
Today's format: {plan['style_desc']} — follow this format strictly so today's post feels different from other days.

Write Instagram content in {lang}. Respond with ONLY a JSON object, no markdown fences, keys:
- "caption": 3-6 lines in the format above. First line = hook. Weave in 2-3 searchable keywords naturally. End with a CTA. No hashtags here.
- "hashtags": array of exactly 15 hashtags (no #): mix niche + topic + {city}/local. Small-to-medium tags, not only huge ones.
- "alt_text": one sentence image description with 1-2 keywords (under 100 chars).
- "slides": array of exactly {n} strings, each under 9 words, matching today's format (slide 1 = hook, last slide = CTA).
"""
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=1400,
            response_mime_type="application/json",
        ),
    )
    data = json.loads(resp.text.replace("```json", "").replace("```", "").strip())
    data["hashtags"] = data.get("hashtags", [])[:15]
    data["slides"] = (data.get("slides", []) + [plan["topic"]] * n)[:n]
    data.update(plan)
    return data


if __name__ == "__main__":
    plan = todays_plan()
    content = generate(plan)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "content.json"), "w") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    print("Topic:", plan["topic"], "| Style:", plan["style"], "| Palette:", plan["palette"])
