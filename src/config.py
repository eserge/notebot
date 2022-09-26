from pydantic import BaseSettings


class Settings(BaseSettings):
    app_host: str = "localhost"
    app_port: int = 8000
    evernote_auth_token: str
    evernote_consumer_key: str
    evernote_consumer_secret: str
    ngrok_bin_path: str = "/usr/local/bin/ngrok"
    telegram_secret: str
    telegram_token: str


def get_settings() -> Settings:
    return Settings()
