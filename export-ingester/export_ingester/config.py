from pathlib import Path

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SFTP_USERNAME: str
    SFTP_PASSWORD: str
    SFTP_HOST: str
    BASE_URL: HttpUrl
    SBATCH_COMMAND: str

    env_path = Path(__file__).parent.parent / ".env"
    # Read and print the contents of the file
    if env_path.exists():
        with open(env_path, 'r') as file:
            contents = file.read()
            print(contents)
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
