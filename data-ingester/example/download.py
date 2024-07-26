"""Example of downloading files via s3 and plain http."""

import asyncio
import io
from contextlib import AsyncExitStack
from pathlib import Path

import aiofiles.tempfile
import httpx

from data_ingester.http import DataImporter, ImportParams, managed_import_queue
from data_ingester.s3 import managed_s3_file_system


async def main():
    key = "mycostreams/a.txt"
    url = f"http://localhost:9090/{key}"

    async with AsyncExitStack() as stack:
        client = await stack.enter_async_context(httpx.AsyncClient())
        temp_dir = Path(
            await stack.enter_async_context(aiofiles.tempfile.TemporaryDirectory())
        )

        # Add data
        await client.put(url, files=(("upload-file", io.BytesIO(b"example")),))

        # Download via http client
        http_download_path = temp_dir / "http.txt"
        async with managed_import_queue(DataImporter(client)) as queue:
            queue.put_nowait(
                ImportParams(
                    url=url,
                    target=http_download_path,
                )
            )
        assert http_download_path.exists()

        # Download via S3 client
        s3_download_path = temp_dir / "s3.txt"
        async with managed_s3_file_system() as s3:
            await s3._get(
                ["mycostreams/a.txt"],
                [f"{temp_dir}/s3.txt"],
            )
        assert s3_download_path.exists()


if __name__ == "__main__":
    asyncio.run(main())
