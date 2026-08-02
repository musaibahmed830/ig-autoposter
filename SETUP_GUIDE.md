# IG Auto-Poster — Setup Guide (Roman Urdu)

Roz automatically **1 feed post + 1 reel** — official Instagram Graph API se (koi ban risk nahi).

## System kya karta hai (roz 6 PM PKT)

1. `topics.json` se aaj ka topic uthata hai (30 topics, rotate hote hain)
2. Gemini API (free tier) se caption + 15 hashtags + alt-text + 4 slide texts likhwata hai
3. Pillow se branded post image (1080x1350) aur 4 vertical slides banata hai
4. ffmpeg se ~12 second ka reel banata hai (zoom + crossfade, optional music)
5. Cloudinary par upload karke Graph API se post + reel publish kar deta hai

---

## Step 1 — Naya account setup (ek dafa)

1. Instagram par account banao (mobile app se, apne asli phone/SIM se — VPN ke baghair)
2. **1-2 hafte warm-up karo**: profile complete karo, 3-4 manual posts, stories, kuch accounts follow karo. Naya account + turant automation unnatural lagta hai.
3. Settings → Account type → **Switch to Professional → Business**

## Step 2 — Meta Developer app (Instagram API with Instagram Login)

Facebook Page linking **zaroori nahi** — ye newer flow seedha Instagram account se connect hota hai.

1. https://developers.facebook.com/apps/ → **Create App** → type: **Business**
2. App mein **Instagram** product add karo → **API setup with Instagram login**
3. Us page par:
   - Permissions: `instagram_business_basic`, `instagram_business_content_publish`
   - **Generate access token** → apna Instagram account authorize karo → token milega (`IGAA…` se start hoga) — yehi **IG_ACCESS_TOKEN** (short-lived)
4. **IG_USER_ID nikalo**: browser mein ya curl se query chalao:
   ```
   https://graph.instagram.com/v21.0/me?fields=id,username&access_token={SHORT_TOKEN}
   ```
   Response ka `id` = **IG_USER_ID**
5. **Long-lived token banao** (60 din chalta hai):
   ```
   https://graph.instagram.com/v21.0/access_token?grant_type=ig_exchange_token&client_secret={INSTAGRAM_APP_SECRET}&access_token={SHORT_TOKEN}
   ```
   Response ka `access_token` = **IG_ACCESS_TOKEN** (long-lived)
   (Har ~50 din baad refresh karna — `grant_type=ig_refresh_token&access_token={LONG_TOKEN}` se — reminder laga lo)

## Step 3 — Cloudinary (free)

Graph API ko media ka **public URL** chahiye, is liye:

1. https://cloudinary.com → free account (25GB bandwidth/month — kaafi hai)
2. Dashboard se copy karo: **Cloud name**, **API Key**, **API Secret**

## Step 4 — GitHub par deploy

1. Naya **private repo** banao, ye poora folder push karo
2. Repo → Settings → **Secrets and variables → Actions**:

   **Secrets** (sensitive):
   | Secret | Value |
   |---|---|
   | `GEMINI_API_KEY` | aistudio.google.com/apikey se free API key |
   | `IG_USER_ID` | Step 2 wala ID |
   | `IG_ACCESS_TOKEN` | long-lived token |
   | `CLOUDINARY_CLOUD` | cloud name |
   | `CLOUDINARY_KEY` | API key |
   | `CLOUDINARY_SECRET` | API secret |

   **Variables** (branding):
   | Variable | Example |
   |---|---|
   | `BRAND_NAME` | Apni Agency |
   | `NICHE` | digital marketing agency |
   | `CITY` | Lahore |
   | `LANGUAGE` | English with Roman Urdu flavor |
   | `BRAND_COLOR` | #0f1b2d |
   | `ACCENT_COLOR` | #f7b32b |

3. **Actions** tab → "Daily IG Post + Reel" → **Run workflow** se manual test karo
4. Uske baad roz **6 PM PKT** khud chalega (`daily.yml` mein cron change kar sakte ho)

### Manual/on-demand post
"Run workflow" dabane par 2 optional fields milte hain:
- **topic**: khaali chhodo to auto-rotation chalegi, ya apna custom topic likho (jaise "TechNova at Karachi Tech Summit 2026")
- **category**: dropdown se content ka category choose karo (Technology, Event, Vlog, Travel, Food, etc.) — sirf tab matter karta hai jab topic bhi diya ho. Caption/hashtags us category ke hisab se adapt ho jate hain, brand niche se hat kar bhi.

