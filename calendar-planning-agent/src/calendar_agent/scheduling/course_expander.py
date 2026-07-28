from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.course_schedule import CourseMeeting, CourseSchedule


def expand_meeting(meeting: CourseMeeting, timezone: ZoneInfo) -> list[CalendarEvent]:
    events: list[CalendarEvent] = []
    cursor = meeting.start_date
    day_offset = (meeting.day_of_week - cursor.weekday()) % 7
    cursor += timedelta(days=day_offset)

    while cursor <= meeting.end_date:
        start = datetime.combine(cursor, meeting.start_time, tzinfo=timezone)
        end = datetime.combine(cursor, meeting.end_time, tzinfo=timezone)
        events.append(
            CalendarEvent(
                title=f"{meeting.course_code} {meeting.section_type}",
                start=start,
                end=end,
                description=f"{meeting.course_code} - {meeting.location}",
                timezone=str(timezone),
            )
        )
        cursor += timedelta(days=7)

    return events


def expand_schedule(schedule: CourseSchedule, timezone: ZoneInfo) -> list[CalendarEvent]:
    events: list[CalendarEvent] = []
    for meeting in schedule.meetings:
        events.extend(expand_meeting(meeting, timezone))
    return sorted(events, key=lambda e: e.start)
