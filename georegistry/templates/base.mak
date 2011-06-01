<!doctype html>
<html lang=en>
<head>
    <meta charset=utf-8 />
	<meta name=author content='Roy Hyunjin Han' />
	<title>${SITE_NAME} ${self.title()}</title>
	<link rel=icon href='${request.static_url('georegistry:static/favicon.ico')}' />
	<link rel=stylesheet href='${request.static_url('georegistry:static/style.css')}' />
	<style>${self.css()}</style>
</head>
<body>
<div id=header>
	<div id=toolbar>${self.toolbar()}</div>
	<div id=navigation>${self.navigation()}
	<%
	linkPacks = [
		('Home', '/'),
		('Users', request.route_path('user_index')),
	]
	if USER_ID:
		linkPacks.append((USER_NICKNAME, request.route_path('user_update')))
	path = request.path
	%>
% for linkName, linkPath in linkPacks:
	&nbsp;
	% if linkPath != path:
		<a href='${linkPath}' class='hover link off'>${linkName}</a>
	% else:
		<b>${linkName}</b>
	% endif
% endfor
	&nbsp;
	% if USER_ID:
		<a href="${request.route_path('user_logout', _query=dict(url=request.path))}" class='hover link off'>Logout</a>
	% elif path != request.route_path('user_login') and request.exception.__class__.__name__ != 'Forbidden':
		<a href="${request.route_path('user_login', _query=dict(url=request.path))}" class='hover link off'>Login</a>
	% else:
		<b>Login</b>
	% endif
	</div>
</div>
<div id=main>
	${next.body()}
</div>
<script src="${request.static_url('georegistry:static/jquery-1.6.1.min.js')}"></script>
${self.root()}
<script>
	function getNumber(x) {return /\d+/.exec(x)[0]}
	function getID(obj) {return getNumber(obj.id)}
    $('.hover').live({
        mouseenter: function() {$(this).removeClass('off').addClass('on')},
        mouseleave: function() {$(this).removeClass('on').addClass('off')}
    });
    $.ajaxSetup({
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown) {
            if ('parsererror' == textStatus) {
                window.location = "${request.route_path('user_login')}?url=" + window.location.pathname;
            }
        }
    });
	${self.js()}
</script>
</body>
</html>\

<%def name='title()'></%def>\
<%def name='css()'></%def>\
<%def name='toolbar()'></%def>\
<%def name='navigation()'></%def>\
<%def name='root()'></%def>\
<%def name='js()'></%def>\
