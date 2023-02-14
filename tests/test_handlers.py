from unittest.mock import AsyncMock, call
import pytest
from handlers import webhook_handler
from models import User


TEST_USER = User(id="test_user_id", auth_token="test_auth_token")


@pytest.fixture
def users():
    return {"test_user_id": TEST_USER}


@pytest.fixture
def mock_save_message_to_note(mocker):
    return mocker.patch("handlers.save_message_to_note")


@pytest.fixture
def update_text_message(mocker, update_constructor, message_constructor):
    from_user = mocker.MagicMock(id="test_user_id")
    message = message_constructor(text="test text message", from_user=from_user)
    update = update_constructor(message=message)
    return update


@pytest.fixture
def state(mocker):
    return mocker.MagicMock(telegram=mocker.Mock(send_message=AsyncMock()))


class TestWebhookHandler:
    @pytest.mark.asyncio
    async def test_handle_text_message(
        self, mock_save_message_to_note, update_text_message, users, state
    ):
        expected_message = update_text_message.message
        telegram = state.telegram

        await webhook_handler(update_text_message, users, state)

        assert mock_save_message_to_note.awaited_once_with(
            call(expected_message, TEST_USER, telegram)
        )
