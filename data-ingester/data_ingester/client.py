import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date
from typing import Any, AsyncGenerator

import asyncssh

LOGGER = logging.getLogger(__name__)


@dataclass
class Settings:
    username: str
    password: str
    host: str = "snellius.surf.nl"
    timeout: int = 3600


class DataIngester:
    COMMAND = "$HOME/amf-track-scratch/data-ingester/scripts/run.sh {date_str}"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def ingest(self, date_: date):
        async with self._managed_conn() as conn:
            await conn.run(
                self._build_command(date_str=date_.strftime("%Y%m%d")),
                check=True,
                timeout=self.settings.timeout,
            )

    @asynccontextmanager
    async def _managed_conn(self) -> AsyncGenerator[asyncssh.SSHClientConnection, None]:
        managed_conn = asyncssh.connect(
            username=self.settings.username,
            password=self.settings.password,
            host=self.settings.host,
        )
        async with managed_conn as conn:
            yield conn

    def _build_command(self, **kwargs: Any) -> str:
        return self.COMMAND.format(**kwargs)
