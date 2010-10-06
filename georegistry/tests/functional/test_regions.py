from georegistry.tests import *

class TestRegionsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='regions', action='index'))
        # Test response...
