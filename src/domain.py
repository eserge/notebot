from typing import Any, Dict

from mako.template import Template

from adapters import Adapters
from entities import Message, Update
from models import MessageChain, Note, User
from transport import save_to_file, send_to_evernote


def _(message) -> str:
    return message


_MESSAGES = {"NotAuthorized": _("Please authorize first by entering `/auth` command")}


async def save_message_to_note(update: Update, user: User, adapters):
    message = receive_message(update)
    note = create_note(message)
    save(note, user)
    await confirm_message_saved(update, adapters)


def receive_message(update: Update) -> Message:
    message = update.message
    assert message
    return message


def create_note(message: Message) -> Note:
    mc = MessageChain()
    mc.attempt_to_append(message)
    return Note(mc)


def save(note: Note, user: User) -> None:
    assert user.auth_token

    note_content = render_html(note)
    save_to_file(note_content)
    send_to_evernote(note.header, note_content, user.auth_token)


def render_html(note: Note) -> str:
    template = Template(filename="tpl/note.mako")
    data = _gather_note_data(note)

    output = template.render(**data)
    return output


def _gather_note_data(note: Note) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "text": note.text,
        "header": note.header,
    }
    if note.message_link:
        data["message_link"] = note.message_link
    if note.links:
        data["links"] = note.links

    return data


async def confirm_message_saved(update: Update, adapters: Adapters):
    assert update.message is not None
    assert update.message.chat is not None

    CONFIRMATION_TEXT = "Saved!"
    chat_id = update.message.chat.id
    await adapters.telegram.send_message(chat_id, CONFIRMATION_TEXT)
