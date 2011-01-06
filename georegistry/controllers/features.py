'Features controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
import simplejson
import geojson
# Import custom modules
from georegistry.lib import helpers as h
from georegistry.lib.base import BaseController, render


class FeaturesController(BaseController):

    def index(self):
        pass

    @jsonify
    def update(self):
        'Add new or edit existing features'
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        if not personID:
            return dict(isOk=0, message='Please log in or provide a valid key')
        # Load features
        try:
            features = geojson.loads(request.POST.get('featureCollection', '')).features
        except geojson.JSONDecodeError:
            return dict(isOk=0, message='Could not parse featureCollection as geojson')
        except AttributeError:
            return dict(isOk=0, message='Could not get features from featureCollection')
        if not features:
            return dict(isOk=0, message='featureCollection must have at least one feature')
        # Load nestedTags
        try:
            nestedTags = request.POST.get('nestedTags', '')
        except simplejson.JSONDecodeError:
            return dict(isOk=0, message='Could not parse nestedTags as json')
        if not nestedTags:
            return dict(isOk=0, message='nestedTags must have at least one tag')
        # Process tags
        # For each feature,
            # Add feature
            # Set tags
        # Return
    POST   /features (featureCollection=geojson, nestedTags=nestedDictionaries, key=string) --> isOk=boolean, featureIDs=integerList, traceback=string
        pass

    def delete(self):
    DELETE /features (featureIDs=integerList, key=string) --> isOk=boolean
        pass
