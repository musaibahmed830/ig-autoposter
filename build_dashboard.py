"""
Dashboard builder — analytics.json + advice.json se elegant static HTML banata hai.
Output: docs/index.html (GitHub Pages se serve hota hai, mobile-friendly).
Chart pure SVG hai (Python se generated) — koi external JS nahi, instant load.
"""
import os, json, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")

INK = "#0c1220"; PANEL = "#121a2b"; LINE = "#1e2a42"
AMBER = "#f7b32b"; TEXT = "#e8ecf4"; DIM = "#8b96ad"
GREEN = "#4ade80"; RED = "#f87171"


def spark_svg(points, w=760, h=220, color=AMBER):
    """Smooth area chart — reach pulse."""
    if len(points) < 2:
        return f'<svg viewBox="0 0 {w} {h}"><text x="{w/2}" y="{h/2}" fill="{DIM}" text-anchor="middle" font-size="14">Data aa raha hai…</text></svg>'
    mx = max(points) or 1
    pad = 18
    xs = [pad + i * (w - 2*pad) / (len(points) - 1) for i in range(len(points))]
    ys = [h - pad - (p / mx) * (h - 2.4*pad) for p in points]
    # smooth path (quadratic midpoints)
    d = f"M {xs[0]:.1f} {ys[0]:.1f}"
    for i in range(1, len(xs)):
        mxp, myp = (xs[i-1]+xs[i])/2, (ys[i-1]+ys[i])/2
        d += f" Q {xs[i-1]:.1f} {ys[i-1]:.1f} {mxp:.1f} {myp:.1f}"
    d += f" T {xs[-1]:.1f} {ys[-1]:.1f}"
    area = d + f" L {xs[-1]:.1f} {h-pad} L {xs[0]:.1f} {h-pad} Z"
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>' for x, y in zip(xs, ys))
    return f'''<svg viewBox="0 0 {w} {h}" role="img" aria-label="Reel reach trend">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{color}" stop-opacity="0.35"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>
</linearGradient>
<filter id="glow"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<path d="{area}" fill="url(#g)"/>
<path d="{d}" fill="none" stroke="{color}" stroke-width="3" filter="url(#glow)" stroke-linecap="round"/>
{dots}</svg>'''


def fmt(n):
    if n is None: return "—"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)


