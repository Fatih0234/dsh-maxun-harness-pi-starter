# Repository research index for implementation

This is a fast navigation index. Verify definitions/call sites in the pinned checkout before editing.

## Maxun

- `server/src/api/sdk.ts` — API-key SDK robot create/execute/run endpoints; likely home for the POC external seam.
- `server/src/routes/storage.ts` — signed-in application robot routes; locate the `/recordings/llm` implementation and its persistence logic.
- `server/src/sdk/workflowEnricher.ts` — one-shot natural-language list workflow generation, semantic labels, intent filtering, pagination, validation.
- `server/src/sdk/selectorValidator.ts` — server-side selector validation, field fill rates, pagination tests.
- `server/src/sdk/browserSide/pageAnalyzer.js` — repeated groups / candidate fields on real validation page.
- `server/src/browser-management/classes/RemoteBrowser.ts` — Playwright browser/context/page, rrweb/recorder/interpreter composition.
- `server/src/browser-management/classes/BrowserPool.ts` — process-local browser ownership/reservations.
- `server/src/browser-management/inputHandlers.ts` — reconstructed-browser input → Playwright actions; pause/manual interaction gate; URL validation.
- `server/src/workflow-management/classes/Generator.ts` — recorded actions → workflow and save path.
- `server/src/workflow-management/classes/Interpreter.ts` — wrapper over `maxun-core`, pause/resume/abort/results.
- `server/src/workflow-management/utils.ts` — selector preference logic.
- `server/src/models/Robot.ts` — persisted robot JSON/metadata.
- `server/src/middlewares/api.ts` — `x-api-key` auth.
- `server/src/routes/auth.ts` — register/login/API-key generation helper routes.
- `src/context/browserSteps.tsx` — `ListStep`, labels, pagination/limit, `scrapeList` action serialization.
- `src/context/browserActions.tsx` — Recorder list `initial → pagination → limit → complete` state.
- `src/components/browser/BrowserWindow.tsx` — React-coupled list capture/group/field behavior.
- `src/components/recorder/DOMBrowserRenderer.tsx` — rrweb Replayer + interaction bridge.
- `src/components/recorder/RightSidePanel.tsx` — list capture progression and preview.
- `src/helpers/clientSelectorGenerator.ts` — client-side repeated structure/fingerprint analysis.
- `src/helpers/clientPaginationDetector.ts` — client pagination detection.
- `node_modules/maxun-core` after `npm install` — inspect the exact installed runtime package (`WorkflowFile`, interpreter, browser-side scraper); do not rely on a separate GitHub repository existing.

## DeepSeek Harness

- `packages/core/tools/src/index.ts` — tool registration/execute contract.
- `packages/core/agent-loop/src/agent.ts` — agent lifecycle/cancellation.
- `packages/core/agent-loop/src/tool-calls.ts` — scheduling, persisted calls/results, presentation metadata.
- `packages/core/session/src/*` — event-sourced session.
- `packages/session/session-projection/src/index.ts` — later durable Maxun state projection.
- `packages/interaction/tool-ask-user/src/index.ts` — model-facing tool plugin pattern with cancellation.
- `packages/api/remotes/*` — later typed host/client business RPC.
- `packages/client/ui-layout/src/client/AppFrame.tsx` — persistent details column; future browser home.
- `packages/client/ui-conversation/src/client/apply.ts` — conversation/details slots.
- `packages/llm/llm-pi-ai/*` — `opencode-go` provider route and credential/config handling.
- `packages/core/agent-default-model/*` — process/session default provider/model.
- `packages/bundle/base/cordis.patch.yml` — base model/provider/settings/goal/todo composition.
- `packages/bundle/web-app/cordis.patch.yml` — Web host/client split and browser UI plugin roster.
- `apps/cli/reference/README.md` — profile layers, `--patch`, source-run commands.

## Supporting source

- `sources/pi-reference` — provider catalog/auth behavior relevant to the shared OpenCode Go setup.
- `sources/rrweb-reference` — browser replay internals for later UI work.
- `sources/playwright-reference` — browser semantics/testing reference.
- `sources/cordis-reference` — plugin/service composition details.
- `sources/maxun-node-sdk-reference` — public Maxun SDK expectations and client patterns.
