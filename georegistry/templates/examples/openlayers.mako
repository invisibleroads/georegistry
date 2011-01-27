<%inherit file="/examples/base.mako"/>

<%def name="title()">Openlayers</%def>

<%def name="head()">
<link href='/files/openlayers/theme/default/style.css' media='screen' rel='stylesheet' type='text/css' /> 
<link href='/files/openlayers/theme/default/google.css' media='screen' rel='stylesheet' type='text/css' /> 
<script src='/files/openlayers/OpenLayers.js' type='text/javascript'></script> 
<script src='http://maps.google.com/maps/api/js?sensor=false' type='text/javascript'></script> 
</%def>

<%def name="css()">
.fNormal {background-color: #dddddd} 
.fHover {background-color: #ff9900}
.fSelect {background-color: #ffff00}
</%def>

<%def name="js()">
    function renderMaps() {
        // Load
        var tagString = getSelectedTags();
        if (layer) {
            map.removeLayer(layer);
            layer.destroy();
            layer = undefined;
            $('#list').html('');
            $('#detail').html('');
        }
        if (!tagString) return;
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
            var items = [], listLines = [];
            $(data.features).each(function() {
                items.push({
                    fid: this.fid,
                    name: this.attributes.name
                });
            });
            items.sort(function(a, b) {
                var nameA = a.name.toLowerCase(), nameB = b.name.toLowerCase();
                if (nameA < nameB) return -1;
                else if (nameA > nameB) return 1;
                else return 0;
            });
            $(items).each(function() {
                listLines.push('<div class="fNormal feature" id=f' + this.fid + '>' + this.name + '</div>');
            });
            $('#list').html(listLines.join('\n'));
            var oldFeatureID;
            $('#list .feature').hover(
                function () {
                    // Change div color
                    this.className = this.className.replace('fNormal', 'fHover');
                    // Change map color
                    listScroll = 0;
                    hoverControl.overFeature(layer.getFeatureByFid(getID(this)));
                }, 
                function () {
                    // Change div color
                    this.className = this.className.replace('fHover', 'fNormal');
                    // Change map color
                    hoverControl.outFeature(layer.getFeatureByFid(getID(this)));
                    listScroll = 1;
                }
            ).click(function() {
                var featureID = getID(this), feature = layer.getFeatureByFid(featureID);
                map.zoomToExtent(feature.geometry.getBounds().scale(1.25));
                if (featureID != oldFeatureID) {
                    selectControl.unselectAll();
                    selectControl.select(feature);
                    oldFeatureID = featureID;
                }
            });
        });
        layer.events.register('featuresremoved', null, function(data) {
            $(data.features).each(function() {
                $('#f' + this.fid).remove();
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
    var listHover, listScroll = 1;
    function hoverFeature(feature) {
        if (listHover) {
            listHover.attr('className', listHover.attr('className').replace('fHover', 'fNormal'));
        }
        listHover = $('#f' + feature.fid);
        listHover.attr('className', listHover.attr('className').replace('fNormal', 'fHover'));
        if (listScroll) {
            var list = $('#list');
            list.scrollTop(list.scrollTop() + listHover.position().top - list.height() / 2);
        }
    }
    function selectFeature(feature) {
        // Change style for corresponding list div
        var listSelect = $('#f' + feature.fid);
        listSelect.attr('className', listSelect.attr('className').replace('fHover', 'fSelect'));
        // Set feature detail
        var attributeByName = feature.attributes, attributeLines = [];
        for (key in attributeByName) {
            attributeLines.push(key + ' = ' + attributeByName[key]);
        }
        attributeLines.sort();
        $('#detail').html('<div id=detailHeader>' + attributeByName['name'] + '</div><br>' + attributeLines.join('<br>'));
    }
    function unselectFeature(feature) {
        // Clear feature detail
        $('#detail').html('');
        // Change style for corresponding list div
        var listSelect = $('#f' + feature.fid);
        listSelect.attr('className', listSelect.attr('className').replace('fSelect', 'fNormal'));
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
</%def>
