Welcome to georegistry's documentation!
=======================================
The ``key`` argument is an API key that is assigned upon registration.  If not specified, the user will still be able to retrieve public tags and maps.
::

    POST   /features (features=geojson, nestedTags=nestedDictionaries, key=string) --> isOk=boolean, featureIDs=integerList, traceback=string
    DELETE /features (featureIDs=integerList, key=string) --> isOk=boolean
    GET    /tags.json (key=string) --> nestedTags=nestedDictionaries
    GET    /maps.json (tags=stringList, filters=geojson, key=string) --> geojson for OpenLayers
    GET    /maps/{Z}/{X}/{Y}.json (tags=stringList, filters=geojson, key=string) --> geojson for Polymaps

Add features
------------
Given a geojson FeatureCollection and a list of tags, store and associate each individual feature with the given properties and tags.  Return featureIDs aligned with the original FeatureCollection.  On error, return traceback.

- Create tags that do not exist.
- Specify private tags with two leading underscores.  Features marked with a private tag will only be visible to the API key that originally created the feature.
- Specify hierarchical tags using nested dictionaries of strings, e.g. ``{parent1: {child1: {grandchild1: {}}, child2: {grandchild2: {}}}}``.

::

    POST   /features (features=geojson, nestedTags=nestedDictionaries, key=string) --> isOk=boolean, featureIDs=integerList, traceback=string

Edit features
-------------
Given a geojson FeatureCollection and a list of tags, overwrite features with matching featureIDs specified as ``id`` in each feature with the given properties and tags.

- Restrict edit access for each feature to the API key that originally created the feature.

::

    POST   /features (features=geojson, nestedTags=nestedDictionaries, key=string) --> isOk=boolean, featureIDs=integerList, traceback=string

Delete features
---------------
Given a integer list of featureIDs, delete corresponding features.

- Restrict delete access for each feature to the API key that originally created the feature.

::

    DELETE /features (featureIDs=integerList, key=string) --> isOk=boolean

Get tags
--------
Get a string list of tags.

- Return public tags.
- Return private tags corresponding to the given API key.

::

    GET    /tags.json (key=string) --> tags=stringList

Render maps for OpenLayers
--------------------------
Get features as geojson given a list of desired tags.  If filters are specified, return only those features that intersect the given filters.

- Return public tags that match the given tags and filters.
- Return private tags corresponding to the given API key that match the given tags and filters.

::

    GET    /maps.json (tags=stringList, filters=geojson, key=string) --> geojson for OpenLayers

Render maps for Polymaps
------------------------
Get features as geojson given a list of desired tags, zoom level and tile coordinates.  If filters are specified, return only those features that intersect the given filters.

- Return public tags that match the given tags and filters.
- Return private tags corresponding to the given API key that match the given tags and filters.

::

    GET    /maps/{Z}/{X}/{Y}.json (tags=stringList, filters=geojson, key=string) --> geojson for Polymaps
