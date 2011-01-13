GeoRegistry API
===============
- The ``key`` argument is an API key assigned on registration.  If unspecified, the user can only retrieve public features.
::

    POST   /features (key=string, proj4=string, featureCollection=geojson, tags=strings, isPublic=binary) --> isOk=binary, featureIDs=integers
    DELETE /features (key=string, featureIDs=integers) --> isOk=binary
    GET    /tags.json (key=string) --> tags=strings
    GET    /maps.json (key=string, proj4=string, tags=strings) --> featureCollection=geojson
    GET    /maps/{Z}/{X}/{Y}.json (key=string, proj4=string, tags=strings) --> featureCollection=geojson


Edit features
-------------
Given geojson features, string tags and proj4 spatial reference, save each feature with the given properties and tags.  Set ``isPublic=1`` to make the features publicly visible.  Specify ``id`` in a geojson feature to overwrite an existing feature; edit access is restricted to the API key that originally created the feature.
::

    POST   /features (key=string, proj4=string, featureCollection=geojson, tags=strings, isPublic=binary) --> isOk=binary, featureIDs=integers


Delete features
---------------
Given a integer list of featureIDs, delete corresponding features; delete access is restricted to the API key that originally created the feature.
::

    POST   /features/delete (key=string, featureIDs=integers) --> isOk=binary


Get tags
--------
Return visible tags.
::

    GET    /tags.json (key=string) --> tags=strings


Render maps
-----------
Given desired tags and desired proj4 spatial reference, get visible geojson features.  Optionally, specify zoom level and tile coordinates.
::

    GET    /maps.json (key=string, proj4=string, tags=strings) --> featureCollection=geojson
    GET    /maps/{Z}/{X}/{Y}.json (key=string, proj4=string, tags=strings) --> featureCollection=geojson
