#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_DIR="$PROJECT_ROOT/.local"
ENV_FILE="$PROJECT_ROOT/.env.local"
mkdir -p "$LOCAL_DIR" "$LOCAL_DIR/evidence"

load_env() {
  if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi
  export DSH_TELEMETRY_DISABLED="${DSH_TELEMETRY_DISABLED:-1}"
  export DSH_PERMISSION_MODE="${DSH_PERMISSION_MODE:-workspace-write}"
  export MAXUN_BASE_URL="${MAXUN_BASE_URL:-http://127.0.0.1:8080/api}"
  export FIXTURE_URL="${FIXTURE_URL:-http://127.0.0.1:4173/page1.html}"
}

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }; }

ensure_pnpm() {
  local local_bin="$LOCAL_DIR/pnpm/node_modules/.bin"
  local desired="11.7.0"

  # Prefer the ignored pinned binary. A Corepack shim can report success for a
  # different version and then select the source package's pnpm at exec time,
  # which is broken under this host's Node/runtime combination.
  if [[ -x "$local_bin/pnpm" ]]; then
    export PATH="$local_bin:$PATH"
    [[ "$(pnpm --version 2>/dev/null)" == "$desired" ]] && return
  fi

  need npm
  if [[ ! -x "$local_bin/pnpm" ]]; then
    echo "Installing pinned pnpm $desired into ignored $LOCAL_DIR/pnpm"
    npm install --no-save --prefix "$LOCAL_DIR/pnpm" "pnpm@$desired" >/dev/null
  fi
  export PATH="$local_bin:$PATH"
  [[ "$(pnpm --version 2>/dev/null)" == "$desired" ]] || { echo "pnpm $desired is unavailable" >&2; exit 1; }
}
