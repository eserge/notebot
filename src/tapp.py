import logging

from telegram.ext import Application, ApplicationBuilder, CommandHandler

from commands import TelegramCommands
from config import Settings, get_settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
settings = get_settings()


def build_app(settings: Settings) -> Application:
    application = ApplicationBuilder().token(settings.telegram_token).build()

    ping_handler = CommandHandler("ping", TelegramCommands.ping)
    auth_handler = CommandHandler("auth", TelegramCommands.auth)

    application.add_handler(ping_handler)
    application.add_handler(auth_handler)

    return application


if __name__ == "__main__":
    application = build_app(settings)
    application.run_polling()
