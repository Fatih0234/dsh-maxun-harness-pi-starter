#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
load_env
need curl
need python3

# Defaults match the researched Maxun API layout; inspect server route mounts if your checkout differs.
AUTH_BASE="${MAXUN_AUTH_BASE_URL:-${MAXUN_BASE_URL%/}/auth}"
EMAIL="${MAXUN_DEV_EMAIL:-pi-maxun@example.test}"
PASSWORD="${MAXUN_DEV_PASSWORD:-pi-maxun-local-password}"
COOKIE="$LOCAL_DIR/maxun-cookie.txt"
BODY="$LOCAL_DIR/maxun-auth-body.json"

payload=$(EMAIL="$EMAIL" PASSWORD="$PASSWORD" python3 - <<'PYMAXPAY'
import json,os
print(json.dumps({'email':os.environ['EMAIL'],'password':os.environ['PASSWORD']}))
PYMAXPAY
)

# Registration may legitimately fail because the user already exists.
curl -sS -c "$COOKIE" -H 'Content-Type: application/json' -d "$payload" "$AUTH_BASE/register" -o "$BODY" || true
curl -fsS -c "$COOKIE" -b "$COOKIE" -H 'Content-Type: application/json' -d "$payload" "$AUTH_BASE/login" -o "$BODY"

curl -fsS -b "$COOKIE" "$AUTH_BASE/api-key" -o "$BODY"
key=$(python3 - "$BODY" <<'PYMAXREAD'
import json,sys
d=json.load(open(sys.argv[1])); print(d.get('api_key') or '')
PYMAXREAD
)
if [[ -z "$key" ]]; then
  curl -fsS -b "$COOKIE" -X POST "$AUTH_BASE/generate-api-key" -o "$BODY"
  key=$(python3 - "$BODY" <<'PYMAXGEN'
import json,sys
d=json.load(open(sys.argv[1])); print(d.get('api_key') or '')
PYMAXGEN
)
fi
[[ -n "$key" ]] || { echo "Could not obtain Maxun API key; inspect $BODY and current Maxun route mounts" >&2; exit 1; }

KEY="$key" ENV_FILE="$ENV_FILE" python3 - <<'PYMAXENV'
from pathlib import Path
import os, shlex
p=Path(os.environ['ENV_FILE']); lines=p.read_text().splitlines() if p.exists() else []
out=[]; found=False
for line in lines:
    if line.startswith('MAXUN_API_KEY='):
        out.append('MAXUN_API_KEY='+shlex.quote(os.environ['KEY'])); found=True
    else: out.append(line)
if not found: out.append('MAXUN_API_KEY='+shlex.quote(os.environ['KEY']))
p.write_text('\n'.join(out)+'\n'); os.chmod(p,0o600)
PYMAXENV
rm -f "$COOKIE" "$BODY"
echo "Maxun API key saved to ignored .env.local. Key not printed."
