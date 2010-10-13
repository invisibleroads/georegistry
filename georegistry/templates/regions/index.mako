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
var geoJSONReader = new OpenLayers.Format.GeoJSON();
// Define controls
$('#countryCode').change(updateMaps);
$('#regionLevel').change(updateMaps);
// Define functions
function updateMaps() {
    // Load parameters
    var countryCode = $('#countryCode').val();
    var regionLevel = $('#regionLevel').val();
    // Get json
    $.get("${h.url('region_show', countryCode='XXX', responseFormat='json')}".replace('XXX', countryCode), {
        regionLevel: regionLevel
    }, function(data) {
        // Remove features
        if (layerOL) {
            mapOL.removeLayer(layerOL);
            layerOL.destroy();
        }
        // Update controls
        $('#regionLevel').html('');
        for (var i = 0; i < data.regionLevelCount; i++) {
            $('#regionLevel').append('<option value=' + i + '>' + i + '</option>');
        }
        // Update features
        layerOL = new OpenLayers.Layer.Vector(data.countryName);
        layerOL.addFeatures(geoJSONReader.read(data.geojson));
        mapOL.addLayer(layerOL);
        mapOL.setCenter(new OpenLayers.LonLat(data.countryCenter), mapOL.getZoomForExtent(new OpenLayers.Bounds(data.countryBounds)) - 1);
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
<select id=regionLevel>
    <option value=0 selected=selected>0</option>
</select>
</%def>

<div id=mapOL></div>
<div id=mapPM></div>
