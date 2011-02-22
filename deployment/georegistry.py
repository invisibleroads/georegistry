'GeoRegistry API Python wrapper'
# Import system modules
import urllib
import urllib2
import simplejson


# Core

baseURL = 'http://georegistry.invisibleroads.com'

def updateFeatures(key, srid, featureCollection, tags, public=False):
    'Update features using the GeoRegistry web service'
    # Initialize
    url = baseURL + '/features'
    # Call
    responseData = call(url, {
        'key': key,
        'srid': srid,
        'featureCollection': featureCollection,
        'tags': '\n'.join(tags),
        'public': 1 if public else 0,
    }, 'POST')
    # Return
    return [int(x) for x in responseData.splitlines()]

def deleteFeatures(key, featureIDs):
    'Delete features using the GeoRegistry web service'
    # Initialize
    url = baseURL + '/features'
    # Call
    call(url, {
        'key': key,
        'featureIDs': '\n'.join(str(x) for x in featureIDs),
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
    return responseData.splitlines()

def viewMaps(key, srid, tags, simplified=True, bboxFormat='yxyx', bbox=None):
    'Assemble a map using the GeoRegistry web service'
    # Initialize
    url = baseURL + '/maps'
    # Call
    responseData = call(url + '.json', {
        'key': key,
        'srid': srid,
        'tags': '\n'.join(tags),
        'bboxFormat': bboxFormat,
        'bbox': bbox if bbox else '',
        'simplified': 1 if simplified else 0,
    }, 'GET')
    # Return
    return responseData


# Helpers

def call(url, valueByName, method):
    'Call a method in the GeoRegistry web service'
    requestData = urllib.urlencode(valueByName.items())
    request = Request(method, url, requestData) if method.upper() == 'POST' else Request(method, url + '?' + requestData)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, error:
        raise GeoRegistryError(error.read())
    return response.read()

class Request(urllib2.Request):

    def __init__(self, method, *args, **kwargs):
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method


# Error

class GeoRegistryError(Exception):
    pass
