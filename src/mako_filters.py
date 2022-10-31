import re
from xml.sax.saxutils import escape

RE_LINK = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"  # noqa: W605

xml_escape = escape


def linebreaks(text):
    return text.replace("\n", "<br/>\n")


def links(text):
    links = re.findall(RE_LINK, text)
    if not links:
        return text

    for link in links:
        text = text.replace(link, f'<a href="{link}">{link}</a>')

    return text
