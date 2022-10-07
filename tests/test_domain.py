import pytest

from domain import process_update, NotAuthorized
from entities import Update
from models import User


@pytest.fixture
def mock_send_to_evernote(mocker):
    return mocker.patch("domain.send_to_evernote")


@pytest.fixture
def mock_save_to_file(mocker):
    return mocker.patch("domain.save_to_file")


@pytest.fixture
def mock_render_html(mocker):
    return mocker.patch("domain.render_html")


@pytest.fixture
def update(update_constructor, user_constructor, message_constructor):
    user = user_constructor()
    message = message_constructor(from_user=user, text="test message")
    update = update_constructor(message=message)
    return update


@pytest.fixture
def update_w_empty_message(update_constructor):
    update = update_constructor(message=None)
    return update


class TestProcessUpdate:
    def test_ok(
        self,
        mock_render_html,
        mock_save_to_file,
        mock_send_to_evernote,
        users_repo,
        update,
    ):
        TEST_TOKEN = "test_token"
        user = update.message.from_user
        users_repo.set(User(id=user.id, auth_token=TEST_TOKEN))

        process_update(update, users_repo)
        assert mock_save_to_file.called
        assert mock_send_to_evernote.called

    def test_missing_message(
        self,
        users_repo,
        update_w_empty_message,
        mock_save_to_file,
        mock_send_to_evernote,
    ):
        with pytest.raises(NotAuthorized):
            process_update(update_w_empty_message, users_repo)

        assert not mock_save_to_file.called
        assert not mock_send_to_evernote.called

    def test_missing_user(
        self,
        users_repo,
        update,
        mock_save_to_file,
        mock_send_to_evernote,
    ):
        with pytest.raises(NotAuthorized):
            process_update(update, users_repo)

        assert not mock_save_to_file.called
        assert not mock_send_to_evernote.called
