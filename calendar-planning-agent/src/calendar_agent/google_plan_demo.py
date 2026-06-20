import argparse
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from calendar_agent.calendar.google_calendar import (
    GoogleCalendarReader,
    GoogleCalendarSettings,
    build_google_api_service,
)
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.workflow.orchestrator import CalendarWorkflow


def positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def nonnegative_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value cannot be negative")
    return parsed


def clock_time(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("time must use HH:MM format") from exc


def calendar_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD format") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview scheduling proposals against selected Google calendars."
    )
    parser.add_argument("--title", default="Focus session")
    parser.add_argument("--description", default="")
    parser.add_argument("--duration", type=positive_integer, default=60, help="minutes")
    parser.add_argument("--sessions", type=positive_integer, default=1)
    parser.add_argument("--start-date", type=calendar_date)
    parser.add_argument("--days", type=positive_integer, default=7)
    parser.add_argument("--daily-start", type=clock_time, default=time(9, 0))
    parser.add_argument("--daily-end", type=clock_time, default=time(21, 0))
    parser.add_argument(
        "--gap", type=nonnegative_integer, default=0, help="minimum gap in minutes"
    )
    return parser


def build_scheduling_request(
    arguments: argparse.Namespace,
    timezone: ZoneInfo,
    *,
    today: date | None = None,
) -> SchedulingRequest:
    start_date = arguments.start_date or today or datetime.now(timezone).date()
    final_date = start_date + timedelta(days=arguments.days - 1)
    return SchedulingRequest(
        title=arguments.title,
        description=arguments.description,
        duration_minutes=arguments.duration,
        number_of_sessions=arguments.sessions,
        window_start=datetime.combine(start_date, arguments.daily_start, timezone),
        window_end=datetime.combine(final_date, arguments.daily_end, timezone),
        daily_start_time=arguments.daily_start,
        daily_end_time=arguments.daily_end,
        minimum_gap_minutes=arguments.gap,
    )


def main() -> None:
    arguments = build_parser().parse_args()
    settings = GoogleCalendarSettings.from_environment()
    timezone = ZoneInfo(settings.default_timezone)
    request = build_scheduling_request(arguments, timezone)
    reader = GoogleCalendarReader(
        build_google_api_service(settings),
        calendar_ids=settings.calendar_ids,
        default_timezone=settings.default_timezone,
    )
    reader.list_calendars()
    workflow = CalendarWorkflow(reader)
    result = workflow.plan(request)

    print("Selected calendar IDs:")
    for calendar_id in settings.calendar_ids:
        print(f"- {calendar_id}")

    print("\nBusy events considered:")
    if not result.existing_events:
        print("- None")
    for event in result.existing_events:
        print(
            f"- [{event.source_calendar_name}] {event.title}: "
            f"{event.start:%Y-%m-%d %H:%M} to {event.end:%H:%M}"
        )

    print("\nProposed events (preview only):")
    if not result.proposed_events:
        print(f"- No complete proposal: {'; '.join(result.errors)}")
    for event in result.proposed_events:
        print(f"- {event.title}: {event.start:%Y-%m-%d %H:%M} to {event.end:%H:%M}")

    print("\nNo Google Calendar events were created or modified.")


if __name__ == "__main__":
    main()
