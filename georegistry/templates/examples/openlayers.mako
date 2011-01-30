<%inherit file="/examples/base.mako"/>

<%def name="title()">Openlayers</%def>

<%def name="head()">
<link href='/files/openlayers/theme/default/style.css' media='screen' rel='stylesheet' type='text/css' /> 
<link href='/files/openlayers/theme/default/google.css' media='screen' rel='stylesheet' type='text/css' /> 
<script src='/files/openlayers/OpenLayers.js' type='text/javascript'></script> 
<script src='http://maps.google.com/maps/api/js?sensor=false' type='text/javascript'></script> 
<style>
    .olLayerGoogleCopyright {display: none}
</style>
</%def>

<%def name="js()">
    function renderMaps() {
        // Load
        var tagString = getSelectedTags();
        if (layer) {
            map.removeLayer(layer);
            layer.destroy();
            layer = undefined;
            $('#detail').html('');
        }
        if (!tagString) {
            $('#list').html('');
            return;
        }
        // Update
        layer = new OpenLayers.Layer.Vector('Features', {
            projection: new OpenLayers.Projection('EPSG:4326'),
            strategies: [new OpenLayers.Strategy.BBOX()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: '/maps.json',
                params: {
                    key: $('#key').val(),
                    srid: 4326,
                    tags: tagString,
                    bboxFormat: 'yxyx',
                    simplified: 1
                },
                format: new OpenLayers.Format.GeoJSON()
            }),
            styleMap: rainbowStyle
        });
        layer.events.register('featuresadded', null, function(data) {
            // Initialize
            var items = [];
            // For each feature,
            $(data.features).each(function() {
                // Push
                items.push({
                    featureID: this.fid,
                    name: this.attributes.name || this.fid + ''
                });
            });
            // Sort
            items.sort(compareByName);
            // Display
            var listLines = [];
            $(items).each(function() {
                listLines.push('<div class="fN feature" id=d' + this.featureID + '>' + this.name + '</div>');
            });
            $('#list').html(listLines.join('\n'));
            $('#list .feature').hover(
                function () {
                    // Change div color
                    this.className = this.className.replace('bN', 'bH');
                    // Change map color
                    scrollList = 0;
                    hoverControl.overFeature(layer.getFeatureByFid(getID(this)));
                }, 
                function () {
                    // Change div color
                    this.className = this.className.replace('bH', 'bN');
                    // Change map color
                    hoverControl.outFeature(layer.getFeatureByFid(getID(this)));
                    scrollList = 1;
                }
            ).click(function() {
                var featureID = getID(this), feature = layer.getFeatureByFid(featureID);
                if (selectedID != featureID) {
                    selectControl.unselectAll();
                    selectControl.select(feature);
                    selectedID = featureID;
                }
            });
        });
        layer.events.register('featuresremoved', null, function(data) {
            $(data.features).each(function() {
                $('#d' + this.fid).remove();
            });
        });
        map.addLayer(layer);
        layer.refresh();
        // Add map hover
        var hoverControl = new OpenLayers.Control.SelectFeature([layer], {
            renderIntent: 'temporary',
            hover: true,
            highlightOnly: true,
            eventListeners: {
                featurehighlighted: function(e) {
                    hoverFeature(e.feature);
                },
            }
        });
        map.addControl(hoverControl);
        hoverControl.activate();
        // Add map select
        var selectControl = new OpenLayers.Control.SelectFeature([layer], {
            renderIntent: 'select',
            hover: false,
            highlightOnly: false,
            onSelect: function(f) {
                selectFeature(f);
            },
            onUnselect: function(f) {
                unselectFeature(f);
            }
        });
        map.addControl(selectControl);
        selectControl.activate();
    }
    var hoveredID, scrollList = 1;
    function hoverFeature(feature) {
        if (hoveredID && hoveredID != feature.fid) {
            // Restore list entry
            listHover = $('#d' + hoveredID);
            if (listHover) listHover.removeClass('bH bS').addClass('bN');
        }
        // Set
        hoveredID = feature.fid;
        // Highlight list entry
        listHover = $('#d' + hoveredID);
        if (listHover) {
            listHover.removeClass('bN bS').addClass('bH');
            if (scrollList) {
                // Scroll list
                var list = $('#list');
                list.scrollTop(list.scrollTop() + listHover.position().top - list.height() / 2);
            }
        }
    }
    function selectFeature(feature) {
        // Change style for corresponding list div
        var listSelect = $('#d' + feature.fid);
        listSelect.removeClass('bN bH').addClass('bS');
        // Set feature detail
        var attributeByName = feature.attributes, attributeLines = [];
        for (key in attributeByName) {
            attributeLines.push(key + ' = ' + attributeByName[key]);
        }
        attributeLines.sort();
        $('#detail').html('<div id=detailHeader>' + attributeByName['name'] + '</div><br>' + attributeLines.join('<br>'));
    }
    function unselectFeature(feature) {
        // Clear
        selectedID = undefined;
        // Clear feature detail
        $('#detail').html('');
        // Change style for corresponding list div
        var listSelect = $('#d' + feature.fid);
        listSelect.removeClass('bH bS').addClass('bN');
    }

    <%text>
    // Define styles
    var colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'];
    var rainbowStyle = new OpenLayers.StyleMap({
        'default': new OpenLayers.Style({
            fillColor: '${getColor}',
            fillOpacity: 0.2,
            strokeColor: '${getColor}',
            strokeWidth: 1,
            pointRadius: 5
        }, {
            context: {
                getColor: function(feature) {
                    return colors[getNumber(feature.fid) % colors.length];
                }
            }
        }),
        'temporary': new OpenLayers.Style({ 
            fillColor: '#ff9900', 
            fillOpacity: 0.6, 
            strokeColor: '#ff9900', 
            strokeOpacity: 1, 
            strokeWidth: 1.1
        }),
        'select': new OpenLayers.Style({
            fillColor: '#ffff00',
            fillOpacity: 0.6,
            strokeColor: '#ffff00',
            strokeOpacity: 1,
            strokeWidth: 1.1
        })
    });
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
        if (layer) {
            layer.refresh({force: true});
        }
    });
    var selectedID;
    $('#detail').hover(
        function() {
            if (selectedID) {
                $(this).css('background-color', '#b2b2b2');
            }
        },
        function() {
            $(this).css('background-color', '#cccccc');
        }
    ).click(function() {
        if (selectedID) {
            var feature = layer.getFeatureByFid(selectedID);
            if (feature && feature.geometry) {
                map.zoomToExtent(feature.geometry.getBounds().scale(1.2));
            }
        }
    });
</%def>
