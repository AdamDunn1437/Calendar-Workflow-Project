from datetime import datetime

from calendar_agent.models.calendar_event import CalendarEvent


def intervals_overlap(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime,
) -> bool:
    return start_a < end_b and start_b < end_a


def events_overlap(first: CalendarEvent, second: CalendarEvent) -> bool:
    return intervals_overlap(first.start, first.end, second.start, second.end)


def conflicts_for_event(
    proposed_event: CalendarEvent,
    existing_events: list[CalendarEvent],
) -> list[CalendarEvent]:
    return [event for event in existing_events if events_overlap(proposed_event, event)]

