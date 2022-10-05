import abc
from typing import Optional

import attrs
from pickledb import PickleDB

from entities import Update
from models import AuthRequest, User


class AbstractRepo(abc.ABC):
    _namespace = "user:"

    def __init__(self, *, db: PickleDB) -> None:
        self.db = db

    def _get_key(self, key: str) -> str:
        return f"{self._namespace}{key}"

    def get(self, key: str):
        ...

    def set(self, key: str, data):
        ...


class Users(AbstractRepo):
    _namespace = "user:"

    def get(self, user_id) -> Optional[User]:
        key = self._get_key(user_id)
        user_data = self.db.get(key)
        if not user_data:
            return None
        return User(**user_data)

    def set(self, user_id, user: User) -> None:
        key = self._get_key(user_id)
        data = {
            "id": user.id,
            "auth_token": user.auth_token,
        }
        self.db.set(key, data)

    def exists(self, user_id) -> bool:
        key = self._get_key(user_id)
        return self.db.exists(key)

    def create_user(self, user_id, auth_token) -> User:
        return User(user_id, auth_token)


class AuthRequests(AbstractRepo):
    _namespace = "auth:"

    def get(self, id: str) -> Optional[AuthRequest]:
        key = self._get_key(id)
        data = self.db.get(key)
        return AuthRequest(**data)

    def set(self, auth_request: AuthRequest) -> None:
        key = self._get_key(auth_request.id)
        self.db.set(key, attrs.asdict(auth_request))

    def unset(self, id: str) -> None:
        key = self._get_key(id)
        self.db.rem(key)


def get_user_from_update(update: Update, users: Users) -> Optional[User]:
    assert update.message
    assert update.message.from_user

    user_id = str(update.message.from_user.id)
    user = users.get(user_id)
    return user
