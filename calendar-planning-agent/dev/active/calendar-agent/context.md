# Context

## SESSION PROGRESS (2026-06-20)

### Completed

- Fake-calendar MVP, CLI demonstration, and automated tests.
- Explicit approval boundary for event creation.
- Durable development-doc pattern adapted to this repository.
- Read-only Google Calendar adapter, OAuth bootstrap, event mapping, and mocked tests.
- Separate reader and writer contracts so Google reads cannot expose event creation.
- Real-account OAuth and primary-calendar read smoke test completed successfully.
- Multi-calendar discovery, explicit selection, source tracking, aggregation, and deduplication implemented.
- Live multi-calendar aggregation verified with the user's selected calendars.
- Configurable read-only planning-preview CLI implemented.
- Live Google-backed planning preview completed successfully without modifying events.

### In Progress

- No implementation task is currently in progress.

### Blockers

- None. The existing read-only token and selected calendar IDs can be reused.

### Verification

- The MVP test suite and CLI approval/rejection paths were verified during the completed phase.
- 23 automated tests pass, including pagination, all-day events, ignored events, malformed data, authentication errors, API errors, and read-only workflow behavior.
- Ruff passes after the Google integration changes.
- The live demo authenticated successfully and returned events from the primary calendar.
- 27 automated tests now pass, including calendar discovery, configuration parsing, merging, deduplication, and fail-closed partial errors.
- 30 automated tests now pass, including planning-preview argument validation and request construction.
- Live multi-calendar discovery and merged event reads completed successfully.
- The live planning preview produced proposals against selected calendars and preserved the read-only boundary.

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
- `src/calendar_agent/google_calendars_demo.py`: lists accessible calendars and selection metadata.
- `src/calendar_agent/google_read_demo.py`: prints merged events from explicitly selected calendars.
- `src/calendar_agent/google_plan_demo.py`: builds and prints real-calendar scheduling previews without writes.
- `src/calendar_agent/workflow/orchestrator.py`: coordinates proposal and creation flow.
- `src/calendar_agent/workflow/approval.py`: enforces proposal approval state.
- `src/calendar_agent/models/`: validates requests, events, proposals, and workflow state.
- `tests/integration/test_fake_calendar_workflow.py`: end-to-end safety net for the current workflow.

## Quick Resume

1. Read this file, then `tasks.md`, then the relevant phase in `plan.md`.
2. Review Phase 5 before implementing any Google Calendar write capability.
3. Define write failure, partial-success, retry, and idempotency behavior before requesting broader OAuth scope.
4. Preserve the existing preview as the required approval input rather than writing directly from a request.
