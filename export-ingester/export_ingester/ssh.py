from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncssh


class SSHClient:
    def __init__(self, client: asyncssh.SSHClientConnection):
        self.client = client

    async def remote_sbatch(self, sbatch_command: str,remote: str) -> str:
        """Executes the sbatch command on the remote server."""
        try:
            result = await self.client.run(f"{sbatch_command} {remote}", check=True)
            return result.stdout  # Return the output of the sbatch command
        except asyncssh.Error as e:
            print(f"Error running sbatch command: {str(e)}")
            return ""


class SSHClientFactory:
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
    async def get_ssh_client(self) -> AsyncGenerator[SSHClient, None]:
        """Context manager to manage the SSH connection."""
        managed_conn = asyncssh.connect(
            host=self.host,
            username=self.username,
            password=self.password,
            known_hosts=None,
        )
        async with managed_conn as conn:
            yield SSHClient(conn)
