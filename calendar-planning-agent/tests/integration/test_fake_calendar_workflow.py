from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from calendar_agent.calendar.fake_calendar import CalendarConflictError, FakeCalendarService
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.workflow_state import ApprovalStatus
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.workflow.orchestrator import CalendarWorkflow
from calendar_agent.models.scheduling_proposal import CreationStatus

TZ = ZoneInfo("America/Toronto")


def event(title: str, start_hour: int, end_hour: int) -> CalendarEvent:
    return CalendarEvent(
        title=title,
        start=datetime(2026, 1, 10, start_hour, 0, tzinfo=TZ),
        end=datetime(2026, 1, 10, end_hour, 0, tzinfo=TZ),
    )


def request() -> SchedulingRequest:
    return SchedulingRequest(
        title="Date activity",
        duration_minutes=60,
        number_of_sessions=2,
        window_start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ),
        window_end=datetime(2026, 1, 10, 17, 0, tzinfo=TZ),
        daily_start_time=time(9, 0),
        daily_end_time=time(17, 0),
        description="Plan a date",
        minimum_gap_minutes=30,
    )


def test_fake_calendar_rejects_conflicting_writes() -> None:
    calendar = FakeCalendarService(initial_events=[event("Existing", 10, 11)])

    with pytest.raises(CalendarConflictError):
        calendar.create_event(event("Conflict", 10, 12))

    assert len(calendar.events) == 1


def test_complete_fake_calendar_workflow_rejects_without_creation() -> None:
    calendar = FakeCalendarService(initial_events=[event("Existing", 10, 11)])
    workflow = CalendarWorkflow(calendar)
    workflow.plan(request())
    proposal = workflow.latest_proposal()

    result = workflow.approve_and_create(proposal.id, approved=False)

    assert result.approval_status is ApprovalStatus.REJECTED
    assert result.created_events == []
    assert len(calendar.events) == 1


def test_complete_fake_calendar_workflow_creates_after_approval() -> None:
    calendar = FakeCalendarService(initial_events=[event("Existing", 10, 11)])
    workflow = CalendarWorkflow(calendar)
    plan_result = workflow.plan(request())
    proposal = workflow.latest_proposal()

    result = workflow.approve_and_create(proposal.id, approved=True)

    assert plan_result.approval_status is ApprovalStatus.PENDING
    assert result.approval_status is ApprovalStatus.APPROVED
    assert len(result.created_events) == 2
    assert len(calendar.events) == 3

    repeated_result = workflow.approve_and_create(proposal.id, approved=True)
    assert repeated_result.created_events == result.created_events
    assert len(calendar.events) == 3


class FailOnSecondCreate(FakeCalendarService):
    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        if len(self.events) == 1:
            raise RuntimeError("simulated API failure")
        return super().create_event(event)


def test_partial_creation_is_reported_without_retry_or_rollback() -> None:
    calendar = FailOnSecondCreate()
    workflow = CalendarWorkflow(calendar)
    workflow.plan(request())
    proposal = workflow.latest_proposal()

    result = workflow.approve_and_create(proposal.id, approved=True)

    assert len(result.created_events) == 1
    assert "creation stopped" in result.errors[0]
    assert workflow.latest_proposal().creation_status is CreationStatus.PARTIALLY_CREATED

    repeated_result = workflow.approve_and_create(proposal.id, approved=True)
    assert repeated_result.created_events == result.created_events
    assert len(calendar.events) == 1
