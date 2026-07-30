"""
Publish karta hai OFFICIAL Instagram Graph API se (koi ban risk nahi).

Flow:
1. post.jpg + reel.mp4 ko Cloudinary par upload (Graph API ko public URL chahiye)
2. Feed post publish (image + caption + hashtags + alt_text)
3. Reel publish (video + caption)

Env vars:
  IG_USER_ID        — Instagram Business account ID
  IG_ACCESS_TOKEN   — long-lived access token
  CLOUDINARY_CLOUD, CLOUDINARY_KEY, CLOUDINARY_SECRET
"""
import os, json, time, hashlib, requests

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out")
GRAPH = "https://graph.facebook.com/v21.0"

IG_ID = os.environ["IG_USER_ID"]
TOKEN = os.environ["IG_ACCESS_TOKEN"]


# ---------- Cloudinary (signed upload) ----------
def cloudinary_upload(path, resource_type):
    cloud = os.environ["CLOUDINARY_CLOUD"]
    key = os.environ["CLOUDINARY_KEY"]
    secret = os.environ["CLOUDINARY_SECRET"]
    ts = str(int(time.time()))
    sig = hashlib.sha1(f"timestamp={ts}{secret}".encode()).hexdigest()
    url = f"https://api.cloudinary.com/v1_1/{cloud}/{resource_type}/upload"
    with open(path, "rb") as f:
        r = requests.post(url, data={"api_key": key, "timestamp": ts, "signature": sig},
                          files={"file": f}, timeout=300)
    r.raise_for_status()
    return r.json()["secure_url"]


# ---------- Graph API helpers ----------
def _wait_ready(container_id, tries=40):
    """Video processing ka wait (reels ke liye zaroori)."""
    for _ in range(tries):
        r = requests.get(f"{GRAPH}/{container_id}",
                         params={"fields": "status_code", "access_token": TOKEN}).json()
        status = r.get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Container error: {r}")
        time.sleep(10)
    raise TimeoutError("Video processing timeout")


def _publish(container_id):
    r = requests.post(f"{GRAPH}/{IG_ID}/media_publish",
                      data={"creation_id": container_id, "access_token": TOKEN})
    r.raise_for_status()
    return r.json()["id"]


def publish_image(image_url, caption, alt_text=""):
    r = requests.post(f"{GRAPH}/{IG_ID}/media", data={
        "image_url": image_url, "caption": caption,
        "alt_text": alt_text, "access_token": TOKEN})
    r.raise_for_status()
    return _publish(r.json()["id"])


def publish_reel(video_url, caption):
    r = requests.post(f"{GRAPH}/{IG_ID}/media", data={
        "media_type": "REELS", "video_url": video_url,
        "caption": caption, "share_to_feed": "true", "access_token": TOKEN})
    r.raise_for_status()
    cid = r.json()["id"]
    _wait_ready(cid)
    return _publish(cid)


def main():
    with open(os.path.join(OUT, "content.json")) as f:
        c = json.load(f)
    caption = c["caption"] + "\n.\n.\n" + " ".join("#" + h for h in c["hashtags"])

    print("Uploading media to Cloudinary...")
    img_url = cloudinary_upload(os.path.join(OUT, "post.jpg"), "image")
    vid_url = cloudinary_upload(os.path.join(OUT, "reel.mp4"), "video")

    print("Publishing feed post...")
    post_id = publish_image(img_url, caption, c.get("alt_text", ""))
    print("Feed post live:", post_id)

    time.sleep(60)  # posts ke beech thoda natural gap

    print("Publishing reel...")
    reel_id = publish_reel(vid_url, caption)
    print("Reel live:", reel_id)

    # History record — variety engine + analytics iske bharose hain
    from variety import load_history, save_history
    hist = load_history()
    hist["posted"].append({"date": c["date"], "topic": c["topic"], "style": c.get("style",""),
                            "palette": c.get("palette",""), "post_id": post_id, "reel_id": reel_id})
    save_history(hist)
    print("History saved.")


if __name__ == "__main__":
    main()
