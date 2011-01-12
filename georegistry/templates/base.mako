## -*- coding: utf-8 -*-
<!doctype html>
<html>
<head>
<meta name="author" content="Roy Hyunjin Han" />
<link rel="shortcut icon" href="/files/favicon.ico">
${h.javascript_link('/files/jquery-1.4.2.min.js')}
${h.stylesheet_link('/files/style.css')}
<title>${h.SITE_NAME} ${self.title()}</title>
<style>${self.css()}</style>\
${self.head()}\
<script>
$(document).ready(function() {
    $('input').addClass('normalFONT');
    $('textarea').addClass('normalFONT');
    $('select').addClass('normalFONT');
    $('a').hover(
        function () {this.className = this.className.replace('OFF', 'ON');}, 
        function () {this.className = this.className.replace('ON', 'OFF');}
    );
    function getNumber(x) {return /\d+/.exec(x)[0]}
    function getID(obj) {return getNumber(obj.id)}
    ${self.js()}\
});
</script>
</head>
<body class=normalFONT>
<div id=header>
<div id=toolbar>${self.toolbar()}</div>
<div id=navigation>
${self.navigation()}
<%
linkPacks = [
    ('People', h.url('person_index')),
]
if h.isPerson():
    linkPacks.append((session['nickname'], h.url('person_update')))
%>\
% for linkName, linkURL in linkPacks:
&nbsp;
% if request.path != linkURL:
<a href="${linkURL}" class=linkOFF>${linkName}</a>
% else:
<b>${linkName}</b>
% endif
% endfor
% if not h.isPerson():
% if not request.path.startswith('/people/login'):
&nbsp;
<a href="${h.url('person_login', url=request.path)}" class=linkOFF>Login</a>
% endif
% else:
&nbsp;
<a href="${h.url('person_logout', url=request.path)}" class=linkOFF>Logout</a>
% endif
</div>
</div>
<div id=main>${next.body()}</div>
</body>
</html>\
<%def name='title()'></%def>\
<%def name='css()'></%def>\
<%def name='head()'></%def>\
<%def name='js()'></%def>\
<%def name='toolbar()'></%def>\
<%def name='navigation()'></%def>\
