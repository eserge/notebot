import pytest
from asyncmock import AsyncMock

from domain import save_message_to_note

from models import User


@pytest.fixture
def mock_send_to_evernote(mocker):
    return mocker.patch("domain.send_to_evernote")


@pytest.fixture
def mock_save_to_file(mocker):
    return mocker.patch("domain.save_to_file")


@pytest.fixture
def mock_template(mocker):
    MockTemplate = mocker.MagicMock(
        render_html=mocker.Mock(return_value="rendered html")
    )
    return mocker.patch("models.Template", new=MockTemplate)


@pytest.fixture
def update(update_constructor, user_constructor, message_constructor):
    user = user_constructor()
    message = message_constructor(from_user=user, text="test message")
    update = update_constructor(message=message)
    return update


@pytest.fixture
def message(message_constructor, user_constructor):
    user = user_constructor()
    message = message_constructor(from_user=user, text="test message")
    return message


@pytest.fixture
def user():
    user = User(id="1234567890", auth_token="test_auth_token")
    return user


@pytest.fixture
def adapters(mocker):
    return mocker.MagicMock(telegram=mocker.Mock(send_message=AsyncMock()))


class TestSaveMessageToNote:
    @pytest.mark.asyncio
    async def test_ok(
        self,
        mock_save_to_file,
        mock_send_to_evernote,
        mock_template,
        message,
        user,
        adapters,
    ):
        await save_message_to_note(message, user, adapters=adapters)

        assert mock_save_to_file.called
        assert mock_send_to_evernote.called
