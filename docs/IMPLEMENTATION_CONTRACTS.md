# Proposed contracts — treat names as provisional

These are shape constraints for the coding agent, not a requirement to use exact route/tool names.

## POC Maxun creation request

Implemented at `POST /api/sdk/robots/list` with `x-api-key` authentication. The endpoint reads the generator credential from trusted Maxun server environment; callers do not send provider or key fields.

```json
{
  "url": "http://127.0.0.1:4173/page1.html",
  "prompt": "Get product name, price, rating, image URL, product URL and review count. Follow pagination and collect the first 5 products.",
  "name": "Fixture Products"
}
```

## POC Maxun creation response

Return a compact, stable summary. Do not return screenshots/base64 or huge raw HTML.

```json
{
  "robotId": "...",
  "name": "Fixture Products",
  "url": "...",
  "type": "extract",
  "fields": ["Product Name", "Price", "Rating", "Image URL", "Product URL", "Review Count"],
  "pagination": { "type": "clickNext" },
  "limit": 5
}
```

If existing Maxun naming differs, normalize at the Harness client boundary rather than changing Maxun internals gratuitously.

## Harness model tools for Goal 1 compatibility

The host plugin is `@deepseek-ai/dsh-tool-maxun`, mounted by `config/deepseek-harness/opencode-go.patch.yml`. It calls Maxun's API-key routes from the Harness process only. The original one-shot tool is retained in this document as historical POC contract; Goal 2 normal construction uses the semantic tools below.

### `maxun_create_list_robot`

Model input:

- `url` required;
- `request` required natural-language extraction request;
- `name` optional.

Model-visible result:

- robot ID;
- selected field names;
- pagination mode;
- limit;
- concise warnings.

### `maxun_run_robot`

Input:

- `robot_id` required.

Result:

- run ID;
- final status;
- compact list rows (subject to normal Harness tool-result spill/pruning behavior).

## Errors

Use structured codes/messages where feasible:

- service unavailable;
- Maxun auth failure;
- workflow generation failed;
- workflow validation failed;
- robot not found;
- run failed/aborted;
- caller cancelled.

Never include either API key in error objects or log messages.

## Goal 2 semantic Recorder Draft API

Implemented behind the same API-key boundary. The model-facing Harness client uses these routes for normal construction:

```text
POST /api/sdk/recorder/drafts
GET  /api/sdk/recorder/drafts/:draftId
POST /api/sdk/recorder/drafts/:draftId/select-list
POST /api/sdk/recorder/drafts/:draftId/fields
POST /api/sdk/recorder/drafts/:draftId/options
POST /api/sdk/recorder/drafts/:draftId/preview
POST /api/sdk/recorder/drafts/:draftId/validate
POST /api/sdk/recorder/drafts/:draftId/compile
```

The draft state is persisted in Maxun's `recorder_draft` table. Responses expose only opaque IDs and semantic metadata:

```text
listCandidateId: { tag, count, samples, attributes, fields, pagination }
fieldId: { sourceLabel, label, attribute, tag, samples, included }
```

Selectors remain private to Maxun's draft state. Field operations are `include`, `exclude`, and `rename`; validation scopes are `current-page` and `multi-page`; compile produces a deterministic native `scrapeList` workflow. Pagination metadata reports `tested: false` for a merely detected next control and is persisted as tested only after preview successfully advances at least one page. Validation coverage is keyed by opaque field ID, not the mutable field label.

Stable identity is separate from mutable labels:

```text
draftId
listCandidateId
fieldId
compiledRobotId
```

## Goal 2 Harness semantic tools

`@deepseek-ai/dsh-tool-maxun` now registers:

- `maxun_create_recorder_draft`
- `maxun_select_list_candidate`
- `maxun_update_draft_field`
- `maxun_preview_recorder_draft`
- `maxun_validate_recorder_draft`
- `maxun_compile_recorder_draft`
- `maxun_run_robot`

The Goal 1 `maxun_create_list_robot` client is no longer registered for normal Goal 2 construction. The Maxun endpoint remains available as a compatibility seam. Draft compile name conflicts return structured `robot_name_conflict`/HTTP 409 errors rather than an internal error.

## Goal 3 durable Harness–Maxun correlation (implemented)

The source of truth is the Harness custom `maxun/correlation` whole-state event. The registered `maxun` projection is cold-foldable and live-driven by `SessionProjectionRegistry`. Its compact state is:

```text
version
serviceInstanceId
browserSessionId + browserStatus
draftId / robotId / runId
url/status summary
ownerSessionId + ownerEpoch
lastValidation / lastError summary
updatedAt
```

The durable path contains lifecycle summaries only. rrweb frames, mouse/pointer events, DOM mutations, screenshots, cookies, selectors, and raw page payloads remain ephemeral and never enter model transcript or correlation events. `Session.fromRestore(...)` and the projection registry reconstruct the state after refresh/cold load.

