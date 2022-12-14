from pydantic import BaseSettings


class Settings(BaseSettings):
    app_host: str = "localhost"
    app_port: int = 8000
    app_data_dir: str = "/data/"
    app_data_filename = "data.db"
    sentry_dsn: str = ""
    evernote_consumer_key: str
    evernote_consumer_secret: str
    evernote_sandbox_enabled: bool = True
    ngrok_bin_path: str = "/usr/local/bin/ngrok"
    telegram_secret: str
    telegram_token: str

    def get_webhook_url(self) -> str:
        return f"/webhook/{self._get_token_websafe()}"

    def _get_token_websafe(self) -> str:
        return self.telegram_token.replace(":", "/")


def get_settings() -> Settings:
    return Settings()
