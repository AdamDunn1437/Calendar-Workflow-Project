from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

import pytest

from calendar_agent.calendar.base import CalendarReader, CalendarService
from calendar_agent.calendar.google_calendar import (
    GOOGLE_CALENDAR_READONLY_SCOPE,
    GoogleCalendarAuthenticationError,
    GoogleCalendarReadError,
    GoogleCalendarReader,
    GoogleCalendarSettings,
    build_google_api_service,
)

TZ = ZoneInfo("America/Toronto")
START = datetime(2026, 7, 4, 0, 0, tzinfo=TZ)
END = datetime(2026, 7, 6, 0, 0, tzinfo=TZ)


def api_with_responses(*responses: dict[str, object]) -> tuple[Mock, Mock]:
    api = Mock()
    events_resource = api.events.return_value
    requests = []
    for response in responses:
        request = Mock()
        request.execute.return_value = response
        requests.append(request)
    events_resource.list.side_effect = requests
    return api, events_resource


def test_google_reader_is_read_only_by_contract() -> None:
    reader = GoogleCalendarReader(Mock())

    assert isinstance(reader, CalendarReader)
    assert not isinstance(reader, CalendarService)
    assert not hasattr(reader, "create_event")


def test_authentication_failure_is_wrapped_and_uses_read_only_scope(tmp_path: Path) -> None:
    settings = GoogleCalendarSettings(
        credentials_path=tmp_path / "missing-credentials.json",
        token_path=tmp_path / "token.json",
    )

    with patch(
        "calendar_agent.calendar.google_calendar.InstalledAppFlow.from_client_secrets_file",
        side_effect=FileNotFoundError,
    ) as load_flow:
        with pytest.raises(GoogleCalendarAuthenticationError, match="read-only"):
            build_google_api_service(settings)

    load_flow.assert_called_once_with(
        str(settings.credentials_path),
        [GOOGLE_CALENDAR_READONLY_SCOPE],
    )


def test_list_events_maps_timed_and_all_day_events_across_pages() -> None:
    api, events_resource = api_with_responses(
        {
            "timeZone": "America/Toronto",
            "items": [
                {
                    "id": "timed-1",
                    "summary": "Coffee",
                    "description": "Catch up",
                    "start": {"dateTime": "2026-07-04T10:00:00-04:00"},
                    "end": {"dateTime": "2026-07-04T11:00:00-04:00"},
                },
                {
                    "id": "ignored",
                    "summary": "Free marker",
                    "transparency": "transparent",
                    "start": {"dateTime": "2026-07-04T12:00:00-04:00"},
                    "end": {"dateTime": "2026-07-04T13:00:00-04:00"},
                },
            ],
            "nextPageToken": "page-2",
        },
        {
            "timeZone": "America/Toronto",
            "items": [
                {
                    "id": "all-day-1",
                    "summary": "Holiday",
                    "start": {"date": "2026-07-05"},
                    "end": {"date": "2026-07-06"},
                },
                {
                    "id": "cancelled",
                    "status": "cancelled",
                    "start": {"dateTime": "2026-07-05T15:00:00-04:00"},
                    "end": {"dateTime": "2026-07-05T16:00:00-04:00"},
                },
            ],
        },
    )
    reader = GoogleCalendarReader(api)

    events = reader.list_events(START, END)

    assert [event.id for event in events] == ["timed-1", "all-day-1"]
    assert events[0].title == "Coffee"
    assert events[0].description == "Catch up"
    assert events[1].start == datetime(2026, 7, 5, 0, 0, tzinfo=TZ)
    assert events[1].end == datetime(2026, 7, 6, 0, 0, tzinfo=TZ)
    assert events_resource.list.call_count == 2
    assert events_resource.list.call_args_list[0].kwargs["pageToken"] is None
    assert events_resource.list.call_args_list[1].kwargs["pageToken"] == "page-2"
    assert events_resource.list.call_args_list[0].kwargs["singleEvents"] is True
    assert events_resource.list.call_args_list[0].kwargs["orderBy"] == "startTime"


def test_invalid_google_event_is_reported_with_its_id() -> None:
    api, _ = api_with_responses(
        {
            "items": [
                {
                    "id": "broken-1",
                    "summary": "Broken",
                    "start": {"dateTime": "not-a-date"},
                    "end": {"dateTime": "2026-07-04T11:00:00-04:00"},
                }
            ]
        }
    )

    with pytest.raises(GoogleCalendarReadError, match="broken-1"):
        GoogleCalendarReader(api).list_events(START, END)


def test_api_failure_is_wrapped_without_returning_partial_results() -> None:
    api = Mock()
    api.events.return_value.list.return_value.execute.side_effect = RuntimeError("API down")

    with pytest.raises(GoogleCalendarReadError, match="could not read events"):
        GoogleCalendarReader(api).list_events(START, END)


def test_list_events_requires_a_valid_timezone_aware_window() -> None:
    reader = GoogleCalendarReader(Mock())

    with pytest.raises(ValueError, match="timezone-aware"):
        reader.list_events(datetime(2026, 7, 4), END)

    with pytest.raises(ValueError, match="end must be after start"):
        reader.list_events(END, START)
