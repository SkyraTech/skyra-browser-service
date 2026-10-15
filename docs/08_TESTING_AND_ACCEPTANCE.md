# Skyra Browser Worker Service — Testing and Acceptance

## Maintained specification — current status

Updated 2026-10-14. This is one of the nine initial project documents and must be retained and updated in place. Remove only redundant per-work reports; do not replace or delete the initial specification set.

FastAPI/Playwright prototype exists. Its global browser/session state and missing extract capability need repair; no target session isolation or durable jobs are established.

The following references hold the detailed current implementation; requirements and proposed designs below must not be read as already built:

- [Current architecture and database design](ARCHITECTURE.md)
- [Current functionality and implementation boundaries](FUNCTIONALITY.md)
- [Current milestone and verification summary](DEVELOPMENT.md)

Prepared: 2026-10-14. Requirement/design baseline. Use the maintained current-status section above to distinguish implemented work from planned work.

## Project acceptance matrix

| ID | Required outcome | Evidence status |
|---|---|---|
| AC-01 | Cookies and storage never cross task/account boundaries | Not executed |
| AC-02 | The extract contract has matching client and service integration tests | Not executed |
| AC-03 | Canceled tasks release pages and browser processes | Not executed |
| AC-04 | Invalid/stale page handles fail rather than act on another tab | Not executed |
| AC-05 | Private-network navigation requires explicit network grant | Not executed |

## Requirement traceability

Each requirement must receive one or more concrete test IDs. The matrix above captures critical scenarios but does not imply exhaustive feature coverage.

| Requirement | Behavior to verify | Test mapping |
|---|---|---|
| FR-01 | Task-owned browser contexts, pages and explicit session lifecycle | Unassigned; required before implementation completion |
| FR-02 | Navigate, inspect, extract, screenshot and controlled interaction | Unassigned; required before implementation completion |
| FR-03 | Session isolation across projects/accounts and bounded lifetime | Unassigned; required before implementation completion |
| FR-04 | Action evidence with page identity and result verification | Unassigned; required before implementation completion |
| FR-05 | Domain/network access policy and secret-aware artifact capture | Unassigned; required before implementation completion |
| FR-06 | Browser resource cleanup after cancellation and process failure | Unassigned; required before implementation completion |

## Test layers

- Unit: domain decisions, policy evaluation, state transitions, parsing and failure classification.
- Contract: input/output examples, error shape, consumer compatibility and event schemas.
- Integration: real isolated storage, adapter behavior, credentials scoping, retries and provider sandbox where available.
- End-to-end: authorized user workflow through actual boundaries; Playwright where a browser/UI is involved and Windows process tests for desktop launches.
- Recovery/security: crash between intent and dispatch, duplicate events, expired leases, denied scopes, cross-tenant attempts, stale approvals and secret redaction.

For package-only projects, independent consumer tests replace server/deployment tests. Provider tests must use approved test accounts; do not send messages, publish content or incur charges against arbitrary live users.

## Release gate

Record commit, tool/dependency versions, test command, environment, timestamps, result and artifact links. All required checks must pass or carry an explicitly reviewed exception. Track line and branch coverage separately; establish project thresholds from the first trustworthy baseline and protect critical paths with direct behavioral tests. A high coverage percentage alone is not acceptance.

Dependency and vulnerability findings are triaged by severity, exploitability and reachability. No unreviewed critical/high finding in the release scope. Active DAST requires an owned, explicitly selected target; baseline scans and active attacks are different operations. Quality runners must isolate untrusted code and cap runtime/resource usage.

The initial documentation pass ran no runtime tests; later implementation evidence is recorded in the current-status references above. Future reports must distinguish simulated providers, local integration and production-like verification.
