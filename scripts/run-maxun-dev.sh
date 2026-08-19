#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"
load_env
M="$PROJECT_ROOT/sources/maxun"
[[ -d "$M/node_modules" ]] || { echo "Install Maxun dependencies first" >&2; exit 1; }
[[ -n "${OPENCODE_API_KEY:-}" ]] || { echo "OPENCODE_API_KEY missing" >&2; exit 1; }

# Existing WorkflowEnricher's OpenAI-compatible path can use these operator credentials.
# The Goal-1 API seam should read MAXUN_AGENT_LLM_* and pass an llmConfig to
# WorkflowEnricher instead of accepting the provider key in model-facing arguments.
export MAXUN_AGENT_LLM_PROVIDER="${MAXUN_AGENT_LLM_PROVIDER:-openai}"
export MAXUN_AGENT_LLM_MODEL="${MAXUN_AGENT_LLM_MODEL:-deepseek-v4-flash}"
export MAXUN_AGENT_LLM_BASE_URL="${MAXUN_AGENT_LLM_BASE_URL:-https://opencode.ai/zen/go/v1}"
export MAXUN_AGENT_LLM_API_KEY="${MAXUN_AGENT_LLM_API_KEY:-$OPENCODE_API_KEY}"
# Also expose the standard OpenAI-compatible names used by existing Maxun helpers.
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-$MAXUN_AGENT_LLM_BASE_URL}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-$MAXUN_AGENT_LLM_API_KEY}"

echo "Starting Maxun dev processes with operator-side OpenAI-compatible LLM configuration (key not printed)."
exec bash -lc "cd $(printf %q "$M") && npm run start:dev"
