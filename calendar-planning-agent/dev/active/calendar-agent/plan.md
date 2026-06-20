# Project Plan

## Executive Summary

Build a safe, testable calendar-planning agent in increments: prove deterministic scheduling against an in-memory calendar first, add read-only access across the user's relevant calendars, connect those reads to real planning previews, and only then consider approved writes and validated natural-language input.

## Current State

The fake-calendar MVP, Google read-only integration, multi-calendar aggregation, and configurable real-calendar planning preview are complete and verified with a real account. Google writes and natural-language parsing have not started.

## 1. Fake Calendar MVP

- Create validated models for events, requests, proposals, and workflow state.
- Implement a fake in-memory calendar service.
- Add deterministic conflict detection and free-time calculation.
- Build proposals from available slots.
- Require explicit approval before creating events.
- Cover the workflow with unit and integration tests.

## 2. Google Calendar Read Integration

- Add a Google Calendar service behind the existing calendar interface.
- Read events only.
- Keep fake-calendar tests as the core scheduling safety net.

Acceptance criteria:

- Google responses are converted into validated `CalendarEvent` models.
- Read failures are surfaced without changing local or remote calendar state.
- Credentials and OAuth tokens remain outside version control.
- Existing fake-calendar tests continue to pass.

Implementation notes:

- `CalendarReader` and write-capable `CalendarService` are separate contracts.
- OAuth uses only the `calendar.readonly` scope.
- The adapter expands recurring events, follows pagination, and validates timed and all-day events.
- A real-account read-only smoke test completed successfully on 2026-06-20.

## 3. Multi-Calendar Read Aggregation

- List calendars available to the authenticated account.
- Allow explicit selection of calendars that should block time.
- Read and merge events from every selected calendar.
- Preserve source-calendar identity for troubleshooting and future display.
- Continue using read-only OAuth access.

Acceptance criteria:

- Users can discover available calendars without copying IDs from each settings page.
- Inclusion is explicit and configurable; hidden or irrelevant calendars can be excluded.
- Events from selected calendars are merged chronologically and duplicate events are handled safely.
- One calendar failure is reported with its calendar identity and never causes a write.
- Tests cover pagination, mixed time zones, all-day events, empty calendars, duplicates, and partial API failures.

Implementation notes:

- `GOOGLE_CALENDAR_IDS` provides explicit comma-separated selection and defaults to `primary`.
- Calendar discovery includes hidden calendars so users can make an informed selection.
- Shared events are deduplicated by iCalendar UID plus start/end time.
- Reads fail closed and identify the failed calendar rather than planning from incomplete availability.
- Live discovery and aggregation completed successfully on 2026-06-20.

## 4. Real-Calendar Planning Preview

- Build validated scheduling requests from explicit CLI arguments.
- Read busy events from the selected Google calendars.
- Run the deterministic scheduling workflow against real availability.
- Print proposed sessions without offering approval or creation.

Acceptance criteria:

- Dates, daily hours, duration, session count, and minimum gap are configurable.
- The preview reports which busy events were considered and which sessions were proposed.
- Invalid CLI values are rejected before API work begins.
- The command cannot create or modify Google Calendar events.
- A live preview avoids known events across every selected calendar.

Implementation notes:

- The live planning preview completed successfully on 2026-06-20.
- The preview reports considered busy events and proposed sessions, then exits without offering a write action.

## 5. Google Calendar Write Integration

- Add event creation behind the same interface.
- Preserve the approval boundary.
- Add tests with mocked Google Calendar responses.

Acceptance criteria:

- Pending and rejected proposals cannot call the external write API.
- Approved proposals create only the events represented by the validated proposal.
- Partial failures are reported clearly and do not trigger silent retries or unrelated changes.

## 6. Natural-Language Parsing

- Convert plain-language requests into `SchedulingRequest` data.
- Validate parsed data before scheduling.
- Ask for missing required scheduling information instead of inventing it.

Acceptance criteria:

- Parser output is validated as a `SchedulingRequest` before scheduling begins.
- Missing or ambiguous required fields are returned for confirmation.
- Time-slot calculation remains deterministic and outside the language model.

## 7. Optional Workflow Framework

- Consider a workflow framework only after the simple orchestrator becomes hard to maintain.
- Keep deterministic scheduling logic outside any framework.

## Cross-Cutting AI Workflow Principles

- Preserve context in the dev docs before and after major changes.
- Keep docs modular: short overview files first, focused reference files only when a topic grows.
- Add agentic infrastructure gradually. Start with a single project-specific guide or skill before considering hooks, slash commands, or specialized agents.
- Treat external infrastructure showcases as pattern libraries, not dependencies.

## Key Risks

- Accidental real-calendar writes: mitigate with read-only integration first and tests at the approval boundary.
- Ambiguous times or time zones: require explicit values and validate all parsed requests.
- Credential exposure: use environment configuration and keep token files out of version control.
- Infrastructure growth outpacing the project: add workflow automation only when a repeated problem justifies it.

## Success Measures

- All scheduling and approval tests remain green through each phase.
- A new session can identify the current state and next task from the dev docs alone.
- No external write occurs without a validated, explicitly approved proposal.
