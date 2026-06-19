from enum import Enum

from pydantic import BaseModel, Field

from calendar_agent.models.calendar_event import CalendarEvent, TimeSlot


class ApprovalStatus(str, Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class WorkflowState(BaseModel):
    original_request: object | None = None
    existing_events: list[CalendarEvent] = Field(default_factory=list)
    available_time_slots: list[TimeSlot] = Field(default_factory=list)
    proposed_events: list[CalendarEvent] = Field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUESTED
    created_events: list[CalendarEvent] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

