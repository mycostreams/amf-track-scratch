from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncGenerator, Callable

import asyncssh

from .models import ExportList, ExportModel


class SFTPClient:
    def __init__(self, client: asyncssh.SFTPClient):
        self.client = client

    async def pipe_exports(
        self,
        path: str,
        exports: list[ExportModel],
        *,
        _mapper: Callable[[list[ExportModel]], bytes] | None = None,
    ):
        mapper = _mapper or partial(ExportList.dump_json, indent=4)
        async with self.client.open(path, "wb") as f:
            await f.write(mapper(exports))


class SFTPClientFactory:
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
    ):
        self.username = username
        self.host = host
        self.password = password

    @asynccontextmanager
    async def get_sftp_client(self) -> AsyncGenerator[SFTPClient, None]:
        managed_conn = asyncssh.connect(
            username=self.username,
            password=self.password,
            host=self.host,
            known_hosts=None,
        )
        async with managed_conn as conn:
            async with conn.start_sftp_client() as sftp:
                yield SFTPClient(sftp)

