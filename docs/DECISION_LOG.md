# Decision log

Append decisions; do not rewrite history casually.

## 2026-08-18 — integration direction

**Decision:** DeepSeek Harness is the outer application; Maxun remains a separate browser/scraper service.

**Reason:** Harness already owns agent/session/tool/UI extension primitives while Maxun owns the strongest scraping/browser implementation. The service boundary also reduces technical and licensing coupling.

## 2026-08-18 — POC uses existing one-shot Maxun generator

**Decision:** Goal 1 may expose/reuse `WorkflowEnricher.generateWorkflowFromPrompt(...)` through an API-key server boundary.

**Reason:** It already performs enough list/group/field/pagination/validation work to prove the product premise quickly.

**Not a production commitment:** interactive construction should later become semantic Recorder Draft operations controlled by the Harness agent, rather than a hidden second LLM inside Maxun.

## 2026-08-18 — model does not own selectors long term

**Decision:** production agent tools should operate on opaque list/field candidates and semantic edits; Maxun constructs/validates selectors.

## 2026-08-18 — browser view belongs outside transcript

**Decision:** live rrweb/browser traffic is ephemeral UI state. Durable Harness state contains only compact correlation/lifecycle summaries.

## 2026-08-18 — provider

**Decision:** development Harness sessions use `opencode-go/deepseek-v4-flash`, sharing the locally configured Pi test credential via environment reference rather than committing the literal key.

## 2026-08-18 — Goal 1 SDK list seam

**Evidence:** `sources/maxun/server/src/api/sdk.ts`, `sources/maxun/server/src/sdk/llmRobot.ts`, `.local/evidence/goal1-verification.json`.

**Decision:** expose `POST /api/sdk/robots/list` behind Maxun API-key authentication. It reads the operator-side generator configuration from `MAXUN_AGENT_LLM_*`/OpenAI-compatible server environment, reuses `WorkflowEnricher.generateWorkflowFromPrompt(...)`, persists the native workflow, and returns `recording_meta.id` plus a compact list summary. Harness uses `POST /api/sdk/robots/:id/execute` for normal execution.

**Consequence:** Goal 1 keeps the hidden Maxun-side LLM as a POC shortcut and keeps selectors/browser state inside Maxun. Production should replace this one-shot route with the separately documented semantic Recorder Draft service rather than making Harness depend on a second model.

## 2026-08-18 — internal SDK run authentication

**Evidence:** `sources/maxun/server/src/api/record.ts`, `.local/evidence/run-output.json`.

**Decision:** server-side SDK execution signs a short-lived internal JWT for its Socket.IO browser connection. The existing API-key HTTP route otherwise created runs that remained `running` because the socket middleware correctly rejected an unauthenticated internal connection.

**Consequence:** API-key callers remain host-side while the existing authenticated browser/run path is reused; no JWT is exposed to Harness or the model.

## 2026-08-18 — Harness workspace launch path

**Evidence:** `scripts/_common.sh`, `scripts/install-source-deps.sh`, `scripts/setup-harness-provider.sh`, `scripts/test-harness-headless.sh`, `scripts/run-harness-web.sh`.

**Decision:** use an ignored local pnpm 11.7.0 fallback when the system Corepack shim fails, and launch Harness from its built CLI artifact rather than the pinned source entrypoint. The source entrypoint imports a `const enum` as a runtime export under the available Node/tsx combination; the built artifact inlines it.

**Consequence:** the starter setup is reproducible on this host without changing either upstream's pinned baseline for the workaround.

## 2026-08-18 — full Harness suite status

**Evidence:** `./scripts/test-harness-suite.sh` completed with 809 test files passed, 8 skipped, 13,509 tests passed, and 109 skipped. The wrapper's reproducibility settings are documented in `scripts/test-harness-suite.sh`.

**Decision:** run the upstream suite through the workspace wrapper rather than raw `pnpm run test`: it forces the pinned pnpm binary, `LC_ALL=C` for the POSIX permission-denial fixture, and a 30-second timeout for the subprocess-heavy oxlint contract.

**Consequence:** the Harness-side test gate passes without modifying unrelated upstream tests; Goal 1 was completed without modifying unrelated upstream tests.

