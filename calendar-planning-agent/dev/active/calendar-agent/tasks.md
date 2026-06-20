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

## Phase 3: Multi-Calendar Read Aggregation - Next

- [ ] List all calendars available to the authenticated account, including paginated results.
  - Acceptance: each calendar has an ID, display name, timezone, access role, and visibility metadata.
- [ ] Define explicit calendar inclusion and exclusion configuration.
  - Acceptance: users can choose which calendars block time without changing source code.
- [ ] Add source-calendar identity to mapped events or an appropriate wrapper model.
  - Acceptance: merged events remain traceable to their original calendar.
- [ ] Read events from all selected calendars and merge them chronologically.
  - Acceptance: planning receives one validated event collection across selected calendars.
- [ ] Define duplicate-event and partial-failure behavior.
  - Acceptance: duplicates do not double-block time and failures identify the affected calendar.
- [ ] Add tests for discovery, selection, pagination, time zones, all-day events, duplicates, empty calendars, and partial failures.
- [ ] Add a multi-calendar read demonstration and update user setup documentation.
- [ ] Run the complete test and lint suite.

## Phase 4: Approved Google Calendar Writes - Not Started

- [ ] Design write failure and partial-success behavior before implementation.
- [ ] Implement writes that are reachable only for approved proposals.
- [ ] Test pending, rejected, approved, and partial-failure paths with mocked APIs.

## Phase 5: Natural-Language Requests - Not Started

- [ ] Define which request fields must be confirmed rather than inferred.
- [ ] Convert model output into validated `SchedulingRequest` data.
- [ ] Test missing, ambiguous, invalid, and valid inputs.
- [ ] Consider a project-specific calendar-planning skill after parsing behavior is stable.

## Quick Resume

Start Phase 3 by implementing read-only calendar discovery, then use its metadata to design explicit calendar selection.
