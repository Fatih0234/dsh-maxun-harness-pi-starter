#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
need pi
OUT="$LOCAL_DIR/pi-provider-smoke.txt"
pi --provider opencode-go --model deepseek-v4-flash -p 'Reply exactly with PI_OPENCODE_GO_OK' | tee "$OUT"
grep -q 'PI_OPENCODE_GO_OK' "$OUT" || { echo "Pi provider sentinel missing" >&2; exit 1; }
cp "$OUT" "$LOCAL_DIR/evidence/pi-provider-smoke.txt"
