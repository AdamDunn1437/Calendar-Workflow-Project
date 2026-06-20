from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from calendar_agent.calendar.base import CalendarReader, CalendarWriteUnsupportedError
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.workflow.orchestrator import CalendarWorkflow

TZ = ZoneInfo("America/Toronto")


class EmptyReader(CalendarReader):
    def list_events(self, start: datetime, end: datetime) -> list:
        return []


def test_read_only_calendar_can_plan_but_cannot_create() -> None:
    workflow = CalendarWorkflow(EmptyReader())
    request = SchedulingRequest(
        title="Focus time",
        duration_minutes=60,
        number_of_sessions=1,
        window_start=datetime(2026, 7, 4, 9, 0, tzinfo=TZ),
        window_end=datetime(2026, 7, 4, 17, 0, tzinfo=TZ),
        daily_start_time=time(9),
        daily_end_time=time(17),
    )

    workflow.plan(request)
    proposal = workflow.latest_proposal()

    with pytest.raises(CalendarWriteUnsupportedError, match="read-only"):
        workflow.approve_and_create(proposal.id, approved=True)
