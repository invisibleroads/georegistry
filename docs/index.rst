GeoRegistry API
===============
- The ``key`` argument is an API key assigned on registration and visible on your account page.  If unspecified, only public features are visible.
- Elements of the ``tags`` argument are separated by newlines.
- Elements of the ``featureIDs`` argument are separated by newlines.
::

    POST   /features (key=string, proj4=string, featureCollection=geojson, tags=strings, public=binary) --> featureIDs=integers
    DELETE /features (key=string, featureIDs=integers)
    GET    /tags.json (key=string) --> tags=strings
    GET    /maps.json (key=string, proj4=string, tags=strings, bbox=reals, simplified=binary) --> featureCollection=geojson


Update features
---------------
Given geojson features, string tags and proj4 spatial reference, save each feature with the given properties and tags.  Set ``public=1`` to make the features publicly visible.  Specify ``id`` in a geojson feature to overwrite an existing feature; edit access is restricted to the API key that originally created the feature.
::

    POST   /features (key=string, proj4=string, featureCollection=geojson, tags=strings, public=binary) --> featureIDs=integers

In jQuery, multiple tags should be separated by newlines.
::

    $.post('http://georegistry.org/features', {
        key: YOUR_API_KEY,
        proj4: '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
        featureCollection: '{                                              \
            "type": "FeatureCollection",                                   \
            "features": [                                                  \
                {                                                          \
                    "type": "Feature",                                     \
                    "geometry": {                                          \
                        "type": "MultiPoint",                              \
                        "coordinates": [                                   \
                            [15.783471, -90.230759],                       \
                            [37.566535, 126.9779692],                      \
                            [5.555717, -0.196306],                         \
                            [14.836156, -91.521959]                        \
                        ]                                                  \
                    },                                                     \
                    "properties": {                                        \
                        "description": "Santa Eulalia; Seoul; Accra; Xela" \
                    }                                                      \
                }, {                                                       \
                    "type": "Feature",                                     \
                    "geometry": {                                          \
                        "type": "LineString",                              \
                        "coordinates": [                                   \
                            [41.8781136, -87.6297982],                     \
                            [33.7489954, -84.3879824],                     \
                            [37.7749295, -122.4194155]                     \
                        ]                                                  \
                    },                                                     \
                    "properties": {                                        \
                        "description": "Chicago; Atlanta; San Francisco"   \
                    }                                                      \
                }                                                          \
            ]                                                              \
        }',
        tags: 'business trips\nparties',
        public: 1
    }, function(data) {
        var featureIDs = data.split('\n');
    });

In Python, multiple tags should be entered as a list.
::

    # Add new features
    featureIDs = georegistry.updateFeatures(
        key=YOUR_API_KEY,
        proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
        featureCollection="""{
            "type": "FeatureCollection", 
            "features": [
                {
                    "type": "Feature", 
                    "geometry": {
                        "type": "LineString", 
                        "coordinates": [
                            [40.7143528, -74.0059731], 
                            [14.6133333, -90.5352778]
                        ]
                    },
                    "properties": {
                        "description": "New York --> Guatemala City",
                        "hours": 9
                    }
                }
            ]
        }""",
        tags=['flights'],
        public=True,
    )
    # Edit existing features by specifying featureIDs
    featureIDs = georegistry.updateFeatures(
        key=YOUR_API_KEY,
        proj4='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
        featureCollection="""{
            "type": "FeatureCollection", 
            "features": [{
                "id": %s,
                "type": "Feature", 
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [40.7143528, -74.0059731], 
                        [14.6133333, -90.5352778],
                        [14.836156, -91.521959]
                    ]
                },
                "properties": {
                    "description": "New York --> Guatemala City --> Xela",
                    "hours": 15
                }
            }]
        }""" % featureIDs[0],
        tags=['flights', 'trips'],
        public=False,
    )


Delete features
---------------
Given a list of featureIDs, delete corresponding features; delete access is restricted to the API key that originally created the feature.
::

    DELETE /features (key=string, featureIDs=integers)

In jQuery, multiple featureIDs should be separated by newlines.
::

    $.ajax({
        url: 'http://georegistry.org/features?key=' + YOUR_API_KEY + '&featureIDs=1%0A2',
        type: 'DELETE',
    });

In Python, multiple featureIDs should be entered as a list.
::

    georegistry.deleteFeatures(
        key=YOUR_API_KEY,
        featureIDs=[1, 2],
    )


Get tags
--------
Return tags with visible features.
::

    GET    /tags.json (key=string) --> tags=strings

jQuery
::

    $.get('http://georegistry.org/tags.json', {
        key: YOUR_API_KEY
    }, function(data) {
        var tags = data.split('\n');
    });

Python
::

    tags = georegistry.getTags(
        key=YOUR_API_KEY,
    )


Render maps
-----------
Given desired tags and desired proj4 spatial reference, get visible geojson features.  Optionally, specify a bounding box (minimum latitude, minimum longitude, maximum latitude, maximum longitude).  Set ``simplified=0`` to disable smart simplification.
::

    GET    /maps.json (key=string, proj4=string, tags=strings, bbox=reals, simplified=binary) --> featureCollection=geojson

jQuery
::
    
    $.get('http://georegistry.org/maps.json', {
        key: YOUR_API_KEY,
        proj4: '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs',
        tags: 'parties',
        bbox: '10, -100, 210, 100',
        simplified: 1
    }, function(data) {
        var mapGeoJSON = data;
    });

Python
::

    mapGeoJSON = georegistry.viewMaps(
        key=YOUR_API_KEY,
        proj4='+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs',
        tags=['parties'],
        bbox='10, -100, 210, 100',
        simplified=True,
    )

OpenLayers
::

Polymaps
::
