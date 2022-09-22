from pydantic import BaseSettings


class Settings(BaseSettings):
    app_host: str = "localhost"
    app_port: int = 8000
    telegram_token: str
    telegram_secret: str
    evernote_consumer_key: str
    evernote_consumer_secret: str
    evernote_auth_token: str


def get_settings() -> Settings:
    return Settings()
