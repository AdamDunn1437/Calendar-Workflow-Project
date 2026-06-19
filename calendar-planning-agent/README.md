# Calendar Planning Agent

This project is the first foundation for a personal calendar-planning workflow. It can inspect a fake in-memory calendar, find free time, detect conflicts, propose events, and create those events only after explicit approval.

Google Calendar is intentionally out of scope for this first version. The calendar operations are behind a small interface so a Google Calendar implementation can be added later without changing the scheduling logic.

## Current Capabilities

- List events in a requested date range.
- Detect overlapping calendar events.
- Find free time across one or more days.
- Respect daily allowed hours.
- Apply minimum gaps around existing events and between proposed sessions.
- Build proposals using the earliest valid slots first.
- Require explicit approval before creating events.
- Demonstrate the workflow with a small command-line program.

## Architecture

- `models/` contains Pydantic models for events, requests, proposals, and workflow state.
- `calendar/` contains the calendar interface and fake in-memory implementation.
- `scheduling/` contains deterministic time calculations and proposal construction.
- `workflow/` coordinates planning, approval, and creation.
- `main.py` is only a CLI demonstration. Business logic stays outside user input handling.

## AI-Assisted Development Approach

This project borrows a few useful infrastructure ideas from agentic coding workflows, adapted to stay small and beginner-friendly:

- Keep context in durable docs. The `dev/active/calendar-agent/` folder records the plan, decisions, and task checklist so future work can resume without relying on chat history.
- Use progressive disclosure. Keep top-level docs short, then add focused reference files only when a topic becomes large enough to need one.
- Prefer one useful workflow improvement at a time. Do not add hooks, agents, or automation until there is a repeated project problem they clearly solve.
- Customize infrastructure to this calendar domain. Patterns from other projects should be translated into calendar-specific safety rules, tests, and docs.
- Preserve the core safety boundary. Any future AI assistant, parser, skill, or calendar integration must still produce validated data and require approval before writes.

## Development Docs

Active planning lives in:

- `dev/active/calendar-agent/plan.md`
- `dev/active/calendar-agent/context.md`
- `dev/active/calendar-agent/tasks.md`

Update these files when major decisions change, especially before adding Google Calendar integration or natural-language parsing.

## Why Approval Exists

Calendar writes are intentionally gated. A pending or rejected proposal cannot create events. This protects the user from accidental calendar changes and gives future Google Calendar writes a clear safety boundary.

## Install Dependencies

If `uv` is available:

```powershell
uv sync --extra dev
```

Otherwise:

```powershell
python -m pip install -e .[dev]
```

## Run The CLI

```powershell
python -m calendar_agent.main
```

Type `yes` when prompted to create the proposed fake-calendar events. Any other response rejects the proposal.

## Run Tests

```powershell
pytest
```

## Out Of Scope For Now

- Google OAuth
- Google Calendar reads or writes
- LangChain or LangGraph
- A database
- A web frontend
- LLM APIs
- Background jobs
- Multiple agents
- Claude/Codex hook systems or custom skills
- Automatic deletion or modification of existing events

## Future Google Calendar Integration

The next phase should add a Google Calendar read service behind the existing `CalendarService` interface. Write support should come later and must preserve the approval boundary already enforced by the workflow.

## Future AI Workflow Infrastructure

Once the fake-calendar and Google Calendar phases are stable, the next useful AI-assist layer would be a small calendar-planning skill or guide that tells future coding agents:

- how to convert natural language into a `SchedulingRequest`,
- which fields must be confirmed instead of guessed,
- how approval must work before writes,
- which tests to run after scheduling changes.

Avoid copying a full infrastructure showcase into this repo. Add only the pieces that solve a real local problem.
