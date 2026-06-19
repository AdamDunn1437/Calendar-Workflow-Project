from datetime import timedelta

from calendar_agent.models.calendar_event import CalendarEvent, TimeSlot
from calendar_agent.models.scheduling_proposal import CreationStatus, SchedulingProposal
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.models.workflow_state import ApprovalStatus


def build_proposal(request: SchedulingRequest, available_slots: list[TimeSlot]) -> SchedulingProposal:
    duration = timedelta(minutes=request.duration_minutes)
    minimum_gap = timedelta(minutes=request.minimum_gap_minutes)
    proposed_events: list[CalendarEvent] = []

    for slot in sorted(available_slots, key=lambda candidate: candidate.start):
        cursor = slot.start
        while cursor + duration <= slot.end and len(proposed_events) < request.number_of_sessions:
            proposed_events.append(
                CalendarEvent(
                    title=request.title,
                    start=cursor,
                    end=cursor + duration,
                    description=request.description,
                )
            )
            cursor = cursor + duration + minimum_gap

        if len(proposed_events) == request.number_of_sessions:
            break

    if len(proposed_events) < request.number_of_sessions:
        return SchedulingProposal(
            request=request,
            proposed_events=[],
            approval_status=ApprovalStatus.NOT_REQUESTED,
            creation_status=CreationStatus.FAILED,
            failure_reason=(
                f"needed {request.number_of_sessions} sessions but found "
                f"{len(proposed_events)} valid sessions"
            ),
        )

    return SchedulingProposal(request=request, proposed_events=proposed_events)

