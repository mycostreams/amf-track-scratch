import asyncio

from .config import Settings
from .ingest import get_managed_context, ingest_exports


async def main():
    settings = Settings()
    async with get_managed_context(settings) as context:
        await ingest_exports(context)


if __name__ == "__main__":
    asyncio.run(main())
