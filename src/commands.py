from evernote.api.client import EvernoteClient

from entities import Update
from config import get_settings


async def ping(update: Update, conns):
    assert update.message is not None
    assert update.message.chat is not None

    PING_RESPONSE = "pong"
    chat = update.message.chat
    return await conns.telegram.send_message(chat.id, PING_RESPONSE)


async def auth(update: Update, conns):
    assert update.message is not None
    assert update.message.chat is not None

    chat = update.message.chat
    settings = get_settings()

    callback_id = "randomToken123"
    callback_url = "http://%s%s" % ("localhost:8000", f"/callback/{callback_id}")

    client = EvernoteClient(
        consumer_key=settings.evernote_consumer_key,
        consumer_secret=settings.evernote_consumer_secret,
        sandbox=True,
    )
    request_token = client.get_request_token(callback_url)
    auth_url = client.get_authorize_url(request_token)

    data = {
        "chat_id": chat.id,
        "oauth_token": request_token["oauth_token"],
        "oauth_token_secret": request_token["oauth_token_secret"],
    }
    conns.storage[callback_id] = data

    AUTH_RESPONSE = (
        f"Auth for chat.id = {chat.id},\n"
        f"Data you'll need: {data},\n\nGo to: {auth_url}"
    )
    return await conns.telegram.send_message(chat.id, AUTH_RESPONSE)
