import binascii
import hashlib
import os
from datetime import datetime, timezone

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


def send_to_evernote() -> None:
    settings = get_settings()
    sandbox = True
    china = False

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
    print("")
    if not version_ok:
        exit(1)

    note_store = client.get_note_store()
    # List all of the notebooks in the user's account
    notebooks = note_store.listNotebooks()
    print("Found ", len(notebooks), " notebooks:")
    for notebook in notebooks:
        print("  * ", notebook.name)

    print()
    print("Creating a new note in the default notebook")
    print()

    # To create a new note, simply create a new Note object and fill in
    # attributes such as the note's title.
    note = Types.Note()
    note.title = "Test note from notebot"

    # To include an attachment such as an image in a note, first create a Resource
    # for the attachment. At a minimum, the Resource contains the binary attachment
    # data, an MD5 hash of the binary data, and the attachment MIME type.
    # It can also include attributes such as filename and location.
    image_path = constants_path = os.path.join(os.path.dirname(__file__), "enlogo.png")
    with open(image_path, "rb") as image_file:
        image = image_file.read()
    md5 = hashlib.md5()
    md5.update(image)
    hash = md5.digest()

    data = Types.Data()
    data.size = len(image)
    data.bodyHash = hash
    data.body = image

    resource = Types.Resource()
    resource.mime = "image/png"
    resource.data = data

    # Now, add the new Resource to the note's list of resources
    note.resources = [resource]

    # To display the Resource as part of the note's content, include an <en-media>
    # tag in the note's ENML content. The en-media tag identifies the corresponding
    # Resource using the MD5 hash.
    hash_hex = binascii.hexlify(hash)
    hash_str = hash_hex.decode("UTF-8")

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += (
        "<!DOCTYPE en-note SYSTEM " '"http://xml.evernote.com/pub/enml2.dtd">'
    )
    note.content += "<en-note>Here is the Evernote logo:<br/>"
    note.content += '<en-media type="image/png" hash="{}"/>'.format(hash_str)
    note.content += "</en-note>"
    notestring = """
    <p>This content couldn't be linked back.</p>
    <p>If you want Monero to be a real competitor to Bitcoin, you need to make XMR accepted on Pornhub.</p>
    """

    # Finally, send the new note to Evernote using the createNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    created_note = note_store.createNote(note)

    print("Successfully created a new note with GUID: ", created_note.guid)
