#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

printf '%-18s %s\n' 'project' "$PROJECT_ROOT"
for cmd in git node npm python3 curl; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%-18s %s\n' "$cmd" "$(command -v "$cmd")"
  else
    printf '%-18s %s\n' "$cmd" 'MISSING'
  fi
done
for cmd in pnpm pi playwright-cli docker; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%-18s %s\n' "$cmd" "$(command -v "$cmd")"
  else
    printf '%-18s %s\n' "$cmd" 'not found (may be optional until its stage)'
  fi
done

AUTH_PATH="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/auth.json"
if [[ -f "$AUTH_PATH" ]]; then
  echo "Pi auth file: found at $AUTH_PATH (contents not printed)"
else
  echo "Pi auth file: not found at $AUTH_PATH" >&2
fi

echo "Next: ./scripts/bootstrap-sources.sh"
