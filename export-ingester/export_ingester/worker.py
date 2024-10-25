import logging
import os
from datetime import date, timedelta

from arq import cron
from arq.connections import RedisSettings
from zoneinfo import ZoneInfo

from .ingest import Settings, get_managed_export_ingester
from .models import ExportParams
from .utils import get_range


def configure_logging():
    logging.basicConfig(level=logging.INFO)


async def startup(ctx: dict):
    configure_logging()

    logging.info("Starting up")

    ctx["settings"] = Settings()


async def run_ingestion(ctx: dict, *, _date: date | None = None):
    settings: Settings = ctx["settings"]
    remote = f"/scratch-shared/amftrack2024/daily/{date.today()}.json"
    time_range = 1
    date_ = date.today() - timedelta(days=time_range)
    start, end = get_range(date_, time_range)
    async with get_managed_export_ingester(settings) as ingester:
        await ingester.ingest(
            f"daily-uploads/{date_}.json", ExportParams(start=start, end=end)
        )
        await ingester.run_sbatch_command(settings.SBATCH_COMMAND, remote)


class WorkerSettings:
    cron_jobs = [
        cron(run_ingestion, hour={16},minute={20}),
    ]

    timezone = ZoneInfo("Europe/Amsterdam")

    on_startup = startup

    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_DSN", "redis://localhost:6379"),
    )
