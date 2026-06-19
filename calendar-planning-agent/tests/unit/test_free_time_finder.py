from datetime import datetime, time
from zoneinfo import ZoneInfo

from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.scheduling.free_time_finder import find_free_time

TZ = ZoneInfo("America/Toronto")


def event(day: int, start_hour: int, end_hour: int) -> CalendarEvent:
    return CalendarEvent(
        title="Busy",
        start=datetime(2026, 1, day, start_hour, 0, tzinfo=TZ),
        end=datetime(2026, 1, day, end_hour, 0, tzinfo=TZ),
    )


def test_free_slots_are_found_around_existing_events() -> None:
    slots = find_free_time(
        existing_events=[event(10, 11, 12)],
        window_start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ),
        window_end=datetime(2026, 1, 10, 17, 0, tzinfo=TZ),
        daily_start_time=time(9, 0),
        daily_end_time=time(17, 0),
        duration_minutes=60,
    )

    assert [(slot.start.hour, slot.end.hour) for slot in slots] == [(9, 11), (12, 17)]


def test_free_slots_work_across_multiple_days() -> None:
    slots = find_free_time(
        existing_events=[event(10, 10, 11), event(11, 14, 15)],
        window_start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ),
        window_end=datetime(2026, 1, 11, 17, 0, tzinfo=TZ),
        daily_start_time=time(9, 0),
        daily_end_time=time(17, 0),
        duration_minutes=120,
    )

    assert len(slots) == 3
    assert [(slot.start.day, slot.start.hour, slot.end.hour) for slot in slots] == [
        (10, 11, 17),
        (11, 9, 14),
        (11, 15, 17),
    ]


def test_daily_allowed_hours_are_respected() -> None:
    slots = find_free_time(
        existing_events=[],
        window_start=datetime(2026, 1, 10, 7, 0, tzinfo=TZ),
        window_end=datetime(2026, 1, 10, 20, 0, tzinfo=TZ),
        daily_start_time=time(10, 0),
        daily_end_time=time(16, 0),
        duration_minutes=60,
    )

    assert len(slots) == 1
    assert slots[0].start.hour == 10
    assert slots[0].end.hour == 16


def test_minimum_gaps_are_respected_around_existing_events() -> None:
    slots = find_free_time(
        existing_events=[event(10, 12, 13)],
        window_start=datetime(2026, 1, 10, 9, 0, tzinfo=TZ),
        window_end=datetime(2026, 1, 10, 17, 0, tzinfo=TZ),
        daily_start_time=time(9, 0),
        daily_end_time=time(17, 0),
        duration_minutes=60,
        minimum_gap_minutes=30,
    )

    assert slots[0].end.hour == 11
    assert slots[0].end.minute == 30
    assert slots[1].start.hour == 13
    assert slots[1].start.minute == 30
