import asyncio
import sys

import uvicorn
import typer
from pyngrok import ngrok

from app import telegram, settings


app = typer.Typer()


def get_public_url(private_port) -> str:
    tunnel = ngrok.connect(private_port, bind_tls=True)
    public_url = tunnel.public_url
    return public_url


def install_webhook(port: int) -> str:
    public_url = get_public_url(port)
    webhook_url = telegram.get_webhook_url()
    public_webhook_url = f"{public_url}{webhook_url}"
    installed = asyncio.run(telegram.install_webhook(public_webhook_url))
    return public_webhook_url if installed else ""


@app.command()
def run(set_webhook: bool = False):
    if set_webhook:
        public_url = install_webhook(port=settings.app_port)
        if public_url:
            print(f"Webhook is set up on {public_url}")
        else:
            print("Failed to set up webbhook")
            return 1

    uvicorn.run("app:app", host=settings.app_host, port=settings.app_port, reload=True)

    if set_webhook:
        ngrok.disconnect(public_url)
        print("Ngrok dropped")

    return 0


if __name__ == "__main__":
    app()