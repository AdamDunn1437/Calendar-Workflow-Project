from datetime import datetime, time

from pydantic import BaseModel, Field, model_validator

from calendar_agent.models.calendar_event import ensure_timezone_aware


class SchedulingRequest(BaseModel):
    title: str
    duration_minutes: int = Field(gt=0)
    number_of_sessions: int = Field(gt=0)
    window_start: datetime
    window_end: datetime
    daily_start_time: time
    daily_end_time: time
    description: str = ""
    minimum_gap_minutes: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_request(self) -> "SchedulingRequest":
        ensure_timezone_aware(self.window_start, "window_start")
        ensure_timezone_aware(self.window_end, "window_end")
        if self.window_end <= self.window_start:
            raise ValueError("window_end must be after window_start")
        if self.daily_end_time <= self.daily_start_time:
            raise ValueError("daily_end_time must be after daily_start_time")
        return self

