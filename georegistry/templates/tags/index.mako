<%inherit file="/base.mako"/>

<%def name="title()">Tags</%def>

<%def name="toolbar()">${len(c.tags)} tags</%def>

<%
import random
random.shuffle(c.tags)
%>

% for tag in c.tags:
${tag.text}<br>
% endfor
