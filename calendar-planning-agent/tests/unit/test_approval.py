from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from calendar_agent.calendar.fake_calendar import FakeCalendarService
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.models.workflow_state import ApprovalStatus
from calendar_agent.scheduling.proposal_builder import build_proposal
from calendar_agent.workflow.approval import (
    ApprovalRequiredError,
    approve_proposal,
    create_approved_events,
    reject_proposal,
)

TZ = ZoneInfo("America/Toronto")


def proposal_request() -> SchedulingRequest:
    return SchedulingRequest(
        title="Date activity",
        duration_minutes=60,
        number_of_sessions=1,
        window_start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ),
        window_end=datetime(2026, 1, 10, 17, 0, tzinfo=TZ),
        daily_start_time=time(9, 0),
        daily_end_time=time(17, 0),
        minimum_gap_minutes=0,
    )


def proposed_event() -> CalendarEvent:
    return CalendarEvent(
        title="Date activity",
        start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ),
        end=datetime(2026, 1, 10, 10, 0, tzinfo=TZ),
    )


def test_pending_proposals_cannot_create_events() -> None:
    proposal = build_proposal(proposal_request(), [proposed_event().as_time_slot()])
    calendar = FakeCalendarService()

    with pytest.raises(ApprovalRequiredError):
        create_approved_events(proposal, calendar)

    assert calendar.events == []


def test_rejected_proposals_cannot_create_events() -> None:
    proposal = reject_proposal(build_proposal(proposal_request(), [proposed_event().as_time_slot()]))
    calendar = FakeCalendarService()

    with pytest.raises(ApprovalRequiredError):
        create_approved_events(proposal, calendar)

    assert proposal.approval_status is ApprovalStatus.REJECTED
    assert calendar.events == []


def test_approved_proposals_create_events() -> None:
    proposal = approve_proposal(build_proposal(proposal_request(), [proposed_event().as_time_slot()]))
    calendar = FakeCalendarService()

    created_events = create_approved_events(proposal, calendar)

    assert len(created_events) == 1
    assert created_events[0].id == "fake-1"
    assert len(calendar.events) == 1

