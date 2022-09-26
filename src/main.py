import sys

import uvicorn
from pyngrok import ngrok, conf

from app import telegram, settings


def get_public_url(private_port, *, ngrok_bin_path) -> str:
    # pyngrok_config = conf.PyngrokConfig(ngrok_path=ngrok_bin_path)
    pyngrok_config = conf.get_default()
    pyngrok_config.ngrok_path = ngrok_bin_path
    tunnel = ngrok.connect(private_port, bind_tls=True, pyngrok_config=pyngrok_config)
    public_url = tunnel.public_url
    return public_url


def main():
    public_url = get_public_url(
        settings.app_port, ngrok_bin_path=settings.ngrok_bin_path
    )
    webhook_url = telegram.get_webhook_url()
    public_webhook_url = f"{public_url}{webhook_url}"

    webhook_installed = telegram.install_webhook(public_webhook_url)
    if webhook_installed:
        print(f"Webhook is set up on {public_webhook_url}")
        uvicorn.run(
            "app:app", host=settings.app_host, port=settings.app_port, reload=True
        )

        ngrok.disconnect(public_url)
        print("Exited")
        return 0
    else:
        print("Failed to set up webbhook")
        return 1


if __name__ == "__main__":
    sys.exit(main())
