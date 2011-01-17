<%inherit file="/base.mako"/>

<%def name="title()">Maps</%def>

<%def name="css()">
#mapOL {position: absolute; top: 0; left: 0; width: 50%; height: 100%}
#mapPM {position: absolute; top: 0; right: 0; width: 50%; height: 100%}
</%def>

<%def name="head()">
${h.stylesheet_link('/files/openlayers/theme/default/style.css')}
${h.stylesheet_link('/files/openlayers/theme/default/google.css')}
${h.javascript_link('/files/openlayers/OpenLayers.js')}
${h.javascript_link('http://maps.google.com/maps/api/js?sensor=false')}
</%def>

<%def name="js()">
<%
from georegistry import model
from georegistry.model import Session

personID = h.getPersonIDViaKey()
person = Session.query(model.Person).get(personID)
personKey = person.key if person else ''
%>
// Make map using OpenLayers
var mapOL = new OpenLayers.Map('mapOL'), layerOL;
mapOL.addControl(new OpenLayers.Control.LayerSwitcher());
mapOL.addLayers([
    new OpenLayers.Layer.Google("Google Physical", {type: google.maps.MapTypeId.TERRAIN}),
    new OpenLayers.Layer.Google("Google Streets", {numZoomLevels: 20}),
    new OpenLayers.Layer.Google("Google Hybrid", {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}),
    new OpenLayers.Layer.Google("Google Satellite", {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22})
]);
// Define controls
$('#tagText').change(updateMaps);
// Define functions
function updateMaps() {
    // Load parameters
    var tagText = $.trim($('#tagText').val() || "${request.params.get('tags', '') | h}");
    if (!tagText) return;
    // Set layer
    if (layerOL) {
        mapOL.removeLayer(layerOL);
        layerOL.destroy();
    }
    layerOL = new OpenLayers.Layer.Vector('Features', {
        strategies: [new OpenLayers.Strategy.BBOX()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "${h.url('map_view_', responseFormat='json')}",
            params: {
                key: "${personKey}",
                srid: 3857,
                tags: tagText
            },
            format: new OpenLayers.Format.GeoJSON(),
            callback: function() {
                alert('hey');
                mapOL.zoomToExtent(layerOL.getDataExtent());
            }
        })
    });
    mapOL.addLayer(layerOL);
}
// Prepare page
updateMaps();
</%def>

<%def name="toolbar()">
<%
from georegistry import model
from georegistry.model import Session

personID = h.getPersonIDViaKey()
visibleTags = Session.query(model.Tag).join(model.Tag.features).filter(model.getFeatureFilter(personID))
%>
<select id=tagText>
    <option value=""></option>
% for tag in visibleTags:
    <option value="${tag.text | h}">${tag.text}</option>
% endfor
</select>
</%def>

<div id=mapOL></div>
<div id=mapPM></div>
