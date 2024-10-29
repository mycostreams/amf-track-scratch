from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator

import httpx

from .api_client import APIClient, ExportParams
from .config import Settings
from .sftp import SFTPClient, SFTPClientFactory


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
