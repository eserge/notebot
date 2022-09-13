from pydantic import BaseSettings


class Settings(BaseSettings):
    app_host: str
    app_port: int
    telegram_token: str
    telegram_secret: str


def get_settings() -> Settings:
    return Settings()
