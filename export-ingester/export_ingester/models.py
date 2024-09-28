from enum import StrEnum, auto
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, TypeAdapter


class EventType(StrEnum):
    STITCH = auto()


class ExportParams(BaseModel):
    type: EventType = EventType.STITCH


class ExportModel(BaseModel):
    type: EventType
    ref_id: UUID
    experiment_id: str
    uploaded_at: AwareDatetime


ExportList = TypeAdapter(list[ExportModel])
