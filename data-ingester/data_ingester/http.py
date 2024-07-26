import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
import httpx


@dataclass
class ImportParams:
    url: str
    target: Path


class DataImporter:
    """
    Class used to perform  single download data.
    """

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def download(self, params: ImportParams):
        async with (
            self.client.stream("GET", params.url) as response,
            aiofiles.open(params.target, "wb") as file,
        ):
            # May need to check status code
            async for chunk in response.aiter_bytes():
                await file.write(chunk)


class ImportQueue(asyncio.Queue[ImportParams]):
    """
    Queue used to limit number of concurrent downloads.
    """


async def worker(
    importer: DataImporter, queue: ImportQueue, *, event: asyncio.Event | None = None
):
    """
    Worker pulls job from import queue and executes import.
    """
    while True:
        params = await queue.get()
        await importer.download(params)

        if event:
            event.set()

        queue.task_done()


@asynccontextmanager
async def managed_import_queue(
    data_importer: DataImporter,
    *,
    pool_size: int = 2,
    _queue: ImportQueue | None = None,
) -> AsyncGenerator[ImportQueue, None]:
    """
    Managed import queue which regulates number of concurrent downloads.
    """
    queue = _queue or ImportQueue()

    workers = [
        asyncio.create_task(worker(data_importer, queue)) for _ in range(pool_size)
    ]

    yield queue

    await queue.join()

    for task in workers:
        task.cancel()

    await asyncio.gather(*workers, return_exceptions=True)
