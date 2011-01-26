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
    function renderMaps() {
        // Load
        var tagString = getSelectedTags();
        // Clean
        if (layer) {
            map.remove(layer);
        }
        if (!tagString) return;
        layer = po.geoJson().url('${h.url("map_view_", responseFormat="json")}?key=' + $('#key').val() + '&srid=4326&tags=' + escape(tagString) + "&bboxFormat=xyxy&bbox={B}&simplified=1").on('load', function (e) {
            for (var i = 0; i < e.features.length; i++) {
                var feature = e.features[i];
                feature.element.setAttribute('class', 'q' + (feature.data.id % 9) + '-' + 9);
            }
        });
        map.add(layer);
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
