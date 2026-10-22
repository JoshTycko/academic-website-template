#!/usr/bin/env bash
# Screenshot every page at desktop and phone width, in light and dark mode,
# using headless Chrome (no packages to install). Output: screenshots/*.png
#
#   bash tools/screenshots.sh            # serves the site itself on port 8765
#   PORT=8000 bash tools/screenshots.sh  # use a server you already started
#
# Each shot is one tall viewport rather than a true full-page capture, so very
# long pages may be cut off at the bottom; raise the heights below if needed.
set -euo pipefail
cd "$(dirname "$0")/.."

CHROME="${CHROME:-}"
if [[ -z "$CHROME" ]]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "$(command -v google-chrome || true)" "$(command -v chromium || true)" \
           "$(command -v chromium-browser || true)"; do
    if [[ -n "$c" && -x "$c" ]]; then CHROME="$c"; break; fi
  done
fi
if [[ -z "$CHROME" ]]; then
  echo "ERROR: no Chrome/Chromium found. Install Chrome or set CHROME=/path/to/chrome." >&2
  exit 1
fi

PORT="${PORT:-}"
if [[ -z "$PORT" ]]; then
  PORT=8765
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  SERVER=$!
  trap 'kill $SERVER 2>/dev/null' EXIT
  sleep 1
fi

mkdir -p screenshots
shoot () {  # page name, width, height, scheme (0 = dark, 1 = light)
  local page=$1 w=$2 h=$3 scheme=$4 mode
  [[ $scheme == 0 ]] && mode=dark || mode=light
  local out="screenshots/${page%.html}-${w}-${mode}.png"
  # virtual-time-budget lets the entrance animations finish before capture.
  "$CHROME" --headless --disable-gpu --hide-scrollbars --virtual-time-budget=3000 \
    --blink-settings=preferredColorScheme=$scheme \
    --window-size="$w,$h" --screenshot="$out" \
    "http://localhost:$PORT/$page" >/dev/null 2>&1
  [[ -s "$out" ]] || { echo "ERROR: $out was not written" >&2; exit 1; }
  echo "$out"
}

for page in index.html publications.html 404.html; do
  for scheme in 1 0; do
    shoot "$page" 1280 2800 "$scheme"
    shoot "$page" 390 4200 "$scheme"
  done
done
