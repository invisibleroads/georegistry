'Tags controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
# Import system modules
import logging; log = logging.getLogger(__name__)
import simplejson
# Import custom modules
from georegistry.lib.base import BaseController, render
from georegistry.lib import helpers as h
from georegistry import model
from georegistry.model import Session


class TagsController(BaseController):

    def index(self, responseFormat='html'):
        'Get tags with visible features'
        # Get responseFormat
        responseFormat = responseFormat.lower()
        if responseFormat not in ['json', 'html']:
            abort(400, 'Must specify a valid responseFormat: json, html')
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        # Get tags with visible features
        c.tags = Session.query(model.Tag).join(model.Tag.features).filter(model.getFeatureFilter(personID)).all()
        # If the user wants json,
        if responseFormat == 'json':
            return '\n'.join(sorted(x.text for x in c.tags))
        # If the user wants html,
        elif responseFormat == 'html':
            return render('/tags/index.mako')
