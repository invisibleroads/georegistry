'Regions controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
# Import system modules
import logging; log = logging.getLogger(__name__)
# Import custom modules
from georegistry.lib.base import BaseController, render


class RegionsController(BaseController):

    def index(self, responseFormat='html'):
        if responseFormat == 'html':
            return render('/regions/index.mako')

    def show(self, countryCode, responseFormat='html'):
        pass