def build():
    def load(name, default):
        p = os.path.join(HERE, name)
        return json.load(open(p)) if os.path.exists(p) else default

    an = load("analytics.json", {"account": {}, "media": [], "updated": ""})
    ad = load("advice.json", {"status": "warming_up", "verdict": "Pehli reports ke baad advice yahan aayegi.", "tips": [], "manual_audio_day": False})
    brand = os.environ.get("BRAND_NAME", "My Brand")

    media = an.get("media", [])
    reel_reach = [m.get("reel", {}).get("reach") for m in media if isinstance(m.get("reel"), dict) and "reach" in m.get("reel", {})]
    reel_views = [m.get("reel", {}).get("views", 0) for m in media if isinstance(m.get("reel"), dict)]
    last7 = [m for m in media[-7:]]
    reach7 = sum((m.get("reel", {}).get("reach", 0) or 0) + (m.get("post", {}).get("reach", 0) or 0) for m in last7)
    likes7 = sum((m.get("reel", {}).get("likes", 0) or 0) + (m.get("post", {}).get("likes", 0) or 0) for m in last7)
    saves7 = sum((m.get("reel", {}).get("saved", 0) or 0) + (m.get("post", {}).get("saved", 0) or 0) for m in last7)
    eng = round((likes7 + saves7) / reach7 * 100, 1) if reach7 else 0
    avg_reel = round(sum(reel_views) / len(reel_views)) if reel_views else 0

    status = ad.get("status", "steady")
    chip_color = {"growing": GREEN, "falling": RED}.get(status, AMBER)
    chip_label = {"growing": "Growing ↑", "falling": "Falling ↓", "steady": "Steady →", "warming_up": "Warming up"}.get(status, status)

    manual_banner = ""
    if ad.get("manual_audio_day"):
        manual_banner = f'''<div class="banner">🎵 <b>Aaj manual reel day hai</b> — out/reel.mp4 ready hai, app se khud post karo aur <b>trending audio</b> lagao (API se trending sound attach nahi hota).</div>'''

    tips_html = "".join(f"<li>{html.escape(str(t))}</li>" for t in ad.get("tips", []))
    tips_block = f'<ul class="tips">{tips_html}</ul>' if tips_html else ""

    rows = ""
    for m in reversed(media[-14:]):
        r, p = m.get("reel", {}) or {}, m.get("post", {}) or {}
        rows += f'''<tr>
<td><span class="d">{html.escape(m.get("date",""))}</span><br><span class="t">{html.escape(m.get("topic","")[:48])}</span></td>
<td><span class="badge">{html.escape(m.get("style","—"))}</span></td>
<td class="num">{fmt(r.get("views"))}</td><td class="num">{fmt(r.get("reach"))}</td>
<td class="num">{fmt((r.get("likes",0) or 0)+(p.get("likes",0) or 0))}</td>
<td class="num">{fmt((r.get("saved",0) or 0)+(p.get("saved",0) or 0))}</td>
<td class="num">{fmt((r.get("shares",0) or 0)+(p.get("shares",0) or 0))}</td>
<td class="num">{fmt(p.get("reach"))}</td></tr>'''
    if not rows:
        rows = f'<tr><td colspan="8" style="text-align:center;color:{DIM};padding:34px">Pehli post ke baad yahan har din ka record aayega.</td></tr>'

    chart = spark_svg(reel_reach[-14:] if reel_reach else [])
    updated = an.get("updated", "")[:16].replace("T", " ")
    followers = fmt(an.get("account", {}).get("followers", 0))

    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(brand)} — Content Autopilot</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root {{ --ink:{INK}; --panel:{PANEL}; --line:{LINE}; --amber:{AMBER}; --text:{TEXT}; --dim:{DIM}; }}
* {{ box-sizing:border-box; margin:0; }}
body {{ background:var(--ink); color:var(--text); font:15px/1.6 Inter,system-ui,sans-serif;
  background-image:radial-gradient(1100px 500px at 80% -10%, rgba(247,179,43,.07), transparent); }}
.wrap {{ max-width:960px; margin:0 auto; padding:32px 20px 64px; }}
header {{ display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:8px; margin-bottom:26px; }}
h1 {{ font:700 26px Sora,sans-serif; letter-spacing:-.02em; }}
h1 em {{ font-style:normal; color:var(--amber); }}
.sub {{ color:var(--dim); font-size:13px; }}
.hright {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; }}
.pill {{ font:500 12.5px 'JetBrains Mono',monospace; text-decoration:none; color:var(--amber);
  border:1px solid var(--amber); border-radius:99px; padding:6px 14px; }}
.pill.live {{ color:{GREEN}; border-color:{GREEN}; }}
.pill.warn {{ color:{RED}; border-color:{RED}; }}
.hero {{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:22px 22px 10px; margin-bottom:18px; }}
.hero-top {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:10px; }}
.hero-top h2 {{ font:600 15px Sora,sans-serif; color:var(--dim); text-transform:uppercase; letter-spacing:.09em; }}
.chip {{ font:500 13px 'JetBrains Mono',monospace; padding:5px 14px; border-radius:99px; border:1px solid {chip_color}; color:{chip_color}; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:18px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:16px 18px; }}
.card .v {{ font:500 26px 'JetBrains Mono',monospace; color:var(--text); }}
.card .l {{ color:var(--dim); font-size:12.5px; margin-top:2px; }}
.advice {{ background:var(--panel); border:1px solid var(--line); border-left:4px solid var(--amber);
  border-radius:14px; padding:18px 20px; margin-bottom:18px; }}
.advice h3 {{ font:600 14px Sora,sans-serif; color:var(--amber); margin-bottom:6px; text-transform:uppercase; letter-spacing:.08em; }}
.tips {{ margin:10px 0 0 18px; color:var(--text); }} .tips li {{ margin-bottom:6px; }}
.banner {{ background:rgba(247,179,43,.12); border:1px solid var(--amber); border-radius:12px;
  padding:13px 16px; margin-bottom:18px; font-size:14px; }}
