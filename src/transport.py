import binascii
import hashlib
import os
from datetime import datetime, timezone
from typing import Optional

import yagmail
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
from evernote.api.client import EvernoteClient

from config import get_settings


def send_email(subject: str, message: str) -> bool:
    settings = get_settings()
    yag = yagmail.SMTP(settings.smtp_user, settings.smtp_pass)
    errors = yag.send(settings.evernote_email, subject, message)
    if not errors:
        print(f"Sent '{subject}' successfully")
    else:
        print(f"Failed to send '{subject}'")
        return False

    return True


def save_to_file(content: str) -> None:
    filename = _get_file_name()
    with open(f"notes/{filename}", "w") as f:
        f.write(content)
        f.flush()
    print(f"{filename} saved!")


def _get_file_name() -> str:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return f"{today}.html"


def send_to_evernote(title: str, content: str) -> Optional[str]:
    settings = get_settings()
    sandbox = True
    china = False

    # Hardcoded AuthToken should be replaced with OAuth flow
    client = EvernoteClient(
        token=settings.evernote_auth_token, sandbox=sandbox, china=china
    )
    user_store = client.get_user_store()

    version_ok = user_store.checkVersion(
        "Evernote EDAMTest (Python)",
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR,
    )
    print("Is my Evernote API version up to date? ", str(version_ok))
    if not version_ok:
        return

    note_store = client.get_note_store()
    print("Creating a new note in the default notebook")

    note = Types.Note()
    note.title = title

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += (
        "<!DOCTYPE en-note SYSTEM " '"http://xml.evernote.com/pub/enml2.dtd">'
    )
    note.content += "<en-note>"
    note.content += content
    note.content += "</en-note>"

    created_note = note_store.createNote(note)
    print("Successfully created a new note with GUID: ", created_note.guid)
    return created_note.guid
