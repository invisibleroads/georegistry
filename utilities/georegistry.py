'GeoRegistry API Python wrapper'
# Import system modules
import urllib2
import simplejson


# Core

def update(key, proj4, featureCollection, tags, isPublic):
    'Update features using the GeoRegistry web service'
    return call('http://georegistry.org/features', dict(
        key=key,
        proj4=proj4,
        featureCollection=featureCollection,
        tags=tags,
        isPublic=isPublic,
    ))

def delete(key, featureIDs):
    'Delete features using the GeoRegistry web service'
    return call('http://georegistry.org/features', dict(
        key=key,
        featureIDs=featureIDs,
    ))


# Helpers

def call(url, data):
    'Call a method in the GeoRegistry web service'
    responseData = simplejson.loads(urllib2.urlopen(url, simplejson.dumps(data)).read())
    isOk = int(responseData.get('isOk'))
    if not isOk:
        raise GeoRegistryError(responseData['message'])
    return responseData


# Error

class GeoRegistryError(Exception):
    pass
