#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
load_env
H="$PROJECT_ROOT/sources/deepseek-harness"
[[ -f "$H/apps/cli/lib/bin.js" ]] || { echo "Build Harness first" >&2; exit 1; }
export DSH_HOME="$LOCAL_DIR/dsh"
mkdir -p "$DSH_HOME"
cp "$PROJECT_ROOT/config/deepseek-harness/settings.yaml" "$DSH_HOME/settings.yaml"
PATCH="$PROJECT_ROOT/config/deepseek-harness/opencode-go.patch.yml"
echo "Starting Harness at its default Web address (normally http://127.0.0.1:3080)"
exec node "$H/apps/cli/lib/bin.js" --profile web --patch "$PATCH" "$@"
