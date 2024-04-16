import logging
from typing import Literal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        extra="ignore",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "CRITICAL"] = "INFO"
    database_url: str = "sqlite:///database.sqlite3"
    fernet_key: bytes = b"3QCDVuzCEWcO0G3J-3gA7W1MguhjCby2ZgsiiEZYfgo="


settings = Settings()
scheduler = AsyncIOScheduler()


logging.basicConfig(
    level=logging.getLevelName(settings.log_level),
    format="%(asctime)s %(levelname)-8s %(pathname)s:%(lineno)d - %(message)s",
    datefmt="%H:%M:%S %d.%m.%Y",
)
