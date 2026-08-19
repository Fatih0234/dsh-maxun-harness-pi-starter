#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
need python3
PORT="${FIXTURE_PORT:-4173}"
DIR="$PROJECT_ROOT/tests/fixtures/catalog"
echo "Serving fixture on http://127.0.0.1:$PORT/page1.html"
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$DIR"
