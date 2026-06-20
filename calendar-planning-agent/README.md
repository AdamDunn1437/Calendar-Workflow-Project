# Calendar Planning Agent

This project is the first foundation for a personal calendar-planning workflow. It can inspect a fake in-memory calendar or read Google Calendar, find free time, detect conflicts, propose events, and create fake-calendar events only after explicit approval.

Google Calendar access is intentionally read-only. Google writes remain out of scope until the approval and failure behavior is designed and tested separately.

## Current Capabilities

- List events in a requested date range.
- Detect overlapping calendar events.
- Find free time across one or more days.
- Respect daily allowed hours.
- Apply minimum gaps around existing events and between proposed sessions.
- Build proposals using the earliest valid slots first.
- Require explicit approval before creating events.
- Demonstrate the workflow with a small command-line program.
- Read paginated, recurring, timed, and all-day Google Calendar events.
- Ignore cancelled events and events marked as free by Google Calendar.
- Discover calendars available to the authenticated Google account.
- Merge explicitly selected calendars while retaining each event's source.

## Architecture

- `models/` contains Pydantic models for events, requests, proposals, and workflow state.
- `calendar/` contains the calendar interface and fake in-memory implementation.
- `calendar/google_calendar.py` contains the read-only Google adapter and OAuth bootstrap.
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

The local workflow is documented in `dev/README.md`. In short: use `plan.md` for strategy and acceptance criteria, `context.md` for current session state and decisions, and `tasks.md` as the implementation checklist. Update the context and checklist after meaningful progress and leave a concrete quick-resume instruction before ending a session.

This pattern is most useful for multi-session work such as Google Calendar integration or natural-language parsing. Skip it for small, self-contained fixes.

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

To include Google Calendar support, install the `google` extra as well:

```powershell
python -m pip install -e .[dev,google]
```

## Configure Read-Only Google Calendar Access

1. Create or select a project in Google Cloud Console.
2. Enable the Google Calendar API.
3. Configure the OAuth consent screen for your account.
4. Create an OAuth client with application type **Desktop app**.
5. Download the client file as `credentials.json` in the project root, or set `GOOGLE_CALENDAR_CREDENTIALS_FILE` to its location.
6. Copy `.env.example` to `.env` if you want to record local path choices. Export those values in your shell because this project does not automatically load `.env` files.

Discover available calendars and their IDs:

```powershell
python -m calendar_agent.google_calendars_demo
```

Select the calendars that should block time by setting a comma-separated environment value:

```powershell
$env:GOOGLE_CALENDAR_IDS="primary,classes@example.com,labs@example.com"
```

Only explicitly listed calendars are read; the default remains `primary`. Then run the read-only demonstration:

```powershell
calendar-agent-google-read
```

Or run it as a module:

```powershell
python -m calendar_agent.google_read_demo
```

The first run opens a browser for consent and stores the refreshable user token at `.secrets/google-calendar-token.json` by default. Credential and token patterns are excluded by `.gitignore`. The adapter requests only Google's `calendar.readonly` OAuth scope and has no `create_event` method.

Multi-calendar reads fail closed: if any selected calendar cannot be read, planning receives no partial availability. Events shared across calendars are deduplicated using their Google iCalendar identity and time range. Every retained event records its source calendar ID and display name.

## Preview A Real Schedule

Generate a proposal against the selected Google calendars without creating or modifying anything:

```powershell
python -m calendar_agent.google_plan_demo `
  --title "Study session" `
  --duration 90 `
  --sessions 3 `
  --days 7 `
  --daily-start 09:00 `
  --daily-end 21:00 `
  --gap 30
```

Optional `--start-date YYYY-MM-DD` chooses a future starting date. Without it, the preview starts today. The command prints the busy events considered, proposed sessions, and an explicit confirmation that no Google event was changed.

References: [Google Calendar Python quickstart](https://developers.google.com/workspace/calendar/api/quickstart/python), [Events list reference](https://developers.google.com/workspace/calendar/api/v3/reference/events/list), and [Calendar authorization scopes](https://developers.google.com/workspace/calendar/api/auth).

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

- Google Calendar writes
- LangChain or LangGraph
- A database
- A web frontend
- LLM APIs
- Background jobs
- Multiple agents
- Claude/Codex hook systems or custom skills
- Automatic deletion or modification of existing events

## Google Calendar Integration

`GoogleCalendarReader` implements the read-only `CalendarReader` contract. It discovers accessible calendars, reads an explicit selection, expands recurring events into instances, follows page tokens, validates API data as `CalendarEvent` models, and normalizes all-day events using the calendar timezone. Write-capable calendars implement the separate `CalendarService` contract, so the Google reader cannot accidentally be used for creation.

Write support should come later and must preserve the approval boundary already enforced by the workflow.

## Future AI Workflow Infrastructure

Once the fake-calendar and Google Calendar phases are stable, the next useful AI-assist layer would be a small calendar-planning skill or guide that tells future coding agents:

- how to convert natural language into a `SchedulingRequest`,
- which fields must be confirmed instead of guessed,
- how approval must work before writes,
- which tests to run after scheduling changes.

Avoid copying a full infrastructure showcase into this repo. Add only the pieces that solve a real local problem.