## Local test (publish ke baghair)

```bash
pip install google-genai requests pillow
export GEMINI_API_KEY=AIza...
export BRAND_NAME="Apni Agency"
DRY_RUN=1 python run_daily.py     # out/ folder mein post.jpg + reel.mp4 check karo
```

## Music (optional)

`assets/music.mp3` rakh do to reel mein background music aa jayega.
**Sirf copyright-free music** use karo (e.g. Pixabay Music, YouTube Audio Library) — copyrighted track se reel mute/block ho sakta hai.

## Zaroori notes

- **Lead-scraping wale account se ye mat jorna** — posting hamesha is naye business account par, alag rakho
- Topics `topics.json` mein edit karo — apne niche ke hisab se
- Token expire ho jaye to Actions fail hoga — Step 2.5 se refresh karo
- Roz 2 publishes = limit (25/day) se bohat neeche, bilkul safe


---

# V2 Features

## Roz alag content (variety engine)
- **60 topics** — koi topic 45 din tak repeat nahi hota (`variety.py` enforce karta hai)
- **7 content formats** rotate: quick tips, myth-bust, question hook, mini story, stat shock, how-to, hot take — 3 din mein same format repeat nahi
- **5 color palettes + 3 layouts** roz rotate (background bhi accent-tinted, har din alag mood)
- **7 reel transitions** + duration variance (3.0–4.0s per slide) + kabhi 4, kabhi 5 slides
- Sab deterministic (date-seeded) — Actions retry par duplicate nahi banta

## Dashboard (GitHub Pages)
1. Repo → Settings → **Pages** → Source: **Deploy from a branch** → Branch: `main`, folder: `/docs`
2. URL milega: `https://<username>.github.io/<repo>/`
3. Roz 1 PM PKT auto-update hota hai: reach chart (14 din), followers, 7-din reach,
   avg reel views, engagement rate, har din ka full record (views/reach/likes/saves/shares), aur Advisor panel
4. **Private repo + Pages** GitHub Free par private repo ke saath nahi chalta — ya repo public rakho
   (secrets phir bhi safe hain, wo Actions secrets mein hain), ya dashboard ko sirf
   `docs/index.html` file download karke dekho, ya GitHub Pro le lo

## Reach Advisor
- Roz last 7 vs pichle 7 din ka avg reel reach compare karta hai
- **Agar reach >20% gira** to: (1) Gemini web-search se AAJ ke tactics research karta hai,
  (2) dashboard par tips dikhata hai, (3) "manual reel day" flag karta hai
- **Trending sounds ka sach:** Instagram API se in-app trending audio attach NAHI ho sakta
  (Meta ne allow hi nahi kiya). Is liye manual reel day par reel file ready milti hai —
  aap app se khud post karo aur trending sound wahan lagao. Baqi din automation chalta hai.

## Music rotation
`assets/music/` mein multiple copyright-free .mp3 rakho — roz rotate honge (Pixabay Music,
YouTube Audio Library se lo. Copyrighted track = reel mute/block risk).


## Connect Instagram wizard (dashboard se)

Ab token/ID ka setup dashboard se hi hota hai — `connect.html`:

1. Dashboard kholo → upar right mein **"Connect Instagram →"** button
2. Wizard 3 steps mein le jata hai (Instagram API with Instagram Login flow — koi Facebook Page linking nahi chahiye):
   - Meta Developer app → Instagram → API setup with Instagram login se token paste karo (link wizard mein hai)
   - Wizard token se aapka account **khud detect** kar ke dikhata hai (photo + followers ke saath)
   - Instagram App Secret daalo → wizard **long-lived token khud bana deta hai**
   - Copy buttons se dono values GitHub Secrets mein daalo + "Is browser mein save karo" dabao
3. Browser-save ke baad dashboard par **live status** dikhta hai: `● @yourhandle · live` (green),
   real-time followers, aur token expire hone se pehle **warning** (45 din ke baad amber ho jata hai)
4. Token expire ho jaye to pill red ho kar "reconnect" bolegi — wizard dobara chala do

**Privacy note:** wizard ke sab API calls aapke apne browser se directly Meta ko jate hain —
token/secret kisi aur server par nahi jata. Browser-save sirf usi device ke localStorage mein rehta hai.
