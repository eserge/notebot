import json

from typing import Deque

import attrs
from collections import deque
from entities import Message


@attrs.define
class MessageChain:
    chain: Deque[Message] = attrs.field(default=deque())

    def _check_message_inclusion(self, message: Message):
        return True

    def attempt_to_append(self, message: Message):
        if self._check_message_inclusion(message):
            self.chain.append(message)


@attrs.define
class Note:
    chain: MessageChain
