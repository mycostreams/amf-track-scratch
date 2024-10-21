from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SFTP_USERNAME: str
    SFTP_PASSWORD: str
    SFTP_HOST: str
    SBATCH_COMMAND: str

    BASE_URL: HttpUrl

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
