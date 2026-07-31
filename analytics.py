"""
Har posted media ki insights fetch karta hai (official Graph API):
- Reels: views(plays), reach, likes, comments, saved, shares, avg watch time
- Posts: reach, likes, comments, saved, shares
Results analytics.json mein — dashboard yahan se parhta hai.
"""
import os, json, datetime, requests

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = "https://graph.instagram.com/v21.0"
TOKEN = os.environ["IG_ACCESS_TOKEN"]
IG_ID = os.environ["IG_USER_ID"]

REEL_METRICS = "views,reach,likes,comments,saved,shares,ig_reels_avg_watch_time"
POST_METRICS = "reach,likes,comments,saved,shares"


def media_insights(media_id, metrics):
    r = requests.get(f"{GRAPH}/{media_id}/insights",
                     params={"metric": metrics, "access_token": TOKEN}, timeout=60)
    if r.status_code != 200:
        return {"error": r.json().get("error", {}).get("message", "unknown")}
    out = {}
    for m in r.json().get("data", []):
        vals = m.get("values", [{}])
        out[m["name"]] = vals[0].get("value", 0)
    return out


def account_snapshot():
    r = requests.get(f"{GRAPH}/{IG_ID}",
                     params={"fields": "username,followers_count,media_count", "access_token": TOKEN},
                     timeout=60).json()
    return {"username": r.get("username", ""), "followers": r.get("followers_count", 0),
            "media_count": r.get("media_count", 0)}


def main():
    with open(os.path.join(HERE, "history.json")) as f:
        hist = json.load(f)

    results = {"updated": datetime.datetime.utcnow().isoformat() + "Z",
               "account": account_snapshot(), "media": []}

    for p in hist["posted"][-30:]:   # last 30 din ki insights refresh
        entry = {"date": p["date"], "topic": p["topic"], "style": p.get("style", "")}
        if p.get("post_id"):
            entry["post"] = media_insights(p["post_id"], POST_METRICS)
        if p.get("reel_id"):
            entry["reel"] = media_insights(p["reel_id"], REEL_METRICS)
        results["media"].append(entry)

    with open(os.path.join(HERE, "analytics.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"Analytics updated for {len(results['media'])} days")


if __name__ == "__main__":
    main()
