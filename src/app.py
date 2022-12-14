import os
import traceback
from typing import Any, Callable, Coroutine, Optional

import pickledb
import sentry_sdk
from fastapi import FastAPI, Request
from starlette.datastructures import State

from commands import auth, ping
from config import get_settings
from domain import save_message_to_note
from ingest_models import Message, Update
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


def state_constructor(app: FastAPI) -> Callable:
    state = app.state

    def initialize_state():
        db = pickledb.load(
            os.path.join(settings.app_data_dir, settings.app_data_filename),
            auto_dump=True,
        )

        state.settings = settings
        state.telegram = Telegram(settings.telegram_token, settings.telegram_secret)
        state.users = Users(db=db)
        state.auth_requests = AuthRequests(db=db)

    return initialize_state


app = FastAPI()
app.include_router(router)
app.add_event_handler("startup", state_constructor(app))


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


@app.post(settings.get_webhook_url())
async def webhook(update: Update, request: Request):
    try:
        state = request.app.state
        message = _get_message(update)
        if not message:
            raise IncompatibleUpdateFormat

        user = get_user_from_message(message, state.users)

        command_handler = dispatch_command(message)
        if command_handler:
            await command_handler(message, user, state)
        else:
            await message_handler(message, user, state)
    except IncompatibleUpdateFormat:
        print("Application needs data missing in the Update object")
        sentry_sdk.capture_exception()
    except Exception:
        # Silence all exceptions to avoid retries on the webhook
        sentry_sdk.capture_exception()
        print(traceback.format_exc())
    finally:
        # If we return anything except OK, webhook will be spammed with retries
        return {}


def dispatch_command(
    message: Message,
) -> Optional[Callable[[Message, Any, Any], Coroutine[Any, Any, Any]]]:
    command = _get_command(message)
    if not command:
        return None

    print(command)
    return get_commands()[command]


async def message_handler(message: Message, user: User, state: State):
    if user.is_authorized:
        await handle_message(message, user, state)
    else:
        state.telegram.send_message(user.id, "Unauthorized, type: /auth")


async def handle_message(message: Message, user: User, state: State) -> None:
    telegram = state.telegram
    await save_message_to_note(message, user, telegram)


def get_user_from_message(message: Message, users: Users) -> User:
    user_id = str(get_user_id_from_message(message))
    user = get_user_by_id(user_id, users)
    if user:
        return user

    return User(user_id, auth_token=None)


def get_user_id_from_message(message: Message) -> int:
    if not message.from_user:
        raise IncompatibleUpdateFormat
    assert message.from_user

    user_id = message.from_user.id
    return user_id


def get_user_by_id(id: str, users: Users) -> Optional[User]:
    user = users.get(id)
    return user


def _get_message(update: Update) -> Optional[Message]:
    return update.message


def _get_command(message: Message) -> Optional[str]:
    print(message)
    # command is a text-only message
    if not message.text:
        return None

    command = message.text
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
