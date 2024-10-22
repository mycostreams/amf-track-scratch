from datetime import timedelta

from pydantic import AwareDatetime, BaseModel, Field, PositiveInt

from export_ingester.models import EventType
from export_ingester.utils import now


class FilterParams(BaseModel):
    event_type: EventType = EventType.STITCH
    end: AwareDatetime = Field(default_factory=now)
    start: AwareDatetime = Field(default_factory=lambda: now() - timedelta(hours=24))
    limit: PositiveInt = Field(250, le=250)
    offset: int = Field(0, ge=0)
