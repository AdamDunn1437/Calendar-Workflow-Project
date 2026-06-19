from datetime import datetime, time

from calendar_agent.calendar.fake_calendar import FakeCalendarService
from calendar_agent.config import DEFAULT_TIMEZONE
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.scheduling_request import SchedulingRequest
from calendar_agent.workflow.orchestrator import CalendarWorkflow


def build_demo_workflow() -> CalendarWorkflow:
    calendar = FakeCalendarService(
        initial_events=[
            CalendarEvent(
                title="Brunch with friends",
                start=datetime(2026, 7, 4, 10, 0, tzinfo=DEFAULT_TIMEZONE),
                end=datetime(2026, 7, 4, 11, 30, tzinfo=DEFAULT_TIMEZONE),
                description="Existing personal plan",
            ),
            CalendarEvent(
                title="Errands",
                start=datetime(2026, 7, 4, 14, 0, tzinfo=DEFAULT_TIMEZONE),
                end=datetime(2026, 7, 4, 15, 0, tzinfo=DEFAULT_TIMEZONE),
                description="Existing personal plan",
            ),
            CalendarEvent(
                title="Family dinner",
                start=datetime(2026, 7, 5, 18, 0, tzinfo=DEFAULT_TIMEZONE),
                end=datetime(2026, 7, 5, 20, 0, tzinfo=DEFAULT_TIMEZONE),
                description="Existing personal plan",
            ),
        ]
    )
    return CalendarWorkflow(calendar)


def build_demo_request() -> SchedulingRequest:
    return SchedulingRequest(
        title="Weekend date activity",
        duration_minutes=90,
        number_of_sessions=2,
        window_start=datetime(2026, 7, 4, 9, 0, tzinfo=DEFAULT_TIMEZONE),
        window_end=datetime(2026, 7, 5, 21, 0, tzinfo=DEFAULT_TIMEZONE),
        daily_start_time=time(9, 0),
        daily_end_time=time(21, 0),
        description="A planned activity block for a weekend date.",
        minimum_gap_minutes=30,
    )


def ask_for_approval() -> bool:
    response = input("Type yes to create these fake-calendar events: ").strip().lower()
    return response == "yes"


def main() -> None:
    workflow = build_demo_workflow()
    request = build_demo_request()
    plan_result = workflow.plan(request)
    proposal = workflow.latest_proposal()

    print("Existing events:")
    for event in plan_result.existing_events:
        print(f"- {event.title}: {event.start:%Y-%m-%d %H:%M} to {event.end:%H:%M}")

    print("\nProposed events:")
    if not proposal.proposed_events:
        print(f"- No proposal created: {proposal.failure_reason}")
        return

    for event in proposal.proposed_events:
        print(f"- {event.title}: {event.start:%Y-%m-%d %H:%M} to {event.end:%H:%M}")

    approved = ask_for_approval()
    result = workflow.approve_and_create(proposal.id, approved=approved)

    if not approved:
        print("\nProposal rejected. No events were created.")
        return

    print("\nCreated events:")
    for event in result.created_events:
        print(f"- {event.id}: {event.title}: {event.start:%Y-%m-%d %H:%M} to {event.end:%H:%M}")


if __name__ == "__main__":
    main()

