import asyncio
import sys
from http import HTTPStatus
from os import environ

import httpx
import uvicorn
from fastapi import FastAPI, Request
from pyngrok import ngrok

# from pyteledantic.models import Update

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
    print(await request.body())
    return {"msg": "Thank you for your update"}


def main():
    tunnel = ngrok.connect(APP_PORT, bind_tls=True)
    public_url = tunnel.public_url
    public_webhook_url = f"{public_url}{WEBHOOK_URL}"

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(set_webhook(public_webhook_url))
    if result:
        print(f"Webhook set up on {public_webhook_url}")
        uvicorn.run(app, host=APP_HOST, port=APP_PORT)

        ngrok.disconnect(tunnel.public_url)
        print("Exited")
    else:
        print("Failed to set up webbhook")


async def set_webhook(webhook_url: str):
    payload = {
        "url": webhook_url,
        "secret_token": TELEGRAM_SECRET,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TELEGRAM_SET_WEBHOOK_URL, data=payload)

    return response.status_code == HTTPStatus.OK


if __name__ == "__main__":
    sys.exit(main())
