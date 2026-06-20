# Context

## SESSION PROGRESS (2026-06-20)

### Completed

- Fake-calendar MVP, CLI demonstration, and automated tests.
- Explicit approval boundary for event creation.
- Durable development-doc pattern adapted to this repository.
- Read-only Google Calendar adapter, OAuth bootstrap, event mapping, and mocked tests.
- Separate reader and writer contracts so Google reads cannot expose event creation.
- Real-account OAuth and primary-calendar read smoke test completed successfully.

### In Progress

- Planning multi-calendar discovery, selection, and event aggregation.

### Blockers

- None. The existing read-only token can be reused for accessible calendars.

### Verification

- The MVP test suite and CLI approval/rejection paths were verified during the completed phase.
- 23 automated tests pass, including pagination, all-day events, ignored events, malformed data, authentication errors, API errors, and read-only workflow behavior.
- Ruff passes after the Google integration changes.
- The live demo authenticated successfully and returned events from the primary calendar.

The first project phase uses a fake in-memory calendar. This makes the scheduling behavior testable without credentials, OAuth, network access, or accidental writes to a real calendar.

## Architectural Decisions

- Read access is behind `CalendarReader`; write-capable implementations use `CalendarService`.
- `FakeCalendarService` assigns IDs and rejects conflicting writes.
- Scheduling calculations are pure functions where possible.
- Free-time calculation uses half-open intervals.
- Proposal building uses earliest valid slots first.
- CLI input is separate from planning and creation logic.

## Safety Boundaries

- Pending proposals cannot create events.
- Rejected proposals cannot create events.
- Existing events are never deleted or modified.
- Google access remains read-only; the current adapter exposes no creation method.
- Credentials must never be committed.

## Minimum Gap Behavior

Minimum gap expands existing events before free-time calculation. For example, a 30-minute gap around a 12:00-13:00 event blocks 11:30-13:30. The proposal builder also inserts the same gap between sessions created from the same available slot.

## AI Infrastructure Notes

The project should use durable docs and progressive disclosure rather than a large agent framework at this stage. The useful imported ideas are:

- keep plan, context, and tasks in files that survive chat resets;
- keep guidance small and split deeper references only when needed;
- add automation only after a repeated workflow problem appears;
- translate external patterns into calendar-specific safety rules.

Future project-specific AI guidance should focus on natural-language request parsing, missing-information handling, and preserving the approval gate before real calendar writes.

## Key Files

- `src/calendar_agent/calendar/base.py`: calendar service boundary that future integrations must implement.
- `src/calendar_agent/calendar/fake_calendar.py`: safe in-memory reference implementation.
- `src/calendar_agent/calendar/google_calendar.py`: read-only Google API adapter and OAuth bootstrap.
- `src/calendar_agent/workflow/orchestrator.py`: coordinates proposal and creation flow.
- `src/calendar_agent/workflow/approval.py`: enforces proposal approval state.
- `src/calendar_agent/models/`: validates requests, events, proposals, and workflow state.
- `tests/integration/test_fake_calendar_workflow.py`: end-to-end safety net for the current workflow.

## Quick Resume

1. Read this file, then `tasks.md`, then the relevant phase in `plan.md`.
2. Begin Phase 3 by listing calendars available through the Google Calendar API.
3. Define an explicit include/exclude configuration for calendars that should block time.
4. Add source-calendar identity before merging events into the planning workflow.
