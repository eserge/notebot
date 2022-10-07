import attrs
from fastapi import FastAPI

from repo import AuthRequests, Users
from telegram import Telegram


class ImproperlyConfigured(Exception):
    pass


@attrs.define
class Adapters:
    app: FastAPI
    telegram: Telegram
    users: Users
    auth_requests: AuthRequests


_adapters = None


def init_adapters(*, app, telegram, users, auth_requests):
    global _adapters
    _adapters = Adapters(
        app=app, telegram=telegram, users=users, auth_requests=auth_requests
    )


def get_adapters():
    global _adapters
    if not _adapters:
        raise ImproperlyConfigured

    return _adapters
