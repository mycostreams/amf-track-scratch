import logging
import os
from contextlib import AsyncExitStack

from arq import cron
from arq.connections import RedisSettings
from zoneinfo import ZoneInfo

from .ingest import Context, Settings, get_managed_context, ingest_exports


def configure_logging():
    logging.basicConfig(level=logging.INFO)


async def startup(ctx: dict):
    configure_logging()

    logging.info("Starting up")

    stack = await AsyncExitStack().__aenter__()
    settings = Settings()

    ctx["stack"] = stack
    ctx["context"] = await stack.enter_async_context(get_managed_context(settings))


async def shutdown(ctx: dict):
    logging.info("Shutting down")

    stack: AsyncExitStack = ctx["stack"]
    stack: AsyncExitStack = await stack.aclose()


async def run_ingestion(ctx: dict):
    context: Context = ctx["context"]
    await ingest_exports(context)


class WorkerSettings:
    cron_jobs = [
        cron(run_ingestion, hour={17}, minute={11, 12}),
    ]

    timezone = ZoneInfo("Europe/Amsterdam")

    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_DSN", "redis://localhost:6379"),
    )
