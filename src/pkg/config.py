from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TELEGRAM_BOT_API_TOKEN: SecretStr
    ADMIN_TELEGRAM_ID: int
    ADMIN_USERNAME: Optional[str] = None
    ADMIN_FIRST_NAME: Optional[str] = None
    ADMIN_LAST_NAME: Optional[str] = None
    GROUP_TELEGRAM_ID: int
    GROUP_TELEGRAM_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
