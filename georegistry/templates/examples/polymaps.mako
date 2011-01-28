
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
    var featurePackByID = {};
    function renderMaps() {
        // Load
        var tagString = getSelectedTags();
        // Clean
        if (layer) map.remove(layer);
        if (!tagString) return;
        layer = po.geoJson().url('${h.url("map_view_", responseFormat="json")}?key=' + $('#key').val() + '&srid=4326&tags=' + escape(tagString) + "&bboxFormat=xyxy&bbox={B}&simplified=1").on('load', function(e) {
            // For each feature,
            $(e.features).each(function() {
                // Store
                featurePackByID[this.data.id] = this;
                // Set hover listener
                this.element.addEventListener('mouseover', getHoverFeature(this), false);
                this.element.addEventListener('mouseout', getUnhoverFeature(this), false);
                // Set click listener
                this.element.addEventListener('click', getSelectFeature(this), false);
                // Set color class
                this.element.setAttribute('class', getColorClass(this.data.id));
                // Set id
                this.element.setAttribute('id', 'e' + this.data.id);
            });
            // Initialize
            var items = [];
            // For each stored feature,
            for (featureID in featurePackByID) {
                // If the feature is visible,
                if ($('#e' + featureID).length) {
                    items.push({
                        featureID: featureID,
                        name: featurePackByID[featureID].data.properties.name || featureID + ''
                    });
                } 
                // If the feature is not visible,
                else {
                    delete featurePackByID[featureID];
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
                    getHoverFeature(featurePackByID[getID(this)])();
                    scrollList = 1;
                }, 
                function () {
                    scrollList = 0;
                    getUnhoverFeature(featurePackByID[getID(this)])();
                    scrollList = 1;
                }
            ).click(function() {
                getSelectFeature(featurePackByID[getID(this)])();
            });
        });
        map.add(layer);
    }

    // Define factories
    var scrollList = 1;
    function getHoverFeature(featurePack) {
        return function(e) {
            // Load
            featureID = featurePack.data.id;
            // Highlight list entry
            var listHover = $('#d' + featureID);
            listHover.removeClass('bN bS').addClass('bH');
            if (scrollList) {
                // Scroll list
                var list = $('#list');
                list.scrollTop(list.scrollTop() + listHover.position().top - list.height() / 2);
            }
            // Highlight map entry
            featurePack.element.setAttribute('class', 'fH');
        };
    }
    function getUnhoverFeature(featurePack) {
        return function(e) {
            // Load
            var featureID = featurePack.data.id;
            // Restore list entry
            var listHover = $('#d' + featureID);
            listHover.removeClass('bH bS').addClass('bN');
            // Restore map entry
            featurePack.element.setAttribute('class', getColorClass(featureID));
        }
    }
    function getSelectFeature(featurePack) {
        return function(e) {
            if (selectedID && selectedID != featurePack.data.id) {
                // Restore list entry
                var listSelect = $('#d' + selectedID);
                if (listSelect) listSelect.removeClass('bH bS').addClass('bN');
                // Restore map entry
                var fP = featurePackByID[selectedID];
                if (fP) fP.element.setAttribute('class', getColorClass(selectedID));
            }
            // Load
            selectedID = featurePack.data.id;
            // Highlight list entry
            var listSelect = $('#d' + selectedID);
            listSelect.removeClass('bN bH').addClass('bS');
            // Highlight map entry
            featurePack.element.setAttribute('class', 'fS');
            // Set feature detail
            var propertyByName = featurePack.data.properties, propertyLines = [];
            for (key in propertyByName) {
                propertyLines.push(key + ' = ' + propertyByName[key]);
            }
            propertyLines.sort();
            $('#detail').html('<div id=detailHeader>' + propertyByName['name'] + '</div><br>' + propertyLines.join('<br>'));
        };
    }
    function getColorClass(featureID) {
        return 'q' + (featureID % 9) + '-' + 9;
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
            var featurePack = featurePackByID[selectedID];
            if (!featurePack || !featurePack.data.geometry) return;
            var minLon = 360, minLat = 360, maxLon = 0, maxLat = 0;
            $(featurePack.data.geometry.coordinates).each(function() {
                $(this).each(function() {
                    var lon = this[0], lat = this[1];
                    if (lon < minLon) minLon = lon;
                    if (lon > maxLon) maxLon = lon;
                    if (lat < minLat) minLat = lat;
                    if (lat > maxLat) maxLat = lat;
                });
            });
            map.extent([{lon: minLon, lat: minLat}, {lon: maxLon, lat: maxLat}]);
        }
    });
</%def>
