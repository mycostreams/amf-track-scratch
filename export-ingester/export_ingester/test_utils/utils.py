from datetime import timedelta
from typing import Callable, Generator, Iterable
from uuid import uuid4

from export_ingester.models import ArchiveMember, ArchiveModel, EventType, ExportModel
from export_ingester.utils import now

from .models import ArchivesFilterParams, ExportsFilterParams


def create_archive_data(count: int = 30) -> Generator[ArchiveModel, None, None]:
    now_ = now()
    for index in range(1, count):
        src_timestamp = now_ - timedelta(days=1)
        yield ArchiveModel(
            id=uuid4(),
            experiment_id="test",
            path=f"/test/{index:02}.tar",
            created_at=src_timestamp,
            members=[
                ArchiveMember(
                    ref_id=uuid4(),
                    timestamp=src_timestamp,
                    checksum=uuid4().hex,
                    size=1,
                    member_key="test",
                )
            ],
        )


def filter_archive_data(
    archives: list[ArchiveModel],
    filter_params: ArchivesFilterParams,
) -> tuple[int, list[ArchiveModel]]:
    filters: list[Callable[[ArchiveModel], bool]] = [
        lambda obj: obj.experiment_id == filter_params.experiment_id,
    ]

    filtered_archives: Iterable[ArchiveModel] = archives
    for filter_ in filters:
        filtered_archives = filter(filter_, filtered_archives)

    filtered_archives = list(filtered_archives)

    count = len(filtered_archives)
    data = filtered_archives[
        filter_params.offset : filter_params.offset + filter_params.limit
    ]

    return count, data


def create_export_data(count: int = 500) -> Generator[ExportModel, None, None]:
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


def filter_export_data(
    exports: list[ExportModel],
    filter_params: ExportsFilterParams,
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
