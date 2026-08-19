# Goal 5 — human/agent browser handoff

## Implementation status

Goal 5 implementation and acceptance are complete under a 5,000,000-token budget. The control-plane contract and evidence are documented in `docs/GOAL5_READINESS.md`; preserve the Goal 4 read-only boundary in future changes.

## Goal

Support:

```text
agent control → user control → user actions → return control → agent re-observes → continue
```

without races or corrupting scraper state.

## Success criteria

- [x] Maxun enforces server-side control ownership.
- [x] Ownership changes increment a control epoch/generation and stale browser-mutating commands are rejected.
- [x] Harness cancellation is bridged to active Maxun browser/interpreter work.
- [x] Existing Maxun pause/resume/abort semantics are reused where appropriate.
- [x] User-control mode distinguishes transient assist actions from deliberately recorded workflow edits.
- [x] On return, the agent receives a fresh observation and stale validations are invalidated.
- [x] Slow-navigation/action race tests pass.
- [x] MFA/login/CAPTCHA handoff works without putting credentials into model/session logs.
