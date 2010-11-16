'Base Controller API'
# Import pylons modules
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
# Import custom modules
from georegistry.model.meta import Session


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            Session.remove()
