from datetime import date, time
from zoneinfo import ZoneInfo

from calendar_agent.models.course_schedule import CourseMeeting
from calendar_agent.scheduling.course_expander import expand_meeting, expand_schedule
from calendar_agent.models.course_schedule import CourseSchedule

TZ = ZoneInfo("America/Toronto")


def meeting(
    day_of_week: int = 2,
    start_time: time = time(14, 30),
    end_time: time = time(15, 30),
    start_date: date = date(2026, 9, 9),
    end_date: date = date(2026, 12, 9),
) -> CourseMeeting:
    return CourseMeeting(
        course_code="AISE 3020A",
        section_type="LEC",
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        location="SEB-2200",
        start_date=start_date,
        end_date=end_date,
    )


def test_single_meeting_expands_to_multiple_events() -> None:
    events = expand_meeting(meeting(), TZ)
    assert len(events) == 14


def test_expanded_events_fall_on_correct_day_of_week() -> None:
    events = expand_meeting(meeting(day_of_week=2), TZ)
    for event in events:
        assert event.start.weekday() == 2


def test_expanded_events_have_correct_start_and_end_times() -> None:
    events = expand_meeting(
        meeting(start_time=time(10, 30), end_time=time(12, 30)),
        TZ,
    )
    for event in events:
        assert event.start.hour == 10
        assert event.start.minute == 30
        assert event.end.hour == 12
        assert event.end.minute == 30


def test_expanded_event_has_correct_title() -> None:
    events = expand_meeting(meeting(), TZ)
    for event in events:
        assert event.title == "AISE 3020A LEC"


def test_expanded_event_has_correct_description() -> None:
    events = expand_meeting(meeting(), TZ)
    for event in events:
        assert event.description == "AISE 3020A - SEB-2200"


def test_no_events_when_day_of_week_not_in_date_range() -> None:
    events = expand_meeting(
        meeting(day_of_week=0, start_date=date(2026, 9, 9), end_date=date(2026, 9, 11)),
        TZ,
    )
    assert len(events) == 0


def test_first_event_on_start_date_when_start_date_matches_day() -> None:
    events = expand_meeting(
        meeting(day_of_week=2, start_date=date(2026, 9, 9)),
        TZ,
    )
    assert events[0].start.date() == date(2026, 9, 9)


def test_first_event_after_start_date_when_start_date_does_not_match_day() -> None:
    events = expand_meeting(
        meeting(day_of_week=3, start_date=date(2026, 9, 9)),
        TZ,
    )
    assert events[0].start.date() == date(2026, 9, 10)


def test_expand_schedule_merges_multiple_meetings() -> None:
    schedule = CourseSchedule(
        course_code="MSE 4401A",
        course_title="ROBOTIC MANIPULATORS",
        meetings=[
            CourseMeeting(
                course_code="MSE 4401A",
                section_type="LEC",
                day_of_week=2,
                start_time=time(10, 30),
                end_time=time(12, 30),
                location="HSB-35",
                start_date=date(2026, 9, 9),
                end_date=date(2026, 12, 9),
            ),
            CourseMeeting(
                course_code="MSE 4401A",
                section_type="LEC",
                day_of_week=4,
                start_time=time(14, 30),
                end_time=time(15, 30),
                location="FNB-3210",
                start_date=date(2026, 9, 9),
                end_date=date(2026, 12, 9),
            ),
        ],
    )
    events = expand_schedule(schedule, TZ)
    assert len(events) == 27
    assert events[0].title == "MSE 4401A LEC"


def test_expanded_events_are_sorted_by_start_time() -> None:
    schedule = CourseSchedule(
        course_code="TEST",
        course_title="Test",
        meetings=[
            meeting(day_of_week=4, start_time=time(14, 0), end_time=time(15, 0)),
            meeting(day_of_week=2, start_time=time(10, 0), end_time=time(11, 0)),
        ],
    )
    events = expand_schedule(schedule, TZ)
    for i in range(len(events) - 1):
        assert events[i].start <= events[i + 1].start
