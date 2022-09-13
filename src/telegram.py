import asyncio
from http import HTTPStatus

import attrs
import httpx


@attrs.define
class Telegram:
    token: str
    secret: str

    API_URL_BASE = "https://api.telegram.org/bot"

    def install_webhook(self, public_webhook_url) -> bool:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self._request_webhook(public_webhook_url))
        return result

    async def _request_webhook(self, webhook_url: str) -> bool:
        payload = {
            "url": webhook_url,
            "secret_token": self.secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self._get_api_set_webhook_url(), data=payload)

        return response.status_code == HTTPStatus.OK

    def _get_api_url_base(self):
        return f"{self.API_URL_BASE}{self.token}/"

    def _get_api_set_webhook_url(self):
        return f"{self._get_api_url_base()}setWebhook"

    def get_webhook_url(self) -> str:
        return f"/webhook/{self._get_token_websafe()}"

    def _get_token_websafe(self) -> str:
        return self.token.replace(":", "/")
