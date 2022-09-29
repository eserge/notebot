import asyncio
from http import HTTPStatus

import attrs
import httpx


@attrs.define
class Telegram:
    token: str
    secret: str

    API_URL_BASE = "https://api.telegram.org/bot"

    async def delete_webhook(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(self._get_api_delete_webhook_url())

        return response.status_code == HTTPStatus.OK

    async def install_webhook(self, webhook_url: str) -> bool:
        payload = {
            "url": webhook_url,
            "secret_token": self.secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self._get_api_set_webhook_url(), data=payload)

        return response.status_code == HTTPStatus.OK

    async def webhook_info(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(self._get_api_set_webhook_url())

        return response

    async def send_message(self, chat_id, text) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_api_send_message_url(),
                data={"text": text, "chat_id": chat_id},
            )

        return response.status_code == HTTPStatus.OK

    def _get_api_url_base(self) -> str:
        return f"{self.API_URL_BASE}{self.token}/"

    def _get_api_set_webhook_url(self) -> str:
        return f"{self._get_api_url_base()}setWebhook"

    def _get_api_delete_webhook_url(self) -> str:
        return f"{self._get_api_url_base()}deleteWebhook"

    def _get_api_webhook_info_url(self) -> str:
        return f"{self._get_api_url_base()}getWebhookInfo"

    def _get_api_send_message_url(self) -> str:
        return f"{self._get_api_url_base()}sendMessage"

    def get_webhook_url(self) -> str:
        return f"/webhook/{self._get_token_websafe()}"

    def _get_token_websafe(self) -> str:
        return self.token.replace(":", "/")
