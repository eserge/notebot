import secrets

from evernote.api.client import EvernoteClient

from entities import Update
from config import get_settings, Settings


TOKEN_LENGTH = 16


async def ping(update: Update, adapters):
    assert update.message is not None
    assert update.message.chat is not None

    PING_RESPONSE = "pong"
    chat = update.message.chat
    return await adapters.telegram.send_message(chat.id, PING_RESPONSE)


async def auth(update: Update, adapters):
    assert update.message is not None
    assert update.message.chat is not None
    assert update.message.from_user is not None

    chat = update.message.chat
    user = update.message.from_user
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
        "chat_id": chat.id,
        "user_id": user.id,
        "oauth_token": request_token["oauth_token"],
        "oauth_token_secret": request_token["oauth_token_secret"],
    }
    adapters.auth_requests.set(callback_id, data)

    AUTH_RESPONSE = (
        f"Starting authentication process.\n"
        f"Please open this link to confirm Evernote access: {auth_url}"
    )
    return await adapters.telegram.send_message(chat.id, AUTH_RESPONSE)


def generate_token():
    return secrets.token_urlsafe(TOKEN_LENGTH)


def get_callback_url(callback_id: str, settings: Settings):
    production = False if settings.app_host == "localhost" else True
    schema = "https" if production else "http"
    host = settings.app_host
    port = "" if production else f":{settings.app_port}"

    return f"{schema}://{host}{port}/callback/{callback_id}"
