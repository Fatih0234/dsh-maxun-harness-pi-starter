# DeepSeek Harness provider setup

## Required route

```text
provider: opencode-go
model: deepseek-v4-flash
```

Harness's Pi-AI adapter supports catalog provider routes and resolves a configured `apiKeyEnv` per request.

This starter uses:

`config/deepseek-harness/settings.yaml`:

```yaml
llm-pi-ai:
  providers:
    opencode-go:
      apiKeyEnv: OPENCODE_API_KEY
```

and `config/deepseek-harness/opencode-go.patch.yml` changes the Harness default model to the route above.

`./scripts/import-pi-opencode-key.py` imports the existing Pi credential from `~/.pi/agent/auth.json` into ignored `.env.local` without printing it.

`./scripts/setup-harness-provider.sh` prepares `.local/dsh/settings.yaml` and dumps the effective Harness composition when the Harness checkout is built.

## Tests

Direct provider wire smoke:

```bash
./scripts/test-opencode-go-direct.sh
```

Harness model-path smoke:

```bash
./scripts/test-harness-headless.sh
```

Run these before debugging Maxun integration.

## Reusing the key for Maxun Goal-1 generation

The POC Maxun one-shot generator also needs an LLM. `scripts/run-maxun-dev.sh` maps the locally resolved test key to Maxun's OpenAI-compatible path using the OpenCode Go base URL. This credential remains server-side and is not passed through Harness tool arguments.
