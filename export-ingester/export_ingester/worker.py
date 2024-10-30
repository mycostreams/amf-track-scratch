import logging
import os
from datetime import date

from arq import cron
from arq.connections import RedisSettings
from zoneinfo import ZoneInfo

from .api_client import ExportParams
from .ingest import Settings, get_managed_export_ingester
from .utils import get_date_start


def configure_logging():
    logging.basicConfig(level=logging.INFO)


async def startup(ctx: dict):
    configure_logging()

    logging.info("Starting up")

    ctx["settings"] = Settings()


async def run_ingestion(ctx: dict, *, _date: date | None = None):
    settings: Settings = ctx["settings"]
    remote = f"/scratch-shared/amftrack2024/daily/{date.today()}.json"
    # TODO these two need to become either parameter or environment variables
    end = get_date_start(date.today())
    start = end - settings.TIME_RANGE
    async with get_managed_export_ingester(settings) as ingester:
        await ingester.ingest(remote, ExportParams(start=start, end=end))
        await ingester.run_sbatch_command(settings.SBATCH_COMMAND, remote)


class WorkerSettings:
    cron_jobs = [
        cron(run_ingestion, hour={11}, minute={21}),
    ]

    timezone = ZoneInfo("Europe/Amsterdam")

    on_startup = startup

    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_DSN", "redis://localhost:6379"),
    )
