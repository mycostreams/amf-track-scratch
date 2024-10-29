import asyncio
from datetime import date, timedelta

from .api_client import ExportParams
from .config import Settings
from .ingest import get_managed_export_ingester
from .utils import get_range


async def main():
    settings = Settings()
    remote = f"/scratch-shared/amftrack2024/daily/{date.today()}.json"
    time_range = 4
    # TODO these two need to become either parameter or environment variables
    date_ = date.today() - timedelta(days=time_range)
    start, end = get_range(date_, time_range)
    async with get_managed_export_ingester(settings) as export_ingester:
        await export_ingester.ingest(remote, ExportParams(start=start, end=end))
        await export_ingester.run_sbatch_command(settings.SBATCH_COMMAND, remote)


if __name__ == "__main__":
    asyncio.run(main())
