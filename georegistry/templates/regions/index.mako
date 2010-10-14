<%inherit file="/base.mako"/>

<%def name="title()">Regions</%def>

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
// Define styles
<%text>
var colors = ["red", "green", "blue", "yellow", "cyan", "magenta"];
var countryStyle = new OpenLayers.StyleMap(new OpenLayers.Style(
    {
        fillColor: "${getColor}",
        fillOpacity: 0.1
    }, 
    {
        context: {
            getColor: function(feature) {
                return colors[getNumber(feature.id) % colors.length];
            }
        }
    }
));
</%text>
// Define controls
$('#countryCode').change(updateMaps);
$('#regionLevel').change(updateMaps);
// Define functions
function updateMaps() {
    // Load parameters
    var countryCode = $('#countryCode').val();
    var regionLevel = $('#regionLevel').val();
    // Get json
    $.get("${h.url('region_show', countryCode='XXX', responseFormat='json')}".replace('XXX', countryCode), function(data) {
        // Verify
        if (!data.isOk) {alert(data.message); return;}
        // Update controls
        $('#regionLevel').html('');
        for (var i = 0; i < data.regionLevelCount; i++) {
            $('#regionLevel').append('<option value=' + i + '>' + i + '</option>');
        }
        $('#regionLevel').val(regionLevel);
        // Update features
        mapOL.setCenter(new OpenLayers.LonLat(data.countryLongitude, data.countryLatitude), mapOL.getZoomForExtent(new OpenLayers.Bounds(data.countryLeft, data.countryBottom, data.countryRight, data.countryTop)));
    }, 'json');
    // Get geojson
    $.get("${h.url('region_show', countryCode='XXX', responseFormat='geojson')}".replace('XXX', countryCode), {
        regionLevel: regionLevel
    }, function(data) {
        // Remove features
        if (layerOL) {
            mapOL.removeLayer(layerOL);
            layerOL.destroy();
        }
        layerOL = new OpenLayers.Layer.Vector(countryCode, {styleMap: countryStyle});
        layerOL.addFeatures(geoJSONReader.read(data));
        mapOL.addLayer(layerOL);
    }, 'json');
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
