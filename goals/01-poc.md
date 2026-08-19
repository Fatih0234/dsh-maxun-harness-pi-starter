# Goal 1 — prove agent-driven native Maxun list robot creation

## Goal

From DeepSeek Harness, using `opencode-go/deepseek-v4-flash`, a user can describe list data to collect from a URL and the agent can cause Maxun to create a **persisted native list-extraction robot**, run that saved robot through Maxun's normal runtime, and return the requested rows.

## Success criteria

All criteria must be satisfied.

- [x] `sources/maxun` is based on Maxun research SHA `6ef14c7c89fac18b5ba771a1228ee064e1d7810f`.
- [x] `sources/deepseek-harness` is based on Harness research SHA `99f6f02fecdb7dff40c3fbc9470f5907c29f74ca`.
- [x] Direct OpenCode Go smoke succeeds with model `deepseek-v4-flash`.
- [x] Harness headless smoke succeeds using provider `opencode-go`, model `deepseek-v4-flash`.
- [x] The existing Maxun one-shot workflow-generation path is covered by a baseline test on the deterministic fixture before/refactoring while possible.
- [x] Maxun exposes a small API-key-authenticated POC operation that reuses existing `WorkflowEnricher.generateWorkflowFromPrompt(...)` behavior and persists a normal extract robot.
- [x] The new Maxun operation does not duplicate the one-shot generation algorithm.
- [x] A Harness host plugin registers a model-facing Maxun creation capability without exposing `MAXUN_API_KEY` to the browser/model.
- [x] Harness can execute the saved robot through Maxun's normal SDK/runtime path.
- [x] The persisted robot contains a native `scrapeList` action rather than generated Playwright source.
- [x] On the fixture request, the robot extracts product name, price, rating, image URL, product URL, review count and follows pagination.
- [x] Limit `5` produces exactly the first five fixture products in order.
- [x] The saved Maxun robot can be executed a second time independently of its creation call/conversation reasoning.
- [x] Maxun-side tests pass.
- [x] Harness-side tests pass.
- [x] A real end-to-end Harness headless run passes.
- [x] A Harness Web scenario is exercised with `playwright-cli` and stored as reproducible evidence.
- [x] Refreshing the Harness Web page after completion does not erase the completed conversation/tool outcome.
- [x] The POC shortcut and production seam are documented separately.

## Evidence

- `.local/evidence/goal1-verification.json` records the provider, native `scrapeList` persistence, pagination, limit, exact first five rows, and independent rerun.
- `.local/evidence/harness-headless-maxun.json` and `.local/evidence/harness-web-acceptance.json` record the Harness headless/Web acceptance flows, including refresh persistence.
- `scripts/verify-source-pins.sh`, `scripts/verify-goal1-evidence.py`, Maxun build, focused tests, and the full Harness suite provide the final gates.

## Non-goals

Browser embedding, human takeover, Recorder Draft service, multi-step semantic editing, generic self-repair, cross-Maxun-restart browser continuity, production multi-tenancy, detail-page augmentation.

## Stop condition

When all criteria pass, update `goals/ACTIVE.md` to Goal 2 only after recording results and remaining unknowns in the decision log.
