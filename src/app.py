import os
import traceback
from typing import Callable

import pickledb
import sentry_sdk
from fastapi import FastAPI, Request
from telegram import Update

from config import get_settings
from exceptions import IncompatibleUpdateFormat
from handlers import webhook_handler
from repo import AuthRequests, Users
from tclient import Telegram
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


print(f"EVERNOTE_SANDBOX_ENABLED: {settings.evernote_sandbox_enabled}")


# @app.post(settings.get_webhook_url())
# async def webhook(request: Request):
#     try:
#         breakpoint()
#         data = await request.json()
#         update = Update(**data)
#         await webhook_handler(update, request.app.state.users, request.app.state)
#     except IncompatibleUpdateFormat:
#         print("Application needs data missing in the Update object")
#         sentry_sdk.capture_exception()
#     except Exception:
#         # Silence all exceptions to avoid retries on the webhook
#         sentry_sdk.capture_exception()
#         print(traceback.format_exc())
#     finally:
#         # If we return anything except OK, webhook will be spammed with retries
#         return {}
