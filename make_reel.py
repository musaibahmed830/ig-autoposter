"""
Reel (ffmpeg) — transition + duration roz variety plan se badalti hai.
Music: assets/music/*.mp3 mein se din ke hisab se rotate (copyright-free rakhna!).
"""
import os, glob, json, subprocess, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
MUSIC_DIR = os.path.join(HERE, "assets", "music")
FADE, FPS = 0.6, 30


def pick_music():
    tracks = sorted(glob.glob(os.path.join(MUSIC_DIR, "*.mp3")))
    if not tracks:
        return None
    return tracks[datetime.date.today().toordinal() % len(tracks)]


def build():
    with open(os.path.join(OUT, "content.json")) as f:
        c = json.load(f)
    slide_sec, trans = c.get("slide_sec", 3.5), c.get("transition", "fade")
    slides = sorted(glob.glob(os.path.join(OUT, "slide_*.jpg")))
    n = len(slides)
    frames = int(slide_sec * FPS)

    inputs, filters = [], []
    for i, s in enumerate(slides):
        inputs += ["-loop", "1", "-t", str(slide_sec), "-i", s]
        filters.append(
            f"[{i}:v]scale=2160:3840,zoompan=z='1+0.0008*on':d={frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={FPS},setsar=1[v{i}]")

    prev, off = "v0", slide_sec - FADE
    for i in range(1, n):
        outl = f"x{i}" if i < n-1 else "vout"
        filters.append(f"[{prev}][v{i}]xfade=transition={trans}:duration={FADE}:offset={off:.2f}[{outl}]")
        prev = outl; off += slide_sec - FADE

    total = slide_sec*n - FADE*(n-1)
    out_path = os.path.join(OUT, "reel.mp4")
    cmd = ["ffmpeg", "-y"] + inputs
    music = pick_music()
    if music:
        cmd += ["-stream_loop", "-1", "-i", music,
                "-filter_complex", ";".join(filters), "-map", "[vout]", "-map", f"{n}:a",
                "-t", f"{total:.2f}", "-af", f"afade=out:st={total-1:.2f}:d=1"]
    else:
        cmd += ["-filter_complex", ";".join(filters), "-map", "[vout]", "-t", f"{total:.2f}"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out_path]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Reel ready: {total:.1f}s, transition={trans}, music={os.path.basename(music) if music else 'none'}")
    return out_path


if __name__ == "__main__":
    build()
