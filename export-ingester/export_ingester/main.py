import asyncio
from datetime import date

from .api_client import ExportParams
from .config import Settings
from .ingest import get_managed_export_ingester
from .utils import get_date_start


async def main():
    settings = Settings()
    remote = f"/scratch-shared/amftrack2024/daily/{date.today()}.json"
    # TODO these two need to become either parameter or environment variables
    start = get_date_start(date.today())
    end = start - settings.TIME_RANGE
    async with get_managed_export_ingester(settings) as export_ingester:
        await export_ingester.ingest(remote, ExportParams(start=start, end=end))
        await export_ingester.run_sbatch_command(settings.SBATCH_COMMAND, remote)


if __name__ == "__main__":
    asyncio.run(main())
