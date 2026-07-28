from datetime import date, time
from zoneinfo import ZoneInfo

from calendar_agent.calendar.base import CalendarService
from calendar_agent.models.calendar_event import CalendarEvent
from calendar_agent.models.course_schedule import CourseMeeting, CourseSchedule
from calendar_agent.scheduling.conflict_checker import conflicts_for_event
from calendar_agent.scheduling.course_expander import expand_schedule


def build_fall_courses() -> list[CourseSchedule]:
    fall_start = date(2026, 9, 9)
    fall_end = date(2026, 12, 9)

    return [
        CourseSchedule(
            course_code="AISE 3020A",
            course_title="AI: ETHICS, BIAS AND PRIVACY",
            instructor="V. Platsko",
            meetings=[
                CourseMeeting(
                    course_code="AISE 3020A",
                    section_type="LEC",
                    day_of_week=2,
                    start_time=time(14, 30),
                    end_time=time(17, 30),
                    location="SEB-2200",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
                CourseMeeting(
                    course_code="AISE 3020A",
                    section_type="LAB",
                    day_of_week=1,
                    start_time=time(10, 30),
                    end_time=time(12, 30),
                    location="ACEB-4435",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
            ],
        ),
        CourseSchedule(
            course_code="AISE 4450A",
            course_title="DATA DRIVEN CONTROL OF CP SYS",
            instructor="I. Polouchine",
            meetings=[
                CourseMeeting(
                    course_code="AISE 4450A",
                    section_type="LEC",
                    day_of_week=3,
                    start_time=time(9, 30),
                    end_time=time(12, 30),
                    location="UCC-37",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
                CourseMeeting(
                    course_code="AISE 4450A",
                    section_type="LAB",
                    day_of_week=4,
                    start_time=time(12, 30),
                    end_time=time(14, 30),
                    location="ACEB-4440",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
            ],
        ),
        CourseSchedule(
            course_code="MSE 3301A",
            course_title="MATERIALS SELECTION & MNFT",
            instructor="E. Johlin",
            meetings=[
                CourseMeeting(
                    course_code="MSE 3301A",
                    section_type="LEC",
                    day_of_week=2,
                    start_time=time(12, 30),
                    end_time=time(13, 30),
                    location="FNB-1250",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
                CourseMeeting(
                    course_code="MSE 3301A",
                    section_type="LEC",
                    day_of_week=4,
                    start_time=time(9, 30),
                    end_time=time(11, 30),
                    location="FNB-3210",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
            ],
        ),
        CourseSchedule(
            course_code="MSE 4401A",
            course_title="ROBOTIC MANIPULATORS",
            instructor="A. Trejos",
            meetings=[
                CourseMeeting(
                    course_code="MSE 4401A",
                    section_type="LEC",
                    day_of_week=2,
                    start_time=time(10, 30),
                    end_time=time(12, 30),
                    location="HSB-35",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
                CourseMeeting(
                    course_code="MSE 4401A",
                    section_type="LEC",
                    day_of_week=4,
                    start_time=time(14, 30),
                    end_time=time(15, 30),
                    location="FNB-3210",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
                CourseMeeting(
                    course_code="MSE 4401A",
                    section_type="LAB",
                    day_of_week=1,
                    start_time=time(13, 30),
                    end_time=time(16, 30),
                    location="ACEB-3435",
                    start_date=fall_start,
                    end_date=fall_end,
                ),
            ],
        ),
        CourseSchedule(
            course_code="MSE 4499",
            course_title="MECHATRONIC DESIGN PROJECT",
            instructor="J. McLeod",
            meetings=[
                CourseMeeting(
                    course_code="MSE 4499",
                    section_type="LEC",
                    day_of_week=1,
                    start_time=time(18, 0),
                    end_time=time(22, 0),
                    location="ACEB-1410",
                    start_date=fall_start,
                    end_date=date(2027, 4, 9),
                ),
            ],
        ),
    ]


def print_plan(
    all_events: list[CalendarEvent],
    existing_events: list[CalendarEvent],
    conflict_pairs: list[tuple[CalendarEvent, list[CalendarEvent]]],
) -> None:
    conflict_set = {id(event) for event, _ in conflict_pairs}
    conflict_map = {id(event): conflicting for event, conflicting in conflict_pairs}

    print("Course Schedule Import Plan")
    print("=" * 60)

    current_code = ""
    for event in all_events:
        parts = event.title.split(" ", 1)
        code = parts[0] if len(parts) > 0 else event.title
        if code != current_code:
            current_code = code
            print(f"\n{code}: {event.title}")
        marker = " [CONFLICT!]" if id(event) in conflict_set else ""
        location = event.description.split(" - ", 1)[1] if " - " in event.description else ""
        print(
            f"  {event.start:%a %m/%d}: {event.start:%H:%M}-{event.end:%H:%M}"
            f"  {location}"
            f"{marker}"
        )

    print(f"\nTotal course events to create: {len(all_events)}")
    print(f"Existing calendar events in range: {len(existing_events)}")
    total_conflicts = sum(len(c) for _, c in conflict_pairs)
    if total_conflicts:
        print(f"WARNING: {total_conflicts} conflict(s) detected!")
        for event, conflicting in conflict_pairs:
            for conflict in conflicting:
                print(
                    f"  {event.title} on {event.start:%a %m/%d %H:%M} "
                    f"conflicts with '{conflict.title}'"
                )
    else:
        print("No conflicts detected.")


def run_course_import(calendar: CalendarService, timezone: ZoneInfo) -> None:
    courses = build_fall_courses()

    all_events: list[CalendarEvent] = []
    for course in courses:
        all_events.extend(expand_schedule(course, timezone))
    all_events.sort(key=lambda e: e.start)

    if not all_events:
        print("No course events to create.")
        return

    window_start = all_events[0].start
    window_end = all_events[-1].end

    existing_events = calendar.list_events(window_start, window_end)

    conflict_pairs: list[tuple[CalendarEvent, list[CalendarEvent]]] = []
    conflict_map: dict[int, list[CalendarEvent]] = {}
    for event in all_events:
        event_conflicts = conflicts_for_event(event, existing_events)
        if event_conflicts:
            conflict_pairs.append((event, event_conflicts))
            conflict_map[id(event)] = event_conflicts

    print_plan(all_events, existing_events, conflict_pairs)

    confirmation = input("\nType yes to create these course events: ").strip().lower()
    if confirmation != "yes":
        print("Course import rejected. No events were created.")
        return

    created_count = 0
    forced_count = 0
    failed_count = 0
    for event in all_events:
        is_conflicted = id(event) in conflict_map
        try:
            created = calendar.create_event(event, force=is_conflicted)
            if is_conflicted:
                print(f"CREATED (overlaps existing): {created.title} ({created.start:%a %m/%d %H:%M})")
                forced_count += 1
            else:
                print(f"CREATED: {created.title} ({created.start:%a %m/%d %H:%M})")
            created_count += 1
        except Exception as exc:
            print(f"FAILED: {event.title} on {event.start:%a %m/%d %H:%M}: {exc}")
            failed_count += 1

    parts = []
    parts.append(f"{created_count} created")
    if forced_count:
        parts.append(f"{forced_count} overlapped existing events (both kept)")
    if failed_count:
        parts.append(f"{failed_count} failed")
    print(f"\nDone: {', '.join(parts)}.")


def main() -> None:
    from calendar_agent.calendar.google_calendar import (
        GoogleCalendarService,
        GoogleCalendarSettings,
        build_google_write_api_service,
    )

    settings = GoogleCalendarSettings.from_environment()
    timezone = ZoneInfo(settings.default_timezone)
    calendar = GoogleCalendarService(
        build_google_write_api_service(settings),
        calendar_ids=settings.calendar_ids,
        write_calendar_id=settings.write_calendar_id,
        default_timezone=settings.default_timezone,
    )
    run_course_import(calendar, timezone)


if __name__ == "__main__":
    main()
