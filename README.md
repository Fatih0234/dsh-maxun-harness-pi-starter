# Maxun × DeepSeek Harness — Pi implementation starter

This workspace is an implementation handoff for a long-running **Pi coding-agent** session. It is intentionally structured around small goals, persistent todos, pinned upstream source, deterministic fixtures, and executable smoke tests.

## Product direction

The fixed outer architecture is:

```text
DeepSeek Harness → Maxun capabilities → browser / scraper robot
```

DeepSeek Harness owns conversation, model/tool orchestration, durable session correlation, and eventually the integrated UI. Maxun remains the owner of browser automation, list analysis, selectors, recorder construction, robot persistence, and robot execution.

Goal 1 proved the original premise with a one-shot Maxun list-robot seam. Goal 2 replaces that hidden construction path for normal Harness use with a semantic Recorder Draft flow:

```text
Harness semantic draft tools
  → Maxun opaque list/field candidates
  → semantic include/exclude/rename and pagination preview
  → current/multi-page validation diagnostics
  → deterministic native scrapeList robot
  → normal Maxun execution
```

The one-shot route remains only as a compatibility seam. Goal 3 adds compact durable lifecycle correlation, refresh/cold reconstruction, explicit ownership, and browser reconnect/degraded state; browser embedding and human handoff remain future goals.

## Start here

From an empty project folder, unzip this package and run:

```bash
./scripts/doctor.sh
./scripts/bootstrap-sources.sh
./scripts/import-pi-opencode-key.py
./scripts/install-source-deps.sh
./scripts/setup-harness-provider.sh
./scripts/test-opencode-go-direct.sh
./scripts/test-harness-headless.sh
./scripts/verify-goal2-evidence.py
```

Then launch Pi in this folder. Pi should read `AGENTS.md`, `goals/ACTIVE.md`, and `todo/seed.md` before touching source.

The bootstrap fetches **full upstream source trees at exact research commits** into `sources/`. They are intentionally not embedded inside this ZIP; that keeps the handoff small, auditable, and reproducible while still giving Pi complete source context locally.

## Important local files

- `.env.local` — generated, ignored, may contain `OPENCODE_API_KEY` and `MAXUN_API_KEY`.
- `.local/` — generated Harness home, logs, smoke-test outputs.
- `sources/` — cloned upstream repositories.
- `goals/` — long-running implementation goals and success criteria.
- `todo/seed.md` — persistent-todo seed for Pi.
- `tests/fixtures/catalog/` — deterministic paginated product-list site.
- `.local/evidence/goal2-verification.json` — credential-free Goal 2 acceptance evidence.
- `.local/evidence/goal3-live.json` — credential-free Goal 3 refresh/reconnect/ownership evidence.
- `scripts/test-goal2-live.py` — reproducible authenticated semantic-draft integration check.
- `scripts/verify-goal3-evidence.py` — Goal 3 evidence verifier.

## Provider

Harness must use:

- provider: `opencode-go`
- model: `deepseek-v4-flash`

The setup reads the existing Pi credential from `~/.pi/agent/auth.json` at runtime and exports it as `OPENCODE_API_KEY`. The literal secret is never committed or included in this archive.

## Source pins

See `config/sources.json`. The two implementation repositories are checked out on local integration branches rooted at the research SHAs. Supporting repositories are detached, read-only references.

## Working philosophy

1. Inspect actual current code before changing it.
2. Use the Goal extension to keep one implementation goal active.
3. Use the persistent todo tool to record executable tasks and findings across sessions.
4. Build the smallest vertical slice first.
5. Use deterministic fixtures before public websites.
6. Prefer existing Maxun capabilities over reimplementation.
7. Keep Maxun and Harness separately deployable.
8. Record design changes in `docs/DECISION_LOG.md`.

## Current implementation status

Goals 1–5 are complete. Goal 3's durable Harness–Maxun correlation baseline is evidenced in `.local/evidence/goal3-live.json`; Goal 4 and Goal 5 acceptance are documented in `docs/GOAL4_READINESS.md` and `docs/GOAL5_READINESS.md`.

Goal 4 is complete under its 5,000,000-token implementation budget: claim-bound stream authorization, masked rrweb replay, screenshot fallback, and a persistent/resizable read-only details view are implemented and evidenced in `.local/evidence/goal4-live.json`, `.local/evidence/goal4-rrweb-masking.json`, `.local/evidence/goal4-web-acceptance.json`, and `.local/evidence/goal4-licensing.json`. Goal 5 is complete under a 5,000,000-token budget: server-side control ownership, epoch fencing, cancellation, human handoff, race protection, fresh observations, workflow provenance, and credential-privacy evidence are recorded in `docs/GOAL5_READINESS.md`. No later goal is active.
