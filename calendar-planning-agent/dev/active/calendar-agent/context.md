# Context

The first project phase uses a fake in-memory calendar. This makes the scheduling behavior testable without credentials, OAuth, network access, or accidental writes to a real calendar.

## Architectural Decisions

- Calendar access is behind `CalendarService`.
- `FakeCalendarService` assigns IDs and rejects conflicting writes.
- Scheduling calculations are pure functions where possible.
- Free-time calculation uses half-open intervals.
- Proposal building uses earliest valid slots first.
- CLI input is separate from planning and creation logic.

## Safety Boundaries

- Pending proposals cannot create events.
- Rejected proposals cannot create events.
- Existing events are never deleted or modified.
- Google Calendar integration is intentionally deferred.
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
