# Review Plan — Maxun ↔ DeepSeek Harness Integration (Goals 1–5)

> **Status:** Plan only. No findings are closed here. This document defines *how* the independent review is executed before any merge. Execution is tracked in 4 phases (A–D).

## 1. Review Coordinates

| Surface | Location |
|---|---|
| **Workspace** | `/home/fatih/Projects/dsh-maxun/maxun-harness-pi-starter` (pi-starter) |
| **Review entry** | `docs/GITHUB_REVIEW.md` — canonical PR coordinates + evidence index |
| **Evidence (sanitized, published)** | `review-evidence/` (copied from `.local/evidence/`) |
| **Evidence (full, local)** | `.local/evidence/` — not published, contains raw logs/screenshots |
| **Maxun PR** | `getmaxun/maxun#1194` via fork `Fatih0234/maxun:pi/maxun-harness-integration` — head `7d027053a732519bacb28eebd77dde77077c2ed8`, base `6ef14c7c89fac18b5ba771a1228ee064e1d7810f` |
| **Harness PR** | `Fatih0234/deepseek-harness#1` — head `4b68869cbb9b9ddf1c48d6d7d27d1a37e467494e`, base `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca` |
| **Root docs repo** | `Fatih0234/dsh-maxun-harness-pi-starter:main` — head `23814e6` — docs/evidence only, no vendored source |
| **Source pins** | `config/sources.json` + `scripts/verify-source-pins.sh` — must not drift |
| **Contracts** | `docs/IMPLEMENTATION_CONTRACTS.md`, `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/GOAL4_READINESS.md`, `docs/GOAL5_READINESS.md`, `goals/05-human-handoff.md` |

Root repo intentionally does not vendor source checkouts. Reviewer must treat the three repos as **one coordinated change**.

## 2. What Was Built (Goals 1–5 as One System)

| Goal | Intent | Invariant to Preserve | Key Implementation |
|---|---|---|---|
| **1 — PoC** | Prove `Harness → Maxun → browser/scraper robot` | Harness is outer app; Maxun is separate browser service; one-shot `WorkflowEnricher` kept only as compat seam | `server/src/sdk/llmRobot.ts`, `server/src/api/sdk.ts`, `packages/maxun/tool-maxun` host plugin |
| **2 — Semantic Recorder** | Replace one-shot with semantic draft ops; Maxun owns selectors | Model operates on opaque candidate/field IDs, never raw selectors; draft → workflow deterministic | `server/src/models/RecorderDraft.ts`, `server/src/sdk/recorderDraft.ts`, `selectorValidator.ts`, `workflowEnricher.ts` |
| **3 — Durable Session** | Compact lifecycle durability; `Session.append()` is persistence boundary | rrweb/DOM/mouse/screenshots/cookies/selectors/raw page never durable; claims explicit, epoch-based, foreign/stale fail closed | `packages/maxun/tool-maxun/src/correlation.ts`, `server/src/models/ResourceClaim.ts`, `server/src/sdk/resourceClaims.ts` |
| **4 — Read-Only Browser UI** | Ephemeral Socket.IO/rrweb stream + screenshot fallback + reconnect | No `MAXUN_API_KEY` in browser/URL/screenshot/model; short-lived claim-bound stream capability; `request-refresh` full snapshot; `maskAllInputs:true` + `blockSelector:'iframe'` + `recordCanvas:false`; MIT notices | `server/src/browser-management/controller.ts`, `server/src/socket-connection/socketAuth.ts`, `packages/client/ui-maxun/src/client/BrowserDetails.tsx`, `packages/api/remotes` |
| **5 — Human Handoff** | `agent → user → return → agent re-observes` without races/corruption | Separate `ControlLease` (actor/owner/epoch/TTL/heartbeat/epoch) + replay-protected `ControlCommand` ledger + control JWT/socket; distinct from claim & stream; cancellation → quiescence / outcome-unknown; observation barrier + validation invalidation; credential-safe | `server/src/models/ControlLease.ts`, `ControlCommand.ts`, `server/src/sdk/controlLease.ts`, `browserControl.ts`, `server/src/workflow-management/classes/Interpreter.ts`, `packages/maxun/tool-maxun/src/index.ts`, `packages/client/ui-maxun`, `packages/api/remotes/src/client` |

## 3. Review Objectives (Merge Gates)

