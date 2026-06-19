from datetime import datetime, time
from zoneinfo import ZoneInfo

from calendar_agent.models.calendar_event import TimeSlot
from calendar_agent.models.scheduling_proposal import CreationStatus
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.models.workflow_state import ApprovalStatus
from calendar_agent.scheduling.proposal_builder import build_proposal

TZ = ZoneInfo("America/Toronto")


def request(number_of_sessions: int = 2) -> SchedulingRequest:
    return SchedulingRequest(
        title="Date activity",
        duration_minutes=60,
        number_of_sessions=number_of_sessions,
        window_start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ),
        window_end=datetime(2026, 1, 10, 17, 0, tzinfo=TZ),
        daily_start_time=time(9, 0),
        daily_end_time=time(17, 0),
        description="Fun plan",
        minimum_gap_minutes=30,
    )


def test_proposal_contains_requested_number_of_sessions_when_possible() -> None:
    proposal = build_proposal(
        request(),
        [TimeSlot(start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ), end=datetime(2026, 1, 10, 13, 0, tzinfo=TZ))],
    )

    assert proposal.approval_status is ApprovalStatus.PENDING
    assert len(proposal.proposed_events) == 2
    assert proposal.proposed_events[0].start.hour == 9
    assert proposal.proposed_events[1].start.hour == 10
    assert proposal.proposed_events[1].start.minute == 30


def test_proposal_building_fails_when_insufficient_time_exists() -> None:
    proposal = build_proposal(
        request(number_of_sessions=3),
        [TimeSlot(start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ), end=datetime(2026, 1, 10, 11, 0, tzinfo=TZ))],
    )

    assert proposal.creation_status is CreationStatus.FAILED
    assert proposal.approval_status is ApprovalStatus.NOT_REQUESTED
    assert proposal.proposed_events == []
    assert proposal.failure_reason is not None

