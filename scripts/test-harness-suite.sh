#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
load_env
ensure_pnpm
H="$PROJECT_ROOT/sources/deepseek-harness"
[[ -d "$H/node_modules" ]] || { echo "Install Harness dependencies first" >&2; exit 1; }

# The sandbox contract fixture relies on POSIX English diagnostics. The longer
# timeout covers the repository's oxlint subprocess contract under this host's
# parallel Vitest load without weakening any assertion.
export LANG=C
export LANGUAGE=C
export LC_ALL=C
TIMEOUT="${DSH_TEST_TIMEOUT:-30000}"
(cd "$H" && pnpm exec vitest run --testTimeout "$TIMEOUT")
