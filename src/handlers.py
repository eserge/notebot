from typing import Any, Callable, Coroutine, Optional

from starlette.datastructures import State
from telegram import Message, Update

from commands import auth, ping
from domain import save_message_to_note
from exceptions import IncompatibleUpdateFormat

# from ingest_models import Message, Update
from models import User
from repo import Users, get_user_by_id

_COMMANDS = {}  # type: ignore


def get_commands() -> dict:
    global _COMMANDS
    if not _COMMANDS:
        _COMMANDS = {
            "/ping": ping,
            "/auth": auth,
        }

    # print(f"Installed commands: {_COMMANDS.keys()}")
    return _COMMANDS


async def webhook_handler(update: Update, users: Users, state: State) -> None:
    message = _get_message(update)
    if not message:
        return

    user = get_user_from_message(message, users)
    command = dispatch_command(message)
    if command:
        await command(message, user, state)
    else:
        await message_handler(message, user, state)


def _get_message(update: Update) -> Optional[Message]:
    return update.message


def get_user_from_message(message: Message, users: Users) -> User:
    user_id = str(get_user_id_from_message(message))
    user = get_user_by_id(user_id, users)
    if user:
        return user

    return User(user_id, auth_token=None)


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


def get_user_id_from_message(message: Message) -> int:
    if not message.from_user:
        raise IncompatibleUpdateFormat
    assert message.from_user

    user_id = message.from_user.id
    return user_id


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
