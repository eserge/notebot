<%! import mako_filters  %>
% if message_link:
<p><a href="${message_link}">${message_link}</a></p>
% else:
<p>This content couldn't be linked back.</p>
% endif
% for paragraph in text:
<p>${paragraph| mako_filters.xml_escape, mako_filters.linebreaks, mako_filters.links}</p>
% endfor
% if links:
<h3>Links:</h3>
<ul>
    % for link in links:
    <li><a href="${link['url'] | mako_filters.xml_escape }">${link['text']}</a></li>
    % endfor
</ul>
% endif
