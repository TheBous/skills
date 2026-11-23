#!/usr/bin/env bash
# Launch demo-shop, screenshot the product page at desktop and phone width, stop it. Prints the evidence folder.
set -euo pipefail
cd "$(dirname "$0")/.."
CHROME=$(ls ~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1)
[ -x "$CHROME" ] || { echo "doctor: headless chromium not found" >&2; exit 1; }
OUT="$PWD/.verify/evidence/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT"
PORT=$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 -m http.server "$PORT" --bind 127.0.0.1 >"$OUT/server.log" 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
for _ in $(seq 1 50); do curl -sf "http://127.0.0.1:$PORT/" >/dev/null && break; sleep 0.2; done
shot() { "$CHROME" --no-sandbox --headless --disable-gpu --hide-scrollbars --screenshot="$OUT/$1.png" --window-size="$2" "http://127.0.0.1:$PORT/" >/dev/null 2>&1; }
shot desktop 1280,800
shot phone 390,844
echo "evidence: $OUT"
