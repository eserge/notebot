from datetime import datetime as Datetime
from typing import Any

import pytest

from ingest_models import Update, Message, Chat, User
from repo import AbstractRepo


class FakeRepo(AbstractRepo):
    def __init__(self):
        self._data = {}

    def get(self, id: str | int) -> Any:
        id = str(id)
        return self._data.get(id)

    def set(self, obj: Any) -> None:
        id = obj.id
        id = str(id)
        self._data[id] = obj

    def unset(self, id: str | int) -> None:
        id = str(id)
        del self._data[id]

    def exists(self, id: str | int) -> bool:
        return self.get(id) is not None


@pytest.fixture
def users_repo():
    return FakeRepo()


@pytest.fixture
def auth_requests_repo():
    return FakeRepo()


@pytest.fixture
def message_constructor():
    MESSAGE_ID = 1234567890
    CHAT_ID = 9876543210

    def _message_constructor(text=None, from_user=None):
        chat = Chat(id=CHAT_ID, type="private")
        message = Message(
            message_id=MESSAGE_ID,
            date=Datetime.now(),
            text=text,
            chat=chat,
        )
        message.from_user = from_user
        return message

    return _message_constructor


@pytest.fixture
def update_constructor():
    UPDATE_ID = 1234
    # DEFAULT - param=update_contructor.DEFAULT (that is different from None)

    def _update_constructor(update_id=None, message=None):
        if update_id is None:
            update_id = UPDATE_ID

        update = Update(update_id=update_id, message=message)
        return update

    return _update_constructor


@pytest.fixture
def user_constructor():
    ID = 1
    IS_BOT = False
    FIRST_NAME = "Jon Snow"

    def _user_constructor(id=None, is_bot=None, first_name=None):
        if id is None:
            id = ID
        if is_bot is None:
            is_bot = IS_BOT
        if first_name is None:
            first_name = FIRST_NAME

        user = User(id=id, is_bot=is_bot, first_name=first_name)
        return user

    return _user_constructor
