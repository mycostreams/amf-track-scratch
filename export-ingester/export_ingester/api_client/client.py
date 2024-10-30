import asyncio
import urllib.parse
from enum import StrEnum
from functools import partial
from typing import AsyncGenerator, Callable, TypeVar
import logging

import httpx

from .models import (
    ArchiveModel,
    ArchiveParams,
    ArchiveSummaryModel,
    DataT,
    ExportModel,
    ExportParams,
    PaginatedResponse,
    Params,
)

T = TypeVar("T")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Routes(StrEnum):
    EXPORTS = "/api/1/exports"
    ARCHIVES = "/api/1/archives"


class APIClient:
    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient,
        *,
        max_concurrency: int = 10,
    ):
        self.base_url = base_url
        self.client = client

        self.sem = asyncio.Semaphore(max_concurrency)

    async def get_exports(self, params: ExportParams) -> list[ExportModel]:
        return [item async for item in self._stream_exports(params)]

    async def get_archives(
        self,
        params: ArchiveParams,
    ) -> list[ArchiveModel]:
        logger.info("Fetching archives with parameters: %s", params)
        return [item async for item in self._stream_archives(params)]

    async def _stream_exports(
        self,
        params: ExportParams,
    ) -> AsyncGenerator[ExportModel, None]:
        export_stream = self._stream_paginated_response(
            Routes.EXPORTS,
            params,
            PaginatedResponse[ExportModel],
        )
        async for item in export_stream:
            yield item

    async def _stream_archives(
        self,
        params: ArchiveParams,
    ) -> AsyncGenerator[ArchiveModel, None]:
        archive_summary_stream = self._stream_paginated_response(
            Routes.ARCHIVES,
            params,
            PaginatedResponse[ArchiveSummaryModel],
        )
        async for item in archive_summary_stream:
            yield await self._get_response(
                str(item.url),
                ArchiveModel.model_validate_json,
            )

    async def _stream_paginated_response(
        self,
        url: str,
        params: Params,
        paginator_cls: type[PaginatedResponse[DataT]],
    ) -> AsyncGenerator[DataT, None]:
        default_params = params.model_dump(mode="json")

        get_response = partial(
            self._get_response, url, paginator_cls.model_validate_json
        )
        logger.debug("Requesting initial data from %s with params: %s", url, default_params)
        initial_data = await get_response({"offset": 0, **default_params})
        for item in initial_data.data:
            yield item

        tasks: list[asyncio.Task[PaginatedResponse[DataT]]] = []
        for index in range(initial_data.count // params.limit):
            next_params = {"offset": (index + 1) * params.limit, **default_params}
            tasks.append(asyncio.create_task(get_response(next_params)))

        for task in asyncio.as_completed(tasks):
            next_data = await task
            for item in next_data.data:
                yield item

    async def _get_response(
        self,
        endpoint: str,
        mapper: Callable[[bytes], T],
        params: dict | None = None,
    ) -> T:
        async with self.sem:
            logger.debug("Sending request to %s with params: %s", endpoint, params)
            response = await self.client.get(
                urllib.parse.urljoin(self.base_url, endpoint),
                headers={"Host": "fastapi.localhost"},
                params=params,
            )
            logger.debug("response is ", response.content)

            return mapper(response.content)
