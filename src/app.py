from cgitb import handler
from turtle import update
from typing import Coroutine, Optional
from fastapi import FastAPI

from config import get_settings
from domain import process_message, get_message
from entities import Update
from telegram import Telegram


settings = get_settings()
telegram = Telegram(settings.telegram_token, settings.telegram_secret)
app = FastAPI()


@app.get("/healthcheck/")
async def healthcheck():
    return {"healthcheck": "OK"}


async def ping(update: Update):
    PING_RESPONSE = "pong"
    return await telegram.send_message(update.message.chat.id, PING_RESPONSE)


COMMANDS = {
    "/ping": ping,
}


def dispatch_command(update: Update) -> Optional[Coroutine]:
    command = update.message.text
    # Command if it's a oneliner starting with "/"
    # And it is declared in COMMANDS
    if not command:
        return
    if not command.startswith("/"):
        return
    if command.count("\n") > 0:
        return
    if command in COMMANDS:
        return COMMANDS[command]


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
    CONFIRMATION_TEXT = "Saved!"
    chat_id = update.message.chat.id
    await telegram.send_message(chat_id, CONFIRMATION_TEXT)
