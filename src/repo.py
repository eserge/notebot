import abc
from typing import Optional

import attrs
from pickledb import PickleDB
from telegram.ext import BasePersistence

from models import AuthRequest, User


class AbstractRepo(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str):
        ...

    @abc.abstractmethod
    def set(self, *args, **kwargs) -> None:
        ...


class PickleDBRepo(AbstractRepo):
    _namespace: str

    def __init__(self, *, db: PickleDB) -> None:
        self.db = db

    def _get_key(self, key: str) -> str:
        return f"{self._namespace}{key}"

    @abc.abstractmethod
    def get(self, key: str):
        ...

    @abc.abstractmethod
    def set(self, data) -> None:
        ...


class Users(PickleDBRepo):
    _namespace = "user:"

    def get(self, id: str) -> Optional[User]:
        key = self._get_key(id)
        user_data = self.db.get(key)
        if not user_data:
            return None
        return User(**user_data)

    def set(self, user: User) -> None:
        key = self._get_key(user.id)
        self.db.set(key, attrs.asdict(user))

    def exists(self, id: str) -> bool:
        key = self._get_key(id)
        return self.db.exists(key)


class AuthRequests(PickleDBRepo):
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


def get_user_by_id(id: str, users: Users) -> Optional[User]:
    user = users.get(id)
    return user


class PTBUsers(AbstractRepo):
    def __init__(self, *, db: BasePersistence) -> None:
        self._db = db

    def get(self, id: str) -> Optional[User]:
        pass

    def set(self, user: User) -> None:
        pass

    def exists(self, id: str) -> bool:
        pass
