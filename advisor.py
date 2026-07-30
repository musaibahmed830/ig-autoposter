"""
Reach advisor:
- Last 7 vs pichle 7 din ka avg reel reach compare karta hai
- Agar reach gir raha hai (>20% down ya 3 din flat/low) to Claude API + web_search se
  CURRENT growth tactics research karwata hai aur dashboard ke liye advice likhta hai
- Trending audio note: API se IG ka in-app trending audio attach NAHI ho sakta —
  is liye advisor "manual trending-audio day" flag karta hai (us din reel ready milegi,
  aap app se trending sound ke saath khud post karo)
"""
import os, json, datetime, statistics

HERE = os.path.dirname(os.path.abspath(__file__))


def reel_reaches(media):
    out = []
    for m in media:
        r = m.get("reel", {})
        if isinstance(r, dict) and "reach" in r:
            out.append((m["date"], r["reach"]))
    return out


def analyze():
    with open(os.path.join(HERE, "analytics.json")) as f:
        data = json.load(f)
    reaches = reel_reaches(data.get("media", []))
    if len(reaches) < 6:
        return {"status": "warming_up",
                "verdict": "Data jama ho raha hai — kam az kam 6 din ke baad trend milega.",
                "manual_audio_day": False, "tips": []}

    vals = [r for _, r in reaches]
    recent = vals[-7:]
    prev = vals[-14:-7] or vals[:-7]
    avg_r, avg_p = statistics.mean(recent), statistics.mean(prev) if prev else 0
    change = ((avg_r - avg_p) / avg_p * 100) if avg_p else 0

    falling = change < -20 or (len(recent) >= 3 and max(recent[-3:]) < statistics.mean(vals) * 0.6)
    status = "falling" if falling else ("growing" if change > 10 else "steady")

    result = {"status": status, "avg_recent": round(avg_r), "avg_prev": round(avg_p),
              "change_pct": round(change, 1), "manual_audio_day": falling, "tips": []}

    if falling:
        result["verdict"] = ("Reach gir raha hai. Aaj ki reel MANUALLY post karo — app se, "
                             "trending audio laga ke (API se trending sound attach nahi hota). "
                             "Neeche taaza research-based tips hain.")
        result["tips"] = research_tips()
    elif status == "growing":
        result["verdict"] = f"Reach barh raha hai (+{change:.0f}%) — strategy kaam kar rahi hai, continue!"
    else:
        result["verdict"] = "Reach steady hai. Hooks par experiment karte raho."
    return result


def research_tips():
    """Claude + web_search se current (aaj ke) reach tactics."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1500,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
            messages=[{"role": "user", "content":
                "Search the web for the CURRENT best tactics (this month) to increase Instagram Reels "
                "reach for a small business account. Then respond with ONLY a JSON array of 5 short, "
                "specific, actionable tips (each under 25 words). No markdown fences."}])
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        text = text.replace("```json", "").replace("```", "").strip()
        start = text.find("["); end = text.rfind("]") + 1
        return json.loads(text[start:end])[:5]
    except Exception as e:
        return [f"(Research fail hui: {e}) Fallback: pehle 2 second ka hook strong karo, "
                "trending audio manually lagao, share-able content banao."]


if __name__ == "__main__":
    advice = analyze()
    with open(os.path.join(HERE, "advice.json"), "w") as f:
        json.dump({"date": datetime.date.today().isoformat(), **advice}, f, ensure_ascii=False, indent=2)
    print("Advisor:", advice["status"], "-", advice["verdict"])
