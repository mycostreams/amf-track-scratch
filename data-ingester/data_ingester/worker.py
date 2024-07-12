import os
from datetime import date, timedelta

from arq import cron
from arq.connections import RedisSettings

from .client import DataIngester, Settings


async def remote_ingest(ctx: dict, *, _date: date | None = None):
    data_ingester: DataIngester = ctx["data_ingester"]
    await data_ingester.ingest(_date or date.today() - timedelta(days=1))


async def startup(ctx: dict):
    settings = Settings(
        username=os.environ["username"],
        password=os.environ["password"],
    )

    ctx["data_ingester"] = DataIngester(settings)


class WorkerSettings:
    cron_jobs = [
        cron(remote_ingest, hour={3}, minute={0}),
    ]
    on_startup = startup
    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_DSN", "redis://localhost:6379"),
    )
