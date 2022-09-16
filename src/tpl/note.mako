<%!
import re

def linebreaks(text):
    return text.replace("\n", "<br/>\n")

def links(text):
    links = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text)
    if not links:
        return text

    for link in links:
        text = text.replace(link, f'<a href="{link}">{link}</a>')

    return text
%>
<html>
<body>
% if message_link:
<p><a href="${message_link}">${message_link}</a></p>
% else:
<p>This content couldn't be linked back.</p>
% endif
% for paragraph in text:
<p>${paragraph| linebreaks, links}</p>
% endfor
</body>
</html>
