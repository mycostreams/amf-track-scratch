import asyncio
import urllib.parse
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator, Callable

import httpx

from .config import Settings
from .models import ExportModel, ExportParams, ExportsModel
from .sftp import SFTPClient, SFTPClientFactory


class APIClient:
    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient,
        *,
        _mapper: Callable[[bytes], ExportsModel] = ExportsModel.model_validate_json,
    ):
        self.base_url = base_url
        self.client = client
        self.mapper = _mapper

    async def get_exports(self, params: ExportParams) -> list[ExportModel]:
        return [item async for item in self.stream_exports(params)]

    async def stream_exports(
        self,
        params: ExportParams,
    ) -> AsyncGenerator[ExportModel, None]:
        default_params = params.model_dump(mode="json", by_alias=True)

        initial_data = await self._get_response({"offset": 0, **default_params})
        for item in initial_data.data:
            yield item

        tasks: list[asyncio.Task[ExportsModel]] = []
        for index in range(initial_data.count // params.limit):
            next_params = {"offset": (index + 1) * params.limit, **default_params}
            tasks.append(asyncio.create_task(self._get_response(next_params)))

        for task in asyncio.as_completed(tasks):
            next_data = await task
            for item in next_data.data:
                yield item

    async def _get_response(self, params: dict) -> ExportsModel:
        response = await self.client.get(
            urllib.parse.urljoin(self.base_url, "/api/1/exports"),
            headers={"Host": "fastapi.localhost"},
            params=params,
        )
        return self.mapper(response.content)


class ExportIngester:
    def __init__(
        self,
        api_client: APIClient,
        sftp_client: SFTPClient,
    ):
        self.api_client = api_client
        self.sftp_client = sftp_client

    async def ingest(
        self,
        remote_path: str,
        params: ExportParams,
    ):
        await self.sftp_client.pipe_exports(
            remote_path,
            await self.api_client.get_exports(params),
        )


@asynccontextmanager
async def get_managed_export_ingester(
    settings: Settings,
) -> AsyncGenerator[ExportIngester, None]:
    stack = await AsyncExitStack().__aenter__()

    sftp_client_factory = SFTPClientFactory(
        settings.SFTP_USERNAME,
        settings.SFTP_PASSWORD,
        settings.SFTP_HOST,
    )

    http_client = await stack.enter_async_context(httpx.AsyncClient())
    sftp_client = await stack.enter_async_context(sftp_client_factory.get_sftp_client())

    yield ExportIngester(
        APIClient(str(settings.BASE_URL), http_client),
        sftp_client,
    )

    await stack.aclose()
