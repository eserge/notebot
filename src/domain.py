from typing import Any, Dict, Optional
from mako.template import Template

from entities import Message, Update
from models import MessageChain, Note
from transport import save_to_file, send_to_evernote


def get_message(update: Update) -> Optional[Message]:
    return update.message


def process_message(message: Optional[Message]) -> None:
    if not message:
        return None
    mc = MessageChain()
    mc.attempt_to_append(message)
    note = Note(mc)
    save(note)


def save(note: Note) -> None:
    note_content = render_html(note)
    save_to_file(note_content)
    send_to_evernote(note.header, note_content)


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
