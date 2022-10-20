import os
import traceback
from typing import Any, Callable, Coroutine, Optional

import pickledb
import sentry_sdk
from fastapi import FastAPI

from adapters import get_adapters, init_adapters
from commands import auth, ping
from config import get_settings
from domain import save_message_to_note
from entities import Message, Update
from models import User
from repo import AuthRequests, Users
from telegram import Telegram
from views import router

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
app.include_router(router)
init_adapters(app=app, telegram=telegram, users=users, auth_requests=auth_requests)


_COMMANDS = {}  # type: ignore


def get_commands() -> dict:
    global _COMMANDS
    if not _COMMANDS:
        _COMMANDS = {
            "/ping": ping,
            "/auth": auth,
        }

    return _COMMANDS


print(f"Installed commands: {get_commands().keys()}")
print(f"EVERNOTE_SANDBOX_ENABLED: {settings.evernote_sandbox_enabled}")


class NotAuthorized(Exception):
    pass


class IncompatibleUpdateFormat(Exception):
    pass


@app.post(telegram.get_webhook_url())
async def webhook(update: Update):
    try:
        adapters = get_adapters()
        user = get_user_from_update(update, adapters.users)
        command_handler = dispatch_command(update)
        if command_handler:
            await command_handler(update, adapters)
        else:
            await update_handler(update, user, adapters)
    except IncompatibleUpdateFormat:
        print("Application needs data missing in the Update object")
    except Exception:
        # Silence all exceptions
        print("TODO: Send to Sentry")
        print(traceback.format_exc())
    finally:
        # If we return anything except OK, webhook will be spammed with retries
        return {}


def dispatch_command(
    update: Update,
) -> Optional[Callable[[Update, Any], Coroutine[Any, Any, Any]]]:
    command = _get_command(update)
    if not command:
        return None

    print(command)
    return get_commands()[command]


async def update_handler(update, user, adapters):
    message = _get_message(update)
    if not message:
        raise IncompatibleUpdateFormat

    if user.is_authorized:
        await handle_update(update, user, adapters)
    else:
        adapters.telegram.send_message(user.id)


async def handle_update(update: Update, user: User, adapters) -> None:
    await save_message_to_note(update, user, adapters)


def get_user_from_update(update: Update, users: Users) -> User:
    user_id = str(get_user_id_from_update(update))
    user = get_user_by_id(user_id, users)
    if user:
        return user

    return User(user_id, auth_token=None)


def get_user_id_from_update(update: Update) -> int:
    if not update.message:
        raise IncompatibleUpdateFormat
    if not update.message.from_user:
        raise IncompatibleUpdateFormat

    assert update.message
    assert update.message.from_user

    user_id = update.message.from_user.id
    return user_id


def get_user_by_id(id: str, users: Users) -> Optional[User]:
    user = users.get(id)
    return user


def _get_message(update: Update) -> Optional[Message]:
    return update.message


def _get_command(update: Update) -> Optional[str]:
    print(update)
    if not update.message:
        return None

    # command is a text-only message
    if not update.message.text:
        return None

    command = update.message.text
    if _is_supported_command(command):
        return command

    return None


def _is_supported_command(command: str) -> bool:
    # Command if it's a oneliner starting with "/"
    # And it is declared in COMMANDS
    if not command.startswith("/"):
        return False
    unslash = command[1:]
    if not unslash.isalnum():
        return False
    if command.count("\n") > 0:
        return False

    return command in get_commands()
