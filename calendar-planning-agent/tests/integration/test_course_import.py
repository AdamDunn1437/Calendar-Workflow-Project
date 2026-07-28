from zoneinfo import ZoneInfo

import pytest

from calendar_agent.calendar.fake_calendar import FakeCalendarService
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.scheduling.conflict_checker import conflicts_for_event
from calendar_agent.scheduling.course_expander import expand_schedule
from calendar_agent.course_import_demo import build_fall_courses

TZ = ZoneInfo("America/Toronto")


def test_course_import_creates_events_in_fake_calendar() -> None:
    calendar = FakeCalendarService()
    courses = build_fall_courses()

    all_events: list[CalendarEvent] = []
    for course in courses:
        all_events.extend(expand_schedule(course, TZ))

    for event in all_events:
        calendar.create_event(event)

    assert len(calendar.events) == len(all_events)


def test_course_import_detects_conflicts() -> None:
    all_events = _expand_all()
    if not all_events:
        pytest.skip("no events to test")

    existing = CalendarEvent(
        title="Existing meeting",
        start=all_events[0].start,
        end=all_events[0].end,
    )
    calendar = FakeCalendarService(initial_events=[existing])

    conflicts = {}
    for event in all_events:
        event_conflicts = conflicts_for_event(event, calendar.list_events(event.start, event.end))
        if event_conflicts:
            conflicts[id(event)] = event_conflicts

    assert len(conflicts) >= 1


def test_all_courses_have_at_least_one_meeting() -> None:
    courses = build_fall_courses()
    for course in courses:
        assert len(course.meetings) >= 1, f"{course.course_code} has no meetings"


def test_mse_3301_lab_without_time_is_not_included() -> None:
    for course in build_fall_courses():
        if course.course_code == "MSE 3301A":
            for meeting in course.meetings:
                assert meeting.section_type != "LAB", "MSE 3301A LAB should not be imported"


def _expand_all() -> list[CalendarEvent]:
    courses = build_fall_courses()
    all_events: list[CalendarEvent] = []
    for course in courses:
        all_events.extend(expand_schedule(course, TZ))
    return all_events
