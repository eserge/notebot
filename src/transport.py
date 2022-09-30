from datetime import datetime, timezone
from typing import Optional

import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient
from mako.template import Template

from config import get_settings


def save_to_file(content: str) -> None:
    filename = _get_file_name()
    with open(f"notes/{filename}", "w") as f:
        f.write(content)
        f.flush()
    print(f"{filename} saved!")


def _get_file_name() -> str:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return f"{today}.html"


def send_to_evernote(title: str, content: str, auth_token: str) -> Optional[str]:
    settings = get_settings()
    sandbox = True
    china = False

    # Hardcoded AuthToken should be replaced with OAuth flow
    client = EvernoteClient(token=auth_token, sandbox=sandbox, china=china)
    user_store = client.get_user_store()

    version_ok = user_store.checkVersion(
        "Evernote EDAMTest (Python)",
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR,
    )
    print("Is my Evernote API version up to date? ", str(version_ok))
    if not version_ok:
        return None

    note_store = client.get_note_store()
    print("Creating a new note in the default notebook")

    template = Template(filename="tpl/evernote.mako")

    note = Types.Note()
    note.title = title
    note.content = template.render(content=content).strip()
    created_note = note_store.createNote(note)

    print("Successfully created a new note with GUID: ", created_note.guid)
    return created_note.guid
