from pydantic import BaseSettings


class Settings(BaseSettings):
    app_host: str
    app_port: int
    telegram_token: str
    telegram_secret: str
    smtp_server: str
    smtp_port: int = 25
    smtp_user: str
    smtp_pass: str
    evernote_email: str


def get_settings() -> Settings:
    return Settings()
