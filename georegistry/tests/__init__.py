"""
Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
# Import pylons modules
from pylons import url
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from routes.util import URLGenerator
# Import system modules
from unittest import TestCase
from webtest import TestApp
import simplejson
# Import custom modules
import pylons.test
from georegistry import model
from georegistry.model import Session


__all__ = ['environ', 'url', 'TestController', 'adjust']
# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])
environ = {}


class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

    def assertEqualJSON(self, response, isOk):
        'Assert response JSON'
        responseData = simplejson.loads(response.body)
        print responseData
        self.assertEqual(responseData['isOk'], isOk)
        return responseData


# Helpers

def adjust(valueByName, **kwargs):
    'Adjust valueByName using specified key and value'
    return dict(valueByName.items() + kwargs.items())
