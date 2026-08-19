#!/usr/bin/env python3
from __future__ import annotations
import json, os, shlex, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
auth_path = Path(os.environ.get('PI_CODING_AGENT_DIR', str(Path.home()/'.pi/agent'))) / 'auth.json'
out_path = root / '.env.local'

if not auth_path.exists():
    raise SystemExit(f'Pi auth file not found: {auth_path}')
data = json.loads(auth_path.read_text())
entry = data.get('opencode-go') or data.get('opencode')
if not isinstance(entry, dict):
    raise SystemExit('No opencode-go (or opencode fallback) credential found in Pi auth.json')
raw = entry.get('key')
if not isinstance(raw, str) or not raw.strip():
    raise SystemExit('Pi OpenCode credential has no usable key field')
raw = raw.strip()
if raw.startswith('!'):
    key = subprocess.check_output(raw[1:], shell=True, text=True).strip()
elif raw in os.environ and os.environ[raw].strip():
    key = os.environ[raw].strip()
else:
    key = raw
if not key:
    raise SystemExit('Resolved OpenCode key is empty')

existing = {}
if out_path.exists():
    for line in out_path.read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1); existing[k]=v
existing.update({
    'OPENCODE_API_KEY': shlex.quote(key),
    'MAXUN_AGENT_LLM_PROVIDER': existing.get('MAXUN_AGENT_LLM_PROVIDER', 'openai'),
    'MAXUN_AGENT_LLM_MODEL': existing.get('MAXUN_AGENT_LLM_MODEL', 'deepseek-v4-flash'),
    'MAXUN_AGENT_LLM_BASE_URL': existing.get('MAXUN_AGENT_LLM_BASE_URL', 'https://opencode.ai/zen/go/v1'),
    'MAXUN_BASE_URL': existing.get('MAXUN_BASE_URL', 'http://127.0.0.1:8080/api'),
    'MAXUN_API_KEY': existing.get('MAXUN_API_KEY', ''),
    'FIXTURE_URL': existing.get('FIXTURE_URL', 'http://127.0.0.1:4173/page1.html'),
    'DSH_TELEMETRY_DISABLED': '1',
    'DSH_PERMISSION_MODE': 'workspace-write',
})
order=['OPENCODE_API_KEY','MAXUN_AGENT_LLM_PROVIDER','MAXUN_AGENT_LLM_MODEL','MAXUN_AGENT_LLM_BASE_URL','MAXUN_BASE_URL','MAXUN_API_KEY','FIXTURE_URL','DSH_TELEMETRY_DISABLED','DSH_PERMISSION_MODE']
out_path.write_text('\n'.join(f'{k}={existing[k]}' for k in order) + '\n')
os.chmod(out_path, 0o600)
print(f'Imported OpenCode credential into ignored {out_path} with mode 0600. Key not printed.')
