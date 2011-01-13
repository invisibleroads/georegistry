'GeoRegistry API Python wrapper'
# Import system modules
import urllib2
import simplejson


# Core

def update(key, proj4, featureCollection, tags, isPublic):
    'Update features using the GeoRegistry web service'
    return call('http://georegistry.org/features', {
        'key': key,
        'proj4': proj4,
        'featureCollection': featureCollection,
        'tags': tags,
        'isPublic': isPublic,
    }, 'POST')

def delete(key, featureIDs):
    'Delete features using the GeoRegistry web service'
    return call('http://georegistry.org/features', {
        'key': key,
        'featureIDs': featureIDs,
    }, 'DELETE')


# Helpers

def call(url, data, method):
    'Call a method in the GeoRegistry web service'
    request = Request(method, url, simplejson.dumps(data)).read()
    responseData = simplejson.loads(urllib2.urlopen(request))
    isOk = int(responseData.get('isOk'))
    if not isOk:
        raise GeoRegistryError(responseData['message'])
    return responseData

class Request(urllib2.Request):

    def __init__(self, method, *args, **kwargs):
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method


# Error

class GeoRegistryError(Exception):
    pass
