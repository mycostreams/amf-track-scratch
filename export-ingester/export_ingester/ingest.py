import urllib.parse
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator, Callable

import httpx
from s3fs import S3FileSystem

from .config import Settings
from .models import ExportList, ExportModel, ExportParams


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


class S3Client:
    def __init__(self, s3: S3FileSystem):
        self.s3 = s3

    async def pipe_exports(
        self,
        path: str,
        exports: list[ExportModel],
        *,
        _mapper: Callable[[list[ExportModel]], bytes] | None = None,
    ):
        mapper = _mapper or ExportList.dump_json
        await self.s3._pipe(path, mapper(exports))


class ExportIngester:
    def __init__(
        self,
        api_client: APIClient,
        s3_client: S3Client,
    ):
        self.api_client = api_client
        self.s3_client = s3_client

    async def ingest(
        self,
        remote_path: str,
        params: ExportParams,
    ):
        await self.s3_client.pipe_exports(
            remote_path, await self.api_client.get_exports(params)
        )


@asynccontextmanager
async def managed_s3_filesystem(
    filesystem: S3FileSystem,
) -> AsyncGenerator[S3FileSystem, None]:
    session = await filesystem.set_session()

    yield filesystem

    await session.close()


@asynccontextmanager
async def get_managed_export_ingester(
    settings: Settings,
) -> AsyncGenerator[ExportIngester, None]:
    s3 = S3FileSystem(
        key=settings.AWS_ACCESS_KEY_ID,
        secret=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=str(settings.AWS_ENDPOINT_URL),
        asynchronous=True,
    )

    stack = await AsyncExitStack().__aenter__()

    client = await stack.enter_async_context(httpx.AsyncClient())
    await stack.enter_async_context(managed_s3_filesystem(s3))

    yield ExportIngester(
        APIClient(str(settings.BASE_URL), client),
        S3Client(s3),
    )

    await stack.aclose()
