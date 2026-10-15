# Skyra Browser Worker Service — Functionality

Last maintained: 2026-10-14. This is the canonical project requirement/capability reference. Current implementation and planned work are explicitly distinguished.

## Product and users

Scoped browser sessions for research, application interaction and evidence capture. Supports Jarvis and quality workflows through explicit lifecycle and resource grants.

Users: Skyra owner and authorized employees; service consumers act under scoped user/project/account identity. Commercial products stay independent of internal Jarvis privileges.

## Current implementation

FastAPI/Playwright prototype exists. Its global browser/session state and missing extract capability need repair; no target session isolation or durable jobs are established.

## Required capabilities

- Task-owned browser contexts, pages and explicit session lifecycle
- Navigate, inspect, extract, screenshot and controlled interaction
- Session isolation across projects/accounts and bounded lifetime
- Action evidence with page identity and result verification
- Domain/network access policy and secret-aware artifact capture
- Browser resource cleanup after cancellation and process failure

## Interface direction

The following interfaces are design proposals from the project baseline, not a guarantee of working endpoints. Existing prototype routes must be checked against their source before consumer integration.

| Proposed operation | Purpose |
|---|---|
| `POST /v1/sessions` | Create a task-scoped browser context |
| `POST /v1/sessions/{id}/navigate` | Navigate within granted network scope |
| `POST /v1/sessions/{id}/extract` | Extract specified page data using validated selectors |
| `POST /v1/sessions/{id}/actions` | Perform a bounded action on an identified page |
| `DELETE /v1/sessions/{id}` | Close owned browser resources idempotently |

## Acceptance requirements

- Cookies and storage never cross task/account boundaries
- The extract contract has matching client and service integration tests
- Canceled tasks release pages and browser processes
- Invalid/stale page handles fail rather than act on another tab
- Private-network navigation requires explicit network grant

## Explicit boundaries and open decisions

- Browser automation is not equivalent to reliable API integration
- Search-provider contracts and allowed targets must be explicit
- Native Windows application control is outside browser session scope

A proposal, simulation or passing build does not authorize production release. Account connection, publication, money movement and employee/payroll actions obey their configured permission policies.

## Initial specification set

Retain and update the original nine documents. They describe product requirements, system architecture, development rules, design, tasks, memory, API/events, testing/acceptance and security/operations. These current overview files supplement them; they do not replace them.

- [Product requirements](01_PRODUCT_REQUIREMENTS.md)
- [System architecture](02_SYSTEM_ARCHITECTURE.md)
- [Development rules](03_DEVELOPMENT_RULES.md)
- [Design system](04_DESIGN_SYSTEM.md)
- [Project tasks](05_PROJECT_TASKS.md)
- [Project memory](06_PROJECT_MEMORY.md)
- [API and event contracts](07_API_AND_EVENTS.md)
- [Testing and acceptance](08_TESTING_AND_ACCEPTANCE.md)
- [Security and operations](09_SECURITY_AND_OPERATIONS.md)
