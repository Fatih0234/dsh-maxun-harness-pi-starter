# Test strategy

## Principle

The first integration should be deterministic. Public ecommerce sites are secondary exploratory tests because anti-bot behavior and markup changes make failures ambiguous.

## Fixture

Run:

```bash
./scripts/serve-fixtures.sh
```

Page 1:

```text
http://127.0.0.1:4173/page1.html
```

The fixture has six products, two per page, with ordinary `Next` navigation. Goal 1 requests the first five.

## Expected semantic fields

- product name
- price
- rating
- review count
- image URL
- product URL

Do not make acceptance depend on one exact capitalization of Maxun's semantic labels. The E2E assertion should map the selected labels to requested semantics and values.

## Goal 2 semantic contract

The normal construction sequence is:

```text
create draft → select opaque list → semantic field edits → preview
→ multi-page validation → compile native scrapeList → normal run
```

Run the live contract with a Docker-reachable fixture URL:

```bash
GOAL2_FIXTURE_URL=http://172.21.0.1:4173/page1.html \
GOAL2_CONFLICT_NAME='Fixture Products' ./scripts/test-goal2-live.py
```

The contract verifies that public draft/compile responses contain no server-owned selectors, pagination becomes `tested` only after a second page is observed, validation coverage is keyed by field ID, and robot-name conflicts are structured.

## Goal 3 durable-state contract

The implemented contract verifies:

```text
custom durable events → compact correlation projection → refresh/cold reconstruction
```

Unit and mocked Harness coverage:

```bash
./node_modules/.bin/vitest run \
  packages/maxun/tool-maxun/tests/correlation.spec.ts \
  packages/maxun/tool-maxun/tests/tool-maxun.spec.ts
```

Live acceptance, using the existing deterministic draft/robot and host-side `MAXUN_API_KEY`:

```bash
GOAL3_LIVE=1 ./node_modules/.bin/vitest run packages/maxun/tool-maxun/tests/goal3-live.spec.ts
python3 scripts/verify-goal3-evidence.py
```

Acceptance covers a surviving browser reconnect after `Session.fromRestore`, a gone browser while durable draft/robot IDs remain available, explicit same-owner/idempotent and competing-owner/epoch-checked claims, projection reconstruction, empty derived model messages, and proof that rrweb/mouse/DOM markers and credentials never enter the persisted event artifact. The opt-in live test is skipped unless `GOAL3_LIVE=1`.

## Goal 4 browser UI readiness contract

Goal 4 implementation is complete. Its tests preserve the Goal 3 boundary while adding the visual path. The live acceptance entry points are `scripts/test-goal4-live.js`, `scripts/test-goal4-rrweb-masking.js`, and `apps/web/tests/maxun-browser.e2e.ts`:

- **Stream authorization:** owner/epoch/expiry checks, foreign-session rejection, gone-browser behavior, reconnect after Harness reload, and service-instance/browser/session correlation.
- **Privacy:** deterministic sensitive fixture covering password, ordinary input, contenteditable, iframe, canvas, and sensitive text; assert masking/blocking and no credential/frame leakage into model messages or durable session events.
- **Renderer:** full-snapshot start, incremental event replay, full-snapshot reset, reconnect/backoff, bounded buffering, cleanup on session/browser change, and screenshot fallback.
- **Harness UI:** persistent/resizable details placement, session/browser-keyed remount, active/reconnecting/gone/degraded states, and proof that no historical chat row or model turn changes.
- **Integration:** Playwright Web reload with a surviving Maxun browser and screenshot fallback; Goal 3 covers gone/foreign/stale ownership cases.
- **Licensing:** preserve the selected renderer dependency/license/notice review as non-secret evidence.

## Goal 5 human/agent handoff acceptance

Goal 5 implementation is complete. Live tests cover two-owner control conflicts, stale/foreign epochs, delayed navigation/action races, cancellation during browser work, fresh-observation barriers, workflow-edit provenance, and MFA/login/CAPTCHA credential exclusion. Secret sentinels remain outside evidence, and the complete Goal 1–4 regression set passes.

The handoff contract and executable acceptance audit are `docs/GOAL5_READINESS.md` and `scripts/verify-goal5-readiness.py`.

## Layers

### Provider smoke

```bash
./scripts/test-opencode-go-direct.sh
./scripts/test-harness-headless.sh
```

### Maxun tests

- shared generation/persistence helper unit/integration coverage;
- Recorder Draft discovery/persistence with opaque public state;
- API-key authorization and structured robot-name conflict;
- invalid URL/request and validation diagnostics;
- pagination preview/testing and field-ID coverage;
- persisted workflow contains native `scrapeList`;
- rerun saved robot and Goal 1 compatibility route.

### Harness tests

Use an HTTP mock for the Maxun service first:

- correct request and `x-api-key` header;
- cancellation;
- Maxun error normalization;
- no API-key leakage in output;
- tool schemas and model-visible result size.

### Real integration

Fixture → Maxun creation API → saved robot → execute → expected first five products.

### Agent integration

Harness headless session with `opencode-go/deepseek-v4-flash` should autonomously use the Maxun tools from the natural-language request.

### Web acceptance

Use the installed `playwright-cli` only after inspecting its help:

```bash
playwright-cli --help
```

Exercise the Harness Web UI, create a session, send the fixture request, wait for tool/result completion, verify five rows/summary, reload and verify the completed result remains visible.

Store non-secret evidence under `.local/evidence/`.
