import asyncio
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import AsyncGenerator

import httpx
from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from s3fs import S3FileSystem


class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ENDPOINT_URL: HttpUrl
    BUCKET_NAME: str = "mycostreams-dev-559d46"
    
    BASE_URL: HttpUrl = "http://tsu-dsk001.ipa.amolf.nl"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@asynccontextmanager
async def managed_s3_filesystem(
    filesystem: S3FileSystem,
) -> AsyncGenerator[S3FileSystem, None]:
    session = await filesystem.set_session()

    yield filesystem

    await session.close()


async def main(*, _settings: Settings | None = None):
    settings = _settings or Settings()

    filename = f"{date.today()}.json"

    client = httpx.AsyncClient(
        base_url=str(settings.BASE_URL),
        headers={"Host": "fastapi.localhost"},
    )

    s3 = S3FileSystem(
        key=settings.AWS_ACCESS_KEY_ID,
        secret=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=str(settings.AWS_ENDPOINT_URL),
        asynchronous=True,
    )

    async with managed_s3_filesystem(s3), client:
        response = await client.get("/api/1/exports")

        await s3._pipe(
            f"{settings.BUCKET_NAME}/{filename}",
            response.content,
        )


if __name__ == "__main__":
    asyncio.run(main())
