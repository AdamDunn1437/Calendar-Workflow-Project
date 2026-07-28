import sys
from unittest.mock import Mock

from calendar_agent import google_write_demo


def configure_cli(monkeypatch, api: Mock, confirmation: str) -> Mock:
    events_resource = api.events.return_value
    events_resource.list.return_value.execute.return_value = {
        "timeZone": "America/Toronto",
        "items": [],
    }
    monkeypatch.setattr(
        google_write_demo,
        "build_google_write_api_service",
        lambda settings: api,
    )
    monkeypatch.setattr("builtins.input", lambda prompt: confirmation)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "google_write_demo",
            "--title",
            "Calendar Agent Test",
            "--duration",
            "15",
            "--sessions",
            "1",
            "--start-date",
            "2026-07-04",
            "--days",
            "1",
            "--daily-start",
            "09:00",
            "--daily-end",
            "10:00",
        ],
    )
    return events_resource


def test_write_demo_rejects_without_calling_google_insert(
    monkeypatch,
    capsys,
) -> None:
    events_resource = configure_cli(monkeypatch, Mock(), "no")

    google_write_demo.main()

    events_resource.insert.assert_not_called()
    assert "Proposal rejected" in capsys.readouterr().out


def test_write_demo_creates_only_after_exact_yes(monkeypatch, capsys) -> None:
    events_resource = configure_cli(monkeypatch, Mock(), "yes")
    events_resource.insert.return_value.execute.return_value = {
        "id": "created-test-event",
        "summary": "Calendar Agent Test",
        "start": {"dateTime": "2026-07-04T09:00:00-04:00"},
        "end": {"dateTime": "2026-07-04T09:15:00-04:00"},
    }

    google_write_demo.main()

    assert events_resource.insert.call_count == 1
    assert events_resource.insert.call_args.kwargs["calendarId"] == "primary"
    assert "Created: Calendar Agent Test" in capsys.readouterr().out
