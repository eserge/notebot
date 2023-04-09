import secrets

from evernote.api.client import EvernoteClient
from starlette.datastructures import State
from telegram import Message, Update
from telegram.ext import ContextTypes

from config import Settings, get_settings
from models import AuthRequest, User

TOKEN_LENGTH = 16
PING_RESPONSE = "pong"


async def ping(message: Message, user: User, state: State):
    assert message.chat is not None

    chat = message.chat
    return await state.telegram.send_message(chat.id, PING_RESPONSE)


async def auth(message: Message, user: User, state: State):
    assert message.chat is not None
    assert message.from_user is not None

    chat = message.chat
    settings = get_settings()

    callback_id = generate_token()
    callback_url = get_callback_url(callback_id, settings)

    client = EvernoteClient(
        consumer_key=settings.evernote_consumer_key,
        consumer_secret=settings.evernote_consumer_secret,
        sandbox=settings.evernote_sandbox_enabled,
    )
    request_token = client.get_request_token(callback_url)
    auth_url = client.get_authorize_url(request_token)

    data = {
        "id": callback_id,
        "chat_id": chat.id,
        "user_id": user.id,
        "oauth_token": request_token["oauth_token"],
        "oauth_token_secret": request_token["oauth_token_secret"],
    }
    auth_request = AuthRequest(**data)
    state.auth_requests.set(auth_request)

    AUTH_RESPONSE = (
        f"Starting authentication process.\n"
        f"Please open this link to confirm Evernote access: {auth_url}"
    )
    return await state.telegram.send_message(chat.id, AUTH_RESPONSE)


def generate_token():
    return secrets.token_urlsafe(TOKEN_LENGTH)


def get_callback_url(callback_id: str, settings: Settings):
    production = False if settings.app_host == "localhost" else True
    schema = "https" if production else "http"
    host = settings.app_host
    port = "" if production else f":{settings.app_port}"

    return f"{schema}://{host}{port}/callback/{callback_id}"


class TelegramCommands:
    @staticmethod
    async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
        breakpoint()
        settings = get_settings()
        callback_id = generate_token()
        callback_url = get_callback_url(callback_id, settings)

        client = EvernoteClient(
            consumer_key=settings.evernote_consumer_key,
            consumer_secret=settings.evernote_consumer_secret,
            sandbox=settings.evernote_sandbox_enabled,
        )
        request_token = client.get_request_token(callback_url)
        auth_url = client.get_authorize_url(request_token)

        auth_response = (
            f"Starting authentication process.\n"
            f"Please open this link to confirm Evernote access: {auth_url}"
        )

        context.user_data["auth_request"] = AuthRequest(
            id=callback_id,
            chat_id=update.effective_chat.id,
            user_id=update.effective_user.id,
            oauth_token=request_token["oauth_token"],
            oauth_token_secret=request_token["oauth_token_secret"],
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=auth_response
        )

    @staticmethod
    async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=PING_RESPONSE
        )
