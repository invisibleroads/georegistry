GeoRegistry API
===============
`GeoRegistry.org <http://georegistry.org>`_ is a free web service for storing geospatial data.

- The ``key`` argument is an API key assigned on registration and visible on your account page.  If unspecified, only public features are visible.
- Elements of the ``tags`` argument are separated by newlines.
- Elements of the ``featureIDs`` argument are separated by newlines.
- When reading or writing a geojson FeatureCollection in the latitude and longitude spatial reference, note that longitude is the **x** coordinate and latitude is the **y** coordinate.

::

    POST   /features (key=string, srid=integer, featureCollection=geojson, tags=strings, public=binary) --> featureIDs=integers
    DELETE /features (key=string, featureIDs=integers)
    GET    /tags.json (key=string) --> tags=strings
    GET    /maps.json (key=string, srid=integer, tags=strings, bboxFormat=string, bbox=reals, simplified=binary) --> featureCollection=geojson


Update features
---------------
Given a geojson featureCollection, string tags and spatial reference srid, save each feature with the given properties and tags.  

- Set ``public=1`` to make the features publicly visible.  
- Specify ``id`` in a geojson feature to overwrite an existing feature.  Edit access is restricted to the API key that originally created the feature.
- When writing a geojson FeatureCollection in the latitude and longitude spatial reference, note that longitude is the **x** coordinate and latitude is the **y** coordinate.

::

    POST   /features (key=string, srid=integer, featureCollection=geojson, tags=strings, public=binary) --> featureIDs=integers

In jQuery, multiple tags should be separated by newlines.
::

    $.post('http://georegistry.org/features', {
        key: YOUR_API_KEY,
        srid: 4326,
        featureCollection: '{                                              \
            "type": "FeatureCollection",                                   \
            "features": [                                                  \
                {                                                          \
                    "type": "Feature",                                     \
                    "geometry": {                                          \
                        "type": "MultiPoint",                              \
                        "coordinates": [                                   \
                            [-90.230759, 15.783471],                       \
                            [126.9779692, 37.566535],                      \
                            [-0.196306, 5.555717],                         \
                            [-91.521959, 14.836156]                        \
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
                            [-87.6297982, 41.8781136],                     \
                            [-84.3879824, 33.7489954],                     \
                            [-122.4194155, 37.7749295]                     \
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
        srid=4326,
        featureCollection="""{
            "type": "FeatureCollection", 
            "features": [
                {
                    "type": "Feature", 
                    "geometry": {
                        "type": "LineString", 
                        "coordinates": [
                            [-74.0059731, 40.7143528], 
                            [-90.5352778, 14.6133333]
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
        srid=4326,
        featureCollection="""{
            "type": "FeatureCollection", 
            "features": [{
                "id": %s,
                "type": "Feature", 
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-74.0059731, 40.7143528], 
                        [-90.5352778, 14.6133333],
                        [-91.521959, 14.836156]
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
Given a list of featureIDs, delete corresponding features.  Delete access is restricted to the API key that originally created the feature.
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

In jQuery, multiple tags will be separated by newlines.
::

    $.get('http://georegistry.org/tags.json', {
        key: YOUR_API_KEY
    }, function(data) {
        var tags = data.split('\n');
    });

In Python, multiple tags will be a list.
::

    tags = georegistry.getTags(
        key=YOUR_API_KEY,
    )


Render maps
-----------
Given desired tags and desired spatial reference srid, get visible geojson features.  

- Set ``simplified=0`` to disable smart simplification.
- Set ``bboxFormat=yxyx`` if you are using OpenLayers and ``bboxFormat=xyxy`` if you are using Polymaps.
- Specify a bounding box ``bbox`` to limit your result set.
- When reading a geojson FeatureCollection in the latitude and longitude spatial reference, note that longitude is the **x** coordinate and latitude is the **y** coordinate.

::

    GET    /maps.json (key=string, srid=integer, tags=strings, bboxFormat=string, bbox=reals, simplified=binary) --> featureCollection=geojson

In jQuery, you can retrieve the raw geojson.
::
    
    $.get('http://georegistry.org/maps.json', {
        key: YOUR_API_KEY,
        srid: 3857,
        tags: 'parties',
        bboxFormat: 'yxyx',
        bbox: '-180, -90, 180, 90',
        simplified: 1
    }, function(data) {
        var mapGeoJSON = data;
    });

In Python, you can retrieve the raw geojson.
::

    mapGeoJSON = georegistry.viewMaps(
        key=YOUR_API_KEY,
        srid=3857,
        tags=['flights'],
        bboxFormat: 'yxyx',
        bbox='-180, -90, 180, 90',
        simplified=True,
    )

OpenLayers
::

    layerOL = new OpenLayers.Layer.Vector('Features', {
        projection: new OpenLayers.Projection('EPSG:3857'),
        strategies: [new OpenLayers.Strategy.BBOX()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: 'http://georegistry.org/maps.json',
            params: {
                key: '${personKey}',
                srid: 3857,
                tags: tagText,
                bboxFormat: 'yxyx',
                simplified: 1
            },
            format: new OpenLayers.Format.GeoJSON()
        })
    });

Polymaps
::

    layerPO = po.geoJson().url("http://georegistry.org/maps.json?key=${personKey}&srid=4326&tags=" + tagText + "&bboxFormat=xyxy&bbox={B}&simplified=1");
