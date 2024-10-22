from enum import StrEnum, auto
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, HttpUrl, TypeAdapter


class EventType(StrEnum):
    STITCH = auto()


class ExportParams(BaseModel):
    event_type: EventType = EventType.STITCH
    start: AwareDatetime
    end: AwareDatetime
    limit: int = 250


class ExportModel(BaseModel):
    ref_id: UUID
    experiment_id: str
    # timestamp: AwareDatetime
    type: EventType
    url: HttpUrl
    uploaded_at: AwareDatetime


class ExportsModel(BaseModel):
    count: int
    data: list[ExportModel]


ExportList = TypeAdapter(list[ExportModel])
