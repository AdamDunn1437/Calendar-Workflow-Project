from abc import ABC, abstractmethod
from datetime import datetime

from calendar_agent.models.calendar_event import CalendarEvent


class CalendarService(ABC):
    @abstractmethod
    def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """Return stored events that overlap the requested range."""

    @abstractmethod
    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create one event and return the stored event with an ID."""

