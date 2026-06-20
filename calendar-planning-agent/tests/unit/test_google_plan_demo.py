import argparse
from argparse import Namespace
from datetime import date, time
from zoneinfo import ZoneInfo

import pytest

from calendar_agent.google_plan_demo import (
    build_scheduling_request,
    clock_time,
    nonnegative_integer,
    positive_integer,
)

TZ = ZoneInfo("America/Toronto")


def arguments(**overrides: object) -> Namespace:
    values = {
        "title": "Study session",
        "description": "Review notes",
        "duration": 90,
        "sessions": 2,
        "start_date": None,
        "days": 3,
        "daily_start": time(9),
        "daily_end": time(17),
        "gap": 30,
    }
    values.update(overrides)
    return Namespace(**values)


def test_build_scheduling_request_creates_timezone_aware_multi_day_window() -> None:
    request = build_scheduling_request(
        arguments(),
        TZ,
        today=date(2026, 6, 20),
    )

    assert request.title == "Study session"
    assert request.window_start.isoformat() == "2026-06-20T09:00:00-04:00"
    assert request.window_end.isoformat() == "2026-06-22T17:00:00-04:00"
    assert request.minimum_gap_minutes == 30


def test_explicit_start_date_replaces_today() -> None:
    request = build_scheduling_request(
        arguments(start_date=date(2026, 7, 1), days=1),
        TZ,
        today=date(2026, 6, 20),
    )

    assert request.window_start.date() == date(2026, 7, 1)
    assert request.window_end.date() == date(2026, 7, 1)


def test_cli_value_parsers_reject_invalid_values() -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="greater than zero"):
        positive_integer("0")

    with pytest.raises(argparse.ArgumentTypeError, match="HH:MM"):
        clock_time("morning")

    with pytest.raises(argparse.ArgumentTypeError, match="negative"):
        nonnegative_integer("-1")
