import sys

import uvicorn
from pyngrok import ngrok

from app import APP_HOST, APP_PORT, WEBHOOK_URL, install_webhook


def get_public_url(private_port) -> str:
    tunnel = ngrok.connect(private_port, bind_tls=True)
    public_url = tunnel.public_url
    return public_url


def main():
    public_url = get_public_url(APP_PORT)
    public_webhook_url = f"{public_url}{WEBHOOK_URL}"

    webhook_installed = install_webhook(public_webhook_url)
    if webhook_installed:
        print(f"Webhook is set up on {public_webhook_url}")
        uvicorn.run("app:app", host=APP_HOST, port=APP_PORT, reload=True)

        ngrok.disconnect(public_url)
        print("Exited")
    else:
        print("Failed to set up webbhook")


if __name__ == "__main__":
    sys.exit(main())
