# Instructions for Pi

You are implementing an agentic web-scraper builder using **DeepSeek Harness as the primary application** and **Maxun as the browser/scraper subsystem**.

This is a long-running project. Maintain continuity using the installed Goal extension and persistent todo-item tool.

## Mandatory session-start routine

At the beginning of every new Pi session:

1. Read this file.
2. Read `goals/ACTIVE.md` and the referenced goal file.
3. Inspect the persistent todo list. If it has not been seeded, create/update it from `todo/seed.md` using the installed todo tool.
4. Inspect `docs/DECISION_LOG.md` and recent git changes before assuming prior work.
5. Verify source pins with `./scripts/verify-source-pins.sh`.
6. Keep **one implementation goal active**. Use the Goal extension's native operations rather than inventing another goal tracker. If its command names differ from what you expect, inspect the extension help instead of guessing.

Do not mark a goal complete because code exists. Mark it complete only when every success criterion has executable evidence.

## Fixed architectural preference

Only this outer decision is fixed:

```text
DeepSeek Harness → Maxun capabilities → browser / scraper robot
```

Do not embed an entire DeepSeek application inside Maxun.

Everything below this boundary must remain evidence-driven. Preserve the distinction between a temporary POC shortcut and an architecture worth keeping.

## Goal 5 is complete

Goals 1–5 are complete. Goal 5 used a 5,000,000-token budget. Its implementation contract and evidence are in `docs/GOAL5_READINESS.md`; authoritative success criteria remain in `goals/05-human-handoff.md`.

The preserved Goal 4 proof is:

> Harness persists a compact, durable correlation projection for Maxun drafts, browsers, robots, and runs; reconstructs it after refresh/cold session; reconnects or degrades predictably; excludes live browser traffic from transcript/session persistence; and prevents accidental multi-session claims.

Goal 3 success criteria and evidence are authoritative in `goals/03-durable-session-state.md`. Goal 4 implementation, acceptance, and evidence are authoritative in `goals/04-browser-ui.md` and `docs/GOAL4_READINESS.md`. Goal 5 implementation, acceptance, and control-plane constraints are authoritative in `goals/05-human-handoff.md` and `docs/GOAL5_READINESS.md`. Preserve the existing browser view's read-only stream and Goal 5's control, cancellation, privacy, and race guarantees.

### Goal 3 historical non-goals

Do not regress the completed Goal 3 baseline while working on later goals:

- Goal 3's compact durable correlation must not absorb live browser traffic;
- Goal 4's browser view must remain read-only; Goal 5 control uses its separate authenticated path;
- generic selector self-repair;
- horizontal scaling;
- production multi-tenancy beyond explicit ownership guards;
- detail-page augmentation;
- every Maxun robot type.

## What the research established about Maxun

Treat these as strong starting hypotheses, then verify them against the pinned checkout before editing:

- A persisted list robot is a native Maxun `WorkflowFile`/`WhereWhatPair[]` containing a `scrapeList` action. Generated Playwright code is **not** the durable representation.
- `server/src/api/sdk.ts` already exposes API-key robot CRUD/create/execute/run operations.
- `server/src/sdk/workflowEnricher.ts` already contains a one-shot `generateWorkflowFromPrompt(...)` flow that can analyze repeating groups, detect fields, label/filter fields, validate fill rates, detect pagination, apply a limit, and build a normal `scrapeList` workflow.
- The existing signed-in storage route uses that one-shot generator. For the POC, the smallest Maxun change should expose equivalent functionality behind the SDK/API-key boundary rather than rebuilding its logic.
- `server/src/sdk/selectorValidator.ts` and `server/src/sdk/browserSide/pageAnalyzer.js` are important production building blocks.
- The Recorder's interactive `initial → pagination → limit → complete` orchestration is largely React state. Do not make that React state the long-term external agent API.
- Maxun `RemoteBrowser`/BrowserPool owns Playwright state. BrowserPool is process-local.
- Maxun rrweb reconstructs a remote browser in an iframe, but high-frequency rrweb data must never become model transcript state.

## Goal 2 Maxun implementation guidance

Before changing code, trace the current Recorder, selector, validation, persistence, and runtime paths in the pinned Maxun checkout. Reuse Maxun ownership rather than duplicating browser analyzers or inventing a model-facing selector language.

The semantic service must:

- persist a first-class Recorder Draft independent of React state;
- expose opaque list and field IDs plus samples, tags, attributes, and pagination metadata;
- accept semantic list selection and field include/exclude/rename operations;
- keep CSS/XPath selectors private to Maxun;
- preview and actually test pagination, then expose structured current-page/multi-page diagnostics;
- compile deterministically into a native `scrapeList` workflow and persist a normal Robot;
- return structured API errors, including robot-name conflicts, without credentials or selectors.

The live contract is `scripts/test-goal2-live.py`; its generated evidence and the Goal 2 success checklist are the acceptance gate.

## Goal 1 Maxun implementation guidance (completed historical seam)

Before changing code, trace the exact current call chain from the existing LLM robot creation route to persistence. Reuse that implementation.

The preferred POC seam is a small API-key-authenticated operation with semantics like:

```text
create list robot from URL + prompt + optional name
```

The one-shot `WorkflowEnricher` is itself LLM-assisted. For Goal 1, configure that LLM **operator-side in Maxun**, using the same test OpenCode Go credential and OpenAI-compatible endpoint. The starter exports:

```text
MAXUN_AGENT_LLM_PROVIDER=openai
MAXUN_AGENT_LLM_MODEL=deepseek-v4-flash
MAXUN_AGENT_LLM_BASE_URL=https://opencode.ai/zen/go/v1
MAXUN_AGENT_LLM_API_KEY=<resolved locally from OPENCODE_API_KEY>
```

