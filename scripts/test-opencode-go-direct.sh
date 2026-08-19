#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
load_env
need curl
need python3
[[ -n "${OPENCODE_API_KEY:-}" ]] || { echo "OPENCODE_API_KEY missing" >&2; exit 1; }
OUT="$LOCAL_DIR/opencode-go-direct.json"
CODE=$(curl -sS -o "$OUT" -w '%{http_code}' \
  -H "Authorization: Bearer $OPENCODE_API_KEY" \
  -H 'Content-Type: application/json' \
  https://opencode.ai/zen/go/v1/chat/completions \
  --data-binary '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Reply exactly with OPENCODE_GO_OK"}],"max_tokens":64}')
if [[ "$CODE" -lt 200 || "$CODE" -ge 300 ]]; then
  echo "OpenCode Go smoke HTTP $CODE" >&2
  python3 - "$OUT" <<'PYODERR'
import json,sys
try:
 d=json.load(open(sys.argv[1])); print(json.dumps(d,indent=2)[:2000])
except Exception: print(open(sys.argv[1]).read()[:2000])
PYODERR
  exit 1
fi
python3 - "$OUT" <<'PYOD'
import json,sys
d=json.load(open(sys.argv[1])); text=d.get('choices',[{}])[0].get('message',{}).get('content','')
print(text)
if 'OPENCODE_GO_OK' not in text: raise SystemExit('Provider responded but sentinel was not found')
PYOD
cp "$OUT" "$LOCAL_DIR/evidence/provider-direct.json"
echo "Direct opencode-go/deepseek-v4-flash smoke passed."
