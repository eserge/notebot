import asyncio

from fastapi import FastAPI

from config import get_settings
from domain import process_message, get_message
from entities import Update
from telegram import Telegram


TELEGRAM_API_URL_BASE = f"https://api.telegram.org/bot{get_settings().telegram_token}/"
TELEGRAM_SET_WEBHOOK_URL = f"{TELEGRAM_API_URL_BASE}setWebhook"
WEBHOOK_URL = f"/webhook/{get_settings().get_telegram_token_websafe()}"

settings = get_settings()
telegram = Telegram(settings.telegram_token, settings.telegram_secret)
app = FastAPI()


@app.get("/healthcheck/")
async def healthcheck():
    return {"healthcheck": "OK"}


@app.post(telegram.get_webhook_url())
async def webhook(update: Update):
    message = get_message(update)
    process_message(message)
    return {}
