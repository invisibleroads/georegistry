'Examples controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
# Import system modules
import logging; log = logging.getLogger(__name__)
# Import custom modules
from georegistry.lib.base import BaseController, render


class ExamplesController(BaseController):

    def openlayers(self):
        return render('/examples/openlayers.mako')

    def polymaps(self):
        return render('/examples/polymaps.mako')
