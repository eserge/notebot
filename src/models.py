from typing import Deque, List

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
    def get_text(messages: Messages) -> str:
        message = messages[0]
        if message.text:
            return message.text
        if message.caption:
            return message.caption

    @staticmethod
    def get_photos():
        return


class Note:
    messages: Messages

    def __init__(self, chain: MessageChain) -> None:
        self.messages = list(chain.chain)
        self.adapter = MessageAdapter

    @property
    def text(self) -> str:
        return self.adapter.get_text(self.messages)
