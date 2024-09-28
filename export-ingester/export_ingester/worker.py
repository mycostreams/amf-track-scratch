import logging
import os
from contextlib import AsyncExitStack
from datetime import date

from arq import cron
from arq.connections import RedisSettings
from zoneinfo import ZoneInfo

from .ingest import Settings, get_managed_export_ingester
from .models import ExportParams


def configure_logging():
    logging.basicConfig(level=logging.INFO)


async def startup(ctx: dict):
    configure_logging()

    logging.info("Starting up")

    settings = Settings()

    ctx["settings"] = settings

async def shutdown(ctx: dict):
    logging.info("Shutting down")

    stack: AsyncExitStack = ctx["stack"]
    stack: AsyncExitStack = await stack.aclose()


async def run_ingestion(ctx: dict, *, _date: date | None = None):
    settings: Settings = ctx["settings"]
    date_ = _date or date.today()
    async with get_managed_export_ingester(settings) as ingester:
        await ingester.ingest(f"daily-uploads/{date_}.json", ExportParams())


class WorkerSettings:
    cron_jobs = [
        cron(run_ingestion, hour={11}),
    ]

    timezone = ZoneInfo("Europe/Amsterdam")

    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_DSN", "redis://localhost:6379"),
    )
