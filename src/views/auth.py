import attrs
from evernote.api.client import EvernoteClient
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from mako.template import Template

from models import User

auth_router = APIRouter()


@auth_router.get("/callback/{callback_id}", response_class=HTMLResponse)
async def callback(
    callback_id: str,
    request: Request,
    oauth_token: str | None = None,
    oauth_verifier: str | None = None,
    sandbox_lnb: bool | None = None,
):
    state = request.app.state
    settings = state.settings
    if not oauth_verifier:
        # If oauth_verifier is missing, user chose not to
        # authorize our bot, or something went wrong
        return Template(filename="tpl/auth_fail.mako").render()

    callback_data = {
        "callback_id": callback_id,
        "oauth_token": oauth_token,
        "oauth_verifier": oauth_verifier,
        "sandbox_lnb": sandbox_lnb,
    }

    if auth_request := state.auth_requests.get(callback_id):
        user_id = auth_request.user_id
        print(attrs.asdict(auth_request), callback_data)

        try:
            client = EvernoteClient(
                consumer_key=settings.evernote_consumer_key,
                consumer_secret=settings.evernote_consumer_secret,
                sandbox=settings.evernote_sandbox_enabled,
            )
            access_token = client.get_access_token(
                oauth_token=auth_request.oauth_token,
                oauth_token_secret=auth_request.oauth_token_secret,
                oauth_verifier=oauth_verifier,
            )
        except KeyError:
            return Template(filename="tpl/auth_fail.mako").render()

        evernote_user = client.get_user_store().getUser()
        await state.telegram.send_message(
            auth_request.chat_id,
            f"Hello, {evernote_user.username}!\nYou have been authorized",
        )

        user = User(id=user_id, auth_token=access_token)
        state.users.set(user)
        state.auth_requests.unset(callback_id)

        return Template(filename="tpl/auth_success.mako").render()

    return Template(filename="tpl/auth_fail.mako").render()