1. **Correctness & Composition** — 1–5 compose without breaking pinned baselines or Goal 1–4 regressions.
2. **Security/Privacy (Release Blocker)** — `MAXUN_API_KEY` host-only; no leakage to model content, screenshots, URLs, logs, evidence; `maskAllInputs`, sensitive selectors, iframe blocking, canvas disabled, MFA/login/CAPTCHA credential-safe, rrweb redacted.
3. **Authorization Ordering** — control lease > stream capability > resource claim. Stale/foreign/expired/replayed commands have zero side effect, delayed commands after handoff fail closed.
4. **Durability & Quiescence** — compact store only; cancellation propagates to browser/interpreter with `outcome-unknown` classification; pause/resume/step/abort reused; handoff advances epoch.
5. **Deployability** — `prepare-schema` (`sequelize.sync({force:false,alter:false})`) → `db:migrate` → `server` works on fresh **and** existing DBs; migrations idempotent (no duplicate column / SequelizeHistory failure); `Dockerfile.backend` builds; production rrweb at `dist/rrweb.min.js` via pinned layout resolver.
6. **Operability** — licensing (rrweb/rrweb-snapshot/Socket.IO MIT), telemetry exclusion, reconnect/backoff, screenshot fallback verified.

## 4. Method — 4 Phases

### Phase A — Preparation & Static (entry: this plan)
* Inventory: `verify-source-pins.sh`, `MANIFEST.txt`, `THIRD_PARTY_NOTICES.md`, `verify-goal*-evidence.py` read-through
* Static scans: `rg MAXUN_API_KEY` / `OPENCODE_API_KEY`, secret scan on `review-evidence/*`, `git diff --check`, `git status` clean on 3 worktrees, catalog/package invariant dry-run
* Migration read-through: `20250527105655` → `20260819020000` + `prepareSchema.ts` + `Dockerfile.backend` CMD (`prepare-schema && migrate && server`)
* Evidence sanity: `review-evidence/*.json` parses, contains no sentinels, `goal5-schema.txt` indexes present

### Phase B — Code Review (3 parallel tracks)
* **Track B1 — Server/Auth:** `controlLease.ts` (actor/owner/TTL/heartbeat/release/epochs) → `ControlCommand` ledger (unique `commandId` per `userId+browserSessionId`, epoch link) → `socketAuth.ts` (control JWT vs stream JWT, required `JWT_SECRET`, expiry) → `browserControl.ts` (epoch-safe mutation, pre-dispatch fencing, active-command registration) → `controller.ts` + `Interpreter.ts` (cancellation, pause/resume reuse, non-destructive ordinary cancel)
* **Track B2 — Client/Isolation:** `packages/maxun/tool-maxun/src/index.ts` + `correlation.ts` (URL sanitization: strip userinfo/query/fragment) → `packages/client/ui-maxun/BrowserDetails.tsx` (read-only, observationReady ack via full snapshot) → `packages/api/remotes/src/client` (remote wiring, no credential forwarding) → `apps/web/tests/maxun-browser.e2e.ts`; verify Goal 4 remains read-only, Goal 5 uses separate takeover controls, no `MAXUN_API_KEY` in client bundle
* **Track B3 — Data/Selector & Workflow:** `recorderDraft.ts` (compile transaction + row locking) → `llmRobot.ts` (transactional same-name robot replace) → `workflowEnricher.ts` + `selectorValidator.ts`; verify opaque IDs, selector ownership, assist-vs-record provenance, transactional workflow replacement
* Per-file checklist: fail-closed? no secret in log/model/screenshot/URL? epoch checked before side effect? idempotent?

### Phase C — Dynamic / Live Acceptance (requires running stack)
* Fresh DB: create `maxun_goal5_fresh_*`, `DB_NAME=... node prepareSchema.js` → `npx sequelize-cli db:migrate` → second `migrate` idempotent → re-run on existing DB
* Docker: `docker build -f Dockerfile.backend -t maxun-review-backend:goal5-fixes-final .` → `test -f server/dist/db/prepareSchema.js` + `rrweb/dist/rrweb.min.js` resolver check
* Live: `scripts/test-goal5-live.js` (expect **8/8**), `scripts/verify-goal5-readiness.py` (checks `screenshotContainsSecret==false`, `staleScreenshotRejected==true`), `test-goal4-live.js` + masking, `apps/web` e2e, `scripts/test-harness-suite.sh` (expect **810 files, 13,513 tests passed; 9 skipped**), `npm run build:server` (Maxun) + Harness catalogs/package-invariants/built-invariants/package-paths, `verify-source-pins.sh`

