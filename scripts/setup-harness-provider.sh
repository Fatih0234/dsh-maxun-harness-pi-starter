#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
load_env
[[ -n "${OPENCODE_API_KEY:-}" ]] || { echo "OPENCODE_API_KEY missing. Run import-pi-opencode-key.py" >&2; exit 1; }
H="$PROJECT_ROOT/sources/deepseek-harness"
[[ -d "$H/.git" ]] || { echo "Harness source missing" >&2; exit 1; }
[[ -f "$H/apps/cli/lib/bin.js" ]] || { echo "Build Harness first" >&2; exit 1; }
DSH_HOME_DIR="$LOCAL_DIR/dsh"
mkdir -p "$DSH_HOME_DIR"
cp "$PROJECT_ROOT/config/deepseek-harness/settings.yaml" "$DSH_HOME_DIR/settings.yaml"
chmod 600 "$DSH_HOME_DIR/settings.yaml"

export DSH_HOME="$DSH_HOME_DIR"
PATCH="$PROJECT_ROOT/config/deepseek-harness/opencode-go.patch.yml"
if [[ -d "$H/node_modules" ]]; then
  echo "Dumping effective Harness config"
  (cd "$PROJECT_ROOT" && node "$H/apps/cli/lib/bin.js" --profile web --patch "$PATCH" --dump-config) > "$LOCAL_DIR/harness-composed.yml" 2> "$LOCAL_DIR/harness-composed.stderr" || {
    echo "Config dump failed; inspect $LOCAL_DIR/harness-composed.stderr" >&2; exit 1;
  }
  grep -q 'provider: opencode-go' "$LOCAL_DIR/harness-composed.yml" || { echo "opencode-go default not present in composed config" >&2; exit 1; }
  grep -q 'model: deepseek-v4-flash' "$LOCAL_DIR/harness-composed.yml" || { echo "deepseek-v4-flash default not present" >&2; exit 1; }
  echo "Harness provider config verified."
else
  echo "Prepared $DSH_HOME_DIR/settings.yaml. Build Harness before config verification."
fi
