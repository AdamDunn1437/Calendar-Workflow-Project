from zoneinfo import ZoneInfo

from calendar_agent.calendar.google_calendar import (
    GoogleCalendarService,
    GoogleCalendarSettings,
    build_google_write_api_service,
)
from calendar_agent.google_plan_demo import build_parser, build_scheduling_request
from calendar_agent.workflow.orchestrator import CalendarWorkflow


def main() -> None:
    parser = build_parser()
    parser.description = "Preview and explicitly approve Google Calendar event creation."
    arguments = parser.parse_args()
    settings = GoogleCalendarSettings.from_environment()
    request = build_scheduling_request(arguments, ZoneInfo(settings.default_timezone))
    calendar = GoogleCalendarService(
        build_google_write_api_service(settings),
        calendar_ids=settings.calendar_ids,
        write_calendar_id=settings.write_calendar_id,
        default_timezone=settings.default_timezone,
    )
    workflow = CalendarWorkflow(calendar)
    result = workflow.plan(request)
    proposal = workflow.latest_proposal()

    print(f"Write target: {settings.write_calendar_id}")
    print("\nProposed events:")
    if not result.proposed_events:
        print(f"- No complete proposal: {'; '.join(result.errors)}")
        return
    for event in result.proposed_events:
        print(f"- {event.title}: {event.start:%Y-%m-%d %H:%M} to {event.end:%H:%M}")

    confirmation = input("\nType yes to create exactly these events: ").strip().lower()
    creation_result = workflow.approve_and_create(proposal.id, approved=confirmation == "yes")
    if confirmation != "yes":
        print("Proposal rejected. No Google Calendar events were created.")
        return

    for event in creation_result.created_events:
        print(f"Created: {event.title} ({event.id})")
    if creation_result.errors:
        print(f"Stopped: {'; '.join(creation_result.errors)}")
        print("Already-created events were not rolled back or retried.")


if __name__ == "__main__":
    main()
