# Skyra Browser Worker Service — Development

Last maintained: 2026-10-14. This is the cross-milestone summary; the initial task and memory documents are also retained and maintained. Keep architecture and implementation decisions in [ARCHITECTURE.md](ARCHITECTURE.md), requirements in [FUNCTIONALITY.md](FUNCTIONALITY.md).

## Current status

FastAPI/Playwright prototype exists. Its global browser/session state and missing extract capability need repair; no target session isolation or durable jobs are established.

## Planned phases

- [ ] Phase 1: Replace shared global state with task/session ownership.
- [ ] Phase 2: Implement versioned navigation, extraction and interaction contracts.
- [ ] Phase 3: Add domain controls, lifecycle limits and evidence capture.
- [ ] Phase 4: Integrate Jarvis and quality-worker browser profiles.
- [ ] Phase 5: Verify concurrent sessions and crash cleanup.

No phase is marked complete without implementation and recorded acceptance evidence. The earlier baseline inspection is not a runtime test result.

## Development and review rules

- Scope changes to a requirement and meaningful acceptance evidence. Keep providers/storage in adapters and policy outside model logic.
- Prefer reproducible dependency/formatter/type-check configuration. Validate versions before upgrades; no rewrite merely for language uniformity.
- Use structured errors, bounded timeouts, cancellation and retry classification. Label mocks explicitly; they cannot establish production acceptance.
- Review scope, migrations, credentials, failure/recovery behavior and logs. Model agreement is not independent verification.
- Keep product-owned tests with the product. Quality tools aggregate evidence; they do not replace tests with a coverage percentage.
- Do not stage, commit or push. The owner reviews and commits manually. Complete a substantial milestone, inspect Git status/diffs, provide one appropriate commit message, and wait for owner confirmation before the next milestone.
- Update the initial nine project documents and these current implementation references in place as relevant. Add architecture decisions/change rows here or in architecture; do not create per-task Markdown reports. Detailed execution artifacts belong in runtime storage and Git retains document history.

## Documentation checkpoint

2026-10-14: initial specifications are retained alongside consolidated current architecture/functionality/development references; only redundant per-work reports are removed. Current vs proposed schema/capabilities are separated. No application code or runtime data changed by consolidation.

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
