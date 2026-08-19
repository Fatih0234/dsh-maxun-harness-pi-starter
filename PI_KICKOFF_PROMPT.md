# Pi kickoff prompt

Paste the following as the first instruction to Pi after opening this project folder:

> Read `AGENTS.md`, `goals/ACTIVE.md`, `goals/05-human-handoff.md`, `docs/GOAL5_READINESS.md`, `todo/seed.md`, and `docs/DECISION_LOG.md` before editing anything. Goals 1–5 are complete; preserve the Goal 3 durable Harness–Maxun baseline, Goal 4 read-only browser boundary, and Goal 5 control/credential guarantees. No later goal is active. Run the source/provider/bootstrap checks described by the project as needed. Inspect the pinned Maxun and DeepSeek Harness implementations before making design decisions, and record any deviation from this handoff in the decision log.

The agent should preserve the completed Goals 3–4 baselines, review `docs/GOAL5_READINESS.md` for the control-plane handoff, and use repository inspection to resolve implementation questions instead of asking the user for code-location facts. Keep the existing Goal 4 view read-only until Goal 5's server-side ownership, epoch, cancellation, race, and privacy gates are implemented and evidenced.
