# Goal 3 — durable Harness ↔ Maxun correlation and lifecycle

## Goal

Persist compact Maxun integration state in Harness so a Harness reload/cold session can reconnect to surviving Maxun resources or degrade predictably when a browser is gone.

## Target durable projection

- Maxun service instance ID
- browser session ID
- draft ID
- robot ID
- run ID
- current URL/status summary
- control owner/epoch placeholder
- last validation/error summary

## Implemented contract

Harness owns the durable `maxun/correlation` whole-state event and `maxun` projection. Maxun owns authenticated browser health, persisted Recorder Draft/robot state, and explicit resource claims. The Harness tools expose claim/release and browser create/health/release operations; browser health requires the durable session's explicit claim.

## Success criteria

- [x] Custom durable session events are the source of truth for correlation.
- [x] A session projection reconstructs current Maxun state after Harness refresh/cold restore.
- [x] rrweb/mouse/DOM mutation traffic is never persisted to the model transcript/session log.
- [x] If Maxun browser survives, Harness reconnects.
- [x] If Maxun browser is gone, durable draft/robot state survives and Harness reports the distinction as degraded.
- [x] Multiple Harness sessions cannot accidentally claim the same Maxun browser/draft without an explicit operation.

Evidence: `.local/evidence/goal3-live.json`, verified by `scripts/verify-goal3-evidence.py`; automated coverage is in `packages/maxun/tool-maxun/tests/correlation.spec.ts`, `tool-maxun.spec.ts`, and opt-in `goal3-live.spec.ts`.

## Completion audit

Verified on the pinned Maxun/Harness sources:

- Maxun server build: `npm run build:server`.
- Harness host build/typecheck, tool catalog generation/check, focused correlation/tool tests, and full suite: **810 files passed, 9 skipped; 13,512 tests passed, 110 skipped**.
- Live Goal 3 test: cold-restored same session ID, existing browser claim/reconnect, gone-browser `resource_not_found`, degraded projection, durable draft/robot lookup, competing-session conflict, stale epoch rejection, and foreign browser-release rejection.
- Credential-free evidence and source pins: `scripts/verify-goal3-evidence.py` and `scripts/verify-source-pins.sh` passed.

Goals 4 and 5 are complete; their implementation and acceptance evidence are documented in `docs/GOAL4_READINESS.md` and `docs/GOAL5_READINESS.md`.
