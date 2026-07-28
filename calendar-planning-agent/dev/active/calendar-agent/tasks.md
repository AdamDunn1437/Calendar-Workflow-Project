# Tasks

## Phase 1: Fake Calendar MVP - Complete

- [x] Inspect repository.
- [x] Create project scaffold.
- [x] Add Pydantic domain models.
- [x] Add calendar interface.
- [x] Add fake in-memory calendar service.
- [x] Add conflict detection.
- [x] Add free-time calculation.
- [x] Add proposal builder.
- [x] Add approval boundary.
- [x] Add workflow orchestrator.
- [x] Add CLI demonstration.
- [x] Add unit tests.
- [x] Add integration tests.
- [x] Add README and agent instructions.
- [x] Install dependencies.
- [x] Run tests.
- [x] Run formatter or linter.
- [x] Verify CLI with rejected proposal.
- [x] Verify CLI with approved proposal.
- [x] Review git diff.
- [x] Integrate lightweight AI workflow principles into docs.

## Phase 2: Google Calendar Read Integration - Complete

- [x] Decide OAuth flow and local token-storage policy.
  - Acceptance: secrets and refresh tokens are excluded from version control and setup is documented.
- [x] Define external event mapping and API error behavior.
  - Acceptance: all returned events are validated as `CalendarEvent` values and read failures cause no writes.
- [x] Separate `CalendarReader` from write-capable `CalendarService`.
- [x] Implement a read-only Google service behind `CalendarReader`.
  - Acceptance: scheduling code works without knowing which calendar implementation supplied the events.
- [x] Add mocked unit and integration tests.
  - Acceptance: success, pagination, malformed data, authorization failure, and API failure paths are covered.
- [x] Re-run the complete test and lint suite.
- [x] Complete a real-account read-only smoke test.
  - Acceptance: the demo lists expected events and no write scope or write method is present.

## Phase 3: Multi-Calendar Read Aggregation - Complete

- [x] List all calendars available to the authenticated account, including paginated results.
  - Acceptance: each calendar has an ID, display name, timezone, access role, and visibility metadata.
- [x] Define explicit calendar inclusion and exclusion configuration.
  - Acceptance: users can choose which calendars block time without changing source code.
- [x] Add source-calendar identity to mapped events or an appropriate wrapper model.
  - Acceptance: merged events remain traceable to their original calendar.
- [x] Read events from all selected calendars and merge them chronologically.
  - Acceptance: planning receives one validated event collection across selected calendars.
- [x] Define duplicate-event and partial-failure behavior.
  - Acceptance: duplicates do not double-block time and failures identify the affected calendar.
- [x] Add tests for discovery, selection, pagination, time zones, all-day events, duplicates, empty calendars, and partial failures.
- [x] Add a multi-calendar read demonstration and update user setup documentation.
- [x] Run the complete test and lint suite.
- [x] Complete a real-account multi-calendar smoke test.
  - Acceptance: discovery lists expected calendars and the read demo merges only selected calendars with correct source labels.

## Phase 4: Real-Calendar Planning Preview - Complete

- [x] Add explicit CLI arguments for scheduling constraints.
- [x] Build a validated, timezone-aware `SchedulingRequest` from CLI input.
- [x] Run `CalendarWorkflow.plan()` against selected Google calendars.
- [x] Print source-labelled busy events and proposed sessions.
- [x] Keep the preview path entirely read-only with no approval or creation action.
- [x] Add unit tests for request construction and invalid argument values.
- [x] Document preview usage and run the full test and lint suite.
- [x] Complete a live planning-preview smoke test.
  - Acceptance: proposed sessions avoid all printed busy events and no Google event is changed.

## Phase 5: Approved Google Calendar Writes - Complete

- [x] Design write failure, idempotency, conflict recheck, retry, and partial-success behavior.
- [x] Keep broader OAuth permission in a separate token from read-only access.
- [x] Implement create-only writes to one explicit destination calendar.
- [x] Keep writes reachable only through approved proposals.
- [x] Test pending, rejected, approved, conflict, repeat-approval, and partial-failure paths.
- [x] Test the interactive CLI rejection and exact-approval paths end to end with a mocked API.
- [x] Run the full test and lint suite.
- [x] Complete one deliberate live write smoke test (user-reported successful on 2026-06-23).

## Phase 6: Natural-Language Requests - Not Started

- [ ] Define which request fields must be confirmed rather than inferred.
- [ ] Convert model output into validated `SchedulingRequest` data.
- [ ] Test missing, ambiguous, invalid, and valid inputs.
- [ ] Consider a project-specific calendar-planning skill after parsing behavior is stable.

## Quick Resume

The baseline calendar agent is complete through approved Google writes. Keep Phase 6 natural-language work separate so the deterministic scheduler and approval boundary remain stable.
