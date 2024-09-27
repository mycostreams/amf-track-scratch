from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ENDPOINT_URL: HttpUrl
    BUCKET_NAME: str = "mycostreams-dev-559d46"

    BASE_URL: HttpUrl = "http://tsu-dsk001.ipa.amolf.nl"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
