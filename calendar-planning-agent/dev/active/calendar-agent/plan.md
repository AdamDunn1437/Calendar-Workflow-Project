# Project Plan

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

## 3. Google Calendar Write Integration

- Add event creation behind the same interface.
- Preserve the approval boundary.
- Add tests with mocked Google Calendar responses.

## 4. Natural-Language Parsing

- Convert plain-language requests into `SchedulingRequest` data.
- Validate parsed data before scheduling.
- Ask for missing required scheduling information instead of inventing it.

## 5. Optional Workflow Framework

- Consider a workflow framework only after the simple orchestrator becomes hard to maintain.
- Keep deterministic scheduling logic outside any framework.

## Cross-Cutting AI Workflow Principles

- Preserve context in the dev docs before and after major changes.
- Keep docs modular: short overview files first, focused reference files only when a topic grows.
- Add agentic infrastructure gradually. Start with a single project-specific guide or skill before considering hooks, slash commands, or specialized agents.
- Treat external infrastructure showcases as pattern libraries, not dependencies.
