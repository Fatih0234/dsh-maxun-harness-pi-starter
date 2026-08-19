# Security notes

## Required for Goals 1 and 2

- Keep `OPENCODE_API_KEY` and `MAXUN_API_KEY` out of git, model content, screenshots, and logs.
- Harness host plugin owns the Maxun API key; browser code never receives it.
- Recorder Draft and compile responses expose opaque IDs/semantic metadata only; server-owned selectors stay in Maxun draft/workflow state.
- Disable Harness telemetry during local development (`DSH_TELEMETRY_DISABLED=1`).
- Use trusted fixture URLs for local acceptance.

## Goal 3 durable correlation controls

- `MAXUN_API_KEY` remains host-side; correlation events and all model-visible tool results are credential-free.
- `maxun/correlation` stores only service/resource IDs, lifecycle summaries, validation/error counts, and owner epoch. It excludes rrweb frames, mouse/pointer events, DOM mutations, screenshots, cookies, selectors, and raw page payloads.
- Maxun resource claims are explicit and unique per authenticated user/resource. Competing sessions receive structured HTTP 409 `claim_conflict`; releases and browser health checks require the owner session and epoch.
- Browser health requires an explicit claim and returns a non-disclosing not-found result for a gone or unauthorized browser. Durable draft/robot identifiers are not treated as proof that a browser is still alive.

## Known Maxun concern from code inspection

Maxun's navigation validation limits protocols to HTTP/HTTPS but explicitly does not fully mitigate internal-host SSRF. Before arbitrary public URL access, add/review:

- localhost/loopback/private/link-local/cloud metadata blocks;
- DNS/redirect revalidation;
- DNS rebinding mitigation;
- outbound browser-worker network policy.

## Multi-tenancy concern to verify

API-key middleware maps a key to a user, but inspect every SDK robot/run lookup and confirm it also scopes resource access to that user. Add a two-user authorization test before treating the SDK as a production multi-tenant boundary.

## Untrusted page content

DOM/HTML/page text is untrusted data and can contain prompt injection. The model must not treat instructions from a scraped page as authorization or system policy.

## Goal 4 browser visualization readiness

Goal 4 implementation is complete. The authenticated browser boundary is:

- Keep `MAXUN_API_KEY` strictly in the Harness host/Maxun service boundary; never put it in browser JavaScript, a URL, a screenshot, a Socket.IO auth payload, or a model result.
- Use a short-lived stream capability or host proxy bound to `serviceInstanceId`, `browserSessionId`, `ownerSessionId`, claim epoch, and expiry. Durable IDs alone are not authorization.
- Treat rrweb frames, pointer/mouse events, DOM mutations, screenshots, cookies, selectors, and raw page data as ephemeral UI data. They must not enter `Session.append()`, the model transcript, or durable correlation events.
- Authorization evidence covers a foreign capability rejection, claim-bound owner/epoch checks, gone-browser cleanup, and reconnect after Harness reload; stale/foreign release cases remain covered by Goal 3.
- Maxun uses `maskAllInputs: true`, explicit sensitive-text selectors, `blockSelector: 'iframe'`, and `recordCanvas: false`. Password, ordinary text, contenteditable, iframe, canvas, and marked-sensitive fixtures are covered by `.local/evidence/goal4-rrweb-masking.json`.
- The Harness view is read-only; it has no browser input, navigation, or takeover controls. Browser mutation and human control are Goal 5 concerns.
- The installed `rrweb`, `rrweb-snapshot`, and Socket.IO client dependencies are MIT; generated `THIRD_PARTY_NOTICES.md` records the dependency review.

See `docs/GOAL4_READINESS.md` for the completed browser-view contract. Goal 5 implementation and acceptance are documented in `docs/GOAL5_READINESS.md`.

## Goal 5 control-plane security gates (implemented)

- Browser mutation requires a separate Maxun control lease; Goal 3 resource ownership and Goal 4 stream authorization are not sufficient control authorization.
- Every mutating command must validate authenticated user, browser/session, actor, control epoch, expiry/heartbeat, and command identity server-side. Handoff and cancellation must invalidate delayed commands.
- Human login, MFA, and CAPTCHA content remains ephemeral. Credentials and secret page data must not enter rrweb, screenshots, logs, model messages, workflow edits, or durable session events; screenshot fallback masks inputs, frames, and marked-sensitive elements, and durable URLs strip userinfo/query/fragment components.
- Goal 4's client remains read-only; these Goal 5 gates have executable race and privacy evidence.
