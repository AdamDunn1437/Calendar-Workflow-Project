from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.models.workflow_state import ApprovalStatus


class CreationStatus(str, Enum):
    NOT_CREATED = "NOT_CREATED"
    CREATED = "CREATED"
    FAILED = "FAILED"


class SchedulingProposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    request: SchedulingRequest
    proposed_events: list[CalendarEvent] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    creation_status: CreationStatus = CreationStatus.NOT_CREATED
    failure_reason: str | None = None