.log {{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:8px 6px; overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; min-width:640px; }}
th {{ font:600 11.5px Sora,sans-serif; color:var(--dim); text-transform:uppercase; letter-spacing:.07em;
  text-align:left; padding:12px 12px 8px; border-bottom:1px solid var(--line); }}
td {{ padding:12px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
.num {{ font:500 14px 'JetBrains Mono',monospace; text-align:right; }}
th.num-h {{ text-align:right; }}
.d {{ font:500 12px 'JetBrains Mono',monospace; color:var(--dim); }}
.t {{ font-size:13.5px; }}
.badge {{ font-size:11.5px; color:var(--amber); border:1px solid var(--line); padding:3px 9px; border-radius:99px; white-space:nowrap; }}
footer {{ color:var(--dim); font-size:12px; margin-top:22px; text-align:center; }}
@media (prefers-reduced-motion:no-preference) {{ .hero svg path {{ transition:d .4s; }} }}
</style></head><body><div class="wrap">
<header><h1>{html.escape(brand)} <em>· Autopilot</em></h1>
<div class="hright"><a id="igstatus" class="pill" href="connect.html">Connect Instagram →</a><span class="sub">Updated {updated} UTC</span></div></header>
{manual_banner}
<section class="hero"><div class="hero-top"><h2>Reel reach — last 14 din</h2><span class="chip">{chip_label}</span></div>{chart}</section>
<section class="cards">
<div class="card"><div class="v">{followers}</div><div class="l">Followers</div></div>
<div class="card"><div class="v">{fmt(reach7)}</div><div class="l">Reach · 7 din</div></div>
<div class="card"><div class="v">{fmt(avg_reel)}</div><div class="l">Avg reel views</div></div>
<div class="card"><div class="v">{eng}%</div><div class="l">Engagement rate</div></div>
<div class="card"><div class="v">{len(media)}</div><div class="l">Din tracked</div></div>
</section>
<section class="advice"><h3>Advisor</h3><p>{html.escape(ad.get("verdict",""))}</p>{tips_block}</section>
<section class="log"><table>
<thead><tr><th>Din / Topic</th><th>Format</th><th class="num-h">Reel views</th><th class="num-h">Reel reach</th>
<th class="num-h">Likes</th><th class="num-h">Saves</th><th class="num-h">Shares</th><th class="num-h">Post reach</th></tr></thead>
<tbody>{rows}</tbody></table></section>
<footer>Auto-generated daily · Official Instagram Graph API · <a href="connect.html" style="color:var(--dim)">Connection settings</a></footer>
</div>
<script>
(function(){{
  var el=document.getElementById('igstatus');
  var raw=localStorage.getItem('ig_autopilot'); if(!raw)return;
  var cfg; try{{cfg=JSON.parse(raw)}}catch(e){{return}}
  var days=(Date.now()-(cfg.saved||0))/86400000;
  fetch('https://graph.facebook.com/v21.0/'+cfg.igId+'?fields=username,followers_count&access_token='+encodeURIComponent(cfg.token))
    .then(function(r){{return r.json()}})
    .then(function(d){{
      if(d.error){{el.textContent='⚠ Token expired — reconnect';el.classList.add('warn');return}}
      el.textContent='● @'+d.username+' · live';el.classList.add('live');
      var v=document.querySelector('.cards .card .v');
      if(v&&d.followers_count!=null){{v.textContent=d.followers_count>=1000?(d.followers_count/1000).toFixed(1)+'K':d.followers_count}}
      if(days>45){{el.textContent='● @'+d.username+' · token '+Math.round(60-days)+' din mein expire';el.classList.remove('live');el.classList.add('warn')}}
    }}).catch(function(){{}});
}})();
</script>
</body></html>'''

    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "index.html"), "w") as f:
        f.write(page)
    print("Dashboard built: docs/index.html")


if __name__ == "__main__":
    build()
