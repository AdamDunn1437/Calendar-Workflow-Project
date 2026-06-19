from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from calendar_agent.config import DEFAULT_TIMEZONE_NAME


def ensure_timezone_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


class TimeSlot(BaseModel):
    model_config = ConfigDict(frozen=True)

    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_times(self) -> "TimeSlot":
        ensure_timezone_aware(self.start, "start")
        ensure_timezone_aware(self.end, "end")
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


class CalendarEvent(BaseModel):
    id: str | None = None
    title: str
    start: datetime
    end: datetime
    description: str = ""
    timezone: str = Field(default=DEFAULT_TIMEZONE_NAME)

    @model_validator(mode="after")
    def validate_times(self) -> "CalendarEvent":
        ensure_timezone_aware(self.start, "start")
        ensure_timezone_aware(self.end, "end")
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self

    def as_time_slot(self) -> TimeSlot:
        return TimeSlot(start=self.start, end=self.end)

