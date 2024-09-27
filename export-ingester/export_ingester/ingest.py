from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
from datetime import date
from typing import AsyncGenerator, Callable

import httpx
from s3fs import S3FileSystem

from .config import Settings


@asynccontextmanager
async def managed_s3_filesystem(
    filesystem: S3FileSystem,
) -> AsyncGenerator[S3FileSystem, None]:
    session = await filesystem.set_session()

    yield filesystem

    await session.close()


@dataclass
class Context:
    client: httpx.AsyncClient
    s3: S3FileSystem
    name_generator: Callable[[], str]


@asynccontextmanager
async def get_managed_context(settings: Settings) -> AsyncGenerator[Context, None]:
    context = Context(
        client=httpx.AsyncClient(
            base_url=str(settings.BASE_URL),
            headers={"Host": "fastapi.localhost"},
        ),
        s3=S3FileSystem(
            key=settings.AWS_ACCESS_KEY_ID,
            secret=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=str(settings.AWS_ENDPOINT_URL),
            asynchronous=True,
        ),
        name_generator=lambda: f"{settings.BUCKET_NAME}/{date.today()}.json",
    )

    stack = await AsyncExitStack().__aenter__()

    await stack.enter_async_context(context.client)
    await stack.enter_async_context(managed_s3_filesystem(context.s3))

    yield context

    await stack.aclose()


async def ingest_exports(context: Context):
    response = await context.client.get("/api/1/exports")
    await context.s3._pipe(context.name_generator(), response.content)
