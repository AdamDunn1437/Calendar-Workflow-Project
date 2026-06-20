# Development Documentation

This directory preserves enough project state for a future coding session to resume without relying on chat history.

## The Pattern

Use three documents for work that is likely to take more than one session or involves several related changes:

```text
dev/active/<task-name>/
|-- plan.md
|-- context.md
`-- tasks.md
```

- `plan.md` explains the goal, phases, risks, and acceptance criteria.
- `context.md` records current progress, decisions, constraints, important files, and the exact next step.
- `tasks.md` is the actionable checklist and should reflect the real implementation state.

The current project-level documents live in `dev/active/calendar-agent/`.

## Working Agreement

At the start of a substantial task:

1. Read `context.md`, then `tasks.md`, then the relevant part of `plan.md`.
2. Add or refine the planned phase and its acceptance criteria.
3. Mark one clear next task as in progress in `context.md`.

During implementation:

1. Update `context.md` after a significant decision, discovery, blocker, or milestone.
2. Check off a task only after its acceptance criteria are satisfied.
3. Add newly discovered work to both the plan and checklist when it changes scope.

Before ending a session:

1. Make `SESSION PROGRESS` match reality.
2. Record tests or verification already run.
3. Write a concrete `Quick Resume` instruction.

When a task is complete, move its directory from `dev/active/` to `dev/archive/` if the history remains useful.

## When Not to Use It

Skip new dev docs for a trivial edit, a small single-file fix, or work that can be completed and verified in one short session. The documents should reduce rediscovery, not create ceremony.

## Calendar-Specific Requirements

Any plan involving real calendar data or model-produced input must explicitly cover:

- typed validation at system boundaries;
- deterministic scheduling calculations;
- explicit approval before calendar writes;
- credential and OAuth-token handling;
- tests for rejected, pending, and approved proposals;
- rollback or safe failure behavior for external calendar calls.
