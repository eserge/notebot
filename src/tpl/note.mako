<%! import mako_filters as filters  %>
<html>
<body>
% if message_link:
<p><a href="${message_link}">${message_link}</a></p>
% else:
<p>This content couldn't be linked back.</p>
% endif
% for paragraph in text:
<p>${paragraph| filters.linebreaks, filters.links}</p>
% endfor
</body>
</html>
