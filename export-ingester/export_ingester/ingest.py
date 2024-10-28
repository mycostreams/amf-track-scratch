import urllib.parse
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator, Callable

import httpx

from .config import Settings
from .models import ExportModel, ExportParams, ExportsFormat, ExportsModel
from .sftp import SSHClient, SSHClientFactory


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
        _mapper: Callable[[bytes], ExportsModel] | None = None,
    ) -> list[ExportModel]:
        response = await self.client.get(
            urllib.parse.urljoin(self.base_url, "/api/1/exports"),
            headers={"Host": "fastapi.localhost"},
            params=params.model_dump(mode="json", by_alias=True),
        )

        mapper = _mapper or ExportsFormat.validate_json
        exports_model = mapper(response.content)  # Parse the full response
        return exports_model.data  # Return only the list of ExportModel


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
