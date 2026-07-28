from calendar_agent.calendar.base import (
    CalendarReader,
    CalendarService,
    CalendarWriteUnsupportedError,
)
from calendar_agent.models.scheduling_proposal import CreationStatus, SchedulingProposal
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.models.workflow_state import ApprovalStatus, WorkflowState
from calendar_agent.scheduling.free_time_finder import find_free_time
from calendar_agent.scheduling.proposal_builder import build_proposal
from calendar_agent.workflow.approval import (
    CalendarBatchCreationError,
    approve_proposal,
    create_approved_events,
    reject_proposal,
)


class CalendarWorkflow:
    def __init__(self, calendar_service: CalendarReader) -> None:
        self.calendar_service = calendar_service
        self._proposals: dict[str, SchedulingProposal] = {}

    def plan(self, request: SchedulingRequest) -> WorkflowState:
        existing_events = self.calendar_service.list_events(request.window_start, request.window_end)
        available_slots = find_free_time(
            existing_events=existing_events,
            window_start=request.window_start,
            window_end=request.window_end,
            daily_start_time=request.daily_start_time,
            daily_end_time=request.daily_end_time,
            duration_minutes=request.duration_minutes,
            minimum_gap_minutes=request.minimum_gap_minutes,
        )
        proposal = build_proposal(request, available_slots)
        self._proposals[proposal.id] = proposal

        errors = [proposal.failure_reason] if proposal.failure_reason else []
        return WorkflowState(
            original_request=request,
            existing_events=existing_events,
            available_time_slots=available_slots,
            proposed_events=proposal.proposed_events,
            approval_status=proposal.approval_status,
            errors=errors,
        )

    def latest_proposal(self) -> SchedulingProposal:
        if not self._proposals:
            raise LookupError("no proposals have been planned")
        return next(reversed(self._proposals.values()))

    def approve_and_create(self, proposal_id: str, approved: bool) -> WorkflowState:
        proposal = self._proposals[proposal_id]

        if proposal.creation_status is CreationStatus.CREATED:
            return WorkflowState(
                original_request=proposal.request,
                proposed_events=proposal.proposed_events,
                approval_status=proposal.approval_status,
                created_events=proposal.created_events,
            )

        if proposal.creation_status in {
            CreationStatus.FAILED,
            CreationStatus.PARTIALLY_CREATED,
        }:
            return WorkflowState(
                original_request=proposal.request,
                proposed_events=proposal.proposed_events,
                approval_status=proposal.approval_status,
                created_events=proposal.created_events,
                errors=[proposal.failure_reason or "proposal failed"],
            )

        if not approved:
            proposal = reject_proposal(proposal, "user rejected proposal")
            self._proposals[proposal.id] = proposal
            return WorkflowState(
                original_request=proposal.request,
                proposed_events=proposal.proposed_events,
                approval_status=ApprovalStatus.REJECTED,
            )

        if not isinstance(self.calendar_service, CalendarService):
            raise CalendarWriteUnsupportedError(
                "this calendar connection is read-only and cannot create events"
            )

        proposal = approve_proposal(proposal)
        try:
            created_events = create_approved_events(proposal, self.calendar_service)
        except CalendarBatchCreationError as exc:
            creation_status = (
                CreationStatus.PARTIALLY_CREATED
                if exc.created_events
                else CreationStatus.FAILED
            )
            proposal = proposal.model_copy(
                update={
                    "approval_status": ApprovalStatus.APPROVED,
                    "creation_status": creation_status,
                    "created_events": exc.created_events,
                    "failure_reason": str(exc),
                }
            )
            self._proposals[proposal.id] = proposal
            return WorkflowState(
                original_request=proposal.request,
                proposed_events=proposal.proposed_events,
                approval_status=ApprovalStatus.APPROVED,
                created_events=exc.created_events,
                errors=[str(exc)],
            )

        proposal = proposal.model_copy(
            update={
                "creation_status": CreationStatus.CREATED,
                "created_events": created_events,
            }
        )
        self._proposals[proposal.id] = proposal
        return WorkflowState(
            original_request=proposal.request,
            proposed_events=proposal.proposed_events,
            approval_status=ApprovalStatus.APPROVED,
            created_events=created_events,
        )
