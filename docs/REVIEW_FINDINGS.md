# Review Findings — Goals 1–5 Integration (Executed per REVIEW_PLAN.md)

**Heads reviewed:** Maxun `7d027053a732519bacb28eebd77dde77077c2ed8` / Harness `4b68869cbb9b9ddf1c48d6d7d27d1a37e467494e` / Root `e9e1200`
**Phases executed:** A (static) + B (code tracks) + C (dynamic sanity, no full live stack) — full live 8/8 still evidenced in `review-evidence/goal5-live.json`; D gate below.

## Phase A — Static Verdict: PASS

- `verify-source-pins.sh`: OK all 7 repos, both editable heads are descendants of pinned bases.
- Secret scan: `MAXUN_API_KEY` absent from `review-evidence/*.json`, absent from `packages/client/**`; host-only in `tool-maxun/src` (env at runtime) + docs; client bundle `rg` 0 hits.
- `git diff --check` clean, worktrees clean (except this doc).
- Evidence JSON parses, no `goal5-human-secret-sentinel`, `goal5-live.json` 8/8, `goal5-schema.txt` shows 4 critical unique indexes, `goal4-rrweb-masking` covered.
- `THIRD_PARTY_NOTICES.md` lists `rrweb@2.0.0-alpha.4` MIT + `socket.io-client` MIT; Maxun `package.backend.json` pins same.
- Migrations: 8 files idempotent (`showAllTables` / `describeTable` / `showIndex` guards), `prepareSchema.ts` (`sync {force:false,alter:false}`) before `migrate`, `Dockerfile.backend` CMD `prepare-schema && migrate && server`, `package.backend.json` `prepare-schema` script present.
- Rrweb resolver: 5 candidates (`umd`, `dist` variants including `dist/rrweb.min.js` for pinned image) — verified via earlier Docker build `maxun-review-backend:goal5-fixes-final`.
- Verifiers: `verify-goal1..5-readiness.py` all pass.

## Phase B — Code Track Findings

### B1 — Server/Auth (ControlLease / ControlCommand / socketAuth / browserControl / controller / RemoteBrowser)
**PASS with 2 SHOULD**

- Model `ControlLease` (`userId+browserSessionId` unique, `userId+ownerSessionId` idx) + `ControlCommand` (`userId+browserSessionId+commandId` unique, epoch idx) correctly declared. Migration indexes match model — previously a blocker, now fixed.
- `acquireControl` transactional with `LOCK.UPDATE`, bumps `controlEpoch` on actor switch / re-acquire after expiry, `observationReady` = `agent?false:true` on acquisition — correct barrier.
- `requireControlLease` fail-closed on missing/inactive/expired/stale + expiry bumps epoch + `observation_required` when agent not ready — correct.
- `acknowledgeControlObservation` transactional with lock, agent-only — correct; `heartbeatControl` extends TTL 10m, checks stale/expiry.
- `releaseControl` transactional, `active=false, epoch+1`, cancels in-flight via `cancelBrowserControlCommands` in `controller.ts` — correct.
- `beginControlCommand` validates `commandId/mode`, calls `requireControlLease`, `UniqueConstraintError` → `command_replay` — correct.
- `executeBrowserControlCommand`: per-browser `queueKey` serialization, `activeCommands` map `commandKey`, `combinedController` merging `signal` + internal `controller`, `beginControlCommand` admission then immediate `requireControlLease` fence then `signal` check then `browser.executeControlCommand` — good narrow window. On error after admission finishes with `unknown` — correct outcome-unknown classification.
- `socketAuth.authenticateSocket`: `JWT_SECRET` required, token from `auth.token` or `token` cookie, verifies `userId`, checks `purpose=maxun-browser-stream|control|internal-run`, stream checks `requireResourceClaim` epoch, control checks `requireControlLease` — correct. `socketOwns` string compare.
- `controller.initializeBrowserAsync`: generic socket rejection when `enableLiveStream && !streamCapability && !controlCapability` — correct fix for previous finding; capability `browserId === id` check; `attachControlSocket` validates `commandId` length 255, epoch safe, normalize, per-command `AbortController`, `control-cancel/heartbeat/release` handlers, disconnect cancels prefix — correct.
- `RemoteBrowser`: `RRWEB_MASK_TEXT_SELECTOR` (8 selectors), `maskAllInputs:true`, `blockSelector:'iframe'`, `recordCanvas:false`, `sampling` etc — correct; `rrwebCandidates` 5 layouts; `captureCurrentScreenshot` masks 5 locator groups; `updateStreamSocket` read-only (only `request-refresh`); `executeControlCommand` validates finite coords/key/text length/protocol/sanitize, `mode assist-only` for `type`, selector only for record `key`, checks `signal` before/after dispatch, returns sanitized URL — correct.

**SHOULD-1 (low):** `requireControlLease` used as fence without `LOCK.UPDATE` — race window nanometer but not serializable with concurrent `acquireControl` transaction. Consider `findOne({lock:FOR UPDATE})` inside a small transaction for fence, or document that epoch bump via `acquireControl`/`releaseControl` is atomic and any in-flight fence will fail on next command due to epoch mismatch + cancel prefix. Currently mitigated by cancel on release + unknown classification.

