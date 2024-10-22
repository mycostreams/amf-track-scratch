from datetime import timedelta
from typing import Callable, Generator, Iterable
from uuid import uuid4

from export_ingester.models import EventType, ExportModel
from export_ingester.utils import now

from .models import FilterParams


def create_data(count: int = 500) -> Generator[ExportModel, None, None]:
    now_ = now()
    for index in range(1, count):
        src_timestamp = now_ - timedelta(hours=index)
        yield ExportModel(
            type=EventType.STITCH,
            experiment_id="test",
            ref_id=uuid4(),
            url="http://test.com",
            uploaded_at=src_timestamp,
            timestamp=src_timestamp,
        )


def filter_data(
    exports: list[ExportModel],
    filter_params: FilterParams,
) -> tuple[int, list[ExportModel]]:
    filters: list[Callable[[ExportModel], bool]] = [
        lambda obj: obj.type == filter_params.event_type,
        lambda obj: obj.timestamp < filter_params.end,
        lambda obj: obj.timestamp > filter_params.start,
    ]

    filtered_exports: Iterable[ExportModel] = exports
    for filter_ in filters:
        filtered_exports = filter(filter_, filtered_exports)

    filtered_exports = list(filtered_exports)

    count = len(filtered_exports)
    data = filtered_exports[
        filter_params.offset : filter_params.offset + filter_params.limit
    ]

    return count, data
