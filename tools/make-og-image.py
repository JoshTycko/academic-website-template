#!/usr/bin/env python3
"""Render the link-preview image (img/og.png, 1200x630) from the homepage.

The card shows the name (the homepage <h1>) and the role line (the hero
eyebrow) in the site's own fonts and light-mode colors, so it updates itself
when those change. Links shared in Slack, iMessage, X, LinkedIn, and so on show
this image.

    python3 tools/make-og-image.py            # this site
    python3 tools/make-og-image.py path/to/site

Needs Google Chrome or Chromium (set CHROME=/path/to/chrome if it isn't found).
"""
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

W, H = 1200, 630  # Open Graph's recommended size (1.91:1)

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent).resolve()
index = (root / "index.html").read_text()


def grab(pattern, what):
    m = re.search(pattern, index, re.S)
    if not m:
        sys.exit(f"ERROR: could not find {what} in {root / 'index.html'}")
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()


name = grab(r"<h1[^>]*>(.*?)</h1>", "the <h1> name")
role = grab(r'<p class="eyebrow[^"]*">(.*?)</p>', "the hero eyebrow (role line)")
# Light-mode tokens: the first :root block in the homepage's inline style.
root_block = grab(r":root\s*\{(.*?)\}", "the :root color tokens")
tokens = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", root_block))
for t in ("paper", "ink", "accent", "rule"):
    if t not in tokens:
        sys.exit(f"ERROR: --{t} not defined in the first :root block of index.html")

card = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Newsreader';src:url('fonts/newsreader-var.woff2') format('woff2');font-weight:200 800;}}
html,body{{margin:0;width:{W}px;height:{H}px;background:{tokens['paper']};}}
body{{display:flex;flex-direction:column;justify-content:center;padding:0 104px;box-sizing:border-box;
  border-bottom:6px solid {tokens['accent']};}}
.role{{font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace;font-size:26px;font-weight:500;
  letter-spacing:0.1em;text-transform:uppercase;color:{tokens['accent']};margin:0 0 28px;}}
h1{{font-family:'Newsreader',Georgia,serif;font-weight:450;font-size:104px;line-height:1;
  letter-spacing:-0.021em;color:{tokens['ink']};margin:0;}}
</style></head><body>
<p class="role">{html.escape(role)}</p>
<h1>{html.escape(name)}</h1>
</body></html>"""

chrome = os.environ.get("CHROME") or next(
    (c for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                 "/Applications/Chromium.app/Contents/MacOS/Chromium",
                 shutil.which("google-chrome"), shutil.which("chromium"),
                 shutil.which("chromium-browser")] if c and os.path.exists(c)), None)
if not chrome:
    sys.exit("ERROR: no Chrome/Chromium found. Install Chrome or set CHROME=/path/to/chrome.")

tmp = root / "_og-card.html"  # inside the site so the relative font path resolves
out = root / "img" / "og.png"
tmp.write_text(card)
try:
    if out.exists():
        out.unlink()
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--virtual-time-budget=2000",
                    f"--window-size={W},{H}", f"--screenshot={out}", tmp.as_uri()],
                   check=True, capture_output=True)
finally:
    tmp.unlink()
if not out.exists() or out.stat().st_size == 0:
    sys.exit(f"ERROR: Chrome did not write {out}")
print(f"wrote {out} ({W}x{H}): {name} / {role}")
