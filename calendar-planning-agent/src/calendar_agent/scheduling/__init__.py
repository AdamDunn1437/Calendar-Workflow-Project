from calendar_agent.scheduling.conflict_checker import (
    conflicts_for_event,
    events_overlap,
    intervals_overlap,
)
from calendar_agent.scheduling.course_expander import expand_meeting, expand_schedule
from calendar_agent.scheduling.free_time_finder import find_free_time
from calendar_agent.scheduling.proposal_builder import build_proposal

__all__ = [
    "build_proposal",
    "conflicts_for_event",
    "events_overlap",
    "expand_meeting",
    "expand_schedule",
    "find_free_time",
    "intervals_overlap",
]

