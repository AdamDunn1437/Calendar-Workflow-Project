from calendar_agent.calendar.base import CalendarService
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.scheduling_proposal import SchedulingProposal
from calendar_agent.models.workflow_state import ApprovalStatus


class ApprovalRequiredError(PermissionError):
    pass


class CalendarBatchCreationError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        created_events: list[CalendarEvent],
        failed_event: CalendarEvent,
    ) -> None:
        super().__init__(message)
        self.created_events = created_events
        self.failed_event = failed_event


def approve_proposal(proposal: SchedulingProposal) -> SchedulingProposal:
    return proposal.model_copy(update={"approval_status": ApprovalStatus.APPROVED})


def reject_proposal(proposal: SchedulingProposal, reason: str | None = None) -> SchedulingProposal:
    return proposal.model_copy(
        update={
            "approval_status": ApprovalStatus.REJECTED,
            "failure_reason": reason or proposal.failure_reason,
        }
    )


def create_approved_events(
    proposal: SchedulingProposal,
    calendar_service: CalendarService,
) -> list[CalendarEvent]:
    if proposal.approval_status is not ApprovalStatus.APPROVED:
        raise ApprovalRequiredError("proposal must be approved before creating events")

    created_events: list[CalendarEvent] = []
    for event in proposal.proposed_events:
        try:
            created_events.append(calendar_service.create_event(event))
        except Exception as exc:
            raise CalendarBatchCreationError(
                f"creation stopped at {event.title!r}: {exc}",
                created_events=created_events,
                failed_event=event,
            ) from exc
    return created_events
