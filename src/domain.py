from typing import Any, Dict, Optional

from mako.template import Template

from entities import Message, Update
from models import MessageChain, Note, User
from repo import Users
from transport import save_to_file, send_to_evernote


class NotAuthorized(Exception):
    pass


def process_update(update: Update, users: Users) -> None:
    user = authorize_by_update(update, users)
    note = create_note(update)
    save(note, user)


def authorize_by_update(update: Update, users: Users) -> User:
    message = get_message(update)
    if not message:
        raise NotAuthorized

    user = get_user_from_update(update, users)
    if user and user.auth_token:
        return user

    raise NotAuthorized


def get_message(update: Update) -> Optional[Message]:
    return update.message


def get_user_from_update(update: Update, users: Users) -> Optional[User]:
    assert update.message
    assert update.message.from_user

    user_id = str(update.message.from_user.id)
    user = users.get(user_id)
    return user


def create_note(update: Update) -> Note:
    message = get_message(update)
    assert message

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
