'GeoRegistry API Python wrapper'
# Import system modules
import urllib2
import simplejson


# Constants

baseURL = 'http://georegistry.org'


# Core

def updateFeatures(key, proj4, featureCollection, tags, isPublic):
    'Update features using the GeoRegistry web service'
    # Initialize
    url = baseURL + '/features'
    # Call
    responseData = call(url, {
        'key': key,
        'proj4': proj4,
        'featureCollection': featureCollection,
        'tags': simplejson.dumps(tags),
        'isPublic': isPublic,
    }, 'POST')
    # Return
    return responseData['featureIDs']

def deleteFeatures(key, featureIDs):
    'Delete features using the GeoRegistry web service'
    # Initialize
    url = baseURL + '/features'
    # Call
    call(url, {
        'key': key,
        'featureIDs': simplejson.dumps(featureIDs),
    }, 'DELETE')

def getTags(key):
    'Get tags with visible features using the GeoRegistry web service'
    # Initialize
    url = baseURL + '/tags'
    # Call
    responseData = call(url + '.json', {
        'key': key,
    }, 'GET')
    # Return
    return responseData['tags']

def viewMap(key, proj4, tags, xyz=None):
    'Assemble a map using the GeoRegistry web service'
    # Initialize
    url = baseURL + '/maps'
    # Expand
    if xyz:
        x, y, z = xyz
        url += '/%s/%s/%s' % (z, x, y)
    # Call
    responseData = call(url + '.json', {
        'key': key,
        'proj4': proj4,
        'tags': simplejson.dumps(tags),
    }, 'GET')
    # Return
    return responseData['geojson']


# Helpers

def call(url, data, method):
    'Call a method in the GeoRegistry web service'
    request = Request(method, url, data).read()
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
