from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.userstore.constants as UserStoreConstants
from evernote.api.client import EvernoteClient
from mako.template import Template

from config import get_settings


def send_to_evernote(title: str, content: str, auth_token: str) -> Optional[str]:
    settings = get_settings()

    try:
        note_store = get_note_store(auth_token, settings.evernote_sandbox_enabled)
    except RuntimeError:
        print("Using non up to date Evernote client, unable to save")
        return None

    template = Template(filename="tpl/evernote.mako")
    note_content = template.render(content=content).strip()

    note = Types.Note()
    note.title = title
    note.content = note_content
    created_note = note_store.createNote(note)

    print("Successfully created a new note with GUID: ", created_note.guid)
    return created_note.guid


@lru_cache
def get_note_store(auth_token: str, sandbox: bool) -> NoteStore:
    china = False
    client = EvernoteClient(token=auth_token, sandbox=sandbox, china=china)

    user_store = client.get_user_store()
    version_ok = user_store.checkVersion(
        "Evernote EDAMTest (Python)",
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR,
    )
    print("Is my Evernote API version up to date? ", str(version_ok))
    if not version_ok:
        raise RuntimeError("Evenote API version is not up to date")

    note_store = client.get_note_store()
    return note_store


def save_to_file(content: str) -> None:
    filename = _get_file_name()
    with open(f"notes/{filename}", "w") as f:
        f.write(content)
        f.flush()
    print(f"{filename} saved!")


def _get_file_name() -> str:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return f"{today}.html"
