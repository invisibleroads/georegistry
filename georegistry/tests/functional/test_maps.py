from georegistry.tests import *

class TestMapsController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='maps', action='index'))
        # Test response...
