# Personal Agent Workspace Prompts

Use these prompts when you want an agent to help organize personal coding projects, reusable agent instructions, references, and experiments. The safest pattern is to make the agent inspect first, propose changes second, and only edit after you approve the plan.

## Recommended Structure

```text
Calendar Workflow/
  agents/
    shared/
    coding/
    personal/

  projects/
    project-name/
      AGENTS.md
      dev/
        README.md
        active/
          agent-name/
            plan.md
            context.md
            tasks.md
        archive/

  references/
    imported-examples/

  experiments/
    scratch-agent-prototypes/
```

## How To Use These Prompts

1. Use the inspection prompt first whenever the workspace or project structure is uncertain.
2. Review the proposed changes before allowing file moves, renames, or new folders.
3. Use the apply prompt only after the plan looks right.
4. Use the new-project prompt when starting a fresh app or coding project.
5. Keep shared reusable agent instructions separate from project-specific status and task tracking.

## Prompt 1: Inspect And Recommend

```text
You are helping me organize this workspace for personal coding agents.

Before making changes:
1. Inspect the current folder structure.
2. Identify whether this is:
   - a project repo,
   - a shared agent infrastructure folder,
   - a references/examples folder,
   - or a scratch/experiment area.
3. Look for existing instruction files such as AGENTS.md, README.md, dev/README.md, or dev/active/*/{plan,context,tasks}.md.
4. Explain the current structure briefly.
5. Recommend the smallest changes needed to align it with this organization:

- Shared reusable agents live in /agents
- Individual coding projects live in /projects/<project-name>
- Project-specific agent state lives inside that project under /dev/active/<agent-name>/
- Completed agent work goes under /dev/archive/
- External examples and imported repos go under /references/
- Temporary prototypes go under /experiments/

Do not move or rename files yet. First propose the changes and wait for my approval.
```

## Prompt 2: Apply The Approved Plan

```text
Apply the approved organization plan.

Rules:
- Preserve existing git repositories.
- Do not move .git folders unless I explicitly approve it.
- Do not delete anything.
- If a project already has AGENTS.md or dev/active docs, update them instead of replacing them.
- If creating new agent handoff docs, create:
  - dev/active/<agent-name>/plan.md
  - dev/active/<agent-name>/context.md
  - dev/active/<agent-name>/tasks.md
- Keep shared reusable agent instructions separate from project-specific status.
- After changes, summarize what moved, what was created, and what still needs review.
```

## Prompt 3: Start A New Coding Project

```text
Set up this as a new personal coding-agent project.

Create or update:
- AGENTS.md with repo-specific instructions
- dev/README.md with the development workflow
- dev/active/<agent-name>/plan.md
- dev/active/<agent-name>/context.md
- dev/active/<agent-name>/tasks.md

Use the shared workspace structure:
- /agents for reusable agent patterns
- /projects for actual apps/repos
- /references for imported examples
- /experiments for throwaway prototypes

Keep the setup minimal. Do not add automation, hooks, or complex tooling unless the current project clearly needs it.
```

## Prompt 4: Check Whether A Project Is Organized Correctly

```text
Review this project's agent organization.

Check:
- Whether AGENTS.md exists and gives clear repo-specific instructions.
- Whether dev/README.md explains the project workflow.
- Whether dev/active/<agent-name>/plan.md, context.md, and tasks.md exist for current work.
- Whether shared reusable agent instructions are outside the project-specific dev/active state.
- Whether references, imported examples, and experiments are separated from production project code.

Do not edit anything yet. Report what is correct, what is missing, and the smallest safe fix.
```

## Prompt 5: Update Agent Handoff Docs

```text
Update the agent handoff docs for this project.

Use these files as the canonical handoff layer:
- dev/active/<agent-name>/plan.md
- dev/active/<agent-name>/context.md
- dev/active/<agent-name>/tasks.md

Keep the update concise:
- plan.md should say what milestone or direction is active.
- context.md should record important decisions, boundaries, and implementation facts.
- tasks.md should show completed, current, and next tasks.

Do not rewrite unrelated docs. Preserve existing useful context.
```

## Rule Of Thumb

Shared agents describe how to think and work. Project dev docs describe what is true right now.
