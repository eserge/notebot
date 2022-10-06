from email import message
import pytest
from datetime import datetime as Datetime
from entities import Chat, Message
from models import MessageAdapter


@pytest.fixture
def message_constuctor():
    MESSAGE_ID = 1234567890
    CHAT_ID = 9876543210

    def _message_constructor(text=None):
        chat = Chat(id=CHAT_ID, type="private")
        message = Message(
            message_id=MESSAGE_ID, date=Datetime.now(), text=text, chat=chat
        )
        return message

    return _message_constructor


class TestMessageAdapter:
    def test_trim_wrong_characters_from_header(self, message_constuctor):
        text = "\u200bA test title to be trimmed  \n\nnext line"
        msg = message_constuctor(text=text)
        expected_title = "A test title to be trimmed"

        title = MessageAdapter.get_header([msg])

        assert title == expected_title
