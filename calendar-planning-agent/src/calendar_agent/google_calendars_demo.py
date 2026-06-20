from calendar_agent.calendar.google_calendar import (
    GoogleCalendarReader,
    GoogleCalendarSettings,
    build_google_api_service,
)


def main() -> None:
    settings = GoogleCalendarSettings.from_environment()
    reader = GoogleCalendarReader(
        build_google_api_service(settings),
        calendar_ids=settings.calendar_ids,
        default_timezone=settings.default_timezone,
    )

    print("Calendars available to this Google account:")
    for calendar in reader.list_calendars():
        flags = []
        if calendar.primary:
            flags.append("primary")
        if calendar.selected:
            flags.append("selected in Google")
        if calendar.hidden:
            flags.append("hidden")
        suffix = f" ({', '.join(flags)})" if flags else ""
        print(f"- {calendar.name}{suffix}")
        print(f"  ID: {calendar.id}")
        print(f"  Timezone: {calendar.timezone or 'not specified'}")
        print(f"  Access: {calendar.access_role}")


if __name__ == "__main__":
    main()
