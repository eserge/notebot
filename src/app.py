from cgitb import handler
from email import message
from turtle import update
from typing import Any, Callable, Coroutine, Dict, Optional
from fastapi import FastAPI

from config import get_settings
from domain import process_message, get_message
from entities import Update
from telegram import Telegram


settings = get_settings()
telegram = Telegram(settings.telegram_token, settings.telegram_secret)
app = FastAPI()


@app.get("/healthcheck/")
async def healthcheck() -> Dict:
    return {"healthcheck": "OK"}


async def ping(update: Update):
    assert update.message is not None
    assert update.message.chat is not None

    PING_RESPONSE = "pong"
    chat = update.message.chat
    return await telegram.send_message(chat.id, PING_RESPONSE)


COMMANDS = {
    "/ping": ping,
}


def dispatch_command(
    update: Update,
) -> Optional[Callable[[Update], Coroutine[Any, Any, Any]]]:
    if not update.message:
        return None

    command = update.message.text
    # Command if it's a oneliner starting with "/"
    # And it is declared in COMMANDS
    if not command:
        return None
    if not command.startswith("/"):
        return None
    if command.count("\n") > 0:
        return None
    if command in COMMANDS:
        return COMMANDS[command]

    return None


@app.post(telegram.get_webhook_url())
async def webhook(update: Update):
    handler = dispatch_command(update)
    if handler:
        await handler(update)
    else:
        message = get_message(update)
        process_message(message)
        await confirm_message_saved(update)

    return {}


async def confirm_message_saved(update: Update):
    assert update.message is not None
    assert update.message.chat is not None

    CONFIRMATION_TEXT = "Saved!"
    chat_id = update.message.chat.id
    await telegram.send_message(chat_id, CONFIRMATION_TEXT)