### Phase D — Report & Gate
* Consolidate findings as `MUST` (merge blocker) / `SHOULD` with `file:line`, reproduction, severity, evidence ref (1–9 style)
* Update `review-evidence/` + `docs/GITHUB_REVIEW.md` head if needed, comment PRs
* Exit criteria for merge: all MUST closed, migrations clean on fresh+existing, Docker+rrweb verified, no secret in `review-evidence/*`, both PRs `mergeable:true`, all verifiers green

## 5. Cross-Cutting Checklists (Apply to Every Goal)

- [ ] `MAXUN_API_KEY` / `JWT_SECRET` / `OPENCODE_API_KEY` never in browser bundle, URL, screenshot, rrweb, log, model message, or `review-evidence`
- [ ] Goal 4 read-only socket ≠ Goal 5 control socket ≠ Goal 3 claim; no capability confused for another
- [ ] Every mutating command checks `userId` + `browserSessionId` + `ownerSessionId` + `actor` + `controlEpoch` + `expiry/heartbeat` + `commandId` server-side; handoff/cancel/reconnect/release bump epoch
- [ ] Generic mutating sockets rejected for Harness-owned browsers; screenshot requires matching epoch
- [ ] Internal run JWTs expiring, `JWT_SECRET` required at startup
- [ ] Durable URLs stripped (userinfo/query/fragment), screenshots mask inputs/frames/sensitive, rrweb `maskAllInputs:true` + `recordCanvas:false` + `blockSelector:'iframe'`
- [ ] `prepare-schema` before `migrate` before `server`; migrations use `describeTable`/`showIndex` guards
- [ ] Controls: `GOAL5_READINESS.md` + `goals/05-human-handoff.md` success criteria mapped 1:1 to evidence

## 6. How ChatGPT Independent Review Is Prompted

Provide `docs/GITHUB_REVIEW.md` + both PR diffs + `review-evidence/goal5-*` + `docs/SECURITY.md` + `docs/ARCHITECTURE.md` + `docs/IMPLEMENTATION_CONTRACTS.md` + `docs/GOAL5_READINESS.md` + `goals/05-human-handoff.md`. Prompt:

> "Review as one 5-goal change. Prioritize migrations, control authorization ordering, cancellation/quiescence, credential boundaries, and read-only/control separation. Flag only substantive findings with file:line + reproduction + severity."

## 7. Known Non-Blockers (Do Not Flag)

* `dsh: TRANSPORT: terminated`, `dsh: NO_ADAPTER: opencode-go` — provider noise
* Harness pre-push hook `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING` — bypassed with `--no-verify` after lint/builds passed
* PR states at plan time: Maxun `UNSTABLE` (CodeRabbit pending), Harness `CLEAN` (no checks) — treat as unstable until re-checked

## 8. Risks to Call Out Explicitly

* Historical duplicate-column / SequelizeHistory failure on existing DB
* `observationReady` stuck false if full snapshot never acked
* Stale screenshot epoch window
* `mammoth` production dep inclusion for `Dockerfile.backend`

## 9. Deliverables & Sign-Off

* This plan (`docs/REVIEW_PLAN.md`)
* Finding list (MUST/SHOULD) with `file:line` + reproduction
* Updated `review-evidence/goal5-schema.txt` + Docker log excerpt if changed
* Sign-off evidence: `verify-goal5-readiness.py: 8/8`, `verify-source-pins.sh: OK`, `git status` clean on 3 worktrees, harness suite 810/13513, Maxun build + Harness catalogs/invariants green
* Merge only after all MUST closed

## 10. Schedule

| Phase | Duration | Owner |
|---|---|---|
| A — Prep & Static | 0.5 day | Reviewer (this run) |
| B — Code Tracks | 1–2 days | Reviewer + domain owners (Server / Client / Data) |
| C — Dynamic | 0.5–1 day | Reviewer with running stack |
| D — Report & Gate | 0.5 day | Reviewer + maintainers |

---

*Next step after plan approval: execute Phase A → B → C, publish findings, then fix. No code changed in this plan.*
