from datetime import datetime, timezone
from mako.template import Template

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
    save_to_html(note)


def save_to_html(note: Note):
    template = Template(filename="tpl/note.mako")
    data = _gather_note_data(note)

    output = template.render(**data)
    filename = _get_file_name(note)
    with open(f"notes/{filename}", "w") as f:
        f.write(output)
        f.flush()
    print(f"{filename} saved!")


def _gather_note_data(note: Note) -> dict:
    data = {
        "text": note.text,
    }
    if note.link:
        data["link"] = note.link

    return data


def _get_file_name(note: Note) -> str:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return f"{today}-{note.id}.html"
