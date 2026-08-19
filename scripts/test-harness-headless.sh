#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
load_env
[[ -n "${OPENCODE_API_KEY:-}" ]] || { echo "OPENCODE_API_KEY missing" >&2; exit 1; }
H="$PROJECT_ROOT/sources/deepseek-harness"
[[ -f "$H/apps/cli/lib/bin.js" ]] || { echo "Build Harness first" >&2; exit 1; }
export DSH_HOME="$LOCAL_DIR/dsh"
mkdir -p "$DSH_HOME"
cp "$PROJECT_ROOT/config/deepseek-harness/settings.yaml" "$DSH_HOME/settings.yaml"
PATCH="$PROJECT_ROOT/config/deepseek-harness/opencode-go.patch.yml"
OUT="$LOCAL_DIR/harness-headless-smoke.txt"
(cd "$PROJECT_ROOT" && node "$H/apps/cli/lib/bin.js" --profile headless --patch "$PATCH" "Reply exactly with HARNESS_OPENCODE_GO_OK") | tee "$OUT"
grep -q 'HARNESS_OPENCODE_GO_OK' "$OUT" || { echo "Harness smoke sentinel missing" >&2; exit 1; }
cp "$OUT" "$LOCAL_DIR/evidence/harness-headless-provider.txt"
echo "Harness headless provider smoke passed."
