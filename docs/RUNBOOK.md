# Local runbook

## One-time setup

```bash
./scripts/doctor.sh
./scripts/bootstrap-sources.sh
./scripts/import-pi-opencode-key.py
./scripts/install-source-deps.sh
./scripts/setup-harness-provider.sh
```

## Verify LLM provider

```bash
./scripts/test-opencode-go-direct.sh
./scripts/test-harness-headless.sh
./scripts/test-harness-suite.sh
```

`test-harness-suite.sh` pins pnpm 11.7.0, uses an English locale for the POSIX sandbox fixture, and applies a 30-second Vitest test timeout for this host's subprocess load. Override it with `DSH_TEST_TIMEOUT` when needed.

## Fixture

In one terminal:

```bash
./scripts/serve-fixtures.sh
```

The default fixture URL is `http://127.0.0.1:4173/page1.html`. If Maxun's browser runs in Docker, bind the fixture to `0.0.0.0` and use the Docker network gateway address instead; this workspace's evidence used `http://172.21.0.1:4173/page1.html`.

## Maxun

Use the pinned Maxun repository's own local/Docker setup instructions. The product needs its normal Postgres/worker/runtime dependencies. For Goal 2, launch Maxun with its browser service reachable and use the semantic Recorder Draft API; the Goal 1 one-shot `WorkflowEnricher` path remains only as a compatibility seam:

```bash
./scripts/run-maxun-dev.sh
```

This still requires Maxun's normal database/worker/runtime environment to be configured. Once Maxun is reachable, create a local account/API key either through its UI or:

```bash
./scripts/create-maxun-local-api-key.sh
```

If that helper reports a route mismatch, inspect Maxun's current server route mounts and update the helper rather than weakening authentication.

## Harness Web

```bash
./scripts/run-harness-web.sh
```

Default URL is `http://127.0.0.1:3080`.

## Optional Pi provider smoke

```bash
./scripts/run-pi-provider-smoke.sh
```

## Source and Goal checks

```bash
./scripts/verify-source-pins.sh
set -a; source .env.local; set +a
./scripts/verify-goal1-evidence.py
./scripts/verify-goal2-evidence.py
GOAL2_FIXTURE_URL=http://172.21.0.1:4173/page1.html GOAL2_CONFLICT_NAME='Fixture Products' ./scripts/test-goal2-live.py
(cd sources/deepseek-harness && GOAL3_LIVE=1 ./node_modules/.bin/vitest run packages/maxun/tool-maxun/tests/goal3-live.spec.ts)
./scripts/verify-goal3-evidence.py
```

Goal 2's normal semantic sequence is:

```text
maxun_create_recorder_draft
→ maxun_select_list_candidate
→ maxun_update_draft_field (include/exclude/rename)
→ maxun_preview_recorder_draft
→ maxun_validate_recorder_draft
→ maxun_compile_recorder_draft
→ maxun_run_robot
```

Goal 3 durable lifecycle acceptance uses the host-side key and the persisted Goal 2 draft/robot IDs. It explicitly claims the draft, verifies a second session receives `claim_conflict`, creates and health-checks a Maxun browser, cold-restores the same Harness session ID, reconnects while the browser survives, releases it, and verifies `resource_not_found` plus a degraded correlation projection. Browser/page telemetry is not recorded.

## Goal 4 regression baseline

Goal 4 implementation is complete. Review `docs/GOAL4_READINESS.md` before changing the browser view. The preflight baseline is:

```bash
./scripts/verify-source-pins.sh
./scripts/verify-goal1-evidence.py
./scripts/verify-goal2-evidence.py
./scripts/verify-goal3-evidence.py
(cd sources/maxun && npm run build:server)
(cd sources/deepseek-harness && ./node_modules/.bin/tsc -p tsconfig.host.json --noEmit)
```

Goal 4 executable checks cover claim-bound stream authorization, sensitive-input masking, screenshot fallback, details-panel placement/resize, reload reconnect, and no rrweb/frame leakage into model/session state. Run `scripts/test-goal4-rrweb-masking.js`, `scripts/test-goal4-live.js`, and the opt-in `apps/web/tests/maxun-browser.e2e.ts` acceptance test.

## Goal 5 acceptance

Read `goals/05-human-handoff.md` and `docs/GOAL5_READINESS.md`. The acceptance audit and live evidence must remain green before considering future changes safe:

```bash
python3 scripts/verify-goal5-readiness.py
./scripts/verify-source-pins.sh
```

Trace Maxun pause/resume/step/abort and Harness cancellation before editing. Keep Goal 4's browser details view read-only. Goal 5 implements server-side control ownership, control epochs, cancellation/quiescence, fresh-observation invalidation, workflow provenance, race tests, and credential-free MFA/login/CAPTCHA evidence. Preserve these guarantees in future changes.
