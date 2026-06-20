from abc import ABC, abstractmethod
from datetime import datetime

from calendar_agent.models.calendar_event import CalendarEvent


class CalendarReader(ABC):
    @abstractmethod
    def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """Return stored events that overlap the requested range."""


class CalendarService(CalendarReader):
    """A calendar that supports both reads and explicitly approved writes."""

    @abstractmethod
    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create one event and return the stored event with an ID."""


class CalendarWriteUnsupportedError(PermissionError):
    """Raised when a workflow attempts to write through a read-only calendar."""
