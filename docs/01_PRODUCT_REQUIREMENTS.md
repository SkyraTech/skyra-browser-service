# Skyra Browser Worker Service — Product Requirements

## Maintained specification — current status

Updated 2026-10-14. This is one of the nine initial project documents and must be retained and updated in place. Remove only redundant per-work reports; do not replace or delete the initial specification set.

FastAPI/Playwright prototype exists. Its global browser/session state and missing extract capability need repair; no target session isolation or durable jobs are established.

The following references hold the detailed current implementation; requirements and proposed designs below must not be read as already built:

- [Current architecture and database design](ARCHITECTURE.md)
- [Current functionality and implementation boundaries](FUNCTIONALITY.md)
- [Current milestone and verification summary](DEVELOPMENT.md)

Prepared: 2026-10-14. Requirement/design baseline. Use the maintained current-status section above to distinguish implemented work from planned work.

## Product overview

Scoped browser sessions for research, application interaction and evidence capture. Supports Jarvis and quality workflows through explicit lifecycle and resource grants.

## Problem and current baseline

Existing FastAPI/Playwright service at 59e614c. Browse/search create temporary pages in a shared context; click/type use a global active page. Jarvis calls /extract, which is absent. Search accepts an engine parameter but implementation is Google-specific.

Existing prototypes do not establish production readiness. The objective is a reusable, testable boundary with explicit ownership and verifiable outcomes.

## Target users and goals

Primary users: Skyra owner and authorized employees; consuming applications and delegated agents act under those users' scoped identities. Commercial customers use separately branded products rather than inheriting internal Jarvis privileges.

Success means the capabilities below pass recorded acceptance checks, survive expected failures and expose enough evidence for a human to review the result.

## Core requirements / MVP

- **FR-01:** Task-owned browser contexts, pages and explicit session lifecycle
- **FR-02:** Navigate, inspect, extract, screenshot and controlled interaction
- **FR-03:** Session isolation across projects/accounts and bounded lifetime
- **FR-04:** Action evidence with page identity and result verification
- **FR-05:** Domain/network access policy and secret-aware artifact capture
- **FR-06:** Browser resource cleanup after cancellation and process failure

## Boundaries

This project delivers its declared capabilities only. No automatic production release, account creation, purchase or broader permission is implied by an AI plan. Article-dashboard implementation, ERP, Skyra Platform and QR changes are outside this documentation initiative. Future local models and hosted Jarvis must preserve the same authorization contracts.

## User journey

An authorized caller selects a capability and resource scope, submits validated input, receives either a result or a durable job reference, follows progress and retrieves evidence. Policy may require an exact-action approval before execution. Failures present recovery guidance without claiming success.

## Acceptance and unresolved decisions

See [testing](08_TESTING_AND_ACCEPTANCE.md) for release evidence and [tasks](05_PROJECT_TASKS.md) for implementation sequence.

- Browser automation is not equivalent to reliable API integration
- Search-provider contracts and allowed targets must be explicit
- Native Windows application control is outside browser session scope
