<% 
import datetime
%>
% for offset in xrange(1410, -1, -30):
<option value=${offset}>${(datetime.datetime.utcnow() - datetime.timedelta(minutes=offset)).strftime('%I:%M %p')}</option>
% endfor
