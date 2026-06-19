from calendar_agent.calendar.base import CalendarService
from calendar_agent.models.scheduling_proposal import CreationStatus, SchedulingProposal
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.models.workflow_state import ApprovalStatus, WorkflowState
from calendar_agent.scheduling.free_time_finder import find_free_time
from calendar_agent.scheduling.proposal_builder import build_proposal
from calendar_agent.workflow.approval import approve_proposal, create_approved_events, reject_proposal


class CalendarWorkflow:
    def __init__(self, calendar_service: CalendarService) -> None:
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

        if proposal.creation_status is CreationStatus.FAILED:
            return WorkflowState(
                original_request=proposal.request,
                proposed_events=proposal.proposed_events,
                approval_status=proposal.approval_status,
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

        proposal = approve_proposal(proposal)
        created_events = create_approved_events(proposal, self.calendar_service)
        proposal = proposal.model_copy(update={"creation_status": CreationStatus.CREATED})
        self._proposals[proposal.id] = proposal
        return WorkflowState(
            original_request=proposal.request,
            proposed_events=proposal.proposed_events,
            approval_status=ApprovalStatus.APPROVED,
            created_events=created_events,
        )

