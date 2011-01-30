<%inherit file='/examples/base.mako'/>

<%def name='title()'>Polymaps</%def>

<%def name='head()'>
${h.javascript_link('/files/polymaps.min.js')}
${h.stylesheet_link('/files/colorbrewer.css')}
</%def>

<%def name='css()'>
    .compass .back {fill: #eee; fill-opacity: .8}
    .compass .fore {stroke: #999; stroke-width: 1.5px}
    .compass rect.back.fore {fill: #999; fill-opacity: .3; stroke: #eee; stroke-width: 1px; shape-rendering: crispEdges} 
    .compass .direction {fill: none}
    .compass .chevron {fill: none; stroke: #999; stroke-width: 5px}
    .compass .zoom .chevron {stroke-width: 4px} 
    .compass .active .chevron, .compass .chevron.active {stroke: #fff}
    .compass.active .active .direction {fill: #999}
</%def>

<%def name='js()'>
    var propertyByNameByID = {}, elementsByID = {}, geometriesByID = {};
    function renderMaps() {
        // Load
        var tagString = getSelectedTags();
        // Clean
        if (layer) map.remove(layer);
        if (!tagString) return;
        layer = po.geoJson().url('${h.url("map_view_", responseFormat="json")}?key=' + $('#key').val() + '&srid=4326&tags=' + escape(tagString) + "&bboxFormat=xyxy&bbox={B}&simplified=1").on('load', function(e) {
            // For each feature,
            $(e.features).each(function() {
                // Load
                var featureID = this.data.id;
                // Store propertyByName
                propertyByNameByID[featureID] = this.data.properties;
                // Store element
                if (!elementsByID[featureID]) elementsByID[featureID] = []
                elementsByID[featureID].push(this.element);
                // Store geometry
                if (!geometriesByID[featureID]) geometriesByID[featureID] = []
                geometriesByID[featureID].push(this.data.geometry);
                // Set hover listener
                this.element.addEventListener('mouseover', getHoverFeature(featureID), false);
                this.element.addEventListener('mouseout', getUnhoverFeature(featureID), false);
                // Set click listener
                this.element.addEventListener('click', getSelectFeature(featureID), false);
                // Set color class
                this.element.setAttribute('class', getColorClass(featureID));
                // Set id
                this.element.setAttribute('id', 'e' + featureID);
            });
            // Initialize
            var items = [];
            // For each stored feature,
            for (featureID in propertyByNameByID) {
                // If the feature is visible,
                if ($('#e' + featureID).length) {
                    propertyByName = propertyByNameByID[featureID];
                    items.push({
                        featureID: featureID,
                        name: propertyByName['Name'] || featureID + ''
                    });
                } 
                // If the feature is not visible,
                else {
                    delete propertyByNameByID[featureID];
                }
            }
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
                    scrollList = 0;
                    getHoverFeature(getID(this))();
                    scrollList = 1;
                }, 
                function () {
                    scrollList = 0;
                    getUnhoverFeature(getID(this))();
                    scrollList = 1;
                }
            ).click(function() {
                getSelectFeature(getID(this))();
            });
        });
        map.add(layer);
    }

    // Define factories
    var scrollList = 1;
    function getHoverFeature(featureID) {
        return function(e) {
            // Highlight list entry
            var listHover = $('#d' + featureID);
            if (listHover) {
                listHover.removeClass('bN bS').addClass('bH');
                if (scrollList) {
                    // Scroll list
                    var list = $('#list');
                    list.scrollTop(list.scrollTop() + listHover.position().top - list.height() / 2);
                }
            }
            // Highlight map entry
            setFeatureColor(featureID, 'fH');
        };
    }
    function getUnhoverFeature(featureID) {
        return function(e) {
            // Restore list entry
            var listHover = $('#d' + featureID);
            listHover.removeClass('bH bS').addClass('bN');
            // Restore map entry
            setFeatureColor(featureID, getColorClass(featureID));
        }
    }
    function getSelectFeature(featureID) {
        return function(e) {
            if (selectedID && selectedID != featureID) {
                // Restore list entry
                var listSelect = $('#d' + selectedID);
                if (listSelect) listSelect.removeClass('bH bS').addClass('bN');
                // Restore map entry
                setFeatureColor(selectedID, getColorClass(selectedID));
            }
            // Load
            selectedID = featureID;
            // Highlight list entry
            var listSelect = $('#d' + selectedID);
            listSelect.removeClass('bN bH').addClass('bS');
            // Highlight map entry
            setFeatureColor(selectedID, 'fS');
            // Set feature detail
            var propertyByName = propertyByNameByID[selectedID], propertyLines = [];
            for (key in propertyByName) {
                propertyLines.push(key + ' = ' + propertyByName[key]);
            }
            propertyLines.sort();
            $('#detail').html('<div id=detailHeader>' + propertyByName['name'] + '</div><br>' + propertyLines.join('<br>'));
        };
    }
    function getColorClass(featureID) {
        return 'q' + (8 - (featureID % 9)) + '-' + 9;
    }
    function setFeatureColor(featureID, colorClass) {
        $(elementsByID[featureID]).each(function() {
            this.setAttribute('class', colorClass);
        });
    }

    // Make map using Polymaps
    var po = org.polymaps;
    map = po.map()
        .container(document.getElementById('map').appendChild(po.svg('svg')))
        .center({lat: 40.7143528, lon: -74.0059731})
        .zoom(0)
        .add(po.interact())
        .add(po.image().url(po.url('http://{S}tile.cloudmade.com/8f066e8fa23c4e0abb89650a38555a58/20760/256/{Z}/{X}/{Y}.png').hosts(['a.', 'b.', 'c.', ''])))
        .add(po.compass().pan('none'));
    map.container().setAttribute('class', 'Blues');
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
            // Initialize
            var mapExtent = map.extent(), mapLL = mapExtent[0], mapUR = mapExtent[1];
            var minLon = mapUR.lon, minLat = mapUR.lat, maxLon = mapLL.lon, maxLat = mapLL.lat;
            var geometries = geometriesByID[selectedID];
            var queue = [];
            for (var i = 0; i < geometries.length; i++) {
                queue.push(geometries[i].coordinates);
            }
            while (queue.length) {
                var object = queue.pop();
                if (typeof object[0] == 'number') {
                    var lon = object[0], lat = object[1];
                    if (lon < minLon) minLon = lon;
                    if (lon > maxLon) maxLon = lon;
                    if (lat < minLat) minLat = lat;
                    if (lat > maxLat) maxLat = lat;
                } else {
                    for (var i = 0; i < object.length; i++) {
                        queue.push(object[i]);
                    }
                }
            }
            // Scale to include more background
            var scalingFactor = 1.2;
            var xLengthHalved = (maxLon - minLon) / 2;
            var yLengthHalved = (maxLat - minLat) / 2;
            // Zoom to scaled feature extent
            map.extent([{
                lon: minLon + (1 - scalingFactor) * xLengthHalved,
                lat: minLat + (1 - scalingFactor) * yLengthHalved
            }, {
                lon: minLon + (1 + scalingFactor) * xLengthHalved,
                lat: minLat + (1 + scalingFactor) * yLengthHalved
            }]);
        }
    });
</%def>