## 2026-08-18 — Goal 2 activation

**Decision:** activate `goals/02-semantic-recorder-service.md` with a fresh 5,000,000-token implementation budget. The semantic Recorder Draft service is the next boundary: Maxun owns selector discovery and native workflow compilation, while Harness steers opaque semantic IDs rather than authoring CSS/XPath or calling the hidden one-shot construction path.

**Scope guard:** do not begin durable lifecycle state, browser embedding, or human takeover until Goal 2's draft, preview, validation, deterministic compile, Harness semantic tools, and Recorder compatibility criteria are evidenced.

## 2026-08-18 — Goal 2 semantic draft evidence

**Evidence:** `scripts/test-goal2-live.py`, `.local/evidence/goal2-live.json`, `.local/evidence/goal2-verification.json`, `.local/harness-headless-goal2-final.txt`.

**Decision:** expose only opaque list/field identities and semantic metadata. Maxun retains selectors in persisted draft state; pagination is marked tested only after a preview observes a second page; validation coverage is keyed by opaque field IDs. Compile responses omit pagination selectors, and robot-name collisions are returned as structured `409 robot_name_conflict` errors.

**Consequence:** the Harness agent can inspect, steer, validate, and compile a draft without authoring CSS/XPath or receiving server-owned selectors. The live catalog flow found four candidates, selected six fields, traversed three pages, validated full coverage, compiled native `scrapeList`, and executed five exact fixture rows.

## 2026-08-18 — Goal 3 activation

**Decision:** activate `goals/03-durable-session-state.md` with a fresh 5,000,000-token implementation budget. Goal 3 will add only compact custom durable Harness session events and a correlation projection for Maxun resources; high-frequency rrweb/mouse/DOM traffic remains ephemeral and outside model transcript/session persistence.

**Scope guard:** do not begin browser UI or human takeover until durable correlation, cold-session reconstruction, reconnect/degraded behavior, and explicit ownership guards are evidenced.

## 2026-08-18 — Goal 3 durable correlation contract

**Decision:** use one versioned, whole-state `maxun/correlation` custom session event as the Harness source of truth, projected through the shared `SessionProjectionRegistry`. The event stores only Maxun service/resource IDs, lifecycle status, owner session/epoch, validation summaries, and compact errors. `Session.fromRestore` must reproduce the same projection after refresh/cold load.

**Decision:** make ownership explicit at the Maxun SDK boundary. Durable `maxun_resource_claim` rows are unique per authenticated user/resource, same-owner retries are idempotent, releases are epoch-checked, and a competing Harness session receives `409 claim_conflict`. Browser health requires the explicit claim and reports `resource_not_found` when the process-local browser is gone.

**Evidence:** `.local/evidence/goal3-live.json`, `scripts/verify-goal3-evidence.py`, `packages/maxun/tool-maxun/tests/correlation.spec.ts`, `packages/maxun/tool-maxun/tests/tool-maxun.spec.ts`, and opt-in `goal3-live.spec.ts`. The live contract verified a surviving browser reconnect after cold restore, a degraded gone-browser state while draft/robot IDs remained durable, empty derived model messages, and no credential/rrweb/mouse/DOM markers in persisted correlation events.

## 2026-08-18 — Goal 3 completion audit

**Result:** Goal 3 is complete. Maxun build, Harness host typecheck/build, tool-catalog check, focused tests, full Harness suite, live correlation/ownership test, credential-free evidence verification, and source-pin verification all passed. Goal 4 is not activated; the next scope requires explicit user authorization.

## 2026-08-18 — Goal 4 readiness review

**Result:** The project status was audited and Goal 4 was prepared without activating implementation. Goals 1–3 and their evidence remain the baseline. Maxun already has rrweb emission and a DOM `Replayer`; Harness has session-scoped UI slots and a resident details-shell concept. The missing boundary is a claim-bound ephemeral stream/details integration.

**Guardrails:** Goal 4 must use a short-lived stream capability or host proxy rather than expose `MAXUN_API_KEY`, keep rrweb/mouse/DOM/screenshot data outside the session log, measure and fix the current Maxun `maskAllInputs: false` behavior before authenticated use, provide screenshot fallback, and remain read-only. Human/browser takeover remains Goal 5.