Implement the POC route so it constructs/passes the appropriate `llmConfig` from server environment/config. Do not add the provider key to the tool schema or HTTP request coming from the model. Existing Maxun OpenAI-compatible helpers also recognize `OPENAI_BASE_URL`/`OPENAI_API_KEY`; `scripts/run-maxun-dev.sh` exports both forms during development.

The exact route name is not prescribed. Choose one that fits `server/src/api/sdk.ts` without colliding with existing `/robots/:id` routes.

Expected request shape, conceptually:

```json
{
  "url": "http://127.0.0.1:4173/page1.html",
  "prompt": "Get product name, price, rating, image URL, product URL and review count. Follow pagination and collect the first 5 products.",
  "name": "Fixture Products"
}
```

Expected response must include enough structured information for Harness to reason and display useful progress, for example:

```json
{
  "robotId": "public-Maxun-robot-id",
  "url": "...",
  "fields": ["..."],
  "pagination": { "type": "..." },
  "limit": 5
}
```

The authoritative robot ID for external operations must be the ID expected by Maxun SDK routes (normally `recording_meta.id`), not an internal database row ID.

Do not copy-and-paste the entire storage route. Extract the smallest reusable server function if necessary so both the existing application route and SDK route can share persistence/generation behavior.

Add tests around the new boundary.

## Goal 2 Harness implementation guidance

Harness should use a **host-side semantic integration plugin**, not a browser-side secret-bearing client. The registered normal-construction tools are:

- `maxun_create_recorder_draft`
- `maxun_select_list_candidate`
- `maxun_update_draft_field`
- `maxun_preview_recorder_draft`
- `maxun_validate_recorder_draft`
- `maxun_compile_recorder_draft`
- `maxun_run_robot`

The Goal 1 `maxun_create_list_robot` tool is historical compatibility only and must not be used for normal Goal 2 construction.

The plugin should read:

- `MAXUN_BASE_URL`
- `MAXUN_API_KEY`

from host configuration/environment and call Maxun over HTTP. Never send the Maxun API key to client JavaScript or model-visible tool content.

Follow current Harness Cordis/tool patterns in the pinned source. Inspect existing small tool plugins before implementing. Use Harness cancellation signals where possible.

Return compact semantic tool results. Never expose `MAXUN_API_KEY` or server-owned selectors to model/browser content. Do not add a custom chat renderer unless it materially simplifies acceptance testing.

## Goal 1 Harness implementation guidance (completed historical seam)

The original POC used a small host-side client with `maxun_create_list_robot` and `maxun_run_robot`; preserve its Maxun compatibility route but do not make it the Goal 2 construction path.

## Provider requirement

Harness must run through:

```text
provider = opencode-go
model    = deepseek-v4-flash
```

Run both provider smoke tests **before debugging integration code**:

```bash
./scripts/test-opencode-go-direct.sh
./scripts/test-harness-headless.sh
```

If either fails, fix provider/configuration first.

Do not print the API key. The user permits use of the test key, but there is no engineering benefit to putting it in logs or commits.

## Testing discipline

Use layered tests:

1. unit tests for any extracted Maxun helper;
2. Maxun SDK endpoint integration test;
3. Harness plugin/tool test with a mocked Maxun HTTP service;
4. real Maxun + deterministic fixture test;
5. Harness headless tool-flow test;
6. final Harness Web test using the installed `playwright-cli`.

For `playwright-cli`, inspect `playwright-cli --help` before writing commands. Do not assume a CLI syntax from memory.

The fixture server is:

```bash
./scripts/serve-fixtures.sh
```

and page 1 defaults to:

```text
http://127.0.0.1:4173/page1.html
```

## Acceptance evidence

For each completed success criterion, preserve enough evidence in `.local/evidence/` to reproduce the result: command, important non-secret output, and any relevant screenshots/traces.

Do not commit secrets, browser cookies, database dumps, or raw credential files.

## Architecture beyond Goal 3

Goal 2 established the semantic draft baseline and Goal 3 adds compact durable lifecycle correlation; future explicitly authorized goals may add live browser details and human handoff. The architecture remains:

```text
Harness model tools
      ↓ semantic operations
Maxun Recorder Draft Service
      ↓
Maxun browser + analyzers + validators
      ↓
native WorkflowFile / Robot
```

with separate paths for:

```text
Maxun rrweb/live browser stream → Harness details panel   (ephemeral, UI-only)
Maxun lifecycle summary         → Harness session state    (durable, low-rate)
```

The model should normally select opaque candidate/list/field IDs and semantic operations. Maxun should own selector construction and validation.

## Engineering invariants

- Harness remains the outer product shell.
- Maxun remains separately deployable.
- Preserve native Maxun robots as final runtime artifacts.
- Do not make raw CSS/XPath the main model-facing abstraction.
- Do not make the model drive Maxun's existing React Recorder UI.
- High-frequency browser state stays outside model context and durable conversation logs.
- User questions are not approvals; use each Harness primitive for its intended semantics.
- Keep secrets host-side.
- Maintain an AGPL/MIT service boundary unless a deliberate, reviewed decision changes it.
- Prefer upstream patterns over new local frameworks.

## Source modifications

Editable checkouts:

- `sources/maxun`
- `sources/deepseek-harness`

Supporting checkouts are research references by default. Avoid modifying them unless the active goal explicitly requires it.

Before changing an upstream repository, read its own `AGENTS.md`/contributor instructions.

## Decision making

When repository evidence contradicts this handoff, trust the pinned implementation. Record meaningful deviations in `docs/DECISION_LOG.md` with:

- date;
- evidence/path;
- decision;
- consequence for POC vs production.

Do not silently expand scope.
