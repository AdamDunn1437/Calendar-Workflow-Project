from datetime import datetime, time, timedelta

from calendar_agent.models.calendar_event import CalendarEvent, TimeSlot
from calendar_agent.scheduling.conflict_checker import intervals_overlap


def find_free_time(
    existing_events: list[CalendarEvent],
    window_start: datetime,
    window_end: datetime,
    daily_start_time: time,
    daily_end_time: time,
    duration_minutes: int,
    minimum_gap_minutes: int = 0,
) -> list[TimeSlot]:
    """Find free intervals.

    Minimum gap is applied by expanding existing events on both sides. The proposal
    builder also applies the same gap between sessions selected from a larger slot.
    """
    duration = timedelta(minutes=duration_minutes)
    minimum_gap = timedelta(minutes=minimum_gap_minutes)
    slots: list[TimeSlot] = []
    current_day = window_start.date()

    while current_day <= window_end.date():
        day_start = datetime.combine(current_day, daily_start_time, tzinfo=window_start.tzinfo)
        day_end = datetime.combine(current_day, daily_end_time, tzinfo=window_start.tzinfo)
        allowed_start = max(day_start, window_start)
        allowed_end = min(day_end, window_end)

        if allowed_end > allowed_start:
            busy_intervals = _busy_intervals_for_day(
                existing_events=existing_events,
                allowed_start=allowed_start,
                allowed_end=allowed_end,
                minimum_gap=minimum_gap,
            )
            slots.extend(_free_slots_from_busy_intervals(allowed_start, allowed_end, busy_intervals, duration))

        current_day += timedelta(days=1)

    return sorted(slots, key=lambda slot: slot.start)


def _busy_intervals_for_day(
    existing_events: list[CalendarEvent],
    allowed_start: datetime,
    allowed_end: datetime,
    minimum_gap: timedelta,
) -> list[TimeSlot]:
    busy_intervals: list[TimeSlot] = []
    for event in existing_events:
        expanded_start = event.start - minimum_gap
        expanded_end = event.end + minimum_gap
        if intervals_overlap(expanded_start, expanded_end, allowed_start, allowed_end):
            busy_intervals.append(
                TimeSlot(
                    start=max(expanded_start, allowed_start),
                    end=min(expanded_end, allowed_end),
                )
            )
    return _merge_slots(sorted(busy_intervals, key=lambda slot: slot.start))


def _merge_slots(slots: list[TimeSlot]) -> list[TimeSlot]:
    if not slots:
        return []

    merged = [slots[0]]
    for slot in slots[1:]:
        previous = merged[-1]
        if slot.start <= previous.end:
            merged[-1] = TimeSlot(start=previous.start, end=max(previous.end, slot.end))
        else:
            merged.append(slot)
    return merged


def _free_slots_from_busy_intervals(
    allowed_start: datetime,
    allowed_end: datetime,
    busy_intervals: list[TimeSlot],
    duration: timedelta,
) -> list[TimeSlot]:
    free_slots: list[TimeSlot] = []
    cursor = allowed_start

    for busy in busy_intervals:
        if cursor + duration <= busy.start:
            free_slots.append(TimeSlot(start=cursor, end=busy.start))
        cursor = max(cursor, busy.end)

    if cursor + duration <= allowed_end:
        free_slots.append(TimeSlot(start=cursor, end=allowed_end))

    return free_slots

