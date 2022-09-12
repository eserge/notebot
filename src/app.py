import asyncio
import json
from http import HTTPStatus
from os import environ

import httpx
from fastapi import FastAPI, Request


app = FastAPI()

TELEGRAM_TOKEN = environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("Token is required, exiting!")
    exit(1)

TELEGRAM_SECRET = environ.get("TELEGRAM_SECRET")
if not TELEGRAM_SECRET:
    print("TELEGRAM_SECRET is required, exiting!")
    exit(1)
TELEGRAM_TOKEN_WEBSAFE = TELEGRAM_TOKEN.replace(":", "/")

NGROK_TOKEN = environ.get("NGROK_TOKEN")
if not NGROK_TOKEN:
    print("NGROK_TOKEN is required, exiting!")
    exit(1)

APP_HOST = "localhost"
APP_PORT = 8000
APP_DEV_MODE = True
TELEGRAM_API_URL_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"
TELEGRAM_SET_WEBHOOK_URL = f"{TELEGRAM_API_URL_BASE}setWebhook"
WEBHOOK_URL = f"/webhook/{TELEGRAM_TOKEN_WEBSAFE}"


@app.get("/healthcheck/")
async def healthcheck():
    return {"healthcheck": "OK"}


@app.post(WEBHOOK_URL)
async def webhook(request: Request):
    data = await request.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return {}


def install_webhook(public_webhook_url):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(set_webhook(public_webhook_url))
    return result


async def set_webhook(webhook_url: str):
    payload = {
        "url": webhook_url,
        "secret_token": TELEGRAM_SECRET,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TELEGRAM_SET_WEBHOOK_URL, data=payload)

    return response.status_code == HTTPStatus.OK
