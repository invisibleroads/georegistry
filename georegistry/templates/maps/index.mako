<%inherit file="/base.mako"/>

<%def name="title()">Maps</%def>

<%def name="css()">
#mapOL {position: absolute; top: 0; left: 0; width: 50%; height: 100%}
#mapPO {position: absolute; top: 0; right: 0; width: 50%; height: 100%}
#featuresPO {
    fill: none;
    stroke: black;
    stroke-width: 2px;
    vector-effect: non-scaling-stroke;
}
</%def>

<%def name="head()">
${h.stylesheet_link('/files/openlayers/theme/default/style.css')}
${h.stylesheet_link('/files/openlayers/theme/default/google.css')}
${h.javascript_link('/files/openlayers/OpenLayers.js')}
${h.javascript_link('/files/polymaps.min.js')}
${h.javascript_link('http://maps.google.com/maps/api/js?sensor=false')}
<style>
.olLayerGoogleCopyright {display: none}
</style>
<script>
var mapOL, layerOL;
var mapPO, layerPO;
</script>
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
mapOL = new OpenLayers.Map('mapOL', {
    projection: new OpenLayers.Projection("EPSG:3857")
});
mapOL.addControl(new OpenLayers.Control.LayerSwitcher());
mapOL.addLayers([
    new OpenLayers.Layer.Google("Google Physical", {type: google.maps.MapTypeId.TERRAIN}),
    new OpenLayers.Layer.Google("Google Streets", {numZoomLevels: 20}),
    new OpenLayers.Layer.Google("Google Hybrid", {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}),
    new OpenLayers.Layer.Google("Google Satellite", {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22})
]);
mapOL.setCenter((new OpenLayers.LonLat(-74.0059731, 40.7143528)).transform(new OpenLayers.Projection('EPSG:4326'), mapOL.getProjectionObject()), 0);


// Make map using Polymaps
var po = org.polymaps;
mapPO = po.map()
    .container(document.getElementById('mapPO').appendChild(po.svg('svg')))
    .center({lat: 40.7143528, lon: -74.0059731})
    .zoom(0)
    .add(po.interact())
    .add(po.image().url(po.url("http://{S}tile.cloudmade.com/8f066e8fa23c4e0abb89650a38555a58/20760/256/{Z}/{X}/{Y}.png").hosts(["a.", "b.", "c.", ""])));


// Define functions
function updateMaps() {
    // Load parameters
    var tagText = $.trim($('#tagText').val() || "${request.params.get('tags', '') | h}");
    if (!tagText) return;


    // Update OpenLayers
    if (layerOL) {
        mapOL.removeLayer(layerOL);
        layerOL.destroy();
    }
    layerOL = new OpenLayers.Layer.Vector('Features', {
        projection: new OpenLayers.Projection('EPSG:4326'),
        strategies: [new OpenLayers.Strategy.BBOX()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "${h.url('map_view_', responseFormat='json')}",
            params: {
                key: '${personKey}',
                srid: 4326,
                tags: tagText,
                bboxFormat: 'yxyx',
                simplified: 1
            },
            format: new OpenLayers.Format.GeoJSON()
        }),
        styleMap: new OpenLayers.StyleMap({
            fillColor: 'black',
            strokeColor: 'black',
            strokeWidth: 2,
            pointRadius: 5
        })
    });
    mapOL.addLayer(layerOL);
    layerOL.refresh();


    // Update Polymaps
    if (layerPO) {
        mapPO.remove(layerPO);
    }
    layerPO = po.geoJson().url("${h.url('map_view_', responseFormat='json')}?key=${personKey}&srid=4326&tags=" + tagText + "&bboxFormat=xyxy&bbox={B}&simplified=1");
    layerPO.id('featuresPO');
    mapPO.add(layerPO);
}
// Define controls
$('#tagText').change(updateMaps);
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
<div id=mapPO></div>
