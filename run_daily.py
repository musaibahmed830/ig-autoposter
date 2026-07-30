"""Poora daily pipeline: content -> images -> reel -> publish."""
import os, json, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script):
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, os.path.join(HERE, script)], check=True)


if __name__ == "__main__":
    run("generate_content.py")
    run("make_image.py")
    run("make_reel.py")
    if os.environ.get("DRY_RUN") == "1":
        print("\nDRY_RUN=1 — publish skip kiya. out/ folder check karo.")
    else:
        run("publish.py")
    print("\nDone ✅")
