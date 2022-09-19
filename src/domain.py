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
    save(note)


def save(note: Note) -> None:
    note_content = render_html(note)
    save_to_file(note_content)


def render_html(note: Note) -> str:
    template = Template(filename="tpl/note.mako")
    data = _gather_note_data(note)

    output = template.render(**data)
    return output


def save_to_file(content: str) -> None:
    filename = _get_file_name()
    with open(f"notes/{filename}", "w") as f:
        f.write(content)
        f.flush()
    print(f"{filename} saved!")


def _gather_note_data(note: Note) -> dict:
    data = {
        "text": note.text,
    }
    if note.message_link:
        data["message_link"] = note.message_link
    if note.links:
        data["links"] = note.links

    return data


def _get_file_name() -> str:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return f"{today}.html"
