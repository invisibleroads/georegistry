'Features controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
# Import system modules
import logging; log = logging.getLogger(__name__)
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
        key = request.POST.get('key', '')
        if key:
            person = Session.query(model.Person).filter(model.Person.key==key).first()
            if not person:

            if person:
                personID = person.id

        personID = if key else h.getPersonID()
        # Load features
        # Load nestedTags
        # Process tags
        # For each feature,
            # Add feature
            # Set tags
        # Return
    POST   /features (features=geojson, nestedTags=nestedDictionaries, key=string) --> isOk=boolean, featureIDs=integerList, traceback=string
        pass

    def delete(self):
    DELETE /features (featureIDs=integerList, key=string) --> isOk=boolean
        pass
