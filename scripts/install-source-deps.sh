#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

H="$PROJECT_ROOT/sources/deepseek-harness"
M="$PROJECT_ROOT/sources/maxun"
[[ -d "$H/.git" && -d "$M/.git" ]] || { echo "Run bootstrap-sources.sh first" >&2; exit 1; }

need node
need npm
ensure_pnpm

echo "Installing/building DeepSeek Harness"
(cd "$H" && pnpm install --frozen-lockfile && pnpm run build)

echo "Installing/building Maxun server"
if [[ -f "$M/package-lock.json" ]]; then
  (cd "$M" && npm ci && npm run build:server)
else
  (cd "$M" && npm install && npm run build:server)
fi

echo "Source dependencies built. Maxun still needs its normal database/runtime services before launch."