**Handoff:** `docs/GOAL4_READINESS.md`, `goals/04-browser-ui.md`, and the updated architecture/contracts/security/test-strategy/runbook are the kickoff sources. The implementation goal was not active until explicitly requested.

## 2026-08-18 — Goal 4 activation

**Decision:** Activate `goals/04-browser-ui.md` with a fresh 5,000,000-token budget after the explicit user request. Preserve Goals 1–3 as the regression baseline, keep the browser view read-only, and defer human/browser takeover to Goal 5.

## 2026-08-19 — Goal 4 live stream and browser details

**Decision:** Use a direct Socket.IO connection from a session-scoped Harness details contribution, authorized by a 60-second JWT capability bound to Maxun service/browser/owner/epoch. The browser bundle receives neither `MAXUN_API_KEY` nor an API-key-bearing URL. `ui-maxun` uses a bounded ephemeral rrweb adapter with full-snapshot reset and reconnect refresh; it never calls `Session.append()`.

**Privacy:** `maskAllInputs: true` and explicit sensitive selectors protect form/text values. Iframe subtrees are blocked because `srcdoc` attributes can carry raw secrets before nested masking; canvas recording is disabled. The deterministic fixture covers password, ordinary input, marked text, contenteditable, iframe, and canvas cases.

**Renderer/licensing:** Harness uses the MIT-licensed rrweb `Replayer` in a read-only surface. `rrweb`, `rrweb-snapshot`, and Socket.IO client licenses are recorded by `THIRD_PARTY_NOTICES.md`; the browser surface has no mutation or takeover controls.

**Evidence:** `.local/evidence/goal4-live.json`, `.local/evidence/goal4-rrweb-masking.json`, and `apps/web/tests/maxun-browser.e2e.ts` prove authorization/rejection, reconnect/full snapshots, screenshot fallback, details resize/reload, masking, and no model/session telemetry traffic.

## 2026-08-19 — Goal 5 readiness activation

**Decision:** Activate Goal 5 for repository preparation and implementation planning after the explicit user request. Do not implement browser mutation or human takeover in the preparation pass.

**Control-plane direction:** Add a Maxun-owned control lease separate from the Goal 3 durable resource claim. Bind every mutating command to authenticated user, browser, control owner/actor, control epoch, expiry, and command identity. Keep the Goal 4 stream capability read-only and use a separate control capability/channel.

**Required gates:** cancellation must reach active Maxun interpreter/browser work; handoff transitions must invalidate stale commands and observations; transient assist actions must not mutate durable workflow state; explicit edits need provenance; MFA/login/CAPTCHA credentials must stay outside rrweb, screenshots, logs, model messages, and session events.

**Handoff:** `docs/GOAL5_READINESS.md`, `goals/05-human-handoff.md`, `.local/evidence/goal5-readiness.json`, and `scripts/verify-goal5-readiness.py`.

## 2026-08-19 — Goal 5 implementation activation

**Decision:** Activate Goal 5 implementation with a fresh 5,000,000-token budget after the explicit user request. The initial slice adds a separate Maxun control lease/command ledger, control JWT, epoch-fenced commands, human control socket, cancellation propagation, and compact control/observation correlation. Goal 4 stream capabilities remain read-only.

**Evidence target:** `.local/evidence/goal5-live.json`, Goal 5 race/privacy tests, and the updated Goal 1–4 regression gates.

## 2026-08-19 — Goal 5 acceptance complete

**Result:** Goal 5 is complete. The separate control lease, epoch/replay fencing, cancellation bridge, human handoff UI, assist-vs-record provenance, fresh-observation barrier, slow-race handling, and credential boundary all have executable evidence. The full Harness regression passes with 810 files and 13,513 tests passed; source pins, builds, catalogs, package invariants, and Goals 1–4 evidence verifiers also pass.

**Evidence:** `.local/evidence/goal5-live.json`, `.local/evidence/goal5-web-acceptance.json`, `.local/evidence/goal5-readiness.json`, and `.local/evidence/goal5-harness-suite.txt`. Goal 4 remains a read-only stream; no later goal is active.
