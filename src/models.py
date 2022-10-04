import re
from typing import Any, Deque, Dict, List, Optional

import attrs

from collections import deque
from entities import Message, MessageEntity

Messages = List[Message]
Link = Dict[str, Optional[str]]


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
    LINK_ENTITY_TYPE = "text_link"
    MAX_HEADER_LENGTH = 50

    @staticmethod
    def get_text(messages: Messages) -> List[str | Any]:
        message = messages[0]
        if message.text:
            text = message.text
        elif message.caption:
            text = message.caption

        return MessageAdapter.parse_text(text)

    @staticmethod
    def parse_text(text: str) -> List[str | Any]:
        # split text into paragraphs, denoted
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

    @staticmethod
    def links(messages: Messages) -> List[Link]:
        message = messages[0]
        entities = None
        print(message)
        if message.entities or message.caption_entities:
            entities = message.entities or message.caption_entities

        if not entities:
            return []

        if message.text or message.caption:
            text = message.text or message.caption

        entity_objects = [MessageEntity(**ent) for ent in iter(entities)]

        return [
            {"url": entity.url, "text": MessageAdapter.get_link_text(entity, text)}
            for entity in entity_objects
            if entity.type == MessageAdapter.LINK_ENTITY_TYPE and entity.url
        ]

    @staticmethod
    def get_link_text(entity: MessageEntity, message: Optional[str]) -> Optional[str]:
        if not message:
            return entity.url
        return message[entity.offset : entity.offset + entity.length]

    @staticmethod
    def get_header(messages: Messages) -> str:
        texts = MessageAdapter.get_text(messages)
        return texts[0][: MessageAdapter.MAX_HEADER_LENGTH].split("\n")[0]


class Note:
    """
    An abstract representation of a note.
    Text consisting of a list of paragraphs,
    Header,
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
    def message_link(self) -> Optional[str]:
        return self.adapter.get_link(self.messages)

    @property
    def id(self) -> int:
        return self.adapter.get_id(self.messages)

    @property
    def links(self) -> List[Link]:
        return self.adapter.links(self.messages)

    @property
    def header(self) -> str:
        return self.adapter.get_header(self.messages)


@attrs.define
class User:
    id: str
    auth_token: Optional[str]

    def is_authenticated(self):
        return self.auth_token is not None
