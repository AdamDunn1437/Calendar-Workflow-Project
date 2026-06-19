from calendar_agent.calendar.base import CalendarService
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.scheduling_proposal import SchedulingProposal
from calendar_agent.models.workflow_state import ApprovalStatus


class ApprovalRequiredError(PermissionError):
    pass


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

    return [calendar_service.create_event(event) for event in proposal.proposed_events]

