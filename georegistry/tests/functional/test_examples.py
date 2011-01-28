from georegistry.tests import *

class TestExamplesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='examples', action='index'))
        # Test response...
