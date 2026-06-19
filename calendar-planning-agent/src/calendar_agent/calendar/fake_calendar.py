from datetime import datetime

from calendar_agent.calendar.base import CalendarService
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.scheduling.conflict_checker import conflicts_for_event, intervals_overlap


class CalendarConflictError(ValueError):
    pass


class FakeCalendarService(CalendarService):
    def __init__(self, initial_events: list[CalendarEvent] | None = None) -> None:
        self._events: list[CalendarEvent] = []
        self._next_id = 1
        for event in initial_events or []:
            stored_event = event if event.id else event.model_copy(update={"id": self._new_id()})
            self._events.append(stored_event)

    @property
    def events(self) -> list[CalendarEvent]:
        return list(self._events)

    def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        return [
            event
            for event in sorted(self._events, key=lambda stored: stored.start)
            if intervals_overlap(event.start, event.end, start, end)
        ]

    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        conflicts = conflicts_for_event(event, self._events)
        if conflicts:
            conflict_titles = ", ".join(conflict.title for conflict in conflicts)
            raise CalendarConflictError(f"event conflicts with existing events: {conflict_titles}")

        stored_event = event.model_copy(update={"id": self._new_id()})
        self._events.append(stored_event)
        self._events.sort(key=lambda stored: stored.start)
        return stored_event

    def _new_id(self) -> str:
        event_id = f"fake-{self._next_id}"
        self._next_id += 1
        return event_id

