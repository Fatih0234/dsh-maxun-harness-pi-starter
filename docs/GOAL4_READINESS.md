# Goal 4 readiness — live Maxun browser in Harness

**Status:** Goals 4 and 5 implementation and acceptance are complete; Goal 5 evidence is in `docs/GOAL5_READINESS.md`.

Goals 1–3 are the completed baseline. This document records the accepted Goal 4 slice and its regression evidence; Goal 5 implementation is documented separately.

## General project view

| Goal | Result | Authoritative evidence |
|---|---|---|
| 1 — native list robot POC | Complete | `.local/evidence/goal1-verification.json`, Harness headless/Web evidence, `scripts/verify-goal1-evidence.py` |
| 2 — semantic Recorder Draft service | Complete | `.local/evidence/goal2-verification.json`, `.local/evidence/goal2-live.json`, auth/compatibility evidence, `scripts/verify-goal2-evidence.py` |
| 3 — durable correlation/lifecycle | Complete | `.local/evidence/goal3-live.json`, `.local/evidence/goal3-harness-suite.txt`, `scripts/verify-goal3-evidence.py` |
| 4 — live browser in Harness | Complete | `.local/evidence/goal4-live.json`, `.local/evidence/goal4-rrweb-masking.json`, `.local/evidence/goal4-web-acceptance.json`, and `apps/web/tests/maxun-browser.e2e.ts` |
| 5 — human/agent handoff | Complete | `goals/05-human-handoff.md`, `docs/GOAL5_READINESS.md`; do not widen Goal 4 |

Pinned source baselines remain:

- Maxun: `6ef14c7c89fac18b5ba771a1228ee064e1d7810f`
- DeepSeek Harness: `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`

The two integration source trees contain the intentional uncommitted Goal 1–5 changes shown by `git -C sources/maxun status` and `git -C sources/deepseek-harness status`; do not reset or rebase them. Run the source-pin check before future implementation.

## What is already available

### Maxun

- `RemoteBrowser` already injects rrweb and emits `rrweb-event` frames through the browser Socket.IO namespace.
- Maxun's existing `DOMBrowserRenderer` replays those frames with rrweb's `Replayer`, supports resize, and has existing browser interaction/selection code.
- `BrowserPool`/`RemoteBrowser` provide process-local browser ownership and lifecycle status.
- Goal 3 added authenticated browser-session create/health/release routes, durable resource claims, owner sessions, epochs, and service-instance identity.
- Existing screenshot capture exists for robot-run output, and Goal 4 adds a claim-checked current-browser screenshot route consumed by the Harness fallback button.

### Harness

- The client UI has a slot registry and session-scoped component injection model in `ui-slots`/`web-react`.
- `ui-conversation` owns a resident conversation shell and details shell; Goal 4 adds the session-scoped `conversation.details.browser` child seat.
- `SessionProjectionRegistry` can provide the Goal 3 `maxun` projection to a session-scoped browser view.
- The Maxun host plugin resolves `MAXUN_API_KEY` only in the Harness process; the `ui-maxun` browser bundle receives only short-lived capabilities and exposes no frames, selectors, or credentials to model tools.

## Required Goal 4 slice

1. **Session-bound stream capability**
   - Maxun issues an authenticated, short-lived browser-stream capability; Harness consumption and live authorization are covered by `.local/evidence/goal4-live.json`.
   - Never place `MAXUN_API_KEY` in browser JavaScript, URLs, persisted session events, or model-visible data.
   - Bind the capability to `serviceInstanceId`, `browserSessionId`, `ownerSessionId`, and the current claim epoch.
   - Reject stale, foreign, gone, and expired capabilities without disclosing another user's browser.

2. **Persistent/resizable Harness details surface**
   - `ui-maxun` adds a session-scoped browser details entry using the existing UI slot/renderer architecture.
   - It mounts in the persistent/resizable details area, never as a mutating historical chat row.
   - Keep the view keyed by durable Harness session ID and browser session ID so a page reload reconstructs the same correlation.
   - Show compact status states: unattached, connecting, active, reconnecting, gone, unauthorized, and degraded.

3. **Ephemeral stream adapter**
   - Keep rrweb frames and interaction/pointer traffic out of `Session.append()` and `deriveMessages()`.
   - Reconnect the stream independently of model turns and projection writes.
   - Bound event/backlog memory, handle full-snapshot resets, and tear down sockets on session/browser change.
   - Prefer read-only visualization in Goal 4; browser mutation and user takeover belong to Goal 5.

4. **Screenshot fallback**
   - Maxun provides a claim-checked current-browser screenshot route; `ui-maxun` wires it to the read-only fallback button.
   - Use it when rrweb cannot reconstruct a page or after a full-snapshot timeout.
   - Keep screenshots in ephemeral UI state; only compact status/observation summaries may be durable.

5. **Privacy and licensing gate**
   - Measure the pinned rrweb behavior against password, text-input, contenteditable, iframe, canvas, and sensitive fixture cases.
   - Current Maxun code configures `maskAllInputs: true`, explicit sensitive-text selectors, `blockSelector: 'iframe'`, and `recordCanvas: false`; password/text/contenteditable/iframe/canvas coverage passes.
   - Keep the masking configuration and regression test on every renderer change.
   - The installed `rrweb`/`rrweb-snapshot` and Socket.IO client packages report MIT licenses; generated notices and the decision log preserve the attribution review.

## Suggested implementation order

1. Add/retain contract tests for stream authorization and screenshot authorization at the Maxun SDK boundary.
2. Keep the privacy-safe rrweb configuration and deterministic fixture regression.
3. Keep the Harness browser-stream client as a separate ephemeral service, with reconnect/backoff, bounded buffering, and full-snapshot reset handling.
4. Keep the session-scoped details view in the existing persistent/resizable UI slot.
5. Keep screenshot fallback and degraded/error rendering.
6. Run refresh/reconnect, unauthorized/stale-epoch, gone-browser, masking, resize, and memory-bound tests.
7. Run the full existing Goal 1–3 gates and the Goal 4 Playwright Web acceptance flow.

## Goal 4 decisions (resolved)

- **Resolved:** Harness receives a short-lived claim-bound capability and connects directly to the Maxun Socket.IO namespace; `MAXUN_API_KEY` remains host-side.
- **Resolved:** Harness uses a smaller read-only Replayer surface rather than importing Maxun's mutating recorder renderer.
- **Resolved:** the session-scoped `conversation.details.browser` slot is mounted inside the existing resizable details column.
- **Resolved:** current-browser screenshot fallback is claim-checked, `no-store`, and retained only in component state.
- **Resolved:** inputs/text are masked; iframe subtrees are blocked and canvas recording is disabled.
- **Resolved:** Goal 4 is read-only; all browser mutation and takeover remains Goal 5.

## Exit evidence required

All checkboxes in `goals/04-browser-ui.md` must be checked with executable evidence. At minimum, retain:

- Maxun/Harness stream-auth contract output (`.local/evidence/goal4-live.json`);
- sensitive-input masking test output (`.local/evidence/goal4-rrweb-masking.json`);
- reconnect-after-Harness-reload evidence (`apps/web/tests/maxun-browser.e2e.ts`);
- details-panel resize and non-transcript placement evidence (same test);
- screenshot fallback evidence (same test and live evidence);
- a no-model/no-session-log telemetry assertion (`goal4-live.json` and source boundary review);
- rrweb/Socket.IO licensing and generated notice review;
- full Harness suite, Maxun build, source pins, and Goal 1–3 evidence verification.
