# Goal 5 readiness — human/agent browser handoff

**Status:** Goal 5 implementation and acceptance are complete under a 5,000,000-token budget. The Goal 4 read-only boundary remains enforced for stream visualization.

## Objective

Support the controlled transition:

```text
agent control → user control → user actions → return control → agent re-observes → continue
```

The handoff must be server-authorized, epoch-safe, cancellation-aware, and safe for credentials and scraper workflow state.

## Baseline and source boundaries

Goals 1–4 are complete and remain regression baselines. Goal 4 provides only an ephemeral read-only rrweb stream and screenshot fallback. It remains separate from the Goal 5 control path.

- Maxun source pin: `6ef14c7c89fac18b5ba771a1228ee064e1d7810f`
- DeepSeek Harness source pin: `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`
- Goal 4 acceptance: `.local/evidence/goal4-live.json`, `.local/evidence/goal4-rrweb-masking.json`, `.local/evidence/goal4-web-acceptance.json`
- Goal 3 ownership/correlation acceptance: `.local/evidence/goal3-live.json`

The source trees contain intentional uncommitted integration changes. Do not reset or rebase them; review these integration changes as one coordinated workspace and do not add unrelated upstream changes.

## Existing capabilities audited

| Concern | Existing anchor | Goal 5 implication |
|---|---|---|
| Browser ownership | `server/src/sdk/resourceClaims.ts`, `ResourceClaim`, Goal 3 browser claims | A resource claim identifies the Harness owner; the implemented `ControlLease` separately authorizes human-vs-agent control and carries its own epoch. |
| Interpreter pause/resume | `server/src/workflow-management/classes/Interpreter.ts` (`pause`, `resume`, `step`, `breakpoints`) | The control service reuses the interpreter's cooperative pause/resume semantics behind server-authorized commands; client socket events are not authorization. |
| Stop/abort | `server/src/browser-management/controller.ts`, `routes/storage.ts`, `api/sdk.ts`, `task-runner.ts` | Reuse existing stop/abort behavior, but make the Harness `AbortSignal` reach the active Maxun operation and define the race outcome. |
| Browser input | `server/src/browser-management/inputHandlers.ts`, `socket-connection/connection.ts` | Existing handlers are broad and socket-scoped; the implemented control command queue checks the control lease on every mutating command, not only user authentication. |
| Harness cancellation | `packages/api/gateway`, `packages/core/tools`, `packages/maxun/tool-maxun/src/index.ts` | Remote methods carry cooperative `AbortSignal`s; the implemented control operation invokes Maxun command cancellation and classifies outcome-unknown races rather than only canceling the HTTP response. |
| Goal 4 stream | `RemoteBrowser.updateStreamSocket`, `ui-maxun/BrowserDetails.tsx` | Keep stream and control channels separate. The stream capability is read-only and must never become a takeover credential. |
| Session durability | `packages/maxun/tool-maxun/src/correlation.ts` and Goal 3 projection | Persist only control lifecycle summaries, epochs, and compact observations. Never persist credentials, raw actions, rrweb, DOM, selectors, or screenshots. |

## Implemented control contract

1. **Separate control lease.** Maxun owns a short-lived control lease containing `browserSessionId`, `ownerSessionId`, actor (`agent` or `human`), `controlEpoch`, expiry/heartbeat, and service instance. It is distinct from the durable browser resource claim.
2. **Server-side authorization.** Every mutating command carries an opaque command ID and the expected control epoch. Maxun verifies authenticated user, resource claim, control owner, actor permission, epoch, and command state before touching Playwright or the interpreter.
3. **Epoch transitions.** Agent→human, human→agent, expiry, cancellation, browser reconnect, and release increment the control epoch. Old sockets, queued commands, delayed acknowledgements, and replayed commands fail closed with a structured stale-control error.
4. **Channel separation.** Keep Goal 4 rrweb/screenshot traffic on its read-only capability. Use a distinct control capability/namespace for input and interpreter commands, with no API key and no durable token.
5. **Cancellation bridge.** A Harness cancellation must request Maxun stop/abort, wait for the browser/interpreter to quiesce, and report whether work was applied, not applied, or outcome-unknown. A canceled command must not silently continue after control returns.
6. **Observation barrier.** Returning control to the agent requests a fresh full snapshot plus a compact URL/status/observation summary. It invalidates field/pagination/validation observations from before the handoff before new agent actions are accepted.
7. **Workflow provenance.** Transient assist actions are not recorded into the robot workflow. Deliberate user edits use an explicit, server-owned edit transaction with provenance and conflict checks.
8. **Credential boundary.** MFA, login, and CAPTCHA actions remain human-visible and ephemeral. Credentials must be masked from rrweb, excluded from screenshots/logs/session events/model messages, and never copied into durable workflow state.

## Acceptance gates

The following acceptance gates are implemented and evidenced by `.local/evidence/goal5-live.json` and `.local/evidence/goal5-web-acceptance.json`:

- Two authenticated Harness sessions cannot control the same browser; a second lease returns structured `control_conflict`.
- A stale epoch, foreign owner, expired lease, wrong actor, or replayed command is rejected without browser side effects.
- Delayed click/type/navigation commands cannot apply after a handoff or return-control epoch transition.
- Harness cancellation reaches the active interpreter/browser operation; slow navigation/action tests prove quiescence and classify unknown outcomes.
- Pause/resume/abort reuse Maxun semantics and preserve partial-result behavior where applicable.
- Assist-mode actions are absent from compiled workflow state; explicit recorded edits are transactional and provenance-tagged.
- Returning control advances the observation epoch; agent commands remain blocked until the read-only stream acknowledges a post-transition full snapshot, and stale validations are invalidated.
- MFA/login/CAPTCHA fixtures prove that credentials and secret page content are absent from model messages, session events, screenshots, rrweb evidence, and logs; screenshot fallback masks inputs, frames, and marked-sensitive elements.
- Production packaging builds from `Dockerfile.backend`, runs migrations before startup, and uses model-declared unique lease/replay indexes; Goal 1–4 regression gates, source-pin verification, package/catalog checks, Maxun/Harness builds, and Goal 5 live evidence all pass.

## Deterministic test fixtures covered

- Two Harness owners competing for one browser control lease (covered by the live acceptance script).
- A delayed navigation and delayed click/type command crossing agent↔human transitions (covered by the slow fixture and live acceptance script).
- Cancellation during navigation, interpreter pause, and result cleanup (covered by the cancellation race evidence).
- A transient assist click followed by an explicit recorded workflow edit (covered by the assist-vs-record assertions).
- Return-control observation after a page mutation and after a browser reconnect (covered by the fresh-observation assertions).
- Login/MFA/CAPTCHA pages with sentinel credentials; assertions inspect all durable/session/model/log/screenshot/rrweb boundaries without storing sentinel values in evidence.

## Scope guardrails

- Keep the Goal 4 stream capability read-only; the new control capability is separate and short-lived.
- Do not put credentials, raw page data, selectors, screenshots, or high-frequency events in Harness session state.
- Do not activate production multi-tenancy, distributed browser ownership, or generic selector self-repair as part of Goal 5.
- Control implementation was accepted only after every success criterion in `goals/05-human-handoff.md` had executable evidence.

See `goals/05-human-handoff.md` for the authoritative success checklist. `scripts/test-goal5-live.js` and `scripts/verify-goal5-readiness.py` are the current acceptance entry points.