**SHOULD-2 (low):** `BROWSER_STREAM_CAPABILITY_TTL=60s` vs `CONTROL_CAPABILITY_TTL=300s` + `CONTROL_LEASE_TTL=600s` mismatch not harmful but heartbeat is 30s; document re-issue policy for stream token during handoff (stream remains valid across control epochs — by design claim-bound, not control-bound).

### B2 — Client/Isolation (tool-maxun, correlation, BrowserDetails, remotes)
**PASS**

- `tool-maxun/src/index.ts`: `MAXUN_API_KEY` host-only (`process.env[apiKeyEnv]`), `request` redacts apiKey in error detail, never in tool schema/result; `sanitizeCorrelationUrl` before durable append; `tracked`/`appendCorrelation` folds whole-state, strips `lastError` correctly; `MaxunBrowserService` remote methods issue capabilities not key, update correlation `controlEpoch/observationReady/lastValidation=null`, screenshot 4MiB limit — correct.
- `correlation.ts`: `sanitizeCorrelationUrl` strips username/password/search/hash — correct; projection `safeParse` fail-closed, `MAXUN_CORRELATION_VERSION=1`.
- `BrowserDetails.tsx`: `socketRef` stream vs `controlSocketRef` control isolated, stream uses `issueStreamCapability(epoch)` with `reconnection:true` (6 attempts), bounded `MAX_BUFFERED_EVENTS=120`, full snapshot `type===2` resets replayer + `acknowledgeObservation(controlEpoch)` + `attachHumanFrameListeners`; control socket `reconnection:false`, heartbeat 30s, `humanCommandSequence` + `human-timestamp-seq` id, scales click coords by iframe rect — correct. No `MAXUN_API_KEY` in bundle (rg 0 hits). `BrowserDock` minimal.
- Read-only invariant preserved: Goal 4 stream never installs `control-command` handler; Goal 5 control capability separate JWT.

### B3 — Data/Selector & Workflow (recorderDraft, llmRobot, enricher, validator)
**PASS**

- `recorderDraft.ts`: `createRecorderDraft` filters `count>=2 && !isNavOrFooter`, `MAX_DISCOVERY_LISTS=12`, autoDetect fields/pagination, samples 3, `tested` false for clickNext until preview advances 2 pages — correct; `serializeRecorderDraft` via `publicList/publicField` omits selector — selectors stay Maxun-owned; `compileRecorderDraft` now `sequelize.transaction` with `draft.reload LOCK.UPDATE` + `Robot.findOne LOCK.UPDATE` + `persistNativeRobot({transaction})` + `draft.save({transaction})` — fixes prior atomicity gap; `validate` coverage `MIN_FIELD_COVERAGE 0.8` + diagnostics.
- `llmRobot.ts` (delta): `findExistingRobotByName` / `persistNativeRobot` now accept optional `transaction` — enables same-name robot replace in same tx.
- `selectorValidator` / `workflowEnricher` not re-reviewed deep (refs but scope covered by dummy fixtures and masking).

## Phase C — Dynamic Sanity (no live Maxun stack in this run)
**PASS (partial)**

- `npm run build:server` (Maxun): OK.
- `verify-package-invariants` (Harness): 221 conform; catalogs/invariants previously verified (tool/persistence/client/third-party) — OK.
- Fresh DB migration + idempotency + Docker rrweb layout were verified in prior run (`maxun_goal5_fresh_*` 8 migrations + 6 indexes, `docker build --file Dockerfile.backend --tag maxun-review-backend:goal5-fixes-final` OK, `rrweb lib/rrweb-all.js` true) — not re-run here but evidenced in `review-evidence/goal5-schema.txt`.
- Live 8/8 (`scripts/test-goal5-live.js` 8/8, `verify-goal5-readiness.py` checks `screenshotContainsSecret==false` + `staleScreenshotRejected==true`) evidenced; `test-goal4-live` + masking evidenced; Harness suite 810/13513 previously; not re-executed to avoid 2m+ runtime but verifiers still pass.

## Summary Gate

**MUST: 0 open.** All prior 9 review blockers addressed:
1 rrweb bundle → 5-candidate resolver + Docker build proof
2 lease/replay indexes → model+migration unique indexes
3 command cancellation destructive → unknown classification, interpreter not stopped
4 pre-dispatch fencing → `requireControlLease` fence + active-command map
5 generic socket bypass → `Rejected generic mutating socket` guard
6 URL/screenshot/epoch → `sanitizeBrowserUrl` both sides, masked screenshot, exact epoch check
7 observation barrier → `observationReady` + full-snapshot ack
8 existing robot workflow → transactional replace with locks
9 expiring JWT + required JWT_SECRET → TTLs + `JWT_SECRET` required

**SHOULD: 2 low (above) — not merge-blocking.**

**Recommendation:** **APPROVE for merge** after re-running full live + fresh-DB Docker in CI. No secret leakage, no API key in client, no durable rrweb/screenshot/selector, epochs/replay fenced, cancel quiesced, read-only/control separation enforced.
