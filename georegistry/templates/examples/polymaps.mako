
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
                this.element.addEventListener('mouseover', getHoverFeature(this.data), false);
                // Set click listener
                // this.element.addEventListener('mouseclick', getSelectFeature(this.data), false);
                // Set color class
                this.element.setAttribute('class', 'q' + (this.data.id % 9) + '-' + 9);
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
            items.sort(function(a, b) {
                var nameA = a.name.toLowerCase(), nameB = b.name.toLowerCase();
                if (nameA < nameB) return -1;
                else if (nameA > nameB) return 1;
                else return 0;
            });
            // Display
            var listLines = [];
            $(items).each(function() {
                listLines.push('<div class="fN feature" id=d' + this.featureID + '>' + this.name + '</div>');
            });
            $('#list').html(listLines.join('\n'));
        });
        map.add(layer);
    }

    // Define function factories
    var listHover, listScroll = 1;
    function getHoverFeature(feature) {
        return function() {
            if (listHover) {
                listHover.attr('className', listHover.attr('className').replace('fH', 'fN'));
            }
            listHover = $('#d' + feature.id);
            listHover.attr('className', listHover.attr('className').replace('fN', 'fH'));
            if (listScroll) {
                var list = $('#list');
                list.scrollTop(list.scrollTop() + listHover.position().top - list.height() / 2);
            }
        };
    }
    var selectFeatureByID = {}
    function getSelectFeature(feature) {
        return function() {
        };
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
    map.container().setAttribute('class', 'Spectral');
</%def>
