<%inherit file="/base.mako"/>

<%def name="title()">Regions</%def>

<%def name="css()">
#mapOL {position: absolute; top: 0; left: 0; width: 100%; height: 50%}
#mapPM {position: absolute; bottom: 0; left: 0; width: 100%; height: 50%}
</%def>

<%def name="head()">
// Load OpenLayers
${h.stylesheet_link('/files/openlayers/theme/default/style.css')}
${h.stylesheet_link('/files/openlayers/theme/default/google.css')}
${h.javascript_link('/files/openlayers/OpenLayers.js')}
// Load PolyMaps
// Load GoogleMaps
${h.javascript_link('http://maps.google.com/maps/api/js?sensor=false')}
</%def>

<%def name="js()">
// Define map using OpenLayers
var mapOL = new OpenLayers.Map('mapOL'), layerOL;
mapOL.addControl(new OpenLayers.Control.LayerSwitcher());
mapOL.addLayers([
    new OpenLayers.Layer.Google("Google Physical", {type: google.maps.MapTypeId.TERRAIN}),
    new OpenLayers.Layer.Google("Google Streets", {numZoomLevels: 20}),
    new OpenLayers.Layer.Google("Google Hybrid", {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}),
    new OpenLayers.Layer.Google("Google Satellite", {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22})
]);
// Define controls
$('#countryCode').change(updateMaps);
$('#divisionLevel').change(updateMaps);
// Define functions
function updateMaps() {
    // Load parameters
    var countryCode = $('#countryCode').val();
    var divisionLevel = $('#divisionLevel').val();
    // Get geojson


    // Consider getting json first and have geojson inside


    $.get("${h.url('region_show', countryCode='XXX', responseFormat='geojson')}".replace('XXX', countryCode), {
        divisionLevel: divisionLevel
    }, function(data) {
        // Remove features
        if (layerOL) {
            mapOL.removeLayer(layerOL);
            layerOL.destroy();
        }
        // Update controls
        // Update features
        // Set center
        mapOL.setCenter(new OpenLayers.LonLat(${c.mapCenter}), mapOL.getZoomForExtent(new OpenLayers.Bounds(${c.mapBox})) - 1);
    });
}
// Prepare page
updateMaps();
</%def>

<%def name="toolbar()">
<select id=countryCode>
% for countryCode, countryName in c.countryPacks:
    <option value=${countryCode}
    % if countryCode == c.countryCode:
    selected=selected
    % endif
    >${countryName}</option>
% endfor
</select>
<select id=divisionLevel>
    <option value=0 selected=selected>0</option>
</select>
</%def>

<div id=mapOL></div>
<div id=mapPM></div>
