from entities import Message, Update
from models import MessageChain, Note


def get_message(update: Update) -> Message:
    return update.message


def process_message(message: Message) -> None:
    mc = MessageChain()
    mc.attempt_to_append(message)
    note = Note(mc)
    sendNote(note)


def sendNote(note: Note) -> None:
    print(note)
