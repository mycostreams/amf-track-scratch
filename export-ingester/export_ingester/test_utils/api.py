from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query

from export_ingester.models import (
    ArchiveModel,
    ArchiveSummaryModel,
    ExportModel,
    PaginatedResponse,
)

from .models import ArchivesFilterParams, ExportsFilterParams
from .utils import (
    create_archive_data,
    create_export_data,
    filter_archive_data,
    filter_export_data,
)

EXPORT_DATA = list(create_export_data())

ARCHIVES_DATA = list(create_archive_data())


app = FastAPI()


def get_archive_url(item: ArchiveModel) -> str:
    return str(app.url_path_for("get_archive", id=item.id))


@app.get(
    "/api/1/archives/{id}",
    response_model=ArchiveModel,
)
def get_archive(id: UUID):
    for item in ARCHIVES_DATA:
        if item.id == id:
            return item
    raise HTTPException(status_code=404)


@app.get(
    "/api/1/archives",
    response_model=PaginatedResponse[ArchiveSummaryModel],
)
def get_archives(filter_params: Annotated[ArchivesFilterParams, Query()]) -> dict:
    count, data = filter_archive_data(ARCHIVES_DATA, filter_params=filter_params)
    return {
        "count": count,
        "data": [{"url": get_archive_url(item)} for item in data],
    }


@app.get("/api/1/exports", response_model=PaginatedResponse[ExportModel])
def get_exports(filter_params: Annotated[ExportsFilterParams, Query()]) -> dict:
    count, data = filter_export_data(EXPORT_DATA, filter_params)
    return {
        "count": count,
        "data": data,
    }
