from pydantic import BaseModel, ConfigDict


class CalendarInfo(BaseModel):
    """Metadata used to choose which Google calendars should block time."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    timezone: str | None = None
    access_role: str
    primary: bool = False
    selected: bool = False
    hidden: bool = False
