from http import HTTPStatus

import attrs
import httpx


@attrs.define
class Telegram:
    token: str
    secret: str
    http_client: httpx.AsyncClient = attrs.Factory(httpx.AsyncClient)

    API_URL_BASE = "https://api.telegram.org/bot"

    async def delete_webhook(self) -> bool:
        response = await self.http_client.post(self._get_api_delete_webhook_url())

        return response.status_code == HTTPStatus.OK

    async def install_webhook(self, webhook_url: str) -> bool:
        payload = {
            "url": webhook_url,
            "secret_token": self.secret,
        }
        response = await self.http_client.post(
            self._get_api_set_webhook_url(), data=payload
        )

        return response.status_code == HTTPStatus.OK

    async def webhook_info(self):
        response = await self.http_client.post(self._get_api_set_webhook_url())

        return response

    async def send_message(self, chat_id: str | int, text: str) -> bool:
        response = await self.http_client.post(
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
