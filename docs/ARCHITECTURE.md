# Architecture handoff

## Implemented semantic path (Goals 1–3)

```text
DeepSeek Harness
  └─ semantic Maxun tool plugin
       └─ API-key HTTP
            ├─ create/steer/preview/validate Recorder Draft
            ├─ compile native scrapeList robot
            └─ execute saved robot
                    ↓
                 Maxun
     RecorderDraft + SelectorValidator + Robot persistence + maxun-core runtime
```

The Goal 1 one-shot `WorkflowEnricher` route remains an authenticated compatibility seam only. Normal Harness construction no longer depends on Maxun's hidden generation LLM.

## Architecture to keep

```text
DeepSeek Harness
├─ conversational reasoning
├─ semantic Maxun tools
├─ questions / approvals
├─ durable session projection
└─ browser details panel
          │
          │ low-rate semantic commands
          ▼
Maxun Recorder Draft Service
├─ browser session management
├─ repeated-list analysis
├─ field candidates
├─ selector generation/validation
├─ pagination detection/testing
├─ preview + diagnostics
├─ workflow compiler
└─ robot persistence
          │
          ▼
RemoteBrowser / Playwright / maxun-core
```

Goal 4 active live path:

```text
Maxun RemoteBrowser
  └─ claim-bound ephemeral stream capability / host proxy
       └─ rrweb Socket.IO frames
            └─ Harness session-scoped browser details view
                 ├─ reconnect/backoff/full-snapshot reset
                 ├─ screenshot fallback
                 └─ compact active/gone/degraded status
```

The live path must never append rrweb frames, mouse/pointer events, DOM mutations, screenshots, cookies, selectors, or raw page payloads to the Harness session. Goal 4 should be read-only; browser mutation and human control remain Goal 5.

Separate durable path:

```text
important Maxun lifecycle changes → Harness session events/projection
```

## State ownership

| State | System of record | Durability |
|---|---|---|
| BrowserContext/Page/cookies | Maxun | browser lifetime |
| rrweb mutations, highlights, pointer | Maxun live channel/client | ephemeral |
| list/fields/pagination/limit draft | Maxun Recorder Draft | durable |
| robot workflow | Maxun DB | durable |
| run/results | Maxun DB | durable |
| intent/questions/decisions | Harness Session | durable |
| Maxun resource correlation | Harness custom durable events + projection | durable |

Goal 3 makes the correlation projection explicit: only compact service/browser/draft/robot/run lifecycle summaries are durable. The `maxun/correlation` whole-state event is folded by the `maxun` projection and reconstructed by `Session.fromRestore`/`SessionProjectionRegistry`. rrweb, mouse, DOM mutation, screenshot, cookie, selector, and raw page traffic remains in the ephemeral live channel and outside the model transcript.

Explicit ownership is a Maxun-side durable claim (`draft` or `browser`) keyed by authenticated user/resource with an increasing epoch. The Harness exposes claim/release operations and browser-session create/health/release operations. Browser health is only available to its explicit owner; a process-local browser can reconnect after Harness refresh, while a missing browser produces a degraded correlation state without deleting durable draft/robot state. Goal 4 may consume this projection, but the stream itself needs a separate short-lived capability or host proxy and must not treat durable IDs as stream authorization.

## Model abstraction

The production model should manipulate semantic handles, not selectors:

```text
find_lists → candidate IDs
select_list(candidateId)
inspect_fields → stable field IDs + samples
configure_fields(field IDs / names)
configure_pagination(auto)
preview
validate
save_robot
run_robot
```

Raw selectors remain useful diagnostics and an escape hatch, but Maxun should normally own selector construction.

## Goal 4 UI boundary

The Harness client provides session-scoped slots, a resident conversation shell, and a resizable details shell. `ui-maxun` mounts a session-scoped read-only `conversation.details.browser` contribution keyed by the durable `maxun` projection, with a dock affordance to open it. It is not a historical chat row and does not depend on model tool-result rendering. Direct Socket.IO capability use, iframe blocking, screenshot fallback, and renderer licensing are recorded in `docs/GOAL4_READINESS.md`.

## Goal 5 control-plane boundary

Goal 5 keeps human/agent control separate from both durable resource claims and the Goal 4 read-only stream. Maxun owns a control lease with actor, owner session, epoch, expiry/heartbeat, and command identity; every browser-mutating command is checked against that lease before reaching Playwright or the interpreter. Handoff, cancellation, reconnect, and release advance the epoch so delayed commands fail closed. The Harness forwards cancellation and receives only compact lifecycle/observation summaries; raw human actions and credentials remain ephemeral. See `docs/GOAL5_READINESS.md` for the implemented acceptance gates.
