import json

from typing import Deque

import attrs
from collections import deque
from entities import Message, Update

from utils import JsonDumps


@attrs.define
class MessageChain:
    chain: Deque[Message] = attrs.field(default=deque())

    def _check_message_inclusion(self, message: Message):
        return True

    def attempt_to_append(self, message: Message):
        if self._check_message_inclusion(message):
            self.chain.append(message)

    def __repr__(self) -> str:
        selfstring = "<MessageChain>\n"
        for message in self.chain:
            selfstring += "<Message>\n"
            selfstring += json.dumps(dict(message), cls=JsonDumps, indent=2)
            selfstring += "</Message>"
        selfstring += "</MessageChain>"
        return selfstring


@attrs.define
class Note:
    chain: MessageChain
