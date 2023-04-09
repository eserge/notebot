import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import Settings, get_settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
settings = get_settings()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    breakpoint()
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="pong")


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Authenticating..."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text
    )


def build_app(settings: Settings) -> Application:
    application = ApplicationBuilder().token(settings.telegram_token).build()

    start_handler = CommandHandler("start", start)
    ping_handler = CommandHandler("ping", ping)
    auth_handler = CommandHandler("auth", auth)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(ping_handler)
    application.add_handler(auth_handler)

    return application


if __name__ == "__main__":
    application = build_app(settings)
    application.run_polling()
