from adapters import Adapters
from entities import Message
from models import Note, User
from transport import save_to_file, send_to_evernote


async def save_message_to_note(message: Message, user: User, adapters):
    note = Note.from_message(message)
    save(note, user)
    await confirm_message_saved(message, adapters)


def save(note: Note, user: User) -> None:
    assert user.auth_token

    note_content = note.render_html()
    save_to_file(note_content)
    send_to_evernote(note.header, note_content, user.auth_token)


async def confirm_message_saved(message: Message, adapters: Adapters):
    assert message.chat is not None

    CONFIRMATION_TEXT = "Saved!"
    chat_id = message.chat.id
    await adapters.telegram.send_message(chat_id, CONFIRMATION_TEXT)
