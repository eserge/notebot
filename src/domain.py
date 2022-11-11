from ingest_models import Message
from models import Note, User
from telegram import Telegram
from transport import save_to_file, send_to_evernote


async def save_message_to_note(
    message: Message, user: User, telegram: Telegram
) -> None:
    note = Note.from_message(message)
    save(note, user)
    await confirm_message_saved(message, telegram)


def save(note: Note, user: User) -> None:
    assert user.auth_token

    note_content = note.render_html()
    save_to_file(note_content)
    send_to_evernote(note.header, note_content, user.auth_token)


async def confirm_message_saved(message: Message, telegram: Telegram) -> None:
    assert message.chat is not None

    CONFIRMATION_TEXT = "Saved!"
    chat_id = message.chat.id
    await telegram.send_message(chat_id, CONFIRMATION_TEXT)
