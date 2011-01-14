'Tags controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
# Import system modules
import logging; log = logging.getLogger(__name__)
import simplejson
# Import custom modules
from georegistry.lib.base import BaseController, render


class TagsController(BaseController):

    def index(self):
        'Get tags with visible features'
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        # Get responseFormat
        responseFormat = request.params.get('responseFormat', 'html').lower()
        if responseFormat not in ['html', 'json']:
            return simplejson.dumps(dict(isOk=0, message='Must specify a valid responseFormat: html, json'))
        # Get tags with visible features
        featureFilter = model.Feature.scope == model.scopePublic
        if personID:
            featureFilter |= model.Feature.owner_id == personID
        c.tags = Session.query(model.Tag).join(model.Tag.features).filter(featureFilter).all()
        # If the user wants html,
        if responseFormat == 'html':
            return render('/tags/index.mako')
        # If the user wants json,
        elif responseFormat == 'json':
            return simplejson.dumps(dict(isOk=1, tags=sorted(x.text for x in tags)))
