from datetime import datetime, timezone

import yagmail
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
