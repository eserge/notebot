import re
from typing import Deque, List, Optional

import attrs
from collections import deque
from entities import Message

Messages = List[Message]


@attrs.define
class MessageChain:
    chain: Deque[Message] = attrs.field(factory=deque)

    def attempt_to_append(self, message: Message) -> bool:
        if self._check_message_affiliation(message):
            self.chain.append(message)
            return True
        return False

    def _check_message_affiliation(self, message: Message) -> bool:
        return True


class MessageAdapter:
    @staticmethod
    def get_text(messages: Messages) -> List[str]:
        message = messages[0]
        if message.text:
            text = message.text
        if message.caption:
            text = message.caption

        return MessageAdapter.parse_text(text)

    @staticmethod
    def parse_text(text: str) -> List[str]:
        # split text into paragraphs, where they're denoted
        # by a sequence of 2 or more \n chars
        paragraphs = re.split("\n{2,}", text)
        return paragraphs

    @staticmethod
    def get_link(messages: Messages) -> Optional[str]:
        message = messages[0]
        if not message.forward_from_chat:
            return None
        if not message.forward_from_chat.username:
            return None
        if not message.forward_from_message_id:
            return None

        chat_name = message.forward_from_chat.username
        message_id = message.forward_from_message_id
        return f"https://t.me/{chat_name}/{message_id}"

    @staticmethod
    def get_id(messages: Messages) -> int:
        message = messages[0]
        return message.message_id


class Note:
    """
    An abstract representation of a note.
    Text consisting of a list of paragraphs.
    Attached files and photos
    """

    messages: Messages

    def __init__(self, chain: MessageChain) -> None:
        self.messages = list(chain.chain)
        self.adapter = MessageAdapter

    @property
    def text(self) -> List[str]:
        return self.adapter.get_text(self.messages)

    @property
    def message_link(self) -> str:
        return self.adapter.get_link(self.messages)

    @property
    def id(self) -> int:
        return self.adapter.get_id(self.messages)
