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
from calendar_agent.models.calendar_info import CalendarInfo

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
    calendar_ids: tuple[str, ...] = ("primary",)
    default_timezone: str = DEFAULT_TIMEZONE_NAME

    @classmethod
    def from_environment(cls) -> "GoogleCalendarSettings":
        configured_ids = os.getenv("GOOGLE_CALENDAR_IDS") or os.getenv(
            "GOOGLE_CALENDAR_ID", "primary"
        )
        calendar_ids = tuple(
            calendar_id.strip()
            for calendar_id in configured_ids.split(",")
            if calendar_id.strip()
        )
        if not calendar_ids:
            calendar_ids = ("primary",)

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
            calendar_ids=calendar_ids,
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
        calendar_ids: tuple[str, ...] = ("primary",),
        default_timezone: str = DEFAULT_TIMEZONE_NAME,
    ) -> None:
        self._api_service = api_service
        if not calendar_ids:
            raise ValueError("at least one calendar ID must be selected")
        self._calendar_ids = tuple(dict.fromkeys(calendar_ids))
        self._default_timezone = default_timezone
        self._calendar_names: dict[str, str] = {}

    def list_calendars(self) -> list[CalendarInfo]:
        calendars: list[CalendarInfo] = []
        page_token: str | None = None

        try:
            while True:
                response = (
                    self._api_service.calendarList()
                    .list(pageToken=page_token, showDeleted=False, showHidden=True)
                    .execute()
                )
                for item in response.get("items", []):
                    if item.get("deleted"):
                        continue
                    calendar = CalendarInfo(
                        id=item["id"],
                        name=item.get("summaryOverride") or item.get("summary") or item["id"],
                        timezone=item.get("timeZone"),
                        access_role=item.get("accessRole", "unknown"),
                        primary=item.get("primary", False),
                        selected=item.get("selected", False),
                        hidden=item.get("hidden", False),
                    )
                    calendars.append(calendar)
                    self._calendar_names[calendar.id] = calendar.name
                    if calendar.primary:
                        self._calendar_names["primary"] = calendar.name

                page_token = response.get("nextPageToken")
                if not page_token:
                    break
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            raise GoogleCalendarReadError("Google returned invalid calendar metadata") from exc
        except Exception as exc:
            raise GoogleCalendarReadError("could not list Google calendars") from exc

        return sorted(calendars, key=lambda calendar: (not calendar.primary, calendar.name.lower()))

    def list_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        ensure_timezone_aware(start, "start")
        ensure_timezone_aware(end, "end")
        if end <= start:
            raise ValueError("end must be after start")

        events: list[CalendarEvent] = []
        for calendar_id in self._calendar_ids:
            try:
                events.extend(self._list_events_for_calendar(calendar_id, start, end))
            except Exception as exc:
                calendar_name = self._calendar_names.get(calendar_id, calendar_id)
                raise GoogleCalendarReadError(
                    f"could not read Google calendar {calendar_name!r} ({calendar_id}): {exc}"
                ) from exc

        return self._deduplicate_events(events)

    def _list_events_for_calendar(
        self,
        calendar_id: str,
        start: datetime,
        end: datetime,
    ) -> list[CalendarEvent]:
        events: list[CalendarEvent] = []
        page_token: str | None = None
        calendar_name = self._calendar_names.get(calendar_id, calendar_id)

        while True:
            response = (
                self._api_service.events()
                .list(
                    calendarId=calendar_id,
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
                self._map_event(item, calendar_timezone, calendar_id, calendar_name)
                for item in response.get("items", [])
                if self._blocks_time(item)
            )
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return events

    @staticmethod
    def _deduplicate_events(events: list[CalendarEvent]) -> list[CalendarEvent]:
        unique_events: dict[tuple[str, datetime, datetime], CalendarEvent] = {}
        for event in sorted(events, key=lambda candidate: candidate.start):
            identity = event.external_uid or f"{event.source_calendar_id}:{event.id}"
            unique_events.setdefault((identity, event.start, event.end), event)
        return list(unique_events.values())

    @staticmethod
    def _blocks_time(item: Mapping[str, Any]) -> bool:
        return item.get("status") != "cancelled" and item.get("transparency") != "transparent"

    def _map_event(
        self,
        item: Mapping[str, Any],
        calendar_timezone: str,
        calendar_id: str,
        calendar_name: str,
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
                source_calendar_id=calendar_id,
                source_calendar_name=calendar_name,
                external_uid=item.get("iCalUID"),
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
