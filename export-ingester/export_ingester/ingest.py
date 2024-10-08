import urllib.parse
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator, Callable

import httpx

from .config import Settings
from .models import ExportList, ExportModel, ExportParams
from .sftp import SFTPClient, SFTPClientFactory


class APIClient:
    def __init__(
        self,
        base_url: str,
        client: httpx.AsyncClient,
    ):
        self.base_url = base_url
        self.client = client

    async def get_exports(
        self,
        params: ExportParams,
        *,
        _mapper: Callable[[bytes], list[ExportModel]] | None = None,
    ) -> list[ExportModel]:
        response = await self.client.get(
            urllib.parse.urljoin(self.base_url, "/api/1/exports"),
            headers={"Host": "fastapi.localhost"},
            params=params.model_dump(mode="json", by_alias=True),
        )

        mapper = _mapper or ExportList.validate_json
        return mapper(response.content)


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
