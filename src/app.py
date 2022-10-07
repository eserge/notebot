import os
from typing import Any, Callable, Coroutine, Dict, Optional

import attrs
import pickledb
import sentry_sdk
from evernote.api.client import EvernoteClient
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mako.template import Template

from commands import auth, ping
from config import get_settings
from domain import process_update
from entities import Update
from models import User
from repo import AuthRequests, Users
from telegram import Telegram

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
    )
else:
    print("WARNING: starting without Sentry!")

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


@app.get("/callback/{callback_id}", response_class=HTMLResponse)
async def callback(
    callback_id: str,
    oauth_token: str | None = None,
    oauth_verifier: str | None = None,
    sandbox_lnb: bool | None = None,
):
    if not oauth_verifier:
        # If oauth_verifier is missing, user chose not to
        # authorize our bot, or something went wrong
        return Template(filename="tpl/auth_fail.mako").render()

    callback_data = {
        "callback_id": callback_id,
        "oauth_token": oauth_token,
        "oauth_verifier": oauth_verifier,
        "sandbox_lnb": sandbox_lnb,
    }
    auth_requests = get_adapters().auth_requests
    telegram = get_adapters().telegram

    if auth_request := auth_requests.get(callback_id):
        user_id = auth_request.user_id
        print(attrs.asdict(auth_request), callback_data)

        try:
            client = EvernoteClient(
                consumer_key=settings.evernote_consumer_key,
                consumer_secret=settings.evernote_consumer_secret,
                sandbox=settings.evernote_sandbox_enabled,
            )
            access_token = client.get_access_token(
                oauth_token=auth_request.oauth_token,
                oauth_token_secret=auth_request.oauth_token_secret,
                oauth_verifier=oauth_verifier,
            )
        except KeyError:
            return Template(filename="tpl/auth_fail.mako").render()

        evernote_user = client.get_user_store().getUser()
        print(access_token)
        await telegram.send_message(
            auth_request.chat_id,
            f"Hello, {evernote_user.username}!\nYou have been authorized",
        )

        user = User(id=user_id, auth_token=access_token)
        users.set(user)
        auth_requests.unset(callback_id)

        return Template(filename="tpl/auth_success.mako").render()

    return Template(filename="tpl/auth_fail.mako").render()


COMMANDS = {
    "/ping": ping,
    "/auth": auth,
}

print(f"Installed commands: {COMMANDS.keys()}")
print(f"EVERNOTE_SANDBOX_ENABLED: {settings.evernote_sandbox_enabled}")


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
) -> Optional[Callable[[Update, Any], Coroutine[Any, Any, Any]]]:
    if not update.message:
        return None

    command = update.message.text
    assert command

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
