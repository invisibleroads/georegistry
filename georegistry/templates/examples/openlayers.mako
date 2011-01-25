<%inherit file="/examples/base.mako"/>

<%def name="title()">Openlayers Plain</%def>

<%def name="head()">
<link href='/files/openlayers/theme/default/style.css' media='screen' rel='stylesheet' type='text/css' /> 
<link href='/files/openlayers/theme/default/google.css' media='screen' rel='stylesheet' type='text/css' /> 
<script src='/files/openlayers/OpenLayers.js' type='text/javascript'></script> 
<script src='http://maps.google.com/maps/api/js?sensor=false' type='text/javascript'></script> 
</%def>

<%def name="js()">
    function renderMaps() {
        // Load
        var tags = [];
        $('.tag:checked').each(function() {
            tags.push(this.value);
        });
        var tagString = tags.join('\n');
        // Clean
        if (layer) {
            map.removeLayer(layer);
            layer.destroy();
        }
        if (!tagString) return;
        // Update
        layer = new OpenLayers.Layer.Vector('Features', {
            projection: new OpenLayers.Projection('EPSG:4326'),
            strategies: [new OpenLayers.Strategy.BBOX()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: '/maps.json',
                params: {
                    srid: 4326,
                    tags: tagString,
                    bboxFormat: 'yxyx',
                    simplified: 1
                },
                format: new OpenLayers.Format.GeoJSON()
            }),
            styleMap: rainbowStyle
        });
        map.addLayer(layer);
        layer.refresh();
    }

    <%text>
    // Define styles
    var colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'];
    var rainbowStyle = new OpenLayers.StyleMap(new OpenLayers.Style({
        fillColor: '${getColor}',
        fillOpacity: 0.2,
        strokeColor: '${getColor}',
        strokeWidth: 1,
        pointRadius: 5
    }, {
        context: {
            getColor: function(feature) {
                return colors[getNumber(feature.id) % colors.length];
            }
        }
    }));
    </%text>

    // Make map using OpenLayers
    map = new OpenLayers.Map('map', {
        projection: new OpenLayers.Projection('EPSG:3857')
    });
    map.addControl(new OpenLayers.Control.LayerSwitcher());
    map.addLayers([
        new OpenLayers.Layer.Google('Google Physical', {type: google.maps.MapTypeId.TERRAIN}),
        new OpenLayers.Layer.Google('Google Streets', {numZoomLevels: 20}),
        new OpenLayers.Layer.Google('Google Hybrid', {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}),
        new OpenLayers.Layer.Google('Google Satellite', {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22})
    ]);
    map.setCenter((new OpenLayers.LonLat(-74.0059731, 40.7143528)).transform(new OpenLayers.Projection('EPSG:4326'), map.getProjectionObject()), 0);
    map.events.register('zoomend', null, function() {
        layer.refresh({force: true});
    });
</%def>
