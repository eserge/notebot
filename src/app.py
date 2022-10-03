import os
from sqlite3 import adapters
from typing import Any, Callable, Coroutine, Dict, Optional

import attrs
import pickledb
from evernote.api.client import EvernoteClient
from fastapi import FastAPI

from config import get_settings
from commands import ping, auth
from domain import process_update, get_message
from entities import Update
from repo import Users, AuthRequests
from telegram import Telegram


settings = get_settings()
db = pickledb.load(
    os.path.join(settings.app_data_dir, settings.app_data_filename), auto_dump=True
)
app = FastAPI()

telegram = Telegram(settings.telegram_token, settings.telegram_secret)
users = Users(db=db)
auth_requests = AuthRequests(db=db)


@attrs.define
class Adapters:
    app: FastAPI
    telegram: Telegram
    users: Users
    auth_requests: AuthRequests


_adapters = None


def get_adapters():
    global _adapters
    if not _adapters:
        _adapters = Adapters(
            app=app, telegram=telegram, users=users, auth_requests=auth_requests
        )

    return _adapters


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
    callback_data = {
        "callback_id": callback_id,
        "oauth_token": oauth_token,
        "oauth_verifier": oauth_verifier,
        "sandbox_lnb": sandbox_lnb,
    }
    auth_requests = get_adapters().auth_requests
    telegram = get_adapters().telegram

    if saved_data := auth_requests.get(callback_id):
        user_id = saved_data.get("user_id")
        print(saved_data, callback_data)

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
        await telegram.send_message(
            saved_data["chat_id"],
            f"Hello, {evernote_user.username}!\nYou have been authorized",
        )

        users.set(str(user_id), users.create_user(user_id, access_token))

    return callback_data


COMMANDS = {
    "/ping": ping,
    "/auth": auth,
}

print(f"Installed commands: {COMMANDS.keys()}")


@app.post(telegram.get_webhook_url())
async def webhook(update: Update):
    adapters = get_adapters()
    command_handler = dispatch_command(update)
    if command_handler:
        await command_handler(update, adapters)
    else:
        process_update(update, adapters.users)
        await confirm_message_saved(update, adapters)

    return {}


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


async def confirm_message_saved(update: Update, adapters: Adapters):
    assert update.message is not None
    assert update.message.chat is not None

    CONFIRMATION_TEXT = "Saved!"
    chat_id = update.message.chat.id
    await adapters.telegram.send_message(chat_id, CONFIRMATION_TEXT)
