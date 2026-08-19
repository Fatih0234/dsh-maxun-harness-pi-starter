# Persistent todo seed

Use Pi's installed persistent todo-item tool to create these tasks. Keep statuses in the tool, not by repeatedly editing this file.

1. Read root `AGENTS.md`, active goal, decision log, and both upstream repositories' agent/contributor instructions.
2. Run `doctor.sh`, bootstrap pinned sources, and verify pins.
3. Import the Pi `opencode-go` credential without printing it.
4. Run direct `opencode-go/deepseek-v4-flash` API smoke.
5. Build/configure Harness and run Harness headless provider smoke.
6. Serve deterministic catalog fixture and inspect it manually.
7. Trace current Maxun `/recordings/llm` → `WorkflowEnricher.generateWorkflowFromPrompt` → persistence call chain in pinned source.
8. Run/document a Maxun one-shot generation baseline against the fixture before changing the seam where practical.
9. Design the smallest API-key SDK route/function reuse; record route/request/response contract in decision log.
10. Implement/refactor Maxun shared one-shot generation+persistence function without duplicating algorithms.
11. Add Maxun API-key endpoint tests, including auth and invalid generation behavior.
12. Inspect current Harness small tool/plugin patterns and per-profile plugin installation conventions.
13. Implement a host-side Maxun integration plugin/client.
14. Register `maxun_create_list_robot` and `maxun_run_robot` (or record why a smaller equivalent is better).
15. Add Harness unit tests using a mocked Maxun service; verify no API key enters tool result/error text.
16. Add real fixture integration: first 5 products, semantic fields, pagination, saved robot, independent rerun.
17. Run Harness headless end-to-end flow using `opencode-go/deepseek-v4-flash`.
18. Inspect `playwright-cli --help`; create final Harness Web acceptance flow and evidence.
19. Test Harness browser refresh after completed result.
20. Run full relevant Maxun/Harness test suites and source-pin verification.
21. Update decision log, POC vs production notes, and Goal 1 evidence checklist.
22. Only after every Goal 1 criterion passes, activate Goal 2. (Completed in the current workspace.)

## Goal 2 continuation seed

23. Verify opaque Recorder Draft discovery and persistence without exposing selectors.
24. Verify semantic list/field edits, pagination testing, preview, and current/multi-page validation diagnostics.
25. Verify deterministic native `scrapeList` compilation, normal execution, API-key isolation, and Goal 1 compatibility.
26. Run the full Harness suite, Maxun build, focused plugin/catalog checks, and credential-free evidence verification.
27. Close Goal 2 only after every criterion in `goals/02-semantic-recorder-service.md` is evidenced; do not activate Goal 3 automatically. (Completed in the current workspace.)

## Goal 3 continuation seed

28. Trace Harness durable session events, projections, refresh/cold recovery, and compaction boundaries. (Completed.)
29. Trace Maxun browser/draft/robot/run lifecycle and explicit ownership operations. (Completed.)
30. Define and implement compact correlation events/projection; keep rrweb/mouse/DOM traffic ephemeral. (Completed.)
31. Integrate reconnect/degraded state and owner/epoch conflict handling. (Completed.)
32. Test surviving/gone browser behavior, cold reconstruction, traffic exclusion, and multi-session claims. (Completed; `.local/evidence/goal3-live.json`.)
33. Document and verify every Goal 3 criterion before considering Goal 4. (Completed by `scripts/verify-goal3-evidence.py`; Goal 3 formal closure audit completed.)

## Goal 4 readiness seed

34. Read `docs/GOAL4_READINESS.md`, `goals/04-browser-ui.md`, and current Harness UI slot/details contracts before implementation.
35. Define and test a claim-bound, short-lived browser stream capability or host proxy; never expose `MAXUN_API_KEY` to browser code.
36. Measure rrweb sensitive-input behavior and implement/test masking for password, input, contenteditable, iframe, canvas, and sensitive text cases.
37. Implement the read-only Harness session-scoped browser details view with resize, reconnect, full-snapshot reset, bounded buffering, and degraded states.
38. Add claim-checked current-browser screenshot fallback and keep frames/screenshots outside durable session/model state.
39. Record rrweb renderer licensing/notice review and run Goal 1–3 regression gates plus Goal 4 Web acceptance.
40. Goal 4 is complete; preserve its read-only stream boundary and acceptance evidence.

## Goal 5 implementation seed

41. Read `goals/05-human-handoff.md`, `docs/GOAL5_READINESS.md`, the decision log, and Maxun/Harness contributor instructions before implementation.
42. Audit the existing Maxun pause/resume/step/abort paths and Harness `AbortSignal` cancellation path; record the control-plane gaps without changing behavior.
43. Design a separate server-side control lease with actor, owner session, control epoch, expiry/heartbeat, and command identity; do not overload the Goal 3 resource claim or Goal 4 stream capability.
44. Define stale-command, handoff-transition, cancellation, observation-barrier, workflow-provenance, and credential-redaction contracts.
45. Add deterministic two-owner, delayed-action, cancellation, return-observation, workflow-provenance, and MFA/login/CAPTCHA fixtures before implementing takeover.
46. Implement Goal 5 behind the control-plane gates; keep the read-only stream and browser visualization boundary out of the mutation path.
47. Run Goal 1–4 regression gates, Goal 5 race/privacy tests, builds, catalogs, source-pin verification, and credential-free evidence checks before closing Goal 5.
