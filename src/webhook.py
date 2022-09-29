import asyncio
import typer

from app import telegram, settings


app = typer.Typer()


@app.command()
def install():
    public_webhook_url = _get_public_webhook_url()
    webhook_installed = asyncio.run(telegram.install_webhook(public_webhook_url))
    if webhook_installed:
        print(f"Webhook is set up on {public_webhook_url}")
        return 0
    else:
        print("Failed to set webbhook")
        return 1


@app.command()
def delete():
    webhook_deleted = asyncio.run(telegram.delete_webhook())
    print("Deleted" if webhook_deleted else "Failed to delete")


@app.command()
def reinstall():
    delete()
    install()


def _get_public_webhook_url() -> str:
    SCHEMA = "https"
    HOST = settings.app_host
    URL = telegram.get_webhook_url()
    return f"{SCHEMA}://{HOST}{URL}"


if __name__ == "__main__":
    app()
