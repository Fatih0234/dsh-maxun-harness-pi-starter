# Working with the pinned upstreams

`config/sources.json` records research SHAs. The bootstrap creates local implementation branches for Maxun and Harness, rooted at those commits.

## Rules

- Do not immediately update to the latest upstream while proving Goal 1.
- First make the vertical slice work against the researched implementation.
- If an upstream bug forces an update, record old SHA/new SHA/reason in `docs/DECISION_LOG.md` and rerun the relevant baseline tests.
- Read each repository's own `AGENTS.md` and contribution instructions before editing.
- Keep commits scoped by repository/subsystem.
- Supporting reference checkouts are read-only unless the active goal explicitly requires changes.

## Why pin

Harness is in developer preview and explicitly warns of compatibility-breaking changes. Maxun's SDK/socket/LLM areas are also active. Reproducible source context is more valuable than silently drifting during the first integration.
