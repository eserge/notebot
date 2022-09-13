import asyncio
from http import HTTPStatus

import httpx
from fastapi import FastAPI

from config import get_settings
from domain import process_message, get_message
from entities import Update


TELEGRAM_API_URL_BASE = f"https://api.telegram.org/bot{get_settings().telegram_token}/"
TELEGRAM_SET_WEBHOOK_URL = f"{TELEGRAM_API_URL_BASE}setWebhook"
WEBHOOK_URL = f"/webhook/{get_settings().get_telegram_token_websafe()}"

settings = get_settings()
app = FastAPI()


@app.get("/healthcheck/")
async def healthcheck():
    return {"healthcheck": "OK"}


@app.post(WEBHOOK_URL)
async def webhook(update: Update):
    message = get_message(update)
    process_message(message)
    return {}


def install_webhook(public_webhook_url):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(request_webhook(public_webhook_url))
    return result


async def request_webhook(webhook_url: str):
    payload = {
        "url": webhook_url,
        "secret_token": settings.telegram_secret,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TELEGRAM_SET_WEBHOOK_URL, data=payload)

    return response.status_code == HTTPStatus.OK
