import collections
from typing import Any, Callable, Coroutine, Dict, NamedTuple, Optional

from evernote.api.client import EvernoteClient
from fastapi import FastAPI

import auth
from config import get_settings
from commands import ping, auth
from domain import process_update, get_message
from entities import Update
from telegram import Telegram


settings = get_settings()
telegram = Telegram(settings.telegram_token, settings.telegram_secret)
app = FastAPI()
storage = {}
_connections = None


def get_connections():
    global _connections
    if not _connections:
        Connections = collections.namedtuple(
            "Connections",
            [
                "telegram",
                "storage",
            ],
        )
        _connections = Connections(telegram=telegram, storage=storage)

    return _connections


@app.get("/healthcheck/")
async def healthcheck() -> Dict:
    return {"healthcheck": "OK"}


@app.get("/callback/{callback_id}")
async def callback(
    callback_id: str,
    oauth_token: str | None = None,
    oauth_verifier: str | None = None,
    sandbox_lnb: bool | None = None,
):
    page_data = {
        "callback_id": callback_id,
        "oauth_token": oauth_token,
        "oauth_verifier": oauth_verifier,
        "sandbox_lnb": sandbox_lnb,
    }
    conns = get_connections()
    if callback_id in conns.storage:
        saved_data = conns.storage[callback_id]
        print(saved_data, page_data)

        client = EvernoteClient(
            consumer_key=settings.evernote_consumer_key,
            consumer_secret=settings.evernote_consumer_secret,
            sandbox=True,
        )
        access_token = client.get_access_token(
            oauth_token=saved_data["oauth_token"],
            oauth_token_secret=saved_data["oauth_token_secret"],
            oauth_verifier=oauth_verifier,
        )
        evernote_user = client.get_user_store().getUser()
        print(access_token)
        await conns.telegram.send_message(
            saved_data["chat_id"],
            f"Hello, {evernote_user.username}!\nYou have been authorized",
        )

        return {**page_data, **saved_data, "username": evernote_user.username}

    return page_data


COMMANDS = {
    "/ping": ping,
    "/auth": auth,
}

print(f"Installed commands: {COMMANDS.keys()}")


def dispatch_command(
    update: Update,
) -> Optional[Callable[[Update], Coroutine[Any, Any, Any]]]:
    if not update.message:
        return None

    command = update.message.text
    print(command)
    if _is_command(command):
        return COMMANDS[command]

    return None


def _is_command(command: Optional[str]) -> bool:
    # Command if it's a oneliner starting with "/"
    # And it is declared in COMMANDS
    if not command:
        return False
    if not command.startswith("/"):
        return False
    if command.count("\n") > 0:
        return False
    return command in COMMANDS


@app.post(telegram.get_webhook_url())
async def webhook(update: Update):
    handler = dispatch_command(update)
    if handler:
        await handler(update, get_connections())
    else:
        process_update(update)
        await confirm_message_saved(update)

    return {}


async def confirm_message_saved(update: Update):
    assert update.message is not None
    assert update.message.chat is not None

    CONFIRMATION_TEXT = "Saved!"
    chat_id = update.message.chat.id
    await telegram.send_message(chat_id, CONFIRMATION_TEXT)
