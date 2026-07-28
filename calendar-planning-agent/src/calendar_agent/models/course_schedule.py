from datetime import date, time

from pydantic import BaseModel, Field, model_validator



_DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class CourseMeeting(BaseModel):
    course_code: str
    section_type: str
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    location: str
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_times(self) -> "CourseMeeting":
        if self.end_time <= self.start_time:
            raise ValueError(f"end_time {self.end_time} must be after start_time {self.start_time}")
        if self.end_date < self.start_date:
            raise ValueError(f"end_date {self.end_date} must not be before start_date {self.start_date}")
        return self

    @property
    def day_name(self) -> str:
        return _DAYS_OF_WEEK[self.day_of_week]


class CourseSchedule(BaseModel):
    course_code: str
    course_title: str
    instructor: str = ""
    meetings: list[CourseMeeting] = Field(default_factory=list)
