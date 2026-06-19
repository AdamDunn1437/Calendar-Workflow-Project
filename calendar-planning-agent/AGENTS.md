# Repository Instructions For Coding Agents

- Preserve the approval boundary. Calendar creation must require explicit approval in code.
- Keep scheduling calculations deterministic. Do not ask an LLM to calculate times.
- Validate all external and model-produced data with typed models.
- Never store credentials, OAuth tokens, or secrets in the repository.
- Add tests for behavior changes.
- Keep calendar integrations behind the calendar interface.
- Do not add large frameworks without a demonstrated need.
- Keep the project beginner-friendly with small functions and explicit names.
- Keep durable context in `dev/active/calendar-agent/plan.md`, `context.md`, and `tasks.md`.
- Use progressive disclosure for docs. Keep top-level guidance concise and move deep detail into focused files only when needed.
- Customize external infrastructure patterns to this calendar project instead of copying hooks, agents, or commands wholesale.
- Add only one new automation or agent-assist feature at a time, and document the repeated problem it solves.
