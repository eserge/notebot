<%!
    def linebreaks(text):
        return text.replace("\n", "<br/>\n")
%>
<html>
<body>
% if message_link:
<p><a href="${message_link}">${message_link}</a></p>
% else:
<p>This content couldn't be linked back.</p>
% endif
% for paragraph in text:
<p>${paragraph| linebreaks}</p>
% endfor
</body>
</html>
