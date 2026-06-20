from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from calendar_agent.calendar.google_calendar import (
    GoogleCalendarReader,
    GoogleCalendarSettings,
    build_google_api_service,
)


def main() -> None:
    settings = GoogleCalendarSettings.from_environment()
    timezone = ZoneInfo(settings.default_timezone)
    start = datetime.now(timezone)
    end = start + timedelta(days=7)
    reader = GoogleCalendarReader(
        build_google_api_service(settings),
        calendar_ids=settings.calendar_ids,
        default_timezone=settings.default_timezone,
    )
    reader.list_calendars()

    print(
        f"Events from {start:%Y-%m-%d} through {end:%Y-%m-%d} "
        f"across {len(settings.calendar_ids)} selected calendar(s):"
    )
    for event in reader.list_events(start, end):
        print(
            f"- [{event.source_calendar_name}] {event.title}: "
            f"{event.start:%Y-%m-%d %H:%M} to {event.end:%H:%M}"
        )


if __name__ == "__main__":
    main()
