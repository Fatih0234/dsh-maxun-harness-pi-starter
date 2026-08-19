# Goal 4 — live Maxun browser in Harness

## Goal

Give the user persistent visual confidence by showing the Maxun browser inside Harness without sending the high-frequency browser stream through model context.

## Implementation status

Goal 4 implementation and acceptance are complete under the 5,000,000-token budget and are documented in `docs/GOAL4_READINESS.md`. Goals 1–3 remain complete and provide the durable session/browser correlation, owner claim, epoch, reconnect, and degraded-state baseline. Goal 5 was intentionally out of scope for this completed goal and is now complete under its separate contract in `docs/GOAL5_READINESS.md`.

Important pre-existing findings:

- Maxun already has rrweb emission and a `DOMBrowserRenderer`/`Replayer` implementation, but it is not mounted in Harness's persistent details area.
- The Harness UI has session-scoped slots and a resident details-shell architecture, but no Maxun browser details entry point.
- Maxun configures rrweb with `maskAllInputs: true`, explicit sensitive-text selectors, `blockSelector: 'iframe'`, and `recordCanvas: false`; deterministic coverage now passes for password/text/contenteditable/iframe/canvas fixtures.
- `MAXUN_API_KEY` must remain host-side. Goal 4 browser code must use a short-lived claim-bound capability or a server proxy.

## Success criteria

- [x] Browser lives in Harness's persistent/resizable details area, not as a mutating historical chat row.
- [x] Live stream is independently authenticated and correlated to the current session/browser.
- [x] Browser reconnect after Harness page reload is tested.
- [x] rrweb sensitive-input behavior is measured and redaction/masking is implemented where required.
- [x] Screenshot fallback is available for pages rrweb reconstructs poorly.
- [x] Model receives only compact observations/screenshots when needed, never the full rrweb stream.
- [x] Licensing implications of the chosen renderer approach are recorded.

## Implementation handoff

The implementation and acceptance contract is recorded in `docs/GOAL4_READINESS.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_CONTRACTS.md`, `docs/SECURITY.md`, and `docs/TEST_STRATEGY.md`. Keep Goal 4 read-only; browser mutation and user takeover belong to Goal 5.
