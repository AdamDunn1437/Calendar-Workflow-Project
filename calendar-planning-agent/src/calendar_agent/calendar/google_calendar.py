from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time
import os
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pydantic import ValidationError

from calendar_agent.calendar.base import CalendarReader
from calendar_agent.config import DEFAULT_TIMEZONE_NAME
from calendar_agent.models.calendar_event import CalendarEvent, ensure_timezone_aware

GOOGLE_CALENDAR_READONLY_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"


class GoogleCalendarError(RuntimeError):
    """Base error for Google Calendar integration failures."""


class GoogleCalendarAuthenticationError(GoogleCalendarError):
    """Raised when read-only Google credentials cannot be loaded or created."""


class GoogleCalendarReadError(GoogleCalendarError):
    """Raised when Google events cannot be fetched or validated."""


@dataclass(frozen=True)
class GoogleCalendarSettings:
    credentials_path: Path = Path("credentials.json")
    token_path: Path = Path(".secrets/google-calendar-token.json")
    calendar_id: str = "primary"
    default_timezone: str = DEFAULT_TIMEZONE_NAME

    @classmethod
    def from_environment(cls) -> "GoogleCalendarSettings":
        return cls(
            credentials_path=Path(
                os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "credentials.json")
            ),
            token_path=Path(
                os.getenv(
                    "GOOGLE_CALENDAR_TOKEN_FILE",
                    ".secrets/google-calendar-token.json",
                )
            ),
            calendar_id=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            default_timezone=os.getenv("DEFAULT_TIMEZONE", DEFAULT_TIMEZONE_NAME),
        )


def build_google_api_service(settings: GoogleCalendarSettings) -> Any:
    """Authorize a local desktop user and return a Calendar API client."""
    credentials: Credentials | None = None

    try:
        if settings.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                str(settings.token_path),
                [GOOGLE_CALENDAR_READONLY_SCOPE],
            )

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        elif not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(settings.credentials_path),
                [GOOGLE_CALENDAR_READONLY_SCOPE],
            )
            credentials = flow.run_local_server(port=0)

        settings.token_path.parent.mkdir(parents=True, exist_ok=True)
        settings.token_path.write_text(credentials.to_json(), encoding="utf-8")
        return build("calendar", "v3", credentials=credentials, cache_discovery=False)
    except Exception as exc:
        raise GoogleCalendarAuthenticationError(
            "could not authorize read-only Google Calendar access"
        ) from exc


class GoogleCalendarReader(CalendarReader):
    def __init__(
        self,
        api_service: Any,
        *,
        calendar_id: str = "primary",
        default_timezone: str = DEFAULT_TIMEZONE_NAME,
    ) -> None:
        self._api_service = api_service
        self._calendar_id = calendar_id
        self._default_timezone = default_timezone

    def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        ensure_timezone_aware(start, "start")
        ensure_timezone_aware(end, "end")
        if end <= start:
            raise ValueError("end must be after start")

        events: list[CalendarEvent] = []
        page_token: str | None = None

        try:
            while True:
                response = (
                    self._api_service.events()
                    .list(
                        calendarId=self._calendar_id,
                        timeMin=start.isoformat(),
                        timeMax=end.isoformat(),
                        singleEvents=True,
                        orderBy="startTime",
                        showDeleted=False,
                        pageToken=page_token,
                    )
                    .execute()
                )
                calendar_timezone = response.get("timeZone", self._default_timezone)
                events.extend(
                    self._map_event(item, calendar_timezone)
                    for item in response.get("items", [])
                    if self._blocks_time(item)
                )
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        except GoogleCalendarReadError:
            raise
        except Exception as exc:
            raise GoogleCalendarReadError("could not read events from Google Calendar") from exc

        return sorted(events, key=lambda event: event.start)

    @staticmethod
    def _blocks_time(item: Mapping[str, Any]) -> bool:
        return item.get("status") != "cancelled" and item.get("transparency") != "transparent"

    def _map_event(
        self,
        item: Mapping[str, Any],
        calendar_timezone: str,
    ) -> CalendarEvent:
        event_id = str(item.get("id", "unknown"))
        try:
            start, start_timezone = self._parse_event_time(
                item["start"], calendar_timezone
            )
            end, _ = self._parse_event_time(item["end"], calendar_timezone)
            return CalendarEvent(
                id=item.get("id"),
                title=item.get("summary") or "(Untitled event)",
                start=start,
                end=end,
                description=item.get("description", ""),
                timezone=start_timezone,
            )
        except (KeyError, TypeError, ValueError, ValidationError, ZoneInfoNotFoundError) as exc:
            raise GoogleCalendarReadError(
                f"Google Calendar event {event_id!r} is invalid"
            ) from exc

    def _parse_event_time(
        self,
        value: Mapping[str, Any],
        calendar_timezone: str,
    ) -> tuple[datetime, str]:
        timezone_name = value.get("timeZone") or calendar_timezone or self._default_timezone

        if "dateTime" in value:
            parsed = datetime.fromisoformat(value["dateTime"].replace("Z", "+00:00"))
            ensure_timezone_aware(parsed, "Google event dateTime")
            return parsed, timezone_name

        parsed_date = date.fromisoformat(value["date"])
        return datetime.combine(parsed_date, time.min, ZoneInfo(timezone_name)), timezone_name
