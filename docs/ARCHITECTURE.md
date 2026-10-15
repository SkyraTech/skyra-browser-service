# Skyra Browser Worker Service — Architecture

Last maintained: 2026-10-14. Canonical architecture, data ownership and decision record; update in place.

## Current state

FastAPI/Playwright prototype exists. Its global browser/session state and missing extract capability need repair; no target session isolation or durable jobs are established.

## Responsibility and technology

Scoped browser sessions for research, application interaction and evidence capture. Supports Jarvis and quality workflows through explicit lifecycle and resource grants.

Python/FastAPI/Pydantic and pinned Playwright with matching browser binaries; isolated worker process and pytest integration fixtures.

This stack describes direction where code is not built. Exact upgrades require manifest/lockfile review and compatibility tests; this documentation change installs or upgrades nothing.

## Component and integration boundaries

- [skyra-service-contracts](../../skyra-service-contracts/README.md)
- [skyra-service-foundation](../../skyra-service-contracts/docs/ARCHITECTURE.md#foundation-component)

Use versioned HTTP/OpenAPI/JSON Schema contracts and authorized MCP adapters. Consumers never read/write another service’s database. Credentials, provider accounts and organization/project scope are explicit; optional unavailable services are disabled rather than simulated as success.

## Database architecture

No service-owned database is implemented. This worker should not duplicate Jarvis task state. Current session/capture state is process-local; future durable sessions/artifact references require an explicit owner and retention design. Provider credentials and profiles are protected configuration, not a shared writable customer store.

Browser contexts must be isolated by identity/session/job; a global active page is insufficient for concurrent customers. A session lease may reference `session_id`, `actor`, `profile_ref`, `job_id`, `expires_at` and an artifact owner. This is a proposed session contract, not a new table.

## Execution and failure rules

Persist intent before a side effect. Use bounded ownership leases, idempotency keys and result reconciliation; do not promise exactly-once external delivery without provider support. Verify webhook signatures and deduplicate inbox records. Approval binds exact action, account, resource, payload and expiry; MCP discovery grants no privilege.

## Security and operations

Protect credentials, redact errors/logs, validate configuration and deny cross-organization access. Untrusted model/provider/document content cannot change policy. Define export/deletion and retention by data class; test backup/restore for any durable implementation. Hosted customer services must remain independent of the owner’s laptop. Release evidence includes exact source/toolchain/profile; production deployment remains a separately authorized action.

## Proposed folder direction

Keep domain/application rules separate from transport and provider/storage adapters. Tests live with the owning project; machine-readable contracts and release fixtures are versioned. Existing source folders stay in place until a tested migration. A backend-only service does not need an invented UI dashboard; host interfaces display truthful connection/job/permission states.

## Decisions and unresolved work

- Browser automation is not equivalent to reliable API integration
- Search-provider contracts and allowed targets must be explicit
- Native Windows application control is outside browser session scope

| Date | Architecture change | State |
|---|---|---|
| 2026-10-14 | Project ownership, technology direction and data model consolidated into this maintained file | Proposed where no implementation exists |

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