Maxun ownership and browser routes are authenticated with the host-side API key:

```text
POST   /api/sdk/correlation/claims
DELETE /api/sdk/correlation/claims
POST   /api/sdk/browser-sessions
GET    /api/sdk/browser-sessions/:id?ownerSessionId=...
DELETE /api/sdk/browser-sessions/:id
```

Claims are explicit, unique per user/resource, epoch-checked, and return HTTP 409 `claim_conflict` for another session. Browser health requires the owning session claim and distinguishes a surviving process-local browser from `resource_not_found` after release/gone state.

Harness tools are `maxun_claim_resource`, `maxun_release_resource`, `maxun_create_browser_session`, `maxun_get_browser_session`, and `maxun_release_browser_session`. Their schemas contain no credentials, selectors, browser frames, or DOM telemetry.

## Goal 4 live browser UI contract (implemented)

The browser view is an ephemeral, read-only presentation bound to the durable `maxun` projection. It is not a model tool result and must not append stream data to the Harness session.

Maxun implements the stream-capability and screenshot routes below, and the Harness `ui-maxun` client consumes them through the typed `maxunBrowser` remote. The live path is covered by `.local/evidence/goal4-live.json` and `apps/web/tests/maxun-browser.e2e.ts`.

The stream boundary provides:

```text
POST /api/sdk/browser-sessions/:id/stream-capability
  request: { ownerSessionId, epoch }
  response: {
    capability: "short-lived opaque token",
    expiresAt: "ISO timestamp",
    streamUrl: "http://host:port",
    serviceInstanceId: "...",
    browserSessionId: "...",
    ownerSessionId: "...",
    epoch: 1
  }
```

The browser must never receive `MAXUN_API_KEY`; the capability is claim-, owner-, namespace-, epoch-, and expiry-checked and must not disclose foreign/gone resources. A server-side proxy remains an acceptable alternative if it preserves the same authorization and lifecycle semantics.

The claim-checked current-browser screenshot route is `POST /api/sdk/browser-sessions/:id/screenshot`; it returns `image/png` bytes (or `image/jpeg` when requested) with `cache-control: no-store`. The bytes remain ephemeral.

The ephemeral stream adapter must expose only UI-local state:

```text
connecting | active | reconnecting | snapshot-timeout | gone | unauthorized | degraded
```

It must bound buffered rrweb frames, reset on a full snapshot, tear down on session/browser changes, and provide screenshot fallback without persisting screenshot bytes. Durable correlation may receive compact lifecycle summaries only (`browserStatus`, URL/status, owner epoch, validation/error summary).

Goal 4 keeps rrweb masking regression-tested. Maxun sets `maskAllInputs: true`, masks explicit sensitive-text selectors, blocks iframe subtrees (including `srcdoc` attributes), and disables canvas recording. The deterministic password/text/contenteditable/iframe/canvas measurement passes in `.local/evidence/goal4-rrweb-masking.json`. The installed rrweb and rrweb-snapshot packages report MIT licenses; the Socket.IO client path is also MIT and is recorded by the generated notices.

## Goal 5 human/agent handoff contract (implemented)

Goal 5 uses a Maxun-side control lease separate from the Goal 3 resource claim and Goal 4 read-only stream capability. A mutating command is admissible only when its authenticated user, browser session, control owner/actor, control epoch, expiry/heartbeat, and command identity all match server state. Handoff, expiry, cancellation, reconnect, and release increment the control epoch; stale commands fail closed without browser side effects.

The Harness cancellation signal must reach active Maxun interpreter/browser work and settle only after quiescence or an explicit outcome-unknown classification. Returning control to the agent creates an observation barrier: it requests a fresh snapshot/compact observation and invalidates pre-handoff field, pagination, and validation state. Transient human assist actions are not workflow edits; deliberate edits require a server-owned, provenance-tagged transaction.

The Goal 4 stream remains read-only. Control traffic uses a distinct short-lived capability/channel and never receives `MAXUN_API_KEY`. Credentials and sensitive MFA/login/CAPTCHA page data remain ephemeral and are excluded from rrweb, screenshots, logs, model messages, and durable session events. The implemented contract and acceptance gates are in `docs/GOAL5_READINESS.md`.

## Maxun-side generation LLM configuration for Goal 1

The new SDK seam should obtain the generator's LLM configuration from trusted Maxun server configuration, not from model-facing request arguments. During local Goal 1 testing, use:

```text
provider: openai
model: deepseek-v4-flash
baseURL: https://opencode.ai/zen/go/v1
apiKey: server-side resolved OPENCODE_API_KEY
```

This is a POC deployment choice. The production Recorder Draft API should not be coupled to one hidden Maxun LLM at all; Harness will own semantic reasoning.
