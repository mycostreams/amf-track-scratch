from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator

import httpx

from .api_client import APIClient, ExportParams
from .config import Settings
from .sftp import SSHClient, SSHClientFactory


class ExportIngester:
    def __init__(
        self,
        api_client: APIClient,
        ssh_client: SSHClient,
    ):
        self.api_client = api_client
        self.ssh_client = ssh_client

    async def ingest(
        self,
        remote_path: str,
        params: ExportParams,
    ):
        await self.ssh_client.pipe_exports(
            remote_path,
            await self.api_client.get_exports(params),
        )

    async def run_sbatch_command(self, sbatch_command, remote):
        """Runs the sbatch command on the remote server via SSH."""
        await self.ssh_client.remote_sbatch(sbatch_command, remote)


@asynccontextmanager
async def get_managed_export_ingester(
    settings: Settings,
) -> AsyncGenerator[ExportIngester, None]:
    stack = await AsyncExitStack().__aenter__()

    ssh_client_factory = SSHClientFactory(
        settings.SFTP_USERNAME,
        settings.SFTP_PASSWORD,
        settings.SFTP_HOST,
    )
    http_client = await stack.enter_async_context(httpx.AsyncClient())
    ssh_client = await stack.enter_async_context(ssh_client_factory.get_ssh_client())
    yield ExportIngester(
        APIClient(
            str(settings.BASE_URL),
            http_client,
        ),
        ssh_client,
    )

    await stack.aclose()

