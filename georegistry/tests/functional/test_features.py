from georegistry.tests import *

class TestFeaturesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='features', action='index'))
        # Test response...
