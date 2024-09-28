import logging
import os
from contextlib import AsyncExitStack
from dataclasses import dataclass
from datetime import date

from arq import cron
from arq.connections import RedisSettings
from zoneinfo import ZoneInfo

from .ingest import ExportIngester, Settings, get_managed_export_ingester
from .models import ExportParams


@dataclass
class State:
    settings: Settings
    export_ingester: ExportIngester


def configure_logging():
    logging.basicConfig(level=logging.INFO)


async def startup(ctx: dict):
    configure_logging()

    logging.info("Starting up")

    stack = await AsyncExitStack().__aenter__()
    settings = Settings()

    state = State(
        settings=settings,
        export_ingester=await stack.enter_async_context(
            get_managed_export_ingester(settings),
        ),
    )

    ctx["stack"] = stack
    ctx["state"] = state


async def shutdown(ctx: dict):
    logging.info("Shutting down")

    stack: AsyncExitStack = ctx["stack"]
    stack: AsyncExitStack = await stack.aclose()


async def run_ingestion(ctx: dict, *, _date: date | None = None):
    state: State = ctx["state"]
    date_ = _date or date.today()
    await state.export_ingester.ingest(
        f"uploads/{date_}.json",
        ExportParams(),
    )


class WorkerSettings:
    cron_jobs = [
        cron(run_ingestion, hour={8}),
    ]

    timezone = ZoneInfo("Europe/Amsterdam")

    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_DSN", "redis://localhost:6379"),
    )
