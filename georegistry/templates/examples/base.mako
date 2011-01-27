## -*- coding: utf-8 -*-
<!doctype html> 
<html> 
<head> 

<title>${h.SITE_NAME} Example: ${self.title()}</title>
<meta name='author' content='Roy Hyunjin Han' /> 
<link rel='shortcut icon' href='/files/favicon.ico'> 
${h.javascript_link('/files/jquery-1.4.4.min.js')}

${self.head()}

<style> 
    a {text-decoration: none}
    #navigation {position: fixed; top: 0; left: 0; width: 20em; height: 8em; overflow: auto}
    #toolbar {position: fixed; top: 8em; left: 0; width: 20em; height: 8em; overflow: auto; background-color: #eeeeee}
    #list {position: fixed; top: 16em; left: 0; width: 20em; height: 8em; overflow: auto; background-color: #dddddd}
    #detail {position: fixed; top: 24em; left: 0; width: 20em; bottom: 0; overflow: auto; background-color: #cccccc}
    #detailHeader {font-size: x-large; font-weight: bold}
    #map {position: fixed; top: 0; right: 0; left: 20em; height: 100%}
    .normalFONT {font-family: Helvetica, Arial, sans-serif}
    .linkOFF {color: darkblue; background-color: white}
    .linkON {color: white; background-color: darkblue}
    .fNormal {background-color: #dddddd} 
    .fHover {background-color: #ff9900}
    .fSelect {background-color: #ffff00}
    .olLayerGoogleCopyright {display: none}
    ${self.css()}
</style> 

<script> 
var map, layer;

$(document).ready(function() {

    // Prepare page
    $('a').hover(
        function () {this.className = this.className.replace('OFF', 'ON');}, 
        function () {this.className = this.className.replace('ON', 'OFF');}
    );
    function getNumber(x) {return /\d+/.exec(x)[0]}
    function getID(obj) {return getNumber(obj.id)}
    function compareFeatureByName(a, b) {
        var nameA = a.name.toLowerCase(), nameB = b.name.toLowerCase();
        if (nameA < nameB) return -1;
        else if (nameA > nameB) return 1;
        else return 0;
    }

    // Define functions
    function refreshInterface() {
        loadTags();
        renderMaps();
    }
    function loadTags() {
        $.get('${h.url("tag_index_", responseFormat="json")}', {
            key: $('#key').val()
        }, function(data) {
            var targetDiv = $('#toolbar');
            $(data.split('\n')).each(function() {
                var tag = $.trim(this);
                if (!tag) return;
                targetDiv.append('<input type=checkbox class=tag value="' + tag + '">' + tag + '<br>');
            });
            $('.tag').change(renderMaps);
        });
    }
    function getSelectedTags() {
        var tags = [];
        $('.tag:checked').each(function() {
            tags.push(this.value);
        });
        return tags.join('\n');
    }
    ${self.js()}

    // Prepare page
    refreshInterface();
    $('#refresh').click(refreshInterface);
    $('#key').click(function() {this.select()}).focus();
});
</script> 
</head> 
<body class=normalFONT> 

<%
from georegistry import model
from georegistry.model import Session

personID = h.getPersonIDViaKey()
person = Session.query(model.Person).get(personID)
personKey = person.key if person else ''
%>
<div id=navigation>
    API Key<br>
    <input class=normalFONT id=key value='${personKey}'>
    <input class=normalFONT id=refresh type=button value=Refresh>
    <br>
    <a class=linkOFF href='${h.url("/docs")}'>See Documentation</a><br>
    <a class=linkOFF href='${h.url("person_register")}'>Get API Key</a><br>
% if not h.isPerson():
% if not request.path.startswith('/people/login'):
    <a class=linkOFF href="${h.url('person_login', url=request.path)}">Login</a>
% endif
% else:
    <a class=linkOFF href="${h.url('person_logout', url=request.path)}">Logout</a>
    &mdash;
    <a class=linkOFF href="${h.url('person_update')}">${session['nickname']}</a>
% endif
</div> 

<div id=toolbar></div> 
<div id=map></div> 
<div id=list></div>
<div id=detail></div>
${next.body()}

</body> 
</html>
<%def name='title()'></%def>
<%def name='head()'></%def>
<%def name='css()'></%def>
<%def name='js()'></%def>
