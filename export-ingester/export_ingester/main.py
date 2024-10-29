import asyncio
from datetime import date

from .api_client import ExportParams
from .config import Settings
from .ingest import get_managed_export_ingester


async def main():
    settings = Settings()
    remote = f"daily-uploads/{date.today()}.json"
    async with get_managed_export_ingester(settings) as export_ingester:
        await export_ingester.ingest(remote, ExportParams())
        await export_ingester.run_sbatch_command(settings.SBATCH_COMMAND, remote)


if __name__ == "__main__":
    asyncio.run(main())
