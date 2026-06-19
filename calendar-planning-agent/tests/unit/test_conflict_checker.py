from datetime import datetime
from zoneinfo import ZoneInfo

from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.scheduling.conflict_checker import conflicts_for_event, events_overlap

TZ = ZoneInfo("America/Toronto")


def event(start_hour: int, end_hour: int, title: str = "Event") -> CalendarEvent:
    return CalendarEvent(
        title=title,
        start=datetime(2026, 1, 10, start_hour, 0, tzinfo=TZ),
        end=datetime(2026, 1, 10, end_hour, 0, tzinfo=TZ),
    )


def test_overlapping_events_are_detected() -> None:
    assert events_overlap(event(10, 12), event(11, 13))


def test_adjacent_events_are_not_conflicting() -> None:
    assert not events_overlap(event(10, 12), event(12, 13))


def test_event_containing_another_event_is_conflicting() -> None:
    assert events_overlap(event(9, 17), event(10, 11))


def test_conflicts_for_event_returns_all_conflicts() -> None:
    proposed = event(10, 12, "Proposed")
    existing = [event(8, 9, "Early"), event(11, 13, "Overlap"), event(12, 14, "Adjacent")]

    conflicts = conflicts_for_event(proposed, existing)

    assert [conflict.title for conflict in conflicts] == ["Overlap"]

